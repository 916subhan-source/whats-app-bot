import os
import sys

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from typing import Optional
from fastapi import FastAPI, Request, Query, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import httpx
from dotenv import load_dotenv

from chatbot import process_message
from menu import MENU_PAGES

load_dotenv(override=True)

WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WEBHOOK_VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN", "my_food_bot_secret_123")
PORT = int(os.getenv("PORT", 3000))

app = FastAPI(
    title="🍕 Cherry Peri WhatsApp Food Delivery Bot — FastAPI",
    description="High-performance async WhatsApp Cloud API food delivery chatbot built with FastAPI & Gemini AI",
    version="2.1.0"
)

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# ─────────────────────────────────────────────
# Meta WhatsApp Cloud API Client
# ─────────────────────────────────────────────
async def send_whatsapp_message(to: str, text: str):
    url = f"https://graph.facebook.com/v21.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code >= 400:
            print(f"[ERROR] Failed to send WhatsApp message: {response.text}")
        else:
            print(f"[OK] Text message sent to {to}")
        return response.json()

async def send_whatsapp_image(to: str, media_id: str = None, image_url: str = None, caption: str = None):
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
        "to": to,
        "type": "image",
        "image": image_payload,
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code >= 400:
            print(f"[ERROR] Failed to send WhatsApp image to {to}: {response.text}")
        else:
            print(f"[OK] Image sent to {to}")
        return response.json()

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
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(url, json=payload, headers=headers)
    except Exception:
        pass

# Message processor handler
async def handle_incoming_messages(data: dict):
    try:
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

            # Mark message as read (blue ticks)
            if msg_id:
                await mark_as_read(msg_id)

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
            else:
                # Fallback for voice/images/stickers
                await send_whatsapp_message(
                    from_number,
                    f"Assalam-o-Alaikum {customer_name}! 😊 Please type your food order or write *menu* to see our dishes."
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
            # 🚨 Instant Kitchen / Owner Notification
            # ─────────────────────────────────────────────
            if isinstance(reply, dict) and reply.get("order_confirmed"):
                owner_phone = os.getenv("OWNER_PHONE_NUMBER", "923160998053")
                if owner_phone:
                    clean_owner = owner_phone.replace("+", "").replace(" ", "").replace("-", "").strip()
                    if clean_owner.startswith("0"):
                        clean_owner = "92" + clean_owner[1:]
                    details = reply.get("order_details", {})
                    order_slip = reply.get("text", "")
                    kitchen_alert = (
                        f"🚨 *NEW ORDER RECEIVED IN KITCHEN!* 🍕🍗\n\n"
                        f"{order_slip}\n\n"
                        f"🛵 Khana foran ready karein taake rider rawana ho sake!"
                    )
                    try:
                        print(f"[KITCHEN ALERT] Dispatching notification for order {details.get('order_id')} to owner {clean_owner}...")
                        await send_whatsapp_message(to=clean_owner, text=kitchen_alert)
                        print(f"[KITCHEN ALERT] Notification sent successfully to {clean_owner}!")
                    except Exception as alert_err:
                        print(f"[KITCHEN ALERT ERROR] Failed to send owner alert: {alert_err}")
    except Exception as e:
        print(f"[ERROR] Error handling messages: {e}")

# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────
@app.get("/", summary="Health Check")
async def health_check():
    owner = os.getenv("OWNER_PHONE_NUMBER", "923160998053")
    has_owner = bool(owner)
    masked_owner = (owner[:4] + "***" + owner[-4:]) if len(owner) >= 8 else ("Set" if has_owner else "Not Set")
    return {
        "status": "🟢 running",
        "framework": "FastAPI",
        "bot": "WhatsApp Food Delivery Bot",
        "version": "2.0.0",
        "owner_alert_configured": has_owner,
        "owner_phone_masked": masked_owner,
        "gemini_api_configured": bool(os.getenv("GEMINI_API_KEY")),
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
