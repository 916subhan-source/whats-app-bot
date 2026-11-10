import os
import base64
import httpx
from typing import Optional

WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")

async def download_whatsapp_media(media_id: str, access_token: str = None) -> tuple[Optional[bytes], Optional[str]]:
    token = access_token or os.getenv("WHATSAPP_ACCESS_TOKEN")
    if not token or not media_id:
        return None, None
    headers = {"Authorization": f"Bearer {token}"}
    try:
        url = f"https://graph.facebook.com/v21.0/{media_id}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            meta_res = await client.get(url, headers=headers)
            if meta_res.status_code != 200:
                print(f"[VOICE DOWNLOAD ERROR] Meta media query failed ({meta_res.status_code}): {meta_res.text}")
                return None, None
            media_info = meta_res.json()
            download_url = media_info.get("url")
            mime_type = media_info.get("mime_type", "audio/ogg")
            if not download_url:
                return None, None

            # Download actual audio bytes
            audio_res = await client.get(download_url, headers=headers)
            if audio_res.status_code == 200:
                print(f"[VOICE DOWNLOAD OK] Downloaded {len(audio_res.content)} bytes of audio ({mime_type})")
                return audio_res.content, mime_type
            else:
                print(f"[VOICE DOWNLOAD ERROR] Failed to fetch audio stream ({audio_res.status_code})")
                return None, None
    except Exception as e:
        print(f"[VOICE EXCEPTION] Error downloading media: {e}")
        return None, None

async def transcribe_with_groq(audio_bytes: bytes, mime_type: str, api_key: str) -> Optional[str]:
    try:
        url = "https://api.groq.com/openai/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {api_key}"}
        ext = "ogg" if "ogg" in mime_type else ("mp3" if "mp3" in mime_type else "m4a")
        files = {
            "file": (f"audio.{ext}", audio_bytes, mime_type.split(";")[0])
        }
        data = {
            "model": "whisper-large-v3-turbo",
            "prompt": "Cherry Peri Fast Food D.I. Khan customer food order, deal, burger, pizza, address, Roman Urdu, Urdu",
            "response_format": "text"
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(url, headers=headers, files=files, data=data)
            if res.status_code == 200:
                text = res.text.strip()
                print(f"[GROQ WHISPER OK] Transcribed: \"{text}\"")
                return text
            else:
                print(f"[GROQ ERROR] Status {res.status_code}: {res.text}")
    except Exception as e:
        print(f"[GROQ EXCEPTION] {e}")
    return None

async def transcribe_with_openai(audio_bytes: bytes, mime_type: str, api_key: str) -> Optional[str]:
    try:
        url = "https://api.openai.com/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {api_key}"}
        ext = "ogg" if "ogg" in mime_type else "mp3"
        files = {
            "file": (f"audio.{ext}", audio_bytes, mime_type.split(";")[0])
        }
        data = {
            "model": "whisper-1",
            "prompt": "Cherry Peri Fast Food food order in Urdu or English"
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(url, headers=headers, files=files, data=data)
            if res.status_code == 200:
                text = res.json().get("text", "").strip()
                print(f"[OPENAI WHISPER OK] Transcribed: \"{text}\"")
                return text
    except Exception as e:
        print(f"[OPENAI EXCEPTION] {e}")
    return None

async def transcribe_with_gemini(audio_bytes: bytes, mime_type: str, api_key: str) -> Optional[str]:
    clean_mime = mime_type.split(";")[0].strip() or "audio/ogg"
    b64_audio = base64.b64encode(audio_bytes).decode("utf-8")
    models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-flash-latest"]

    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": clean_mime,
                                "data": b64_audio
                            }
                        },
                        {
                            "text": (
                                "You are a speech-to-text transcriber for a Pakistani food restaurant (Cherry Peri Fast Food in D.I. Khan). "
                                "Transcribe the customer's audio recording word-for-word into Roman Urdu or English. "
                                "Common words: burger, zinger, pizza, deal, student viral deal, broast, fries, drink, address, tank adda, circular road, shop. "
                                "Output ONLY the transcribed words. Do not add any greeting, commentary, or explanation."
                            )
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 200
            }
        }
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        for p in parts:
                            if "text" in p and not p.get("thought", False):
                                text = p["text"].strip()
                                if text:
                                    print(f"[GEMINI AUDIO OK] Transcribed ({model}): \"{text}\"")
                                    return text
        except Exception as e:
            print(f"[GEMINI AUDIO ERROR] {model}: {e}")
    return None

async def transcribe_whatsapp_voice(media_id: str, mime_type: str = "audio/ogg") -> Optional[str]:
    # 1. Download audio bytes from Meta Graph API
    audio_bytes, actual_mime = await download_whatsapp_media(media_id)
    if not audio_bytes:
        print("[VOICE] Could not download audio from WhatsApp.")
        return None

    use_mime = actual_mime or mime_type or "audio/ogg"

    # 2. Try Groq Whisper (ultra-fast transcription)
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        text = await transcribe_with_groq(audio_bytes, use_mime, groq_key)
        if text:
            return text

    # 3. Try Gemini Multimodal Audio
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        text = await transcribe_with_gemini(audio_bytes, use_mime, gemini_key)
        if text:
            return text

    # 4. Try OpenAI Whisper
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        text = await transcribe_with_openai(audio_bytes, use_mime, openai_key)
        if text:
            return text

    print("[VOICE] No speech-to-text API configured or succeeded.")
    return None

