import os
import re
import random
import httpx
from dotenv import load_dotenv
from menu import RESTAURANT_INFO, MENU

load_dotenv(override=True)

# In-memory history and cart per customer
conversation_history = {}
user_carts = {}

def get_history(phone_number: str):
    if phone_number not in conversation_history:
        conversation_history[phone_number] = []
    return conversation_history[phone_number]

def get_cart(phone_number: str):
    if phone_number not in user_carts:
        user_carts[phone_number] = {"items": [], "address": None}
    return user_carts[phone_number]

# Menu knowledge base string
menu_lines = []
for cat in MENU.values():
    menu_lines.append(f"Category: {cat['name']} ({cat['emoji']})")
    for item in cat["items"]:
        menu_lines.append(f"  * {item['name']} -> {RESTAURANT_INFO['currency']} {item['price']}")
    menu_lines.append("")
menu_knowledge_base = "\n".join(menu_lines)

SYSTEM_INSTRUCTION = f"""
You are the warm, friendly, intelligent, and human WhatsApp ordering assistant for "{RESTAURANT_INFO['name']}".

PERSONALITY & LANGUAGE:
1. Talk like a friendly, helpful employee answering on WhatsApp. Never sound like a robot.
2. Fluently speak and understand English, Urdu, and Roman Urdu (e.g. "bhai 1 zinger burger aur coke bhej do", "kya menu hai aapka?", "kitna time lagega?").
3. Match the user's language and tone. If they speak Urdu, reply in sweet/polite Roman Urdu. If English, reply in English.

DUTIES:
1. Help customers choose what to eat, recommend popular items, explain items, and answer questions.
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
            "parts": [{"text": "Understood! I am the friendly AI WhatsApp assistant for Foodie Express."}]
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

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={api_key}"
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

def generate_intelligent_fallback(phone_number: str, message_text: str) -> str:
    text = message_text.lower().strip()
    cart = get_cart(phone_number)

    # 1. Menu request
    if any(k in text for k in ["menu", "kya hai", "list", "rates", "price", "rate", "cheezain"]):
        reply = f"📋 *{RESTAURANT_INFO['name']} — Menu*\n\n"
        for cat in MENU.values():
            reply += f"{cat['emoji']} *{cat['name']}*\n"
            for item in cat["items"]:
                reply += f"  • {item['name']} — *{RESTAURANT_INFO['currency']} {item['price']}*\n"
            reply += "\n"
        reply += f"🛵 Delivery Fee: *{RESTAURANT_INFO['currency']} {RESTAURANT_INFO['deliveryFee']}* ({RESTAURANT_INFO['estimatedTime']})\n\n"
        reply += "Order karne ke liye bas item ka naam likhein (e.g. *1 Zinger Burger aur 1 Coke*)!"
        return reply

    # 2. Check for food items mentioned
    ITEM_KEYWORDS = [
        {"id": "b2", "keywords": ["zinger", "chicken burger"]},
        {"id": "b1", "keywords": ["beef burger", "beef"]},
        {"id": "b3", "keywords": ["double cheese", "cheese burger"]},
        {"id": "b4", "keywords": ["veggie burger"]},
        {"id": "p2", "keywords": ["pepperoni"]},
        {"id": "p1", "keywords": ["margherita"]},
        {"id": "p3", "keywords": ["bbq chicken", "bbq pizza", "bbq"]},
        {"id": "p4", "keywords": ["veggie supreme", "veggie pizza"]},
        {"id": "s1", "keywords": ["fries", "finger chips", "french fries"]},
        {"id": "s2", "keywords": ["nuggets", "chicken nuggets"]},
        {"id": "s3", "keywords": ["garlic bread"]},
        {"id": "s4", "keywords": ["coleslaw"]},
        {"id": "d1", "keywords": ["coke", "coca cola", "cola", "cold drink"]},
        {"id": "d2", "keywords": ["fresh lime", "lime"]},
        {"id": "d3", "keywords": ["mango shake", "shake"]},
        {"id": "d4", "keywords": ["water", "water bottle", "paani"]},
    ]

    all_items_map = {}
    for cat in MENU.values():
        for item in cat["items"]:
            all_items_map[item["id"]] = item

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
        cart["items"] = found_items
        subtotal = 0
        items_list = ""
        for item in found_items:
            item_total = item["price"] * item["quantity"]
            subtotal += item_total
            items_list += f"• {item['quantity']}x {item['name']} — *{RESTAURANT_INFO['currency']} {item_total}*\n"
        total = subtotal + RESTAURANT_INFO["deliveryFee"]

        return (
            f"Wah, zabardast choice! 😋 Aapka order note ho gaya hai:\n\n"
            f"{items_list}\n"
            f"Subtotal: *{RESTAURANT_INFO['currency']} {subtotal}*\n"
            f"Delivery Fee: *{RESTAURANT_INFO['currency']} {RESTAURANT_INFO['deliveryFee']}*\n"
            f"*Total: {RESTAURANT_INFO['currency']} {total}*\n\n"
            f"📍 Meharbani karke apna *Delivery Address* (Ghar / Mohalla / City) send kijiye taake rider foran rawana ho sake!"
        )

    # 3. Address provided
    if cart["items"] and any(k in text for k in ["house", "street", "gali", "mohalla", "road", "near", "dikhan", "islamabad", "sector"]) or (cart["items"] and len(text.split()) >= 3):
        cart["address"] = message_text
        order_id = f"#FE-{random.randint(1000, 9999)}"
        cart["items"] = []

        return (
            f"🎉 *Order Confirmed!* (ID: *{order_id}*)\n\n"
            f"Aapka order kitchen mein tayaar ho raha hai aur *{RESTAURANT_INFO['estimatedTime']}* mein pohnch jayega!\n\n"
            f"📍 *Delivery Address:* {message_text}\n"
            f"💵 *Payment:* Cash on Delivery (COD)\n\n"
            f"Khana garma garam pohnchne tak intezar farmaiye. Shukriya for choosing *{RESTAURANT_INFO['name']}*! ❤️"
        )

    # 4. Location / Address query
    if any(k in text for k in ["location", "kahan", "kider", "kidhar", "address kahan"]):
        return (
            f"📍 *{RESTAURANT_INFO['name']} Location:*\n\n"
            f"Hamara kitchen Circular Road, D.I. Khan main waqay hai! 🏢\n"
            f"Hum pure DI Khan shehar mein *{RESTAURANT_INFO['estimatedTime']}* main garma garam delivery pohnchate hain! 🛵\n\n"
            f"Order book karne ke liye likhein: *menu* ya direct item ka naam batayein!"
        )

    # 5. Timing query
    if any(k in text for k in ["timing", "time", "kab tak", "open", "khula"]):
        return (
            f"🕒 *Kitchen Timings:*\n\n"
            f"Hum rozana *12:00 PM (Dopehar)* se lekar *1:00 AM (Raat)* tak open rehte hain!\n\n"
            f"Abhi fresh khana mangwane ke liye batayein aapke liye kya bhejoon? 😊"
        )

    # 6. Payment query
    if any(k in text for k in ["payment", "pesay", "paise", "easypaisa", "jazzcash", "card"]):
        return (
            f"💵 *Payment Method:*\n\n"
            f"Hum *Cash on Delivery (COD)* aur JazzCash / EasyPaisa accept karte hain rider ke pohnchne par.\n\n"
            f"Aap befikar ho kar order karein! Kya order karna chahenge? 🍕"
        )

    # 7. Cancellations / Negatives ("nhi", "no", "cancel")
    if text in ["nhi", "nahi", "no", "cancel", "bas"]:
        return (
            f"Theek hai janab! Koi masla nahi. 😊\n"
            f"Jab bhi bhook lagay, bas ek message kar dijiye ga. *{RESTAURANT_INFO['name']}* hamesha aapki khidmat ke liye hazir hai! ❤️"
        )

    # 8. Add more items ("aur", "khuch aur")
    if any(k in text for k in ["aur", "more", "add", "bhi"]):
        return (
            f"Jee zaroor! Batayein aur kya add karoon aapke order mein? 😋\n\n"
            f"Burgers 🍔, Pizzas 🍕, Crispy Fries 🍟, ya Cold Drinks 🥤?"
        )

    # 9. Default warm welcome
    return (
        f"Assalam-o-Alaikum! 👋 Welcome to *{RESTAURANT_INFO['name']}*! 🍕\n\n"
        f"Main aapka food ordering assistant hoon. Aaj kya khane ka mood hai?\n\n"
        f"• Hamara *Menu* dekhne ke liye likhein: *menu*\n"
        f"• Ya direct order karein, jaise: *1 Chicken Zinger Burger aur 1 Coke*\n\n"
        f"Bataiye aapke liye kya bhejoon? 😊"
    )

async def process_message(phone_number: str, message_text: str) -> str:
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
        except Exception as e:
            # Fall back to our rich conversational engine instantly
            pass

    return generate_intelligent_fallback(phone_number, message_text)
