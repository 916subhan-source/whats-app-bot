import os
import sys
import re
import asyncio
from datetime import datetime
from typing import Optional
import csv
import io
from fastapi import FastAPI, Request, Query, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import httpx
from dotenv import load_dotenv

from chatbot import process_message, get_kv, set_kv
from menu import MENU_PAGES, MENU
from voice import transcribe_whatsapp_voice, transcribe_audio_bytes, download_evolution_media
from database import (
    init_db, seed_menu_items, db_save_order, db_get_recent_orders, is_postgres,
    db_create_pos_order, db_update_order_status, db_get_sales_analytics, db_seed_sample_orders
)
from pos_view import render_pos_html

ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=ENV_PATH, override=True)

WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WEBHOOK_VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN", "cherryperi_secret_token_123")
PORT = int(os.getenv("PORT", 3000))

# ─────────────────────────────────────────────
# 🚀 Evolution API Configuration
# ─────────────────────────────────────────────
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "").rstrip("/")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")
EVOLUTION_INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE_NAME", "cherri perri")

# In-memory tracking for staff manual override & bot dispatched IDs
bot_dispatched_ids = set()
staff_silenced_until = {} # phone -> datetime timestamp

app = FastAPI(
    title="🍕 Cherry Peri WhatsApp Food Delivery Bot — FastAPI",
    description="High-performance async WhatsApp Cloud API food delivery chatbot built with FastAPI & Gemini AI",
    version="2.2.0"
)

@app.on_event("startup")
async def startup_event():
    try:
        init_db()
        seed_menu_items(MENU)
        db_seed_sample_orders()
        print(f"[STARTUP] Database initialized, seeded, and synced ({'PostgreSQL' if is_postgres() else 'SQLite'})!")
    except Exception as e:
        print(f"[STARTUP WARN] DB initialization error: {e}")

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# ─────────────────────────────────────────────
# ⚡ High-Performance Reusable Connection Pool
# ─────────────────────────────────────────────
_wa_client: Optional[httpx.AsyncClient] = None

def get_wa_client() -> httpx.AsyncClient:
    global _wa_client
    if _wa_client is None or _wa_client.is_closed:
        _wa_client = httpx.AsyncClient(
            timeout=8.0,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=50)
        )
    return _wa_client

async def send_whatsapp_message(to: str, text: str):
    clean_target = to.replace("+", "").replace(" ", "").replace("-", "").strip()
    if clean_target.startswith("0"):
        clean_target = "92" + clean_target[1:]
    if "@" in clean_target:
        clean_target = clean_target.split("@")[0]

    client = get_wa_client()

    # 1. Try Evolution API if configured
    if EVOLUTION_API_URL and EVOLUTION_API_KEY:
        evo_url = f"{EVOLUTION_API_URL}/message/sendText/{EVOLUTION_INSTANCE_NAME}"
        evo_headers = {
            "apikey": EVOLUTION_API_KEY,
            "Content-Type": "application/json"
        }
        evo_payload = {
            "number": clean_target,
            "text": text
        }
        try:
            res = await client.post(evo_url, json=evo_payload, headers=evo_headers)
            if res.status_code < 400:
                data = res.json()
                msg_id = data.get("key", {}).get("id")
                if msg_id:
                    bot_dispatched_ids.add(msg_id)
                print(f"[OK EVO] Text message sent to {clean_target}")
                return data
            else:
                print(f"[WARN EVO] Evolution API failed ({res.status_code}): {res.text[:100]}, trying fallback...")
        except Exception as evo_err:
            print(f"[WARN EVO] Evolution API exception: {evo_err}, trying fallback...")

    # 2. Fallback to Meta Cloud API
    if WHATSAPP_ACCESS_TOKEN and WHATSAPP_PHONE_NUMBER_ID:
        url = f"https://graph.facebook.com/v21.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": clean_target,
            "type": "text",
            "text": {"body": text},
        }
        try:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code >= 400:
                print(f"[ERROR META] Failed to send WhatsApp message: {response.text}")
            else:
                print(f"[OK META] Text message sent to {clean_target}")
            return response.json()
        except Exception as e:
            print(f"[ERROR META] send_whatsapp_message exception: {e}")
            return {"error": str(e)}

    return {"error": "No WhatsApp provider configured"}


async def send_typing_presence(to: str):
    """Instantly triggers 'typing...' in WhatsApp so customer feels zero latency."""
    if not (EVOLUTION_API_URL and EVOLUTION_API_KEY):
        return
    clean_target = to.replace("+", "").replace(" ", "").replace("-", "").strip()
    if clean_target.startswith("0"):
        clean_target = "92" + clean_target[1:]
    if "@" in clean_target:
        clean_target = clean_target.split("@")[0]
    client = get_wa_client()
    try:
        evo_url = f"{EVOLUTION_API_URL}/chat/sendPresence/{EVOLUTION_INSTANCE_NAME}"
        await client.post(
            evo_url,
            json={"number": clean_target, "presence": "composing", "delay": 1200},
            headers={"apikey": EVOLUTION_API_KEY},
            timeout=2.0
        )
    except Exception:
        pass

async def send_whatsapp_image(to: str, media_id: str = None, image_url: str = None, caption: str = None):
    clean_target = to.replace("+", "").replace(" ", "").replace("-", "").strip()
    if clean_target.startswith("0"):
        clean_target = "92" + clean_target[1:]
    if "@" in clean_target:
        clean_target = clean_target.split("@")[0]

    client = get_wa_client()

    # 1. Try Evolution API if configured
    if EVOLUTION_API_URL and EVOLUTION_API_KEY:
        evo_url = f"{EVOLUTION_API_URL}/message/sendMedia/{EVOLUTION_INSTANCE_NAME}"
        evo_headers = {
            "apikey": EVOLUTION_API_KEY,
            "Content-Type": "application/json"
        }
        evo_payload = {
            "number": clean_target,
            "mediatype": "image",
            "mimetype": "image/jpeg",
            "caption": caption or "",
            "media": image_url or ""
        }
        try:
            res = await client.post(evo_url, json=evo_payload, headers=evo_headers)
            if res.status_code < 400:
                data = res.json()
                msg_id = data.get("key", {}).get("id")
                if msg_id:
                    bot_dispatched_ids.add(msg_id)
                print(f"[OK EVO] Image sent to {clean_target}")
                return data
            else:
                print(f"[WARN EVO] Evolution media failed ({res.status_code}): {res.text[:100]}")
        except Exception as evo_err:
            print(f"[WARN EVO] Evolution media exception: {evo_err}")

    # 2. Fallback to Meta Cloud API
    if WHATSAPP_ACCESS_TOKEN and WHATSAPP_PHONE_NUMBER_ID:
        url = f"https://graph.facebook.com/v21.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }
        image_payload = {}
        if media_id:
            image_payload["id"] = media_id
        elif image_url:
            image_payload["link"] = image_url
        if caption:
            image_payload["caption"] = caption

        payload = {
            "messaging_product": "whatsapp",
            "to": clean_target,
            "type": "image",
            "image": image_payload,
        }
        try:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code >= 400:
                print(f"[ERROR META] Failed to send WhatsApp image to {clean_target}: {response.text}")
            else:
                print(f"[OK META] Image sent to {clean_target}")
            return response.json()
        except Exception as e:
            print(f"[ERROR META] send_whatsapp_image exception: {e}")
            return {"error": str(e)}

    return {"error": "No WhatsApp provider configured"}

async def send_whatsapp_buttons(to: str, text: str, buttons: list, header: str = None, footer: str = None):
    url = f"https://graph.facebook.com/v21.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": text},
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": b["id"],
                            "title": b["title"][:20]
                        }
                    }
                    for b in buttons[:3]
                ]
            }
        }
    }
    if header:
        payload["interactive"]["header"] = {"type": "text", "text": header[:60]}
    if footer:
        payload["interactive"]["footer"] = {"text": footer[:60]}

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code >= 400:
            print(f"[ERROR] Failed to send WhatsApp buttons: {response.text}")
        else:
            print(f"[OK] Interactive buttons sent to {to}")
        return response.json()

async def send_whatsapp_list(to: str, text: str, button_label: str, sections: list, header: str = None, footer: str = None):
    url = f"https://graph.facebook.com/v21.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": text},
            "action": {
                "button": button_label[:20],
                "sections": sections
            }
        }
    }
    if header:
        payload["interactive"]["header"] = {"type": "text", "text": header[:60]}
    if footer:
        payload["interactive"]["footer"] = {"text": footer[:60]}

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code >= 400:
            print(f"[ERROR] Failed to send WhatsApp list: {response.text}")
        else:
            print(f"[OK] Interactive list sent to {to}")
        return response.json()

async def mark_as_read(message_id: str):
    url = f"https://graph.facebook.com/v21.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id,
    }
    try:
        client = get_wa_client()
        await client.post(url, json=payload, headers=headers)
    except Exception:
        pass

async def dispatch_kitchen_order(details: dict, order_slip: str, customer_name: str, from_number: str):
    # 1. Save to Database (SQLite & PostgreSQL)
    try:
        order_payload = {
            "order_id": details.get("order_id", "Order"),
            "customer_name": details.get("customer_name", customer_name),
            "customer_phone": details.get("customer_phone", from_number),
            "address": details.get("address", "See slip"),
            "items_list": details.get("items_list", ""),
            "subtotal": details.get("subtotal", 0),
            "delivery_fee": details.get("delivery_fee", 0),
            "total": details.get("total", 0),
            "slip": order_slip
        }
        db_save_order(order_payload)
        print(f"[DB ORDER] Order {order_payload['order_id']} saved to database!")
    except Exception as db_err:
        print(f"[DB ORDER ERROR] {db_err}")

    # 2. Dispatch WhatsApp notification to configured owner numbers
    owner_phones_raw = os.getenv("OWNER_PHONE_NUMBER", "923160998053")
    owner_numbers = [p.strip() for p in re.split(r"[,;]+", owner_phones_raw) if p.strip()]

    kitchen_alert = (
        f"🚨 *NEW ORDER RECEIVED IN KITCHEN!* 🍕\n\n"
        f"{order_slip}\n\n"
        f"🛵 Khana foran ready karein taake rider rawana ho sake!"
    )

    for raw_phone in owner_numbers:
        clean_target = raw_phone.replace("+", "").replace(" ", "").replace("-", "").strip()
        if clean_target.startswith("0"):
            clean_target = "92" + clean_target[1:]

        try:
            print(f"[KITCHEN ALERT] Sending alert for {details.get('order_id')} to {clean_target}...")
            res = await send_whatsapp_message(to=clean_target, text=kitchen_alert)
            if isinstance(res, dict) and "error" in res:
                err_info = res["error"]
                print(f"[KITCHEN ALERT FAILED] Error to {clean_target}: {err_info}")
            else:
                print(f"[KITCHEN ALERT OK] Alert successfully sent to {clean_target}!")
        except Exception as alert_err:
            print(f"[KITCHEN ALERT ERROR] Failed sending to {clean_target}: {alert_err}")

# Message processor handler
async def handle_incoming_messages(data: dict):
    try:
        # ─────────────────────────────────────────────
        # 1. Check for Evolution API Payload (messages.upsert)
        # ─────────────────────────────────────────────
        if (data.get("event") == "messages.upsert") or ("data" in data and "key" in data.get("data", {})):
            evo_data = data.get("data", {})
            key = evo_data.get("key", {})
            remote_jid = key.get("remoteJid", "")

            # Filter out non-private chats (group chats, broadcast status)
            if not remote_jid.endswith("@s.whatsapp.net"):
                return

            from_number = remote_jid.split("@")[0]
            msg_id = key.get("id")
            from_me = key.get("fromMe", False)
            customer_name = evo_data.get("pushName", "Customer")

            # 🚨 Staff Manual Override: If staff sent message from phone, silence AI for 30 mins
            if from_me:
                if msg_id not in bot_dispatched_ids:
                    from datetime import timedelta
                    silence_until = datetime.now() + timedelta(minutes=30)
                    staff_silenced_until[from_number] = silence_until
                    print(f"[STAFF OVERRIDE] Staff messaged {from_number}. AI silenced for 30 mins (until {silence_until.strftime('%I:%M %p')}).")
                return

            # Check if this customer chat is currently silenced for staff
            if from_number in staff_silenced_until:
                if datetime.now() < staff_silenced_until[from_number]:
                    print(f"[AI SILENT] Customer {from_number} messaged, but AI is silenced for human staff handling.")
                    return
                else:
                    del staff_silenced_until[from_number]

            # Extract text from Evolution message object
            msg_obj = evo_data.get("message", {})
            incoming_text = ""
            if "conversation" in msg_obj:
                incoming_text = msg_obj["conversation"]
            elif "extendedTextMessage" in msg_obj:
                incoming_text = msg_obj["extendedTextMessage"].get("text", "")
            elif "imageMessage" in msg_obj:
                incoming_text = msg_obj["imageMessage"].get("caption", "")
            elif "audioMessage" in msg_obj:
                print(f"[AUDIO EVO] Voice note received from {customer_name} ({from_number})")
                audio_bytes = await download_evolution_media(evo_data)
                if audio_bytes:
                    incoming_text = await transcribe_audio_bytes(audio_bytes, "audio/ogg")
                    if not incoming_text or not incoming_text.strip():
                        await send_whatsapp_message(
                            from_number,
                            f"Assalam-o-Alaikum {customer_name}! Aapka voice message theek se sunai nahi diya. Please dobara voice bhejein ya likh kar bata dein."
                        )
                        return
                    print(f"[VOICE CONVERTED EVO] Text: \"{incoming_text}\"")
                else:
                    print(f"[AUDIO EVO ERROR] Could not retrieve audio bytes from Evolution API.")
                    return

            if not incoming_text.strip():
                return

            # Instantly display 'typing...' in customer's WhatsApp
            asyncio.create_task(send_typing_presence(from_number))

            print(f"[MSG EVO] Message from {customer_name} ({from_number}): \"{incoming_text}\"")

            # Process through unified chatbot engine
            reply = await process_message(from_number, incoming_text, customer_name)

            # If customer asked for menu or needs pictures, send official menu cards in parallel
            if isinstance(reply, dict) and reply.get("send_menu_images"):
                print(f"[MENU IMAGES EVO] Sending menu cards concurrently to {from_number}...")
                img_tasks = [
                    send_whatsapp_image(
                        to=from_number,
                        media_id=page.get("id"),
                        image_url=page.get("url"),
                        caption=page.get("caption")
                    )
                    for page in MENU_PAGES
                ]
                await asyncio.gather(*img_tasks, return_exceptions=True)

            text_to_send = reply.get("text", "") if isinstance(reply, dict) else str(reply)
            print(f"[REPLY EVO] Reply to {from_number}: \"{text_to_send[:80]}...\"")
            await send_whatsapp_message(from_number, text_to_send)

            # Kitchen notification if order confirmed
            if isinstance(reply, dict) and reply.get("order_confirmed"):
                details = reply.get("order_details", {})
                order_slip = reply.get("text", "")
                await dispatch_kitchen_order(details, order_slip, customer_name, from_number)
            return

        # ─────────────────────────────────────────────
        # 2. Meta Cloud API Payload
        # ─────────────────────────────────────────────
        entry = data.get("entry", [])
        if not entry:
            return
        changes = entry[0].get("changes", [])
        if not changes:
            return
        value = changes[0].get("value", {})
        contacts = value.get("contacts", [])
        customer_name = "Customer"
        if contacts and isinstance(contacts, list) and len(contacts) > 0:
            customer_name = contacts[0].get("profile", {}).get("name", "Customer")

        messages = value.get("messages", [])

        for message in messages:
            msg_id = message.get("id")
            from_number = message.get("from")
            msg_type = message.get("type")

            # Mark message as read in background without blocking response
            if msg_id:
                asyncio.create_task(mark_as_read(msg_id))

            incoming_text = ""
            if msg_type == "text":
                incoming_text = message.get("text", {}).get("body", "")
            elif msg_type == "interactive":
                interactive = message.get("interactive", {})
                itype = interactive.get("type")
                if itype == "button_reply":
                    incoming_text = interactive.get("button_reply", {}).get("id", "")
                elif itype == "list_reply":
                    incoming_text = interactive.get("list_reply", {}).get("id", "")
            elif msg_type == "audio":
                audio_obj = message.get("audio", {})
                media_id = audio_obj.get("id")
                mime_type = audio_obj.get("mime_type", "audio/ogg")
                print(f"[AUDIO] Voice message received from {customer_name} ({from_number}) [Media ID: {media_id}]")
                incoming_text = await transcribe_whatsapp_voice(media_id, mime_type)
                if not incoming_text or not incoming_text.strip():
                    await send_whatsapp_message(
                        from_number,
                        f"Assalam-o-Alaikum {customer_name}! Aapka voice message theek se sunai nahi diya. Please dobara voice bhejein ya likh kar bata dein."
                    )
                    continue
                print(f"[VOICE CONVERTED] Text: \"{incoming_text}\"")
            else:
                # Fallback for voice/images/stickers
                await send_whatsapp_message(
                    from_number,
                    f"Assalam-o-Alaikum {customer_name}! 😊 Please type your food order or send a voice message, ya *menu* likhein."
                )
                continue

            print(f"[MSG] Message from {customer_name} ({from_number}): \"{incoming_text}\"")

            # Process through warm human-like conversation engine (Gemini AI + Local Fallback)
            reply = await process_message(from_number, incoming_text, customer_name)

            # If reply requests sending menu images (first-time customer or asking for menu)
            if isinstance(reply, dict) and reply.get("send_menu_images"):
                print(f"[MENU IMAGES] Automatically sending 4 menu cards to {from_number}...")
                for page in MENU_PAGES:
                    try:
                        await send_whatsapp_image(
                            to=from_number,
                            media_id=page.get("id"),
                            image_url=page.get("url"),
                            caption=page.get("caption")
                        )
                    except Exception as img_err:
                        print(f"[MENU IMAGE ERROR] {img_err}")

            # Send back pure natural text like a human employee
            text_to_send = reply.get("text") if isinstance(reply, dict) else str(reply)
            print(f"[REPLY] Reply to {from_number}: \"{text_to_send[:80]}...\"")
            await send_whatsapp_message(from_number, text_to_send)

            # ─────────────────────────────────────────────
            # 🚨 Instant Kitchen / Owner Notification & Live Orders Log
            # ─────────────────────────────────────────────
            if isinstance(reply, dict) and reply.get("order_confirmed"):
                details = reply.get("order_details", {})
                order_slip = reply.get("text", "")
                await dispatch_kitchen_order(details, order_slip, customer_name, from_number)
    except Exception as e:
        print(f"[ERROR] Error handling messages: {e}")

# ─────────────────────────────────────────────
# 💻 Point of Sale (POS) & Sales Management System
# ─────────────────────────────────────────────
@app.get("/pos", response_class=HTMLResponse, summary="Cherry Peri POS & Restaurant Sales Management Dashboard")
async def pos_dashboard():
    """Renders the comprehensive Cherry Peri Fast Food POS and daily/monthly sales management system."""
    return HTMLResponse(content=render_pos_html(), status_code=200)

@app.get("/api/menu", summary="Structured Menu for POS Terminal")
async def get_pos_menu():
    """Provides flat item list and structured categories for the POS counter terminal."""
    flat_items = []
    for cat_key, cat in MENU.items():
        cat_name = cat.get("name", cat_key)
        for item in cat.get("items", []):
            if "prices" in item and isinstance(item["prices"], dict):
                for sz, pr in item["prices"].items():
                    flat_items.append({
                        "id": f"{item['id']}_{sz}",
                        "name": f"{item['name']} ({sz.title()})",
                        "price": pr,
                        "category": cat_key,
                        "category_name": cat_name
                    })
            else:
                flat_items.append({
                    "id": item["id"],
                    "name": item["name"],
                    "price": item.get("price", 0),
                    "category": cat_key,
                    "category_name": cat_name
                })
    return {"categories": MENU, "items": flat_items}

@app.get("/api/sales/stats", summary="Daily & Monthly Sales Analytics")
async def get_sales_stats():
    """Returns real-time sales KPI, 30-day trends, top items, and recent orders."""
    return db_get_sales_analytics()

@app.post("/api/pos/order", summary="Create POS Counter / Dine-in / Walk-in Order")
async def create_pos_order(request: Request):
    """Processes a new counter, dine-in, or takeaway order and integrates into sales stats."""
    payload = await request.json()
    order = db_create_pos_order(payload)
    return {"status": "ok", "order_id": order.get("order_id"), "order": order}

@app.post("/api/orders/{order_id:path}/status", summary="Update Kitchen Order Status")
async def update_order_status(order_id: str, request: Request):
    """Updates status: pending, preparing, out_for_delivery, completed, cancelled."""
    import urllib.parse
    clean_id = urllib.parse.unquote(order_id)
    payload = await request.json()
    new_status = payload.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="Missing status field")
    success = db_update_order_status(clean_id, new_status)
    return {"status": "ok" if success else "failed", "order_id": clean_id, "new_status": new_status}

@app.get("/api/sales/export", summary="Export All Sales Records to CSV")
async def export_sales_csv():
    """Generates and downloads an Excel-compatible CSV of all restaurant sales."""
    from database import get_sqlite_connection
    conn = get_sqlite_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, created_at, customer_name, customer_phone, order_type, address,
               items_list, subtotal, delivery_fee, total, status, special_notes
        FROM orders
        ORDER BY created_at DESC;
    """)
    rows = cur.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Order ID", "Date Time", "Customer Name", "Customer Phone", "Order Type",
        "Delivery Address / Table", "Items Ordered", "Subtotal (Rs.)", "Delivery Fee (Rs.)",
        "Total (Rs.)", "Status", "Special Notes"
    ])
    for r in rows:
        writer.writerow([
            r[0], r[1], r[2], r[3], r[4], r[5],
            (r[6] or "").replace("\n", " | "), r[7], r[8], r[9], r[10], r[11]
        ])

    output.seek(0)
    filename = f"cherry_peri_sales_{datetime.now().strftime('%Y%m%d')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────
@app.get("/orders", response_class=HTMLResponse, summary="Live Kitchen Orders Dashboard")
async def kitchen_orders_dashboard():
    orders = db_get_recent_orders(limit=50)
    rows_html = ""
    for o in orders:
        note_badge = f"<div style='background: #78350f; color: #fde68a; padding: 6px 10px; border-radius: 6px; font-size: 0.85rem; margin-top: 6px;'>📝 <strong>Note:</strong> {o.get('special_notes')}</div>" if o.get('special_notes') else ""
        type_str = (o.get('order_type') or 'delivery').upper()
        rows_html += f"""
        <div style="background: #1e293b; border-radius: 12px; padding: 18px; margin-bottom: 16px; border-left: 5px solid #22c55e; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <div>
                    <span style="font-weight: 800; font-size: 1.15rem; color: #38bdf8;">{o.get('order_id')}</span>
                    <span style="background: #0284c7; color: #fff; font-size: 0.75rem; padding: 2px 8px; border-radius: 12px; margin-left: 8px; font-weight: bold;">{type_str}</span>
                </div>
                <span style="color: #94a3b8; font-size: 0.85rem;">🕒 {o.get('timestamp')}</span>
            </div>
            <div style="color: #e2e8f0; margin-bottom: 6px; font-size: 0.95rem;"><strong>👤 Customer:</strong> {o.get('customer_name')} &nbsp;|&nbsp; <strong>📞 Phone:</strong> <a href="tel:{o.get('customer_phone')}" style="color: #38bdf8;">{o.get('customer_phone')}</a></div>
            <div style="color: #e2e8f0; margin-bottom: 10px; font-size: 0.95rem;"><strong>📍 Location:</strong> {o.get('address')}</div>
            <div style="background: #0f172a; padding: 12px; border-radius: 8px; color: #e2e8f0; font-family: -apple-system, sans-serif; white-space: pre-wrap; font-size: 0.9rem; line-height: 1.5; margin-bottom: 10px; border: 1px solid #334155;">{o.get('items_list') or o.get('slip')}</div>
            {note_badge}
            <div style="color: #22c55e; font-weight: bold; font-size: 1.1rem; margin-top: 8px;">💰 Total Bill: Rs. {o.get('total')}</div>
        </div>
        """
    if not rows_html:
        rows_html = "<div style='color: #94a3b8; text-align: center; padding: 60px; font-size: 1.1rem;'>No orders placed yet. Orders will appear here live!</div>"

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Cherry Peri — Live Kitchen Orders</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="refresh" content="10">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0b1120; color: #f8fafc; margin: 0; padding: 20px; }}
        .container {{ max-width: 760px; margin: 0 auto; }}
        h1 {{ display: flex; align-items: center; justify-content: space-between; font-size: 1.4rem; border-bottom: 2px solid #1e293b; padding-bottom: 14px; margin-bottom: 20px; }}
        .badge {{ background: #22c55e; color: #022c22; font-size: 0.8rem; padding: 4px 10px; border-radius: 20px; font-weight: 700; letter-spacing: 0.5px; }}
        .pos-btn {{ background: #e11d48; color: #fff; padding: 8px 16px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 0.85rem; display: inline-flex; align-items: center; gap: 6px; }}
    </style>
</head>
<body>
    <div class="container">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 2px solid #1e293b; padding-bottom: 14px;">
            <h1 style="margin: 0; border: none; padding: 0;">🍕 Cherry Peri Kitchen Orders</h1>
            <div style="display: flex; gap: 10px; align-items: center;">
                <span class="badge">● Live Auto-Refresh</span>
                <a href="/pos" class="pos-btn">🛒 Open POS & Sales</a>
            </div>
        </div>
        {rows_html}
    </div>
</body>
</html>"""
    return html

@app.get("/", summary="Health Check")
async def health_check():
    owner = os.getenv("OWNER_PHONE_NUMBER", "923160998053")
    has_owner = bool(owner)
    masked_owner = (owner[:4] + "***" + owner[-4:]) if len(owner) >= 8 else ("Set" if has_owner else "Not Set")
    return {
        "status": "🟢 running",
        "framework": "FastAPI",
        "bot": "WhatsApp Food Delivery Bot",
        "version": "2.2.0",
        "database": "PostgreSQL" if is_postgres() else "SQLite",
        "owner_alert_configured": has_owner,
        "owner_phone_masked": masked_owner,
        "gemini_api_configured": bool(os.getenv("GEMINI_API_KEY")),
        "evolution_configured": bool(os.getenv("EVOLUTION_API_URL") and os.getenv("EVOLUTION_API_KEY")),
        "evolution_instance": os.getenv("EVOLUTION_INSTANCE_NAME", "cherri perri"),
        "whatsapp_id_configured": bool(os.getenv("WHATSAPP_PHONE_NUMBER_ID")),
        "docs_url": "/docs"
    }

@app.get("/privacy", response_class=HTMLResponse, summary="Privacy Policy for Meta App Review")
async def privacy_policy():
    return """<!DOCTYPE html>
<html>
<head><title>Privacy Policy - Dikhan Care Bot</title><meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body style="font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6;">
  <h1>Privacy Policy</h1>
  <p>Last updated: October 2026</p>
  <p>Dikhan Care ("we", "our", or "us") respects your privacy. This Privacy Policy explains how our WhatsApp chatbot service handles your information.</p>
  <h3>1. Information We Collect</h3>
  <p>We only collect messages and contact numbers you send to our WhatsApp bot to process food orders and customer service inquiries.</p>
  <h3>2. How We Use Information</h3>
  <p>Information is used exclusively to facilitate order placement, status tracking, and delivery communication.</p>
  <h3>3. Data Protection</h3>
  <p>We do not sell, rent, or distribute personal data to third parties. All communications comply with Meta WhatsApp Business Platform policies.</p>
</body>
</html>"""

@app.get("/terms", response_class=HTMLResponse, summary="Terms of Service for Meta App Review")
async def terms_of_service():
    return """<!DOCTYPE html>
<html>
<head><title>Terms of Service - Dikhan Care Bot</title><meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body style="font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6;">
  <h1>Terms of Service</h1>
  <p>By using this WhatsApp service, you agree to place orders legitimately and provide accurate delivery information.</p>
</body>
</html>"""

@app.get("/webhook", summary="Meta Webhook Verification")
async def verify_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == WEBHOOK_VERIFY_TOKEN:
        print("[OK] Webhook verified successfully by Meta!")
        return PlainTextResponse(content=hub_challenge, status_code=200)

    print(f"[ERROR] Webhook verification failed. Token mismatch or bad mode: {hub_mode}")
    raise HTTPException(status_code=403, detail="Verification failed")

@app.post("/webhook", summary="WhatsApp Incoming Message Webhook")
async def receive_webhook(request: Request):
    data = await request.json()
    # Process incoming message directly so serverless functions (e.g. Vercel) don't freeze before completion
    await handle_incoming_messages(data)
    return JSONResponse(content={"status": "received"}, status_code=200)

if __name__ == "__main__":
    import uvicorn
    print(f"\n🍕 FastAPI WhatsApp Bot starting on port {PORT}...")
    print(f"📡 API Docs: http://localhost:{PORT}/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
