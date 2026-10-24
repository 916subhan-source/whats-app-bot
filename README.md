# 🍕 WhatsApp Food Delivery Chatbot

A WhatsApp chatbot that lets customers browse a menu, add items to their cart, and place food delivery orders — all through WhatsApp!

## 📁 Project Structure

```
whatsapp-food-bot/
├── server.js      → Express webhook server
├── chatbot.js     → Conversation engine (state machine)
├── menu.js        → Restaurant menu data
├── .env           → Your API credentials (fill this in!)
├── .env.example   → Template for .env
└── package.json   → Project config
```

## 🚀 Setup Guide

### Step 1: Meta Developer Account

1. Go to [developers.facebook.com](https://developers.facebook.com/)
2. Log in with your Facebook account
3. Click **"Create App"** → **"Other"** → **"Business"**
4. Name your app (e.g., "Food Delivery Bot")

### Step 2: Add WhatsApp to Your App

1. In your app dashboard, click **"Add Product"**
2. Find **WhatsApp** and click **"Set Up"**
3. Go to **WhatsApp → API Setup**
4. Note down your:
   - **Phone Number ID**
   - **Temporary Access Token**

### Step 3: Configure .env

Edit the `.env` file with your credentials:

```env
WHATSAPP_ACCESS_TOKEN=your_access_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
WEBHOOK_VERIFY_TOKEN=my_food_bot_secret_123
PORT=3000
```

### Step 4: Make Your Server Public

WhatsApp needs a public URL to send webhook events. Use **ngrok**:

```bash
# Install ngrok (if not installed)
npm install -g ngrok

# Start ngrok tunnel
ngrok http 3000
```

Copy the **https** URL (e.g., `https://abc123.ngrok.io`)

### Step 5: Configure Webhook in Meta Dashboard

1. Go to **WhatsApp → Configuration** in your Meta app dashboard
2. Click **"Edit"** under Webhook
3. Set:
   - **Callback URL**: `https://your-ngrok-url/webhook`
   - **Verify Token**: `my_food_bot_secret_123` (must match .env)
4. Click **"Verify and Save"**
5. Subscribe to **"messages"** webhook field

### Step 6: Start the Bot

```bash
npm start
```

### Step 7: Test It!

Send **"hi"** to your WhatsApp Business test number!

## 🤖 Bot Commands

| Command | Action |
|---------|--------|
| `hi / hello` | Start the bot |
| `1 / menu` | Browse the menu |
| `2 / cart` | View your cart |
| `3` | Track order (coming soon) |
| `4 / help` | Show help |
| `checkout` | Place your order |
| `clear` | Empty your cart |
| `remove [n]` | Remove item from cart |

## 🛠️ Customization

Edit `menu.js` to change:
- Restaurant name and info
- Menu categories and items
- Prices and currency
- Delivery fee and estimated time
