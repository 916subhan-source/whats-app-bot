import os
import re
import json
import random
import tempfile
import asyncio
from typing import Optional
import httpx
from datetime import datetime
from dotenv import load_dotenv
from menu import RESTAURANT_INFO, MENU, PIZZA_SIZES, PIZZA_CRUSTS

ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=ENV_PATH, override=True)

# ─────────────────────────────────────────────
# ⚡ High-Speed Local & Resilient Store (Replaces unreliable external KV)
# ─────────────────────────────────────────────
_kv_file = os.path.join(tempfile.gettempdir(), "cherry_peri_kv.json")
_mem_store = {}

def _load_disk_store():
    global _mem_store
    try:
        if os.path.exists(_kv_file):
            with open(_kv_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    _mem_store.update(data)
    except Exception:
        pass

def _save_disk_store():
    try:
        with open(_kv_file, "w", encoding="utf-8") as f:
            json.dump(_mem_store, f)
    except Exception:
        pass

_load_disk_store()

_http_client: Optional[httpx.AsyncClient] = None

def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(
            timeout=3.0,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=50)
        )
    return _http_client

async def get_kv(key: str, default=None):
    if key in _mem_store:
        return _mem_store[key]
    _load_disk_store()
    return _mem_store.get(key, default)

async def set_kv(key: str, val):
    _mem_store[key] = val
    _save_disk_store()

# In-memory caches for 0ms ultra-low latency
conversation_history = {}
welcomed_users = set()

async def get_history(phone_number: str) -> list:
    return await get_kv(f"hist_{phone_number}", default=[])

async def save_history(phone_number: str, history: list):
    trimmed = list(history[-10:])
    await set_kv(f"hist_{phone_number}", trimmed)

async def get_cart(phone_number: str) -> dict:
    import time
    now = time.time()
    cart = await get_kv(f"cart_{phone_number}")
    if not cart or not isinstance(cart, dict):
        cart = {"items": [], "address": None, "awaiting_address": False, "updated_at": now}
        await set_kv(f"cart_{phone_number}", cart)
        return cart

    # Auto-expire abandoned carts after 30 minutes of inactivity
    updated_at = cart.get("updated_at", 0)
    if cart.get("items") and updated_at and (now - updated_at > 1800):
        print(f"[CART EXPIRED] Expired stale cart for {phone_number} (>30m inactive).")
        cart = {"items": [], "address": None, "awaiting_address": False, "updated_at": now}
        await set_kv(f"cart_{phone_number}", cart)

    return cart

async def save_cart(phone_number: str, cart: dict):
    import time
    cart["updated_at"] = time.time()
    await set_kv(f"cart_{phone_number}", cart)

async def is_customer_welcomed(phone_number: str) -> bool:
    if phone_number in welcomed_users:
        return True
    is_welcomed = await get_kv(f"welcomed_{phone_number}")
    if is_welcomed:
        welcomed_users.add(phone_number)
        return True
    return False

async def mark_customer_welcomed(phone_number: str):
    welcomed_users.add(phone_number)
    await set_kv(f"welcomed_{phone_number}", True)

def get_all_items_map():
    all_items = {}
    for cat in MENU.values():
        for item in cat["items"]:
            all_items[item["id"]] = item
    return all_items

def format_phone_number(raw_phone: str) -> str:
    clean = re.sub(r"[^\d]", "", raw_phone)
    if clean.startswith("92") and len(clean) == 12:
        return f"0{clean[2:5]}-{clean[5:]}"
    elif clean.startswith("0") and len(clean) == 11:
        return f"{clean[:4]}-{clean[4:]}"
    elif clean.startswith("92") and len(clean) > 8:
        return f"0{clean[2:]}"
    return f"+{clean}" if clean else "Customer"

# Menu knowledge base string for Gemini AI
menu_lines = []
for cat in MENU.values():
    menu_lines.append(f"Category: {cat['name']} ({cat['emoji']})")
    for item in cat["items"]:
        prices_str = ""
        if "prices" in item:
            pr_parts = [f"{sz.title()}: Rs. {p}" for sz, p in item["prices"].items()]
            prices_str = " (" + ", ".join(pr_parts) + ")"
        else:
            prices_str = f" -> {RESTAURANT_INFO['currency']} {item.get('price', 0)}"
        desc = f" - {item.get('desc')}" if item.get("desc") else ""
        menu_lines.append(f"  * {item['name']}{prices_str}{desc}")
    menu_lines.append("")
menu_knowledge_base = "\n".join(menu_lines)

def build_system_instruction(customer_name: str, phone_number: str) -> str:
    formatted_phone = format_phone_number(phone_number)
    clean_name = RESTAURANT_INFO["name"].replace("🍕", "").strip().title()

    return f"""
You are the warm, polite, and attentive WhatsApp food ordering assistant for "{clean_name}" (Circular Road, Opposite Stylo Shopping Center, Dera Ismail Khan).

CUSTOMER PROFILE:
- Name: {customer_name}
- Phone: {formatted_phone}

CRITICAL RULES:

1. ⚠️ AMAZING DEALS (DEALS 1 TO 26) HAVE FIXED ITEMS & SIZES:
   - When a customer orders any Deal (e.g. "Deal 1", "Deal 2", "Deal 21", "Deal 22", etc.):
     * All items, sizes, and drinks in the deal are ALREADY FIXED in the official menu card!
     * NEVER ask what pizza size or burger flavor they want for a deal!
     * Accept the deal immediately: "Theek hai! Apna delivery address send karein." If address is already known, confirm the order immediately!

2. ONLY CLARIFY VAGUE STANDALONE / ALA CARTE ITEMS (NOT DEALS):
   - Only ask questions if the customer orders standalone single items without specifying:
     * If they say just "1 pizza" without size: ask size (Small Rs. 450, Medium Rs. 750, Large Rs. 1100, Family Rs. 1700).
     * If they say just "1 burger" without type: ask "Zinger burger, Anda burger ya Chapli burger?"
   - NEVER ask for size or item options if the customer ordered any Deal!

3. ORDER CONFIRMATION SLIP:
   - Output the slip when items/deals and delivery address are known:

*{clean_name}*
Order #FE-[Random 4 Digits] Confirmed ✅

*Customer Name:* {customer_name}
*Contact Number:* {formatted_phone}
*Delivery Address:* [Customer Address]

*Items:*
• [Qty]x [Item/Deal Name with components] — Rs. [Item Price x Qty]

*Food Total:* Rs. [Total Bill]
*Delivery Charges:* Payable to rider at delivery time
*Payment:* Cash on Delivery / Easypaisa (0341-5531083)
*Estimated Time:* {RESTAURANT_INFO['estimatedTime']}

Khana jald deliver hoga. Shukriya!

4. DELIVERY CHARGES POLICY:
   - Delivery charges are NOT free. They are calculated based on distance and paid directly to the rider at delivery time. NEVER say delivery is free.

5. EMOJI DENSITY RULE:
   - For short messages (greetings, questions, updates): use exactly 1 emoji.
   - For long messages (receipts, full menus, summaries): use at most 2 to 3 emojis total. No emoji spam!
   - Natural conversational Urdu / English.

COMPLETE MENU & EXACT PRICES (FROM OFFICIAL MENU PICTURES):
{menu_knowledge_base}
"""

async def call_gemini_ai(user_history, api_key: str, customer_name: str, phone_number: str) -> str:
    sys_instruction = build_system_instruction(customer_name, phone_number)
    contents = [
        {
            "role": "user",
            "parts": [{"text": f"System Instruction: {sys_instruction}"}]
        },
        {
            "role": "model",
            "parts": [{"text": f"Understood! Main {RESTAURANT_INFO['name']} ka manager hoon. Customer {customer_name} (+{phone_number}) ke sath warmly baat karunga aur final order par exact digital receipt slip banaunga."}]
        }
    ]
    contents.extend(user_history)

    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 600
        }
    }

    # Fast official low-latency models with strict 2.5s timeout
    models_to_try = [
        os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
        "gemini-2.0-flash"
    ]

    client = get_http_client()
    last_err = None
    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        try:
            response = await client.post(url, json=payload, timeout=2.5)
            if response.status_code == 200:
                data = response.json()
                if "candidates" in data and len(data["candidates"]) > 0:
                    parts = data["candidates"][0].get("content", {}).get("parts", [])
                    for p in parts:
                        if "text" in p and not p.get("thought", False):
                            return p["text"].strip()
                    if parts and "text" in parts[0]:
                        return parts[0]["text"].strip()
            elif response.status_code in (401, 403):
                raise ValueError("Invalid Gemini API Key")
            else:
                last_err = f"{model_name} status {response.status_code}"
        except Exception as e:
            if "Invalid Gemini API Key" in str(e):
                raise
            last_err = str(e)

    raise ValueError(f"Gemini API generation failed: {last_err}")

def format_cart_summary(cart):
    subtotal = 0
    items_list = ""
    for item in cart.get("items", []):
        item_total = item["price"] * item["quantity"]
        subtotal += item_total
        items_list += f"• *{item['quantity']}x {item['name']}* — Rs. {item_total}\n"
    total = subtotal
    return items_list.strip(), subtotal, total

def create_order_placement_slip(order_id: str, customer_name: str, phone_number: str, address: str, cart: dict) -> str:
    formatted_phone = format_phone_number(phone_number)
    items_list, subtotal, total = format_cart_summary(cart)
    if not items_list:
        items_list = "• Order items discussed in chat"
    clean_name = RESTAURANT_INFO["name"].replace("🍕", "").strip().title()

    return (
        f"*{clean_name}*\n"
        f"Order {order_id} Confirmed ✅\n\n"
        f"*Customer Name:* {customer_name}\n"
        f"*Contact Number:* {formatted_phone}\n"
        f"*Delivery Address:* {address.strip()}\n\n"
        f"*Items:*\n"
        f"{items_list}\n\n"
        f"*Food Total:* Rs. {total}\n"
        f"*Delivery Charges:* Payable to rider at delivery time\n"
        f"*Payment:* Cash on Delivery / Easypaisa (0341-5531083)\n"
        f"*Estimated Time:* {RESTAURANT_INFO['estimatedTime']}\n\n"
        f"Khana jald deliver hoga. Shukriya!"
    )

def get_human_menu_text() -> str:
    return (
        f"📋 *{RESTAURANT_INFO['name']} — New Menu* 🍽️\n\n"
        f"🌟 *Amazing Deals (1 to 26):*\n"
        f"  • *Deal 1* (Rs. 800): 1 Small Pizza + 1 Zinger Burger + 1L Drink\n"
        f"  • *Deal 3* (Rs. 900): 2 Zinger Burger + 2 Chicken Shawarma + 1L Drink\n"
        f"  • *Deal 11* (Rs. 1,400): 5 Zinger Burger + 1.5L Drink\n"
        f"  • *Deal 21* (Rs. 400): 1 Zinger Burger + Fries + 1 Regular Drink\n"
        f"  • *Deal 22* (Rs. 2,200): 2 Large Pizza + 1.5L Drink\n"
        f"  *(Deals 1 se 26 ki complete photos saath send kar di hain!)*\n\n"
        f"🍕 *Pizzas (Any Flavor):*\n"
        f"  • Small: Rs. 450 (Reg) / Rs. 600 (Special)\n"
        f"  • Medium: Rs. 750 (Reg) / Rs. 950 (Special)\n"
        f"  • Large: Rs. 1,100 (Reg) / Rs. 1,300 (Special)\n"
        f"  • Family: Rs. 1,700 (Reg) / Rs. 2,000 (Special)\n"
        f"  • Square Pizza: Rs. 1,050\n\n"
        f"🍔 *Burgers & Shawarma:*\n"
        f"  • Zinger Burger: Rs. 350 (Reg) / Rs. 270 (Special)\n"
        f"  • Chicken Shawarma: Rs. 200 (Reg) / Rs. 150 (Special)\n"
        f"  • Zinger Shawarma: Rs. 300 (Reg) / Rs. 220 (Special)\n"
        f"  • Zinger Paratha Roll: Rs. 350 (Reg) / Rs. 270 (Special)\n\n"
        f"🛵 *Delivery:* Rider distance ke mutabiq collect karega (30-45 mins)\n"
        f"💵 *Payment:* Cash on Delivery / Easypaisa (0341-5531083)\n\n"
        f"Order karne ke liye item ya deal ka naam send karein!"
    )

def extract_clean_address(raw_text: str) -> str:
    cleaned = re.sub(
        r"\b(?:pizza|burger|deal|deals|khana|order|bhejo|bhej\s*do|mangwana|send|chahiye|de\s*do|hai|hoga|bhejwa\s*do)\b",
        "",
        raw_text,
        flags=re.IGNORECASE
    )
    cleaned = re.sub(r"^\s*(?:on|at|pe|par|ko|for)\s+", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"\s+(?:pe|par|ko|mein|mai|par\s+bhej\s*do)$", "", cleaned, flags=re.IGNORECASE).strip()
    return cleaned or raw_text.strip()

async def generate_human_fallback(phone_number: str, message_text: str, customer_name: str = "Customer"):
    text = message_text.lower().strip()
    cart = await get_cart(phone_number)
    all_items_map = get_all_items_map()

    # 1. Greetings ("hi", "hello", "salam", "aoa", "hey")
    greetings = [
        "hi", "hello", "salam", "assalam o alaikum", "assalam alaikum", "asalam alaikum",
        "asalam o alaikum", "aoa", "hey", "start", "slam", "adaab", "kia hal hai",
        "kya haal hai", "kese ho", "kaisay ho", "kia hal", "kya hal"
    ]
    if any(text == g or text.startswith(f"{g} ") or text.endswith(f" {g}") for g in greetings):
        return f"Assalam-o-Alaikum {customer_name}! Cherry Peri Fast Food mein khush amdeed. Aaj kya mangwayein ge aap?"

    # 2. Menu request / Food list inquiry ("kia kia cheezen hain", "menu", "kya hai", "rate list")
    menu_inquiry_patterns = [
        r"\b(?:menu|mainue|manu|card|catalog|catalogue|rate\s*list|price\s*list)\b",
        r"\b(?:tasveer|tasweer|picture|pictures|pics|pic|photos)\b",
        r"\b(?:kya|kia)\s+.*(?:cheezen|cheezain|cheezein|chizen|chizain|cheez|items|khana)\b",
        r"\b(?:cheezen|cheez ain|cheezein|chizen|chizain)\s+.*(?:hain|hein|kya|kia)\b",
        r"\b(?:kya|kia)\s+(?:kya|kia|hai|hay|kuch|options|milta)\b",
        r"\b(?:kya|kia)\s+available\b",
        r"\b(?:show|send|bhejo|bhejein|dikhao|dikhayein)\s+.*(?:menu|list|card|rates)\b",
        r"\b(?:rate|rates|price|prices)\s+.*(?:kya|kia|batao|batayein)\b"
    ]
    is_menu_inquiry = (
        any(bool(re.search(pat, text)) for pat in menu_inquiry_patterns)
        or any(k in text for k in ["menu", "rate list", "price list", "tasveer", "tasweer", "kya hai", "kia hai", "kya kya", "kia kia", "cheezen", "cheezain", "cheezein"])
    )
    if is_menu_inquiry:
        return get_human_menu_text()

    # 3. Specific Category Inquiries (Deals, Pizzas, Burgers, Delivery Charges)
    if any(k in text for k in ["koi deal", "deals kya", "deals batao", "special deals", "deal konsi", "konsi deal", "viral deal"]):
        return (
            "🌟 *Cherry Peri — Special Deals:*\n\n"
            "1️⃣ *Student Viral Deal* — *Rs. 899*\n"
            "   • 1x 6\" Personal Pizza\n"
            "   • 1x Classic Zinger Burger + Fries\n"
            "   • 1x 345ml Cold Drink\n\n"
            "2️⃣ *Family Viral King Deal* — *Rs. 2,499*\n"
            "   • 1x 9\" Medium Pizza\n"
            "   • 4 Pcs Crispy Broast + Large Fries\n"
            "   • 1x 1.5 Ltr Cold Drink\n\n"
            "Order karne ke liye *Student Deal* ya *Family Deal* likhein! 😊"
        )

    if any(k in text for k in ["pizza flavors", "pizza flavor", "konsa pizza", "kaunsa pizza", "pizza options", "pizza menu", "pizza rates"]):
        return (
            "🍕 *Cherry Peri Pizza Flavors & Rates:*\n\n"
            "🔥 *Regular Pizzas:*\n"
            "• Chicken Tikka, Fajita, Tandoori, Hot N Spicy, Supreme, BBQ, Cheese Lover\n"
            "  6\" Personal: Rs. 500 | 9\" Medium: Rs. 800 | 13\" Large: Rs. 1400 | 17\" XL: Rs. 1900\n\n"
            "👑 *Special Pizzas:*\n"
            "• Malai Boti, Cherry Peri Special, Bihari Kabab, Mughlai, Super Supreme\n"
            "  6\" Personal: Rs. 600 | 9\" Medium: Rs. 950 | 13\" Large: Rs. 1600 | 17\" XL: Rs. 2100\n\n"
            "Apna pasandeeda flavor aur size batayein (e.g. *Tikka 17* ya *Malai Boti Large*)!"
        )

    if any(k in text for k in ["burger menu", "burgers kya", "konsa burger", "burger options"]):
        return (
            "🍔 *Cherry Peri Burgers & Sandwiches:*\n\n"
            "• Simple Zinger — Rs. 250\n"
            "• Zinger Burger with Cheese — Rs. 300\n"
            "• Afghani Burger — Rs. 350\n"
            "• Classic Zinger + Fries — Rs. 450\n"
            "• Cheese Zinger + Fries — Rs. 500\n"
            "• Chicken Grill Burger + Fries — Rs. 550\n"
            "• Mighty Zinger + Fries — Rs. 600\n"
            "• Cherry Peri Special Grill + Fries — Rs. 700\n\n"
            "Order karne ke liye burger ka naam batayein!"
        )

    if any(k in text for k in ["delivery charges", "delivery fee", "rider charges", "delivery free", "free delivery", "delivery kitni"]):
        return "Delivery charges location aur distance ke mutabiq rider delivery ke waqt collect karega. 🛵"

    # 4. View Cart / Total Bill
    if any(k in text for k in ["cart", "bill", "mera order", "total kitna", "basket", "kitne huwe", "kitne huway", "kitne paise", "total bill", "kitna bana", "kitna bill"]) and not any(k in text for k in ["clear", "cancel", "khatam"]):
        if not cart.get("items"):
            return f"Cart khali hai. Kya order karna chahenge?"
        _, _, total = format_cart_summary(cart)
        return f"Total bill Rs. {total} hai. Delivery address send karein."

    # 5. Clear / Cancel Cart
    if any(k in text for k in ["clear", "cancel", "khali", "delete", "nhi chahiye", "nahi chahiye", "band karo", "rehne do", "cancel order", "khatam"]):
        cart["items"] = []
        cart["address"] = None
        cart["awaiting_address"] = False
        await save_cart(phone_number, cart)
        return f"Theek hai, aapka order cancel kar diya gaya."

    # 6. Location / Timings / Payments
    if any(k in text for k in ["location", "kahan", "address", "adrs", "kidhar", "kider", "kaha par", "dukan kahan", "shop kahan"]):
        return "Opposite Stylo Shopping Center, Circular Road, D.I. Khan par hamara restaurant hai."

    if any(k in text for k in ["timing", "timings", "time", "kab tak", "open", "khula", "band", "close", "khulta", "kab band"]):
        return "Rozana dopehar 12:00 se raat 1:00 tak open hain."

    if any(k in text for k in ["payment", "payments", "pesay", "paise", "easypaisa", "easy paisa", "jazzcash", "jazz cash", "card", "online transfer", "account number"]):
        return "Cash on Delivery aur Easypaisa (0341-5531083 — Rashid Naveed) dono accept karte hain."

    # 6. Parse Food Items (Pizzas, Deals 1-26, Burgers, Shawarma, Paratha Rolls, etc.)
    found_items = []

    # ─────────────────────────────────────────────
    # A. 🌟 Amazing Deals 1 to 26 Parser
    # ─────────────────────────────────────────────
    DEALS_DATA = {
        1: {"name": "Deal 1 (1 Small Pizza + 1 Zinger Burger + 1L Drink)", "price": 800},
        2: {"name": "Deal 2 (2 Chicken Shawarma + 2 Chicken Paratha Roll + 1L Drink)", "price": 820},
        3: {"name": "Deal 3 (2 Zinger Burger + 2 Chicken Shawarma + 1L Drink)", "price": 900},
        4: {"name": "Deal 4 (2 Zinger + 1 Omelette Burger + 1 Shawarma + 1L Drink)", "price": 1000},
        5: {"name": "Deal 5 (10 Hot Wings + 10 Nuggets + 1L Drink)", "price": 940},
        6: {"name": "Deal 6 (1 Small Pizza + 2 Zinger + 1 Zinger Shawarma + 1L Drink)", "price": 1000},
        7: {"name": "Deal 7 (2 Small Pizza + 1L Drink)", "price": 950},
        8: {"name": "Deal 8 (1 Medium Pizza + 1 Chapli Burger + 5 Nuggets + 1L Drink)", "price": 1200},
        9: {"name": "Deal 9 (10 Nuggets + 2 Zinger Paratha + 2 Zinger Shawarma + 1L Drink)", "price": 1400},
        10: {"name": "Deal 10 (1 Small Pizza + 1 Zinger + 10 Hot Wings + 1L Drink)", "price": 1250},
        11: {"name": "Deal 11 (5 Zinger Burger + 1.5L Drink)", "price": 1400},
        12: {"name": "Deal 12 (3 Zinger Burger + 3 Zinger Shawarma + 1L Drink)", "price": 1500},
        13: {"name": "Deal 13 (2 Small Pizza + 5 Hot Wings + 1.5L Drink)", "price": 1250},
        14: {"name": "Deal 14 (1 Medium Pizza + 10 Hot Wings + 5 Nuggets + 1L Drink)", "price": 1450},
        15: {"name": "Deal 15 (2 Small Pizza + 2 Zinger Burger + 1.5L Drink)", "price": 1520},
        16: {"name": "Deal 16 (2 Medium Pizza + 1L Drink)", "price": 1550},
        17: {"name": "Deal 17 (5 Zinger Burger + 10 Hot Wings + 1L Drink)", "price": 1850},
        18: {"name": "Deal 18 (1 Large Pizza + 1 Zinger + 1 Shawarma + 5 Wings + 1.5L Drink)", "price": 1900},
        19: {"name": "Deal 19 (1 Large Pizza + 1 Zinger Paratha + 10 Wings + 1.5L Drink)", "price": 1900},
        20: {"name": "Deal 20 (1 Large Pizza + 1 Medium Pizza + 1.5L Drink)", "price": 1900},
        21: {"name": "Deal 21 (1 Zinger Burger + Fries + 1 Regular Drink)", "price": 400},
        22: {"name": "Deal 22 (2 Large Pizza + 1.5L Drink)", "price": 2200},
        23: {"name": "Deal 23 (1 Small Pizza + 1 Medium Pizza + 1.5L Drink)", "price": 1250},
        24: {"name": "Deal 24 (1 Large Pizza + 10 Hot Wings + 10 Nuggets + 1.5L Drink)", "price": 2000},
        25: {"name": "Deal 25 (5 Zinger Shawarma + 10 Wings + 1.5L Drink)", "price": 1600},
        26: {"name": "Deal 26 (5 Zinger Shawarma + 1.5L Drink)", "price": 1180},
    }

    deal_match = re.search(r"\b(?:deal|del|dele|d)\s*(?:no\.?|number|num)?\s*(\d{1,2})\b", text) or re.search(r"\b(\d{1,2})\s*(?:number|no\.?)?\s*deal\b", text)
    if deal_match:
        d_num = int(deal_match.group(1))
        if d_num in DEALS_DATA:
            qty = 1
            qty_m = re.search(r"\b(\d+)\s*(?:x\s*)?deal", text)
            if qty_m:
                qty = int(qty_m.group(1))
            elif re.search(r"\b(?:do|two)\s+(?:x\s*)?deal", text) or re.search(r"\bdeal\s*\d+\s*(?:do|two)\b", text):
                qty = 2
            elif re.search(r"\b(?:teen|three)\s+(?:x\s*)?deal", text) or re.search(r"\bdeal\s*\d+\s*(?:teen|three)\b", text):
                qty = 3
            elif re.search(r"\b(?:char|four)\s+(?:x\s*)?deal", text) or re.search(r"\bdeal\s*\d+\s*(?:char|four)\b", text):
                qty = 4
            deal_info = DEALS_DATA[d_num]
            found_items.append({
                "id": f"deal_{d_num}",
                "name": deal_info["name"],
                "price": deal_info["price"],
                "quantity": qty
            })

    # ─────────────────────────────────────────────
    # B. 🍕 Pizzas (Any Flavor & Sizing)
    # ─────────────────────────────────────────────
    explicit_size_tuple = None
    if any(s in text for s in ["family", "extra large", "xl", "xlarge", "17 inch", "17\""]) or re.search(r"\b17\b", text):
        explicit_size_tuple = ("family", "Family")
    elif any(s in text for s in ["large", "bada", "badi", "11 inch", "11\"", "13 inch", "13\""]) or re.search(r"\b(?:11|13)\b", text):
        explicit_size_tuple = ("large", "Large")
    elif any(s in text for s in ["small", "personal", "chota", "choti", "6 inch", "6\""]) or re.search(r"\b6\b", text):
        explicit_size_tuple = ("small", "Small")
    elif any(s in text for s in ["medium", "darmiyana", "darmiyani", "9 inch", "9\""]) or re.search(r"\b9\b", text):
        explicit_size_tuple = ("medium", "Medium")
    elif "square" in text:
        explicit_size_tuple = ("square", "Square")

    if explicit_size_tuple:
        size_selected, size_label = explicit_size_tuple
        cart["pending_pizza_size"] = size_selected
        cart["pending_pizza_size_label"] = size_label
    elif cart.get("pending_pizza_size"):
        size_selected = cart["pending_pizza_size"]
        size_label = cart.get("pending_pizza_size_label", "Medium")
    else:
        size_selected = None
        size_label = None

    PIZZA_CATALOG = [
        {"id": "sp_malaiboti", "name": "Malai Boti Special Pizza", "is_special": True, "keywords": ["malai boti", "malai botti", "malaiboti", "malai pizza"]},
        {"id": "sp_cherryperi", "name": "Cherry Peri Special Pizza", "is_special": True, "keywords": ["cherry peri special", "cherry peri pizza", "special pizza", "cherry peri"]},
        {"id": "sp_bihari", "name": "Bihari Kabab Special Pizza", "is_special": True, "keywords": ["bihari kabab", "bihari", "behari"]},
        {"id": "p_fajita", "name": "Chicken Fajita Pizza", "is_special": False, "keywords": ["fajita", "fajitha", "fajeeta", "fajeta", "chicken fajita"]},
        {"id": "p_tikka", "name": "Chicken Tikka Pizza", "is_special": False, "keywords": ["tikka", "tika", "chicken tikka", "teeka", "tikka pizza"]},
        {"id": "p_tandoori", "name": "Tandoori Pizza", "is_special": False, "keywords": ["tandoori", "tandori", "tanduri"]},
        {"id": "p_hotnspicy", "name": "Hot N Spicy Pizza", "is_special": False, "keywords": ["hot n spicy", "hot spicy", "hot and spicy"]},
        {"id": "p_bbq", "name": "BBQ Pizza", "is_special": False, "keywords": ["bbq", "barbeque", "bar b q"]},
        {"id": "p_cheese", "name": "Cheese Lover Pizza", "is_special": False, "keywords": ["cheese lover", "cheeselover"]},
        {"id": "p_square", "name": "Square Pizza", "is_special": False, "is_square": True, "keywords": ["square pizza", "square"]},
    ]

    # Only parse standalone pizzas if not already matched as a deal component
    if not found_items:
        matched_p_def = None
        for p_def in PIZZA_CATALOG:
            if any(kw in text for kw in p_def["keywords"]):
                matched_p_def = p_def
                break

        if not matched_p_def and ("pizza" in text or "piza" in text):
            # Generic pizza mentioned
            matched_p_def = {"id": "p_gen", "name": "Chicken Pizza", "is_special": "special" in text, "keywords": ["pizza"]}

        if matched_p_def:
            if matched_p_def.get("is_square"):
                found_items.append({"id": "pz_square", "name": "Square Pizza", "price": 1050, "quantity": 1})
            elif size_selected:
                qty = 1
                pattern = r"(\d+)\s*(?:x\s*)?(?:" + "|".join(re.escape(k) for k in matched_p_def["keywords"]) + ")"
                m = re.search(pattern, text)
                if m:
                    qty = int(m.group(1))
                elif any(w in text for w in ["do ", "2 ", " 2", "two "]):
                    qty = 2
                elif any(w in text for w in ["teen ", "3 ", " 3", "three "]):
                    qty = 3

                # Pricing: Regular (Small 450, Medium 750, Large 1100, Family 1700)
                # Special (Small 600, Medium 950, Large 1300, Family 2000)
                if matched_p_def.get("is_special"):
                    price_map = {"small": 600, "medium": 950, "large": 1300, "family": 2000}
                else:
                    price_map = {"small": 450, "medium": 750, "large": 1100, "family": 1700}

                price = price_map.get(size_selected, 750)
                item_name = f"{matched_p_def['name']} ({size_label})"
                found_items.append({"id": f"{matched_p_def['id']}_{size_selected}", "name": item_name, "price": price, "quantity": qty})

                cart["pending_pizza_size"] = None
                cart["pending_pizza_size_label"] = None
                cart["pending_pizza_flavor"] = None
            else:
                cart["pending_pizza_flavor"] = matched_p_def["id"]
                await save_cart(phone_number, cart)
                return f"Jee {customer_name}, {matched_p_def['name']} mein kaunsa size chahiye? Small (Rs. 450), Medium (Rs. 750), Large (Rs. 1,100) ya Family (Rs. 1,700)?"

    # ─────────────────────────────────────────────
    # C. 🍔 Burgers, Shawarmas, Paratha Rolls & Fast Food Items
    # ─────────────────────────────────────────────
    OTHER_ITEMS = [
        # Burgers
        {"id": "b_double_decker", "keywords": ["double decker", "double decker zinger"], "name": "Double Decker Zinger Burger", "price": 500},
        {"id": "b_jaddah_zinger", "keywords": ["jaddah special zinger", "jaddah zinger"], "name": "Jaddah Special Zinger Burger", "price": 500},
        {"id": "b_zinger", "keywords": ["zinger burger", "chiken zinger", "chicken zinger", "zinger"], "name": "Zinger Burger", "price": 350},
        {"id": "b_pizza_burger", "keywords": ["pizza burger"], "name": "Pizza Burger", "price": 400},
        {"id": "b_sadah_band", "keywords": ["sadah band", "sada band"], "name": "Sadah Band Zinger Burger", "price": 350},
        {"id": "b_chicken_anda", "keywords": ["chicken anda burger", "chicken egg burger"], "name": "Chicken Anda Burger", "price": 320},
        {"id": "b_chicken_omelette", "keywords": ["chicken omelette burger", "omelette burger", "omlet burger"], "name": "Chicken Omelette Burger", "price": 260},
        {"id": "b_double_anda", "keywords": ["double anda burger", "double egg burger"], "name": "Double Anda Burger", "price": 270},
        {"id": "b_chicken", "keywords": ["chicken burger"], "name": "Chicken Burger", "price": 270},
        {"id": "b_chapli", "keywords": ["chapli burger", "chapali burger"], "name": "Chapli Burger", "price": 250},
        {"id": "b_patty", "keywords": ["patty burger", "pety burger"], "name": "Patty Burger", "price": 250},
        {"id": "b_anda_shami", "keywords": ["anda shami", "shami burger", "anda burger"], "name": "Anda Shami Burger", "price": 200},

        # Shawarmas
        {"id": "sh_zinger_platter", "keywords": ["zinger platter", "zinger platter shawarma"], "name": "Zinger Platter Shawarma", "price": 450},
        {"id": "sh_chicken_platter", "keywords": ["chicken platter", "platter shawarma"], "name": "Chicken Platter Shawarma", "price": 400},
        {"id": "sh_zinger", "keywords": ["zinger shawarma", "zinger shwarma"], "name": "Zinger Shawarma", "price": 300},
        {"id": "sh_tikka", "keywords": ["tikka shawarma"], "name": "Tikka Shawarma", "price": 300},
        {"id": "sh_malai", "keywords": ["malai boti shawarma", "malai shawarma"], "name": "Malai Boti Shawarma", "price": 300},
        {"id": "sh_double_kabab", "keywords": ["double kabab shawarma"], "name": "Double Kabab Shawarma", "price": 250},
        {"id": "sh_kabab_chicken", "keywords": ["kabab chicken shawarma"], "name": "Kabab Chicken Shawarma", "price": 250},
        {"id": "sh_chicken", "keywords": ["chicken shawarma", "shawarma", "shwarma"], "name": "Chicken Shawarma", "price": 200},
        {"id": "sh_single_kabab", "keywords": ["single kabab shawarma", "kabab shawarma"], "name": "Single Kabab Shawarma", "price": 190},
        {"id": "sh_crunchy", "keywords": ["crunchy shawarma", "krunch shawarma"], "name": "Crunchy Shawarma", "price": 150},

        # Paratha Rolls
        {"id": "pr_pizza", "keywords": ["pizza paratha"], "name": "Pizza Paratha", "price": 500},
        {"id": "pr_jaddah", "keywords": ["jaddah paratha", "jaddah special paratha"], "name": "Jaddah Special Paratha Roll", "price": 500},
        {"id": "pr_shapata", "keywords": ["shahi roll", "shapata roll", "shapata"], "name": "Shapata / Shahi Paratha Roll", "price": 500},
        {"id": "pr_malai", "keywords": ["malai boti paratha", "malai paratha"], "name": "Malai Boti Paratha Roll", "price": 350},
        {"id": "pr_tikka", "keywords": ["tikka paratha", "tikka roll"], "name": "Tikka Paratha Roll", "price": 320},
        {"id": "pr_zinger", "keywords": ["zinger paratha", "zinger roll"], "name": "Zinger Paratha Roll", "price": 350},
        {"id": "pr_chicken", "keywords": ["chicken paratha roll", "chicken roll", "paratha roll"], "name": "Chicken Paratha Roll", "price": 300},
        {"id": "pr_kabab", "keywords": ["kabab paratha roll", "kabab roll"], "name": "Kabab Paratha Roll", "price": 300},

        # Wraps
        {"id": "wr_jaddah", "keywords": ["jaddah wrap", "jaddah special wrap"], "name": "Jaddah Special Wrap", "price": 500},
        {"id": "wr_tikka", "keywords": ["tikka wrap", "tikka boti wrap"], "name": "Tikka Boti Wrap", "price": 400},
        {"id": "wr_malai", "keywords": ["malai wrap", "malai boti wrap"], "name": "Malai Boti Wrap", "price": 400},
        {"id": "wr_zinger", "keywords": ["zinger wrap"], "name": "Zinger Wrap", "price": 350},
        {"id": "wr_cheese", "keywords": ["chicken cheese wrap", "cheese wrap"], "name": "Chicken Cheese Wrap", "price": 300},

        # Pastas
        {"id": "pas_crunchy", "keywords": ["crunchy pasta"], "name": "Crunchy Pasta (Large)", "price": 550},
        {"id": "pas_cheese", "keywords": ["chicken cheese pasta", "cheese pasta", "pasta"], "name": "Chicken Cheese Pasta (Large)", "price": 500},

        # Sandwiches
        {"id": "sw_grill", "keywords": ["grill sandwich"], "name": "Grill Sandwich", "price": 350},
        {"id": "sw_cheese", "keywords": ["chicken cheese sandwich"], "name": "Chicken Cheese Sandwich", "price": 300},
        {"id": "sw_club", "keywords": ["chicken club sandwich", "club sandwich", "sandwich"], "name": "Chicken Club Sandwich", "price": 300},
        {"id": "sw_egg", "keywords": ["anda sandwich", "egg sandwich"], "name": "Anda Sandwich", "price": 150},

        # Fries
        {"id": "fr_loaded", "keywords": ["loaded fries", "loaded cheese fries"], "name": "Loaded Fries", "price": 400},
        {"id": "fr_cheese", "keywords": ["cheese fries"], "name": "Cheese Fries", "price": 350},
        {"id": "fr_masala", "keywords": ["masala fries"], "name": "Masala Fries", "price": 250},
        {"id": "fr_french", "keywords": ["french fries", "fries", "chips"], "name": "French Fries", "price": 200},

        # Wings & Nuggets
        {"id": "w_hot_10", "keywords": ["10 hot wings", "10 wings", "hot wings"], "name": "Hot Wings (10 Pcs)", "price": 460},
        {"id": "w_hot_5", "keywords": ["5 hot wings", "5 wings"], "name": "Hot Wings (5 Pcs)", "price": 250},
        {"id": "ng_10", "keywords": ["10 nuggets", "nuggets"], "name": "Nuggets (10 Pcs)", "price": 400},
        {"id": "ng_5", "keywords": ["5 nuggets"], "name": "Nuggets (5 Pcs)", "price": 200},
        {"id": "b_zinger_piece", "keywords": ["zinger piece", "piece", "broast piece"], "name": "Zinger Piece", "price": 180},
    ]

    # Only look for standalone items if deal wasn't the main intent or alongside deal
    for item_def in OTHER_ITEMS:
        # Prevent false positives if dealing with deals (e.g. "deal 1" having "zinger" in desc)
        if deal_match and item_def["id"] in ["b_zinger", "sh_chicken", "fr_french", "w_hot_10"]:
            continue
        if any(kw in text for kw in item_def["keywords"]):
            qty = 1
            pattern = r"(\d+)\s*(?:x\s*)?(?:" + "|".join(re.escape(k) for k in item_def["keywords"]) + ")"
            m = re.search(pattern, text)
            if m:
                qty = int(m.group(1))
            elif any(w in text for w in ["do ", "2 ", " 2", "two "]):
                qty = 2
            elif any(w in text for w in ["teen ", "3 ", " 3", "three "]):
                qty = 3
            found_items.append({"id": item_def["id"], "name": item_def["name"], "price": item_def["price"], "quantity": qty})

    # C. Address Keywords & Local Landmarks Check
    ADDRESS_KEYWORDS = [
        "house", "street", "gali", "mohalla", "road", "near", "dikhan", "d.i. khan", "d.i.khan",
        "chowk", "chuk", "chashma", "cantt", "mor", "mod", "muryali", "muaryali", "bazar", "bazaar",
        "colony", "town", "pull", "pul", "ada", "adda", "addah", "kareeb", "opp", "opposite",
        "flat", "floor", "ward", "chak", "hospital", "university", "college", "stop", "market",
        "plaza", "gate", "darwaza", "village", "gaon", "shop", "topanwala", "bannu", "multan",
        "circular", "chungi", "grid"
    ]
    has_explicit_address = any(k in text for k in ADDRESS_KEYWORDS) or bool(re.search(r"\b(?:on|pe|par|near)\s+[a-z0-9]", text))

    # If an address is provided in this turn, record it immediately in the cart
    if has_explicit_address:
        candidate_addr = extract_clean_address(message_text)
        if candidate_addr:
            cart["address"] = candidate_addr
            await save_cart(phone_number, cart)

    # Food or size detection (to distinguish food/size instructions from addresses)
    is_food_or_size = (
        any(k in text for k in [
            "pizza", "burger", "deal", "broast", "wings", "fries", "coke", "drink", "bottle",
            "tikka", "tika", "teeka", "fajita", "fajitha", "fajeeta", "malai", "boti", "botti",
            "tandoori", "tandori", "bihari", "mughlai", "supreme", "zinger", "afghani",
            "spin roll", "roll", "shawarma", "paratha", "kabab", "stuffer", "crown"
        ])
        or bool(re.search(r"\b(17|13|9|6|xl|large|medium|small|personal|family)\b", text))
    )

    # If customer only sent a size (e.g. "17", "13", "large", "xl") and already has a pizza in cart:
    is_size_specified = (
        any(s in text for s in ["extra large", "xl", "xlarge", "large", "medium", "personal", "small", "family"])
        or bool(re.search(r"\b(17|13|9|6)\b", text))
    )
    if not found_items and is_size_specified and cart.get("items"):
        for itm in cart["items"]:
            base_p_def = next((p for p in PIZZA_CATALOG if itm["id"].startswith(p["id"])), None)
            if base_p_def:
                item_info = all_items_map.get(base_p_def["id"], {})
                prices = item_info.get("prices", {})
                new_price = prices.get(size_selected, base_p_def["default_price"])
                itm["id"] = f"{base_p_def['id']}_{size_selected}"
                itm["name"] = f"{base_p_def['name']} ({size_label})"
                itm["price"] = new_price
                found_items.append(itm)
                break

    # If food items found in message:
    if found_items:
        for f_item in found_items:
            # If item is a pizza, check if customer is updating size of existing pizza
            base_id = f_item["id"].rsplit("_", 1)[0]
            existing_diff_size = next((i for i in cart["items"] if i["id"].rsplit("_", 1)[0] == base_id), None)
            if existing_diff_size:
                cart["items"].remove(existing_diff_size)
                cart["items"].append(f_item)
            else:
                existing = next((i for i in cart["items"] if i["id"] == f_item["id"]), None)
                if existing:
                    existing["quantity"] += f_item["quantity"]
                else:
                    cart["items"].append(f_item)

        items_summary = ", ".join([f"{i['quantity']}x {i['name']}" for i in cart["items"]])

        # Check if customer sent address now OR previously during a clarification turn
        active_address = None
        if has_explicit_address:
            active_address = extract_clean_address(message_text)
            cart["address"] = active_address
        elif cart.get("address"):
            active_address = cart["address"]

        # If customer provided address (now or previously), generate confirmation slip immediately!
        if active_address:
            order_id = f"#FE-{random.randint(1000, 9999)}"
            items_list, subtotal, total = format_cart_summary(cart)
            slip_text = create_order_placement_slip(order_id, customer_name, phone_number, active_address, cart)
            order_details = {
                "order_id": order_id,
                "customer_name": customer_name,
                "customer_phone": format_phone_number(phone_number),
                "address": active_address,
                "items_list": items_list,
                "subtotal": subtotal,
                "delivery_fee": 0,
                "total": total,
            }
            cart["items"] = []
            cart["address"] = None
            cart["awaiting_address"] = False
            await save_cart(phone_number, cart)
            return {
                "text": slip_text,
                "order_confirmed": True,
                "order_details": order_details
            }

        cart["awaiting_address"] = True
        await save_cart(phone_number, cart)
        return f"Order note ho gaya ({items_summary})! Delivery address send karein please."

    # D. Address Provided for Existing Cart Items -> Confirm Order Slip
    is_waiting = cart.get("awaiting_address", False)
    valid_address_provided = has_explicit_address or (is_waiting and not is_food_or_size and len(text.strip()) >= 3)

    if cart.get("items") and valid_address_provided:
        delivery_addr = extract_clean_address(message_text) if has_explicit_address else message_text
        cart["address"] = delivery_addr
        cart["awaiting_address"] = False
        order_id = f"#FE-{random.randint(1000, 9999)}"
        items_list, subtotal, total = format_cart_summary(cart)

        # Generate official digital invoice slip
        slip_text = create_order_placement_slip(order_id, customer_name, phone_number, delivery_addr, cart)

        order_details = {
            "order_id": order_id,
            "customer_name": customer_name,
            "customer_phone": format_phone_number(phone_number),
            "address": delivery_addr,
            "items_list": items_list,
            "subtotal": subtotal,
            "delivery_fee": 0,
            "total": total,
        }

        cart["items"] = []  # Reset cart after order placed
        cart["address"] = None
        await save_cart(phone_number, cart)

        return {
            "text": slip_text,
            "order_confirmed": True,
            "order_details": order_details
        }

    # E. Helpful Clarifications for Vague Requests
    if "pizza" in text:
        await save_cart(phone_number, cart)
        if cart.get("pending_pizza_size_label"):
            return f"Jee {customer_name}, {cart['pending_pizza_size_label']} pizza mein kaunsa flavor (Malai Boti, Fajita, Tikka, Tandoori) chahiye?"
        return f"Jee {customer_name}, pizza mein kaunsa flavor (Malai Boti, Fajita, Tikka, Tandoori) aur size (Personal 6\", Medium 9\", Large 13\", XL 17\") chahiye?"
    if "burger" in text:
        return f"Jee {customer_name}, burger mein kaunsa chahiye? Classic Zinger (Rs. 450), Cheese Zinger (Rs. 500), Mighty Zinger (Rs. 600) ya Chicken Grill (Rs. 550)?"

    # 8. Friendly Natural Fallback (5 to 10 words)
    return f"Jee {customer_name}, batayein aapke liye kya bhejwain?"

async def should_send_menu_pictures(phone_number: str, message_text: str) -> bool:
    clean = message_text.lower().strip()

    # 1. Explicit menu / food list inquiries (Always send pictures!)
    menu_inquiry_patterns = [
        r"\b(?:menu|mainue|manu|card|catalog|catalogue|rate\s*list|price\s*list)\b",
        r"\b(?:photo|photos|image|images|tasveer|tasweer|picture|pictures|pics|pic)\b",
        r"\b(?:deal|deals)\s*(?:list|card|dikhao|dikhayein|bhejo|bhejein|batao|batayein|show|send|kya|kia)\b",
        r"\b(?:konsi|kaunsi)\s*(?:deal|deals)\b",
        r"\b(?:kya|kia)\s+.*(?:cheezen|cheezain|cheezein|chizen|chizain|cheez|items|khana)\b",
        r"\b(?:cheezen|cheezain|cheezein|chizen|chizain)\s+.*(?:hain|hein|kya|kia)\b",
        r"\b(?:kya|kia)\s+(?:kya|kia|hai|hay|kuch|options|milta)\b",
        r"\b(?:kya|kia)\s+available\b",
        r"\b(?:show|send|bhejo|bhejein|dikhao|dikhayein)\s+.*(?:menu|list|card|rates|photo|photos|pic|pics|image|images|deals)\b",
        r"\b(?:rate|rates|price|prices)\s+.*(?:kya|kia|batao|batayein)\b"
    ]
    is_explicit_menu = (
        any(bool(re.search(pat, clean)) for pat in menu_inquiry_patterns)
        or any(k in clean for k in ["menu", "rate list", "price list", "tasveer", "tasweer", "kya hai", "kia hai", "kya kya", "kia kia", "cheezen", "cheezain", "cheezein", "deals dikhao", "deals bhejo", "deals list", "photo", "photos", "pics", "pic"])
    )

    if is_explicit_menu:
        return True

    # 2. Never send menu pictures if user is ordering specific food or providing delivery address
    food_or_order_words = [
        "deal", "burger", "pizza", "zinger", "broast", "wings", "fries",
        "sandwich", "pasta", "roll", "shawarma", "wrap", "coke", "drink",
        "bottle", "malai", "tikka", "fajita", "boti", "kabab", "paratha",
        "chowk", "chuk", "chashma", "road", "street", "shop", "cantt", "house", "gali", "mohalla",
        "order", "karna", "mangwana", "bhejo", "bhej do", "chahiye", "dedo", "de do"
    ]
    if any(w in clean for w in food_or_order_words):
        return False

    # 3. Check for initial greetings
    greetings = ["hi", "hello", "salam", "assalam o alaikum", "asalam alaikum", "aoa", "hey", "start", "slam"]
    is_pure_greeting = clean in greetings

    if is_pure_greeting:
        return not (await is_customer_welcomed(phone_number))
    return False

async def process_message(phone_number: str, message_text: str, customer_name: str = "Customer"):
    should_send_menu_images = await should_send_menu_pictures(phone_number, message_text)

    if should_send_menu_images:
        await mark_customer_welcomed(phone_number)

    # Check Gemini AI first if a valid API key is configured
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    is_valid_format = api_key.startswith("AIzaSy")

    if is_valid_format:
        try:
            print(f"[GEMINI] Calling Gemini AI for {customer_name} (+{phone_number})...")
            history = await get_history(phone_number)
            history.append({
                "role": "user",
                "parts": [{"text": message_text}]
            })
            recent_history = history[-10:]
            ai_reply = await call_gemini_ai(recent_history, api_key, customer_name, phone_number)
            history.append({
                "role": "model",
                "parts": [{"text": ai_reply}]
            })
            await save_history(phone_number, history)
            print(f"[GEMINI OK] Reply generated: \"{ai_reply[:60]}...\"")

            # Check if order was confirmed with final slip
            has_slip = (
                "#fe-" in ai_reply.lower()
                or "order #" in ai_reply.lower()
                or ("confirmed" in ai_reply.lower() and ("total" in ai_reply.lower() or "bill" in ai_reply.lower() or "slip" in ai_reply.lower()))
                or ("receipt" in ai_reply.lower() and "rs." in ai_reply.lower())
            )

            if has_slip:
                cart = await get_cart(phone_number)
                order_id = f"#FE-{random.randint(1000, 9999)}"
                id_match = re.search(r"#fe-\d{4}", ai_reply, re.IGNORECASE)
                if id_match:
                    order_id = id_match.group(0).upper()

                items_list, subtotal, total = format_cart_summary(cart) if cart.get("items") else ("Items in order receipt", 0, "COD")
                total_match = re.search(r"total bill[:\s\*]+rs\.?\s*([\d,]+)", ai_reply, re.IGNORECASE)
                if total_match:
                    total = total_match.group(1).replace(",", "")

                order_details = {
                    "order_id": order_id,
                    "customer_name": customer_name,
                    "customer_phone": format_phone_number(phone_number),
                    "address": message_text,
                    "items_list": items_list,
                    "subtotal": subtotal,
                    "delivery_fee": 0,
                    "total": total,
                }
                cart["items"] = []
                cart["awaiting_address"] = False
                await save_cart(phone_number, cart)
                await save_history(phone_number, [])
                return {
                    "text": ai_reply,
                    "order_confirmed": True,
                    "order_details": order_details,
                    "send_menu_images": should_send_menu_images
                }

            return {
                "text": ai_reply,
                "send_menu_images": should_send_menu_images
            }
        except Exception as e:
            print(f"[GEMINI ERROR] {e}")

    print("[FALLBACK] Using local human fallback engine...")
    fallback_res = await generate_human_fallback(phone_number, message_text, customer_name)
    if isinstance(fallback_res, dict):
        fallback_res["send_menu_images"] = should_send_menu_images
        return fallback_res
    return {
        "text": fallback_res,
        "send_menu_images": should_send_menu_images
    }
