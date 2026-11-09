import os
import re
import json
import random
import tempfile
import httpx
from dotenv import load_dotenv
from menu import RESTAURANT_INFO, MENU

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

# Menu knowledge base string for Gemini AI
menu_lines = []
for cat in MENU.values():
    menu_lines.append(f"Category: {cat['name']} ({cat['emoji']})")
    for item in cat["items"]:
        desc = f" - {item.get('desc')}" if item.get("desc") else ""
        menu_lines.append(f"  * {item['name']} -> {RESTAURANT_INFO['currency']} {item['price']}{desc}")
    menu_lines.append("")
menu_knowledge_base = "\n".join(menu_lines)

SYSTEM_INSTRUCTION = f"""
You are the warm, friendly, intelligent, and human WhatsApp ordering assistant for "{RESTAURANT_INFO['name']}".

PERSONALITY & LANGUAGE:
1. Talk like a friendly, helpful employee answering on WhatsApp. Never sound like a robot.
2. Fluently speak and understand English, Urdu, and Roman Urdu (e.g. "bhai 1 zinger burger aur coke bhej do", "kya menu hai aapka?", "kitna time lagega?").
3. Match the user's language and tone. If they speak Urdu, reply in sweet/polite Roman Urdu. If English, reply in English.

DUTIES:
1. Help customers choose what to eat, recommend popular pizzas, burgers, and charcoal grills, and answer questions.
2. Keep calculations accurate based on the menu prices.
3. When taking an order:
   - Keep track of what they want.
   - Ask for their delivery address if they haven't provided it.
   - Provide a clear breakdown: Items, Subtotal, Delivery Fee ({RESTAURANT_INFO['currency']} {RESTAURANT_INFO['deliveryFee']}), and Total.
4. Format messages nicely for WhatsApp with emojis, bullet points, and *bold* for prices.
5. If the order is confirmed with an address, give them an Order ID (like #FE-8892) and wish them a wonderful meal!

RESTAURANT DETAILS:
- Name: {RESTAURANT_INFO['name']}
- Tagline: {RESTAURANT_INFO['tagline']}
- Currency: {RESTAURANT_INFO['currency']}
- Standard Delivery Fee: {RESTAURANT_INFO['currency']} {RESTAURANT_INFO['deliveryFee']}
- Estimated Delivery Time: {RESTAURANT_INFO['estimatedTime']}

COMPLETE MENU ITEMS & PRICES:
{menu_knowledge_base}
"""

async def call_gemini_ai(user_history, api_key: str) -> str:
    contents = [
        {
            "role": "user",
            "parts": [{"text": f"System Instruction: {SYSTEM_INSTRUCTION}"}]
        },
        {
            "role": "model",
            "parts": [{"text": "Understood! I am the friendly AI WhatsApp assistant for Foodie Express & Grill."}]
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

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        if "candidates" in data and len(data["candidates"]) > 0:
            parts = data["candidates"][0].get("content", {}).get("parts", [])
            for p in parts:
                if "text" in p and not p.get("thought", False):
                    return p["text"].strip()
            if parts and "text" in parts[0]:
                return parts[0]["text"].strip()
        raise ValueError("Empty response candidate from Gemini")

def format_cart_summary(cart):
    subtotal = 0
    items_list = ""
    for item in cart["items"]:
        item_total = item["price"] * item["quantity"]
        subtotal += item_total
        items_list += f"• {item['quantity']}x {item['name']} — *{RESTAURANT_INFO['currency']} {item_total}*\n"
    total = subtotal + RESTAURANT_INFO["deliveryFee"]
    return items_list, subtotal, total

def generate_interactive_fallback(phone_number: str, message_text: str):
    text = message_text.lower().strip()
    cart = get_cart(phone_number)
    all_items_map = get_all_items_map()

    # 1. Menu button or menu keyword -> Interactive List of Categories
    if text in ["btn_menu", "menu", "kya hai", "list", "rates", "rate", "cheezain", "khana"]:
        rows = []
        for cat_key, cat in MENU.items():
            item_names = ", ".join([it["name"].split(" ")[0] for it in cat["items"][:3]])
            rows.append({
                "id": f"cat_{cat_key}",
                "title": f"{cat['emoji']} {cat['name']}"[:24],
                "description": f"{item_names}..."[:72]
            })

        return {
            "type": "list",
            "header": f"🍽️ {RESTAURANT_INFO['name']}",
            "text": (
                "Khaane mein kya pasand karenge? 😋\n\n"
                "Neechay *Menu Categories* par click karke apni pasandida category select karein:"
            ),
            "footer": f"Delivery: {RESTAURANT_INFO['currency']} {RESTAURANT_INFO['deliveryFee']} • {RESTAURANT_INFO['estimatedTime']}",
            "button_label": "Menu Categories 🍕",
            "sections": [
                {
                    "title": "Select a Category",
                    "rows": rows
                }
            ]
        }

    # 2. Category Selected from List -> Interactive List of Items
    if text.startswith("cat_"):
        cat_key = text.replace("cat_", "").strip()
        cat = MENU.get(cat_key)
        if cat:
            rows = []
            for item in cat["items"]:
                desc = item.get("desc", "")
                rows.append({
                    "id": f"add_{item['id']}",
                    "title": f"{item['name']}"[:24],
                    "description": f"{RESTAURANT_INFO['currency']} {item['price']} • {desc}"[:72]
                })

            return {
                "type": "list",
                "header": f"{cat['emoji']} {cat['name']}",
                "text": (
                    f"Ye rahe hamare fresh *{cat['name']}*! 😋\n\n"
                    "Cart mein add karne ke liye neechay *Select Item* par tap karein:"
                ),
                "footer": "Cash on Delivery Available",
                "button_label": "Select Item 🛒",
                "sections": [
                    {
                        "title": cat["name"][:24],
                        "rows": rows
                    }
                ]
            }

    # 3. Add Item tapped from List (e.g. add_p1, add_b2, add_g1)
    if text.startswith("add_"):
        item_id = text.replace("add_", "").strip()
        item = all_items_map.get(item_id)
        if item:
            # Check if item already exists in cart -> increment quantity
            existing = next((i for i in cart["items"] if i["id"] == item["id"]), None)
            if existing:
                existing["quantity"] += 1
            else:
                cart["items"].append({**item, "quantity": 1})

            save_carts(user_carts)
            items_list, subtotal, total = format_cart_summary(cart)

            return {
                "type": "button",
                "header": "✅ Item Added to Cart!",
                "text": (
                    f"Wah, zabardast! 😋 *{item['name']}* aapke cart mein add ho gaya hai.\n\n"
                    f"🛒 *Aapka Current Cart:*\n"
                    f"{items_list}\n"
                    f"Subtotal: *{RESTAURANT_INFO['currency']} {subtotal}*\n"
                    f"Delivery: *{RESTAURANT_INFO['currency']} {RESTAURANT_INFO['deliveryFee']}*\n"
                    f"*Total: {RESTAURANT_INFO['currency']} {total}*\n\n"
                    f"Kya aap mazeed items add karna chahte hain ya order place karein?"
                ),
                "footer": "Foodie Express & Grill",
                "buttons": [
                    {"id": "btn_checkout", "title": "✅ Order Now / Checkout"},
                    {"id": "btn_menu", "title": "➕ Add More Items"},
                    {"id": "btn_cart", "title": "🛒 View Cart"}
                ]
            }

    # 4. View Cart (btn_cart, cart)
    if text in ["btn_cart", "cart", "mera order", "basket"]:
        if not cart["items"]:
            return {
                "type": "button",
                "header": "🛒 Your Cart is Empty",
                "text": "Aapke cart mein filhal koi item nahi hai.\n\nMenu dekh kar mazeedaar khana choose karein! 😊",
                "footer": "Foodie Express & Grill",
                "buttons": [
                    {"id": "btn_menu", "title": "📋 View Menu"},
                    {"id": "btn_info", "title": "📍 Location & Timing"}
                ]
            }

        items_list, subtotal, total = format_cart_summary(cart)
        return {
            "type": "button",
            "header": "🛒 Your Food Cart",
            "text": (
                f"Aapka order review:\n\n"
                f"{items_list}\n"
                f"Subtotal: *{RESTAURANT_INFO['currency']} {subtotal}*\n"
                f"Delivery Fee: *{RESTAURANT_INFO['currency']} {RESTAURANT_INFO['deliveryFee']}*\n"
                f"*Total: {RESTAURANT_INFO['currency']} {total}* (COD)\n"
            ),
            "footer": f"Delivery in {RESTAURANT_INFO['estimatedTime']}",
            "buttons": [
                {"id": "btn_checkout", "title": "✅ Proceed Checkout"},
                {"id": "btn_menu", "title": "➕ Add More Items"},
                {"id": "btn_clear", "title": "🗑️ Clear Cart"}
            ]
        }

    # 5. Clear Cart (btn_clear, clear)
    if text in ["btn_clear", "clear", "khali", "delete cart"]:
        cart["items"] = []
        cart["awaiting_address"] = False
        save_carts(user_carts)
        return {
            "type": "button",
            "header": "🗑️ Cart Cleared",
            "text": "Aapka cart empty kar diya gaya hai. Jab bhi dil chahe, naya order shuru karein! 😊",
            "footer": "Foodie Express & Grill",
            "buttons": [
                {"id": "btn_menu", "title": "📋 View Menu"}
            ]
        }

    # 6. Checkout (btn_checkout, checkout, order now)
    if text in ["btn_checkout", "checkout", "order now", "deliver"]:
        if not cart["items"]:
            return {
                "type": "button",
                "header": "🛒 Cart is Empty",
                "text": "Checkout karne se pehle kripya Menu se items choose karein! 🍕",
                "footer": "Foodie Express & Grill",
                "buttons": [
                    {"id": "btn_menu", "title": "📋 View Menu"}
                ]
            }

        cart["awaiting_address"] = True
        save_carts(user_carts)
        items_list, subtotal, total = format_cart_summary(cart)
        return {
            "type": "button",
            "header": "🛵 Delivery Address Required",
            "text": (
                f"Aapka order bilkul tayaar hai:\n\n"
                f"{items_list}\n"
                f"*Total Payable: {RESTAURANT_INFO['currency']} {total}* (Cash on Delivery)\n\n"
                f"📍 Meharbani karke apna *Delivery Address* (Ghar / Mohalla / Road / City) reply mein send kijiye taake rider foran rawana ho sake!"
            ),
            "footer": f"Delivery in {RESTAURANT_INFO['estimatedTime']}",
            "buttons": [
                {"id": "btn_menu", "title": "➕ Add More Items"},
                {"id": "btn_clear", "title": "🗑️ Cancel"}
            ]
        }

    # 7. Location & Timings (btn_info, location, timing)
    if text in ["btn_info", "location", "kahan", "timing", "time", "kab tak", "open"]:
        return {
            "type": "button",
            "header": "📍 Location & Kitchen Timing",
            "text": (
                f"*{RESTAURANT_INFO['name']}*\n"
                f"_{RESTAURANT_INFO['tagline']}_\n\n"
                f"🏢 *Location:* Circular Road, D.I. Khan\n"
                f"🕒 *Timings:* Rozana 12:00 PM (Dopehar) se 1:00 AM (Raat) tak\n"
                f"💵 *Payment:* Cash on Delivery (COD) / JazzCash / EasyPaisa\n"
                f"🛵 *Delivery Time:* {RESTAURANT_INFO['estimatedTime']} pure DI Khan mein!"
            ),
            "footer": "D.I. Khan Fast Delivery",
            "buttons": [
                {"id": "btn_menu", "title": "📋 View Menu"},
                {"id": "btn_cart", "title": "🛒 View Cart"}
            ]
        }

    # 8. Address Provided (order confirmation)
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
        cart["items"] = []  # Reset cart after order placed
        save_carts(user_carts)

        return {
            "type": "button",
            "header": f"🎉 Order Confirmed! ({order_id})",
            "text": (
                f"Shukriya! Aapka order kitchen mein tayaar ho raha hai aur *{RESTAURANT_INFO['estimatedTime']}* mein pohnch jayega!\n\n"
                f"{items_list}\n"
                f"*Total Bill: {RESTAURANT_INFO['currency']} {total}*\n"
                f"📍 *Delivery Address:* {message_text}\n"
                f"💵 *Payment Method:* Cash on Delivery (COD)\n\n"
                f"Khana garma garam pohnchne tak intezar farmaiye. Shukriya for choosing *{RESTAURANT_INFO['name']}*! ❤️"
            ),
            "footer": "Enjoy your delicious meal!",
            "buttons": [
                {"id": "btn_menu", "title": "📋 New Order"},
                {"id": "btn_info", "title": "📍 Kitchen Info"}
            ]
        }
            "buttons": [
                {"id": "btn_menu", "title": "📋 New Order"},
                {"id": "btn_info", "title": "📍 Kitchen Info"}
            ]
        }

    # 9. Natural Language Food Mention (e.g. "1 zinger aur 1 coke")
    ITEM_KEYWORDS = [
        {"id": "b2", "keywords": ["zinger", "chicken burger"]},
        {"id": "b1", "keywords": ["classic beef", "beef burger", "beef"]},
        {"id": "b3", "keywords": ["double cheese", "cheese burger"]},
        {"id": "b4", "keywords": ["veggie burger"]},
        {"id": "p2", "keywords": ["pepperoni"]},
        {"id": "p1", "keywords": ["margherita"]},
        {"id": "p3", "keywords": ["bbq chicken", "bbq pizza", "bbq"]},
        {"id": "p4", "keywords": ["veggie supreme", "veggie pizza"]},
        {"id": "g1", "keywords": ["tikka", "chicken tikka"]},
        {"id": "g2", "keywords": ["malai boti", "malai"]},
        {"id": "g3", "keywords": ["seekh kabab", "kabab"]},
        {"id": "g4", "keywords": ["fish", "grilled fish"]},
        {"id": "s1", "keywords": ["fries", "finger chips", "french fries"]},
        {"id": "s2", "keywords": ["nuggets", "chicken nuggets"]},
        {"id": "s3", "keywords": ["garlic bread"]},
        {"id": "s4", "keywords": ["coleslaw"]},
        {"id": "d1", "keywords": ["coke", "coca cola", "cola", "cold drink"]},
        {"id": "d2", "keywords": ["mint lemonade", "lemonade", "fresh lime"]},
        {"id": "d3", "keywords": ["mango shake", "shake"]},
        {"id": "d4", "keywords": ["water", "water bottle", "paani"]},
    ]

    found_items = []
    for entry in ITEM_KEYWORDS:
        matched = any(kw in text for kw in entry["keywords"])
        if matched:
            item = all_items_map.get(entry["id"])
            if item and not any(f["id"] == item["id"] for f in found_items):
                qty = 1
                pattern = r"(\d+)\s*(?:x\s*)?(?:" + "|".join(entry["keywords"]) + ")"
                m = re.search(pattern, text)
                if m:
                    qty = int(m.group(1))
                elif "do " in text or "2 " in text:
                    qty = 2
                elif "teen " in text or "3 " in text:
                    qty = 3
                found_items.append({**item, "quantity": qty})

    if found_items:
        for f_item in found_items:
            existing = next((i for i in cart["items"] if i["id"] == f_item["id"]), None)
            if existing:
                existing["quantity"] += f_item["quantity"]
            else:
                cart["items"].append(f_item)

        items_list, subtotal, total = format_cart_summary(cart)
        return {
            "type": "button",
            "header": "🛒 Items Added to Order!",
            "text": (
                f"Wah, zabardast choice! 😋 Aapka order note ho gaya hai:\n\n"
                f"{items_list}\n"
                f"Subtotal: *{RESTAURANT_INFO['currency']} {subtotal}*\n"
                f"Delivery Fee: *{RESTAURANT_INFO['currency']} {RESTAURANT_INFO['deliveryFee']}*\n"
                f"*Total: {RESTAURANT_INFO['currency']} {total}*\n\n"
                f"📍 Apna *Delivery Address* likhein ya direct *Checkout* dabayein:"
            ),
            "footer": "Foodie Express & Grill",
            "buttons": [
                {"id": "btn_checkout", "title": "✅ Order Now / Checkout"},
                {"id": "btn_menu", "title": "➕ Add More Items"},
                {"id": "btn_cart", "title": "🛒 View Cart"}
            ]
        }

    # 10. Default Welcome Buttons
    return {
        "type": "button",
        "header": f"🍕 {RESTAURANT_INFO['name']}",
        "text": (
            f"Assalam-o-Alaikum! 👋 Welcome to *{RESTAURANT_INFO['name']}*! 🍕🍗\n\n"
            f"Main aapka online food ordering assistant hoon. Aaj kya khane ka mood hai?\n\n"
            f"Neechay buttons se option chunein ya direct message likhein:"
        ),
        "footer": f"Delivery: {RESTAURANT_INFO['currency']} {RESTAURANT_INFO['deliveryFee']} • Fast COD",
        "buttons": [
            {"id": "btn_menu", "title": "📋 View Menu"},
            {"id": "btn_cart", "title": "🛒 View Cart"},
            {"id": "btn_info", "title": "📍 Location & Timing"}
        ]
    }

async def process_message(phone_number: str, message_text: str):
    # Interactive commands (btn_*, cat_*, add_*) are handled instantly by interactive engine
    if message_text.startswith("btn_") or message_text.startswith("cat_") or message_text.startswith("add_"):
        return generate_interactive_fallback(phone_number, message_text)

    # Check AI if natural language is used
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            history = get_history(phone_number)
            history.append({
                "role": "user",
                "parts": [{"text": message_text}]
            })
            recent_history = history[-6:]
            ai_reply = await call_gemini_ai(recent_history, api_key)
            history.append({
                "role": "model",
                "parts": [{"text": ai_reply}]
            })
            return ai_reply
        except Exception:
            pass

    return generate_interactive_fallback(phone_number, message_text)
