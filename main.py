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
import httpx
from dotenv import load_dotenv

from chatbot import process_message

load_dotenv(override=True)

WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WEBHOOK_VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN", "my_food_bot_secret_123")
PORT = int(os.getenv("PORT", 3000))

app = FastAPI(
    title="🍕 WhatsApp Food Delivery Bot — FastAPI",
    description="High-performance async WhatsApp Cloud API food delivery chatbot built with FastAPI & Gemini AI",
    version="2.0.0"
)

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
            print(f"[OK] Message sent to {to}")
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

# Background task to process messages without delaying Meta webhook 200 response
async def handle_incoming_messages(data: dict):
    try:
        entry = data.get("entry", [])
        if not entry:
            return
        changes = entry[0].get("changes", [])
        if not changes:
            return
        value = changes[0].get("value", {})
        messages = value.get("messages", [])

        for message in messages:
            msg_id = message.get("id")
            from_number = message.get("from")
            msg_type = message.get("type")

            # Mark message as read (blue ticks)
            if msg_id:
                await mark_as_read(msg_id)

            if msg_type != "text":
                await send_whatsapp_message(
                    from_number,
                    "🤖 Sorry, I can only understand text messages right now.\n\nPlease type *hi* or *menu* to get started!"
                )
                continue

            incoming_text = message.get("text", {}).get("body", "")
            print(f"[MSG] Message from {from_number}: \"{incoming_text}\"")

            # Process through conversational AI engine
            reply = await process_message(from_number, incoming_text)
            print(f"[REPLY] Reply to {from_number}: \"{reply[:80]}...\"")

            # Send WhatsApp message back
            await send_whatsapp_message(from_number, reply)
    except Exception as e:
        print(f"[ERROR] Error handling messages: {e}")

# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────
@app.get("/", summary="Health Check")
async def health_check():
    return {
        "status": "🟢 running",
        "framework": "FastAPI",
        "bot": "WhatsApp Food Delivery Bot",
        "version": "2.0.0",
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
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    # Fast 200 response to Meta, process message in background task
    background_tasks.add_task(handle_incoming_messages, data)
    return JSONResponse(content={"status": "received"}, status_code=200)

if __name__ == "__main__":
    import uvicorn
    print(f"\n🍕 FastAPI WhatsApp Bot starting on port {PORT}...")
    print(f"📡 API Docs: http://localhost:{PORT}/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
