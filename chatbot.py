import os
import re
import json
import random
import tempfile
import httpx
from datetime import datetime
from dotenv import load_dotenv
from menu import RESTAURANT_INFO, MENU, PIZZA_SIZES, PIZZA_CRUSTS

load_dotenv(override=True)

# ─────────────────────────────────────────────
# ☁️ Persistent Cloud Storage for Serverless (Vercel)
# ─────────────────────────────────────────────
KV_BUCKET = os.getenv("KV_BUCKET", "QA3HUmSY1Tcfnr3nCQvFN1")

async def get_kv(key: str, default=None):
    try:
        url = f"https://kvdb.io/{KV_BUCKET}/{key}"
        async with httpx.AsyncClient(timeout=3.5) as client:
            r = await client.get(url)
            if r.status_code == 200:
                return r.json()
    except Exception:
        pass
    return default

async def set_kv(key: str, val):
    try:
        url = f"https://kvdb.io/{KV_BUCKET}/{key}"
        async with httpx.AsyncClient(timeout=3.5) as client:
            await client.post(url, content=json.dumps(val))
    except Exception:
        pass

# In-memory caches for low-latency
conversation_history = {}
user_carts = {}
welcomed_users = set()

async def get_history(phone_number: str) -> list:
    if phone_number in conversation_history and conversation_history[phone_number]:
        return list(conversation_history[phone_number])
    remote_hist = await get_kv(f"hist_{phone_number}", default=[])
    conversation_history[phone_number] = remote_hist or []
    return list(conversation_history[phone_number])

async def save_history(phone_number: str, history: list):
    trimmed = list(history[-10:])
    conversation_history[phone_number] = trimmed
    await set_kv(f"hist_{phone_number}", trimmed)

async def get_cart(phone_number: str) -> dict:
    if phone_number in user_carts and user_carts[phone_number].get("items"):
        return user_carts[phone_number]
    remote_cart = await get_kv(f"cart_{phone_number}")
    if remote_cart:
        user_carts[phone_number] = remote_cart
    else:
        user_carts[phone_number] = {"items": [], "address": None, "awaiting_address": False}
    return user_carts[phone_number]

async def save_cart(phone_number: str, cart: dict):
    user_carts[phone_number] = cart
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

1. ⚠️ SPECIAL DEALS HAVE FIXED ITEMS & SIZES (NEVER ASK SIZES OR COMPONENT DETAILS FOR DEALS!):
   - When a customer orders a Deal (e.g. "Student Viral Deal", "Deal 1", "Family Viral King Deal", "Deal 2"):
     * The pizza size, burger type, and drink size are ALREADY FIXED and given in the official menu card!
     * Deal 1 — Student Viral (Rs. 899): 1x 6" Personal Pizza + 1x Classic Zinger with Fries + 1x 345ml Drink.
     * Deal 2 — Family Viral King (Rs. 2499): 1x 9" Medium Pizza + Half Broast (4 Pcs) + 1x Large Flavour Fries + 1x 1.5Ltr Drink.
     * NEVER ask the customer what pizza size or what burger type they want for these deals. It is already given!
     * Accept the deal right away. If address is needed, just ask: "Theek hai! Apna delivery address send karein." If address is already provided, immediately confirm the order!

2. ONLY CLARIFY VAGUE STANDALONE / ALA CARTE ITEMS (NOT DEALS):
   - Only ask questions if the customer orders standalone single items without specifying:
     * If they say just "1 burger" or "2 burgers" without type: ask "Zinger burger ya Grill burger?" (Classic Zinger Rs. 450, Cheese Zinger Rs. 500, Mighty Zinger Rs. 600, Chicken Grill Rs. 550).
     * If they say just "1 pizza" without size or flavor: ask flavor (Tandoori, Fajita, Tikka) and size (Personal 6", Medium 9", Large 13", XL 17").
   - NEVER ask for size or item options if the customer ordered a Deal or already specified the item!

3. ORDER CONFIRMATION SLIP:
   - Output the slip when items/deals and delivery address are known:

*{clean_name}*
Order #FE-[Random 4 Digits] Confirmed ✅

*Customer:* {customer_name}
*Phone:* {formatted_phone}
*Address:* [Customer Address]

*Items:*
• [Qty]x [Item/Deal Name with components] — Rs. [Item Price x Qty]

*Total Bill:* *Rs. [Total Bill]* (Cash on Delivery)
*Estimated Time:* {RESTAURANT_INFO['estimatedTime']}

Khana jald deliver hoga. Shukriya!

4. NO DELIVERY CHARGES:
   - Delivery is 100% FREE in D.I. Khan. NEVER add any delivery charges or delivery fee line. Total is strictly the sum of ordered items/deals.

5. CLEAN & PROFESSIONAL STYLE:
   - Max 1 simple emoji per message (e.g. ✅). No colorful emoji spam.
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

    # Fast low-latency models
    models_to_try = [
        os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
        "gemini-3.8-flash",
        "gemini-flash-latest"
    ]

    last_err = None
    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    if "candidates" in data and len(data["candidates"]) > 0:
                        parts = data["candidates"][0].get("content", {}).get("parts", [])
                        for p in parts:
                            if "text" in p and not p.get("thought", False):
                                return p["text"].strip()
                        if parts and "text" in parts[0]:
                            return parts[0]["text"].strip()
                else:
                    last_err = f"{model_name} returned {response.status_code}"
        except Exception as e:
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
        f"*Customer:* {customer_name}\n"
        f"*Phone:* {formatted_phone}\n"
        f"*Address:* {address.strip()}\n\n"
        f"*Items:*\n"
        f"{items_list}\n\n"
        f"*Total Bill: Rs. {total}* (Cash on Delivery)\n"
        f"*Estimated Time:* {RESTAURANT_INFO['estimatedTime']}\n\n"
        f"Khana jald deliver hoga. Shukriya!"
    )

def get_human_menu_text() -> str:
    return (
        f"📋 *{RESTAURANT_INFO['name']} — Menu* 🍽️\n\n"
        f"🌟 *Special Deals:*\n"
        f"  • *Student Viral Deal* — *Rs. 899*\n"
        f"    (1x 6\" Personal Pizza + 1x Classic Zinger + Fries + 345ml Drink)\n"
        f"  • *Family Viral King Deal* — *Rs. 2,499*\n"
        f"    (1x Medium Pizza + Half Broast 4pcs + Large Fries + 1.5L Drink)\n\n"
        f"🍕 *Pizzas (Personal, Medium, Large, XL):*\n"
        f"  • Regular (Tandoori, Fajita, Tikka, BBQ, Hot & Spicy)\n"
        f"    Rs. 500 (6\") | Rs. 800 (9\") | Rs. 1,400 (13\") | Rs. 1,900 (17\")\n"
        f"  • Special (Cherry Peri Special, Malai Boti, Bihari Kabab)\n"
        f"    Rs. 600 (6\") | Rs. 950 (9\") | Rs. 1,600 (13\") | Rs. 2,100 (17\")\n\n"
        f"🍔 *Burgers & Sandwiches:*\n"
        f"  • Classic Zinger + Fries — *Rs. 450*\n"
        f"  • Cheese Zinger + Fries — *Rs. 500*\n"
        f"  • Mighty Zinger + Fries — *Rs. 600*\n"
        f"  • Chicken Grill Burger + Fries — *Rs. 550*\n"
        f"  • Cherry Peri Special Grill + Fries — *Rs. 700*\n\n"
        f"🍗 *Broast & Wings:*\n"
        f"  • Quarter Broast + Fries — *Rs. 550*\n"
        f"  • Crispy Wings (6 Pcs) — *Rs. 400*\n\n"
        f"🌯 *Rolls & Loaded Fries:*\n"
        f"  • Chicken Cheese Spin Roll — *Rs. 500*\n"
        f"  • Loaded Cheese Fries — *Rs. 400 (S) / Rs. 550 (L)*\n\n"
        f"🥤 *Drinks:*\n"
        f"  • 345ml Cold Drink — *Rs. 100*\n"
        f"  • 1.5 Ltr Cold Drink — *Rs. 220*\n\n"
        f"🛵 *Delivery:* FREE in D.I. Khan (30-45 mins delivery)\n"
        f"💵 *Payment:* Cash on Delivery (COD)\n\n"
        f"Order karne ke liye item ka naam send karein! 😊"
    )

async def generate_human_fallback(phone_number: str, message_text: str, customer_name: str = "Customer"):
    text = message_text.lower().strip()
    cart = await get_cart(phone_number)
    all_items_map = get_all_items_map()

    # 1. Greetings ("hi", "hello", "salam", "aoa", "hey")
    if text in ["hi", "hello", "salam", "assalam o alaikum", "aoa", "hey", "start"]:
        return f"Assalam-o-Alaikum {customer_name}! Aaj kya mangwayein ge aap?"

    # 2. Menu request
    if any(k in text for k in ["menu", "kya hai", "list", "rates", "rate", "cheezain", "khana", "items"]):
        return get_human_menu_text()

    # 3. View Cart / Total Bill
    if any(k in text for k in ["cart", "bill", "mera order", "total kitna", "basket"]) and not any(k in text for k in ["clear", "cancel", "khatam"]):
        if not cart.get("items"):
            return f"Cart khali hai. Kya order karna chahenge?"
        _, _, total = format_cart_summary(cart)
        return f"Total bill Rs. {total} hai. Delivery address send karein."

    # 4. Clear / Cancel Cart
    if any(k in text for k in ["clear", "cancel", "khali", "delete", "nhi chahiye", "band karo"]):
        cart["items"] = []
        cart["awaiting_address"] = False
        await save_cart(phone_number, cart)
        return f"Theek hai, aapka order cancel kar diya gaya."

    # 5. Location / Timings / Payments
    if any(k in text for k in ["location", "kahan", "address kahan", "kidhar", "kider"]):
        return "Opposite Stylo Shopping Center, Circular Road, D.I. Khan par hamara restaurant hai."

    if any(k in text for k in ["timing", "time", "kab tak", "open", "khula", "band"]):
        return "Rozana dopehar 12:00 se raat 1:00 tak open hain."

    if any(k in text for k in ["payment", "pesay", "paise", "easypaisa", "jazzcash", "card"]):
        return "Cash on Delivery aur Easypaisa dono accept karte hain."

    # 6. Address Provided -> Beautiful Official Order Slip Confirmation
    ADDRESS_KEYWORDS = [
        "house", "street", "gali", "mohalla", "road", "near", "dikhan", "d.i. khan", "d.i.khan",
        "chowk", "chuk", "chashma", "cantt", "mor", "bazar", "bazaar", "colony", "town", "pull",
        "pul", "ada", "addah", "kareeb", "opp", "opposite", "flat", "floor", "ward", "chak",
        "hospital", "university", "college", "stop", "market", "plaza", "gate", "darwaza", "village", "gaon"
    ]
    is_address_text = any(k in text for k in ADDRESS_KEYWORDS) or len(text.split()) >= 2
    is_waiting = cart.get("awaiting_address", False)

    if cart.get("items") and (is_waiting or is_address_text):
        cart["address"] = message_text
        cart["awaiting_address"] = False
        order_id = f"#FE-{random.randint(1000, 9999)}"
        items_list, subtotal, total = format_cart_summary(cart)

        # Generate official digital invoice slip
        slip_text = create_order_placement_slip(order_id, customer_name, phone_number, message_text, cart)

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

        cart["items"] = []  # Reset cart after order placed
        await save_cart(phone_number, cart)

        return {
            "text": slip_text,
            "order_confirmed": True,
            "order_details": order_details
        }

    # 7. Food Items Ordering / Parsing
    ITEM_KEYWORDS = [
        {"id": "deal1", "keywords": ["student viral", "student deal", "viral deal 1", "deal 1", "student viral deal", "deal1", "viral deal"], "default_name": "Deal 1 — Student Viral (6\" Pizza + Zinger + Fries + Drink)", "price": 899},
        {"id": "deal2", "keywords": ["family viral", "family viral king", "family deal", "viral deal 2", "deal 2", "deal2"], "default_name": "Deal 2 — Family Viral King (9\" Pizza + 4pc Broast + Large Fries + 1.5L Drink)", "price": 2499},
        {"id": "b1", "keywords": ["classic zinger", "zinger burger", "zinger"], "default_name": "Classic Zinger + Fries", "price": 450},
        {"id": "b2", "keywords": ["cheese zinger"], "default_name": "Cheese Zinger + Fries", "price": 500},
        {"id": "b3", "keywords": ["mighty zinger"], "default_name": "Mighty Zinger + Fries", "price": 600},
        {"id": "b4", "keywords": ["chicken grill", "grill burger"], "default_name": "Chicken Grill Burger + Fries", "price": 550},
        {"id": "b5", "keywords": ["cherry peri special grill", "special grill burger"], "default_name": "Cherry Peri Special Grill + Fries", "price": 700},
        {"id": "br1", "keywords": ["quarter broast", "broast"], "default_name": "Quarter Broast + Fries (2 Pcs)", "price": 550},
        {"id": "w1", "keywords": ["crispy wings", "wings"], "default_name": "Crispy Wings (6 Pcs)", "price": 400},
        {"id": "r1", "keywords": ["spin roll", "chicken cheese spin roll"], "default_name": "Chicken Cheese Spin Roll", "price": 500},
        {"id": "lf1", "keywords": ["loaded fries", "loaded cheese fries"], "default_name": "Loaded Cheese Fries", "price": 400},
        {"id": "f1", "keywords": ["plain fries", "fries"], "default_name": "Plain Fries", "price": 250},
        {"id": "d1", "keywords": ["coke", "coca cola", "cold drink", "drink", "pepsi"], "default_name": "Cold Drink (345ml)", "price": 100},
        {"id": "d2", "keywords": ["1.5 ltr", "badi bottle", "1.5 liter"], "default_name": "Cold Drink (1.5 Ltr)", "price": 220},
        {"id": "p1", "keywords": ["fajita", "chicken fajita"], "is_pizza": True, "base_name": "Chicken Fajita Pizza"},
        {"id": "p2", "keywords": ["tikka", "chicken tikka pizza"], "is_pizza": True, "base_name": "Chicken Tikka Pizza"},
        {"id": "p3", "keywords": ["tandoori", "tandoori pizza"], "is_pizza": True, "base_name": "Tandoori Pizza"},
        {"id": "p4", "keywords": ["cherry peri special pizza", "special pizza"], "is_pizza": True, "base_name": "Cherry Peri Special Pizza"},
        {"id": "p5", "keywords": ["malai boti pizza"], "is_pizza": True, "base_name": "Malai Boti Pizza"},
    ]

    size_selected = "medium"
    size_label = "Medium"
    if any(s in text for s in ["personal", "small", "chota", "choti", "6 inch", "6\""]):
        size_selected = "personal"
        size_label = "Personal (6\")"
    elif any(s in text for s in ["large", "bada", "badi", "13 inch", "13\""]):
        size_selected = "large"
        size_label = "Large (13\")"
    elif any(s in text for s in ["xl", "xlarge", "extra large", "17 inch", "17\""]):
        size_selected = "xlarge"
        size_label = "XL Family (17\")"

    found_items = []
    for entry in ITEM_KEYWORDS:
        matched = any(kw in text for kw in entry["keywords"])
        if matched:
            qty = 1
            pattern = r"(\d+)\s*(?:x\s*)?(?:" + "|".join(entry["keywords"]) + ")"
            m = re.search(pattern, text)
            if m:
                qty = int(m.group(1))
            elif "do " in text or "2 " in text:
                qty = 2
            elif "teen " in text or "3 " in text:
                qty = 3

            if entry.get("is_pizza"):
                p_item = all_items_map.get(entry["id"], {})
                base_price = p_item.get("prices", {}).get(size_selected, 800)
                item_name = f"{entry['base_name']} ({size_label})"
                found_items.append({"id": f"{entry['id']}_{size_selected}", "name": item_name, "price": base_price, "quantity": qty})
            else:
                found_items.append({"id": entry["id"], "name": entry["default_name"], "price": entry["price"], "quantity": qty})

    if found_items:
        for f_item in found_items:
            existing = next((i for i in cart["items"] if i["id"] == f_item["id"]), None)
            if existing:
                existing["quantity"] += f_item["quantity"]
            else:
                cart["items"].append(f_item)

        cart["awaiting_address"] = True
        await save_cart(phone_number, cart)
        return f"Order note ho gaya! Delivery address send karein please."

    # 8. Friendly Natural Fallback (5 to 10 words)
    return f"Jee {customer_name}, batayein aapke liye kya bhejwain?"

async def should_send_menu_pictures(phone_number: str, message_text: str) -> bool:
    clean = message_text.lower().strip()

    # Never send menu pictures if user is ordering food or providing delivery address
    food_or_order_words = [
        "deal", "burger", "pizza", "zinger", "broast", "wings", "fries",
        "sandwich", "pasta", "roll", "shawarma", "wrap", "coke", "drink",
        "bottle", "malai", "tikka", "fajita", "boti", "kabab", "paratha",
        "chowk", "chuk", "chashma", "road", "street", "shop", "cantt", "house", "gali", "mohalla",
        "order", "karna", "mangwana", "bhejo", "bhej do", "chahiye", "dedo", "send", "de do"
    ]
    if any(w in clean for w in food_or_order_words):
        return False

    # Check for initial greetings or explicit menu commands
    greetings = ["hi", "hello", "salam", "assalam o alaikum", "aoa", "hey", "start"]
    is_pure_greeting = clean in greetings
    is_explicit_menu = bool(re.search(r"\b(menu|tasweer|pictures)\b", clean))

    is_welcomed = await is_customer_welcomed(phone_number)
    return (is_pure_greeting and not is_welcomed) or is_explicit_menu

async def process_message(phone_number: str, message_text: str, customer_name: str = "Customer"):
    should_send_menu_images = await should_send_menu_pictures(phone_number, message_text)

    if should_send_menu_images:
        await mark_customer_welcomed(phone_number)

    # Check Gemini AI first for fluid, warm, human conversation
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
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
            has_slip = "#fe-" in ai_reply.lower() or ("confirmed" in ai_reply.lower() and "total bill" in ai_reply.lower())

            if has_slip:
                cart = await get_cart(phone_number)
                order_id = f"#FE-{random.randint(1000, 9999)}"
                items_list, subtotal, total = format_cart_summary(cart) if cart.get("items") else ("Items discussed in chat", 0, "COD")
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
