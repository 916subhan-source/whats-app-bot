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

# Persistent cart file across serverless invocations
CARTS_FILE = os.path.join(tempfile.gettempdir(), "whatsapp_food_bot_carts.json")

def load_carts() -> dict:
    try:
        if os.path.exists(CARTS_FILE):
            with open(CARTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_carts(carts: dict):
    try:
        with open(CARTS_FILE, "w", encoding="utf-8") as f:
            json.dump(carts, f, ensure_ascii=False)
    except Exception:
        pass

user_carts = load_carts()
conversation_history = {}

def get_history(phone_number: str):
    if phone_number not in conversation_history:
        conversation_history[phone_number] = []
    return conversation_history[phone_number]

def get_cart(phone_number: str):
    global user_carts
    if not user_carts:
        user_carts = load_carts()
    if phone_number not in user_carts:
        user_carts[phone_number] = {"items": [], "address": None, "awaiting_address": False}
    return user_carts[phone_number]

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
            prices_str = " (Small: Rs. " + str(item["prices"]["small"]) + ", Medium: Rs. " + str(item["prices"]["medium"]) + ", Large: Rs. " + str(item["prices"]["large"]) + ")"
        else:
            prices_str = f" -> {RESTAURANT_INFO['currency']} {item['price']}"
        desc = f" - {item.get('desc')}" if item.get("desc") else ""
        menu_lines.append(f"  * {item['name']}{prices_str}{desc}")
    menu_lines.append("")
menu_knowledge_base = "\n".join(menu_lines)

def build_system_instruction(customer_name: str, phone_number: str) -> str:
    formatted_phone = format_phone_number(phone_number)
    clean_name = RESTAURANT_INFO["name"].replace("🍕", "").strip().title()

    return f"""
You are the warm, polite, and helpful WhatsApp ordering assistant for "{clean_name}".

AUTO-DETECTED CUSTOMER:
- Name: {customer_name}
- Number: {formatted_phone}

CRITICAL RULES:
1. NO DELIVERY CHARGES: Delivery is completely FREE. NEVER add any delivery fee and NEVER mention delivery charges in the bill or replies! Total is simply the sum of the items.
2. STRICT EMOJI LIMIT: Use at most ONE simple emoji in the entire reply. NEVER spam colorful emojis on every line! Keep it clean, minimal, and professional.
3. FLEXIBLE & NATURAL RESPONSE LENGTH:
   - Adapt your response length naturally to the customer's request.
   - For simple greetings, short orders, or confirmations: keep replies concise, direct, and quick.
   - For menu inquiries, recommendations, deals, flavor choices, or questions: be thorough, helpful, and descriptive without cutting off useful details.
   - Speak fluently in friendly Roman Urdu or English depending on the customer's language.
4. FINAL ORDER RECEIPT SLIP:
   ONLY when the customer provides their delivery address, output the order summary in this clean format (no delivery fee, maximum 1 emoji):

*{clean_name}*
Order #FE-[Random 4 Digits] Confirmed ✅

*Customer:* {customer_name}
*Phone:* {formatted_phone}
*Address:* [Customer Address]

*Items:*
• [Qty]x [Item Name with Size/Crust] — Rs. [Item Price x Qty]

*Total Bill:* *Rs. [Total Bill]* (Cash on Delivery)
*Estimated Time:* {RESTAURANT_INFO['estimatedTime']}

Khana jald deliver hoga. Shukriya!

MENU & PRICES:
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
        f"🍕 *Pizzas (Available in Small, Medium, Large & XL):*\n"
        f"  • Chicken Fajita — Rs. 450 (S) | Rs. 750 (M) | Rs. 1,150 (L)\n"
        f"  • Pepperoni Classic — Rs. 450 (S) | Rs. 750 (M) | Rs. 1,150 (L)\n"
        f"  • BBQ Smoky Chicken — Rs. 500 (S) | Rs. 800 (M) | Rs. 1,200 (L)\n"
        f"  • Cheese Margherita — Rs. 400 (S) | Rs. 650 (M) | Rs. 1,000 (L)\n"
        f"  • Veggie Supreme — Rs. 400 (S) | Rs. 650 (M) | Rs. 1,000 (L)\n"
        f"  _(Crust Options: Cheese Stuffed +Rs. 150, Kabab Crown +Rs. 200)_\n\n"
        f"🍗 *Grill & Charcoal BBQ:*\n"
        f"  • Chicken Tikka (Leg/Breast) — *Rs. 450*\n"
        f"  • Chicken Malai Boti (8 Pcs) — *Rs. 650*\n"
        f"  • Beef Seekh Kabab (4 Pcs) — *Rs. 550*\n"
        f"  • Grilled Fish Fillet — *Rs. 850*\n\n"
        f"🍔 *Burgers:*\n"
        f"  • Classic Beef Burger — *Rs. 350*\n"
        f"  • Chicken Zinger Burger — *Rs. 400*\n"
        f"  • Double Cheese Burger — *Rs. 500*\n"
        f"  • Veggie Burger — *Rs. 300*\n\n"
        f"🍟 *Sides:*\n"
        f"  • French Fries — *Rs. 150*\n"
        f"  • Chicken Nuggets (6pc) — *Rs. 250*\n"
        f"  • Garlic Bread (4pc) — *Rs. 200*\n"
        f"  • Fresh Coleslaw — *Rs. 100*\n\n"
        f"🥤 *Drinks & Shakes:*\n"
        f"  • Coca Cola (500ml) — *Rs. 80*\n"
        f"  • Fresh Mint Lemonade — *Rs. 140*\n"
        f"  • Mango Shake (Thick) — *Rs. 200*\n"
        f"  • Mineral Water — *Rs. 50*\n\n"
        f"🛵 *Delivery:* Rs. 50 (Pure DI Khan mein 30-45 mins delivery!)\n"
        f"💵 *Payment:* Cash on Delivery (COD)\n\n"
        f"Order karne ke liye bas item ka naam likh kar send karein, jaise:\n"
        f"👉 *1 Zinger Burger aur 1 Coke* ya *1 Medium Pepperoni Pizza* 😊"
    )

def generate_human_fallback(phone_number: str, message_text: str, customer_name: str = "Customer"):
    text = message_text.lower().strip()
    cart = get_cart(phone_number)
    all_items_map = get_all_items_map()

    # 1. Greetings ("hi", "hello", "salam", "aoa", "hey")
    if text in ["hi", "hello", "salam", "assalam o alaikum", "aoa", "hey", "start"]:
        return f"Assalam-o-Alaikum {customer_name}! Aaj kya mangwayein ge aap?"

    # 2. Menu request
    if any(k in text for k in ["menu", "kya hai", "list", "rates", "rate", "cheezain", "khana", "items"]):
        return get_human_menu_text()

    # 3. View Cart / Total Bill
    if any(k in text for k in ["cart", "bill", "mera order", "total kitna", "basket"]) and not any(k in text for k in ["clear", "cancel", "khatam"]):
        if not cart["items"]:
            return f"Cart khali hai. Kya order karna chahenge?"
        _, _, total = format_cart_summary(cart)
        return f"Total bill Rs. {total} hai. Delivery address send karein."

    # 4. Clear / Cancel Cart
    if any(k in text for k in ["clear", "cancel", "khali", "delete", "nhi chahiye", "band karo"]):
        cart["items"] = []
        cart["awaiting_address"] = False
        save_carts(user_carts)
        return f"Theek hai, aapka order cancel kar diya gaya."

    # 5. Location / Timings / Payments
    if any(k in text for k in ["location", "kahan", "address kahan", "kidhar", "kider"]):
        return "Circular Road, D.I. Khan par hamara kitchen hai."

    if any(k in text for k in ["timing", "time", "kab tak", "open", "khula", "band"]):
        return "Rozana dopehar 12:00 se raat 1:00 tak open hain."

    if any(k in text for k in ["payment", "pesay", "paise", "easypaisa", "jazzcash", "card"]):
        return "Cash on Delivery aur JazzCash dono accept karte hain."

    # 6. Address Provided -> Beautiful Official Order Slip Confirmation
    ADDRESS_KEYWORDS = [
        "house", "street", "gali", "mohalla", "road", "near", "dikhan", "d.i. khan", "d.i.khan",
        "chowk", "chuk", "chashma", "cantt", "mor", "bazar", "bazaar", "colony", "town", "pull",
        "pul", "ada", "addah", "kareeb", "opp", "opposite", "flat", "floor", "ward", "chak",
        "hospital", "university", "college", "stop", "market", "plaza", "gate", "darwaza", "village", "gaon"
    ]
    is_address_text = any(k in text for k in ADDRESS_KEYWORDS) or len(text.split()) >= 2
    is_waiting = cart.get("awaiting_address", False)

    if cart["items"] and (is_waiting or is_address_text):
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
            "delivery_fee": RESTAURANT_INFO["deliveryFee"],
            "total": total,
        }

        cart["items"] = []  # Reset cart after order placed
        save_carts(user_carts)

        return {
            "text": slip_text,
            "order_confirmed": True,
            "order_details": order_details
        }

    # 7. Food Items Ordering / Parsing
    ITEM_KEYWORDS = [
        {"id": "b2", "keywords": ["zinger", "chicken burger"], "default_name": "Chicken Zinger Burger", "price": 400},
        {"id": "b1", "keywords": ["classic beef", "beef burger", "beef"], "default_name": "Classic Beef Burger", "price": 350},
        {"id": "b3", "keywords": ["double cheese", "cheese burger"], "default_name": "Double Cheese Burger", "price": 500},
        {"id": "b4", "keywords": ["veggie burger"], "default_name": "Veggie Burger", "price": 300},
        {"id": "p1", "keywords": ["fajita", "chicken fajita"], "is_pizza": True, "base_name": "Chicken Fajita Pizza"},
        {"id": "p2", "keywords": ["pepperoni"], "is_pizza": True, "base_name": "Pepperoni Classic Pizza"},
        {"id": "p3", "keywords": ["bbq chicken", "bbq pizza", "bbq"], "is_pizza": True, "base_name": "BBQ Smoky Chicken Pizza"},
        {"id": "p4", "keywords": ["margherita", "cheese pizza"], "is_pizza": True, "base_name": "Cheese Margherita Pizza"},
        {"id": "p5", "keywords": ["veggie supreme", "veggie pizza"], "is_pizza": True, "base_name": "Veggie Supreme Pizza"},
        {"id": "g1", "keywords": ["tikka", "chicken tikka"], "default_name": "Chicken Tikka (Quarter)", "price": 450},
        {"id": "g2", "keywords": ["malai boti", "malai"], "default_name": "Chicken Malai Boti (8 Pcs)", "price": 650},
        {"id": "g3", "keywords": ["seekh kabab", "kabab"], "default_name": "Beef Seekh Kabab (4 Pcs)", "price": 550},
        {"id": "g4", "keywords": ["fish", "grilled fish"], "default_name": "Grilled Fish Fillet", "price": 850},
        {"id": "s1", "keywords": ["fries", "finger chips", "french fries"], "default_name": "French Fries", "price": 150},
        {"id": "s2", "keywords": ["nuggets", "chicken nuggets"], "default_name": "Chicken Nuggets (6pc)", "price": 250},
        {"id": "s3", "keywords": ["garlic bread"], "default_name": "Garlic Bread (4pc)", "price": 200},
        {"id": "s4", "keywords": ["coleslaw"], "default_name": "Fresh Coleslaw", "price": 100},
        {"id": "d1", "keywords": ["coke", "coca cola", "cola", "cold drink"], "default_name": "Coca Cola (500ml)", "price": 80},
        {"id": "d2", "keywords": ["mint lemonade", "lemonade", "fresh lime"], "default_name": "Fresh Mint Lemonade", "price": 140},
        {"id": "d3", "keywords": ["mango shake", "shake"], "default_name": "Mango Shake (Special)", "price": 200},
        {"id": "d4", "keywords": ["water", "water bottle", "paani"], "default_name": "Mineral Water (500ml)", "price": 50},
    ]

    size_selected = "medium"
    size_label = "Medium"
    if any(s in text for s in ["small", "chota", "choti", "7 inch", "7\""]):
        size_selected = "small"
        size_label = "Small"
    elif any(s in text for s in ["large", "bada", "badi", "13 inch", "13\""]):
        size_selected = "large"
        size_label = "Large"
    elif any(s in text for s in ["xl", "xlarge", "extra large", "16 inch", "16\""]):
        size_selected = "xlarge"
        size_label = "X-Large"

    crust_extra = 0
    crust_label = ""
    if any(c in text for c in ["cheese stuffed", "cheese crust", "stuffed crust", "cheese bhari"]):
        crust_extra = 150
        crust_label = " - Cheese Stuffed"
    elif any(c in text for c in ["crown", "kabab crown", "kabab crust"]):
        crust_extra = 200
        crust_label = " - Kabab Crown"

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
                base_price = p_item.get("prices", {}).get(size_selected, 750)
                item_price = base_price + crust_extra
                item_name = f"{entry['base_name']} ({size_label}{crust_label})"
                found_items.append({"id": f"{entry['id']}_{size_selected}", "name": item_name, "price": item_price, "quantity": qty})
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
        save_carts(user_carts)
        items_list, subtotal, total = format_cart_summary(cart)

        return f"Order note ho gaya! Delivery address send karein please."

    # 8. Friendly Natural Fallback (5 to 10 words)
    return f"Jee {customer_name}, batayein aapke liye kya bhejwain?"

async def process_message(phone_number: str, message_text: str, customer_name: str = "Customer"):
    # Check Gemini AI first for fluid, warm, human conversation
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            print(f"[GEMINI] Calling Gemini AI for {customer_name} (+{phone_number})...")
            history = get_history(phone_number)
            history.append({
                "role": "user",
                "parts": [{"text": message_text}]
            })
            recent_history = history[-6:]
            ai_reply = await call_gemini_ai(recent_history, api_key, customer_name, phone_number)
            history.append({
                "role": "model",
                "parts": [{"text": ai_reply}]
            })
            print(f"[GEMINI OK] Reply generated: \"{ai_reply[:60]}...\"")

            # Check if order was confirmed or address provided
            cart = get_cart(phone_number)
            addr_words = [
                "chowk", "chuk", "chashma", "house", "gali", "mohalla", "road", "cantt", "dikhan", "near", "sector", "colony",
                "mor", "bazar", "bazaar", "town", "pull", "pul", "ada", "addah", "flat", "ward", "street"
            ]
            is_address = any(k in message_text.lower() for k in addr_words) or cart.get("awaiting_address")
            has_slip = "#fe-" in ai_reply.lower() or "order slip" in ai_reply.lower() or "order id" in ai_reply.lower()

            if is_address or has_slip:
                order_id = f"#FE-{random.randint(1000, 9999)}"
                # If AI didn't format the full slip or kept it too short, generate the official slip
                if not has_slip and cart.get("items"):
                    final_text = create_order_placement_slip(order_id, customer_name, phone_number, message_text, cart)
                else:
                    final_text = ai_reply

                items_list, subtotal, total = format_cart_summary(cart) if cart.get("items") else ("Items discussed in chat", 0, "COD")
                order_details = {
                    "order_id": order_id,
                    "customer_name": customer_name,
                    "customer_phone": format_phone_number(phone_number),
                    "address": message_text,
                    "items_list": items_list,
                    "subtotal": subtotal,
                    "delivery_fee": RESTAURANT_INFO["deliveryFee"],
                    "total": total,
                }
                cart["items"] = []
                cart["awaiting_address"] = False
                save_carts(user_carts)
                return {
                    "text": final_text,
                    "order_confirmed": True,
                    "order_details": order_details
                }

            return ai_reply
        except Exception as e:
            print(f"[GEMINI ERROR] {e}")

    print("[FALLBACK] Using local human fallback engine...")
    return generate_human_fallback(phone_number, message_text, customer_name)
