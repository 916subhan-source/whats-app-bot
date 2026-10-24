// ============================================
// 🚀 WhatsApp Food Delivery Bot — Server
// ============================================

const path = require("path");
require("dotenv").config({ path: path.resolve(__dirname, ".env"), override: true });
const express = require("express");
const axios = require("axios");
const { processMessage } = require("./chatbot");

const app = express();
app.use(express.json());

const {
  WHATSAPP_ACCESS_TOKEN,
  WHATSAPP_PHONE_NUMBER_ID,
  WEBHOOK_VERIFY_TOKEN,
  PORT = 3000,
} = process.env;

// ─────────────────────────────────────────────
// Health Check
// ─────────────────────────────────────────────
app.get("/", (req, res) => {
  res.json({
    status: "🟢 running",
    bot: "WhatsApp Food Delivery Bot",
    version: "1.0.0",
  });
});

// Privacy Policy (Required by Meta to switch App to Live Mode)
app.get("/privacy", (req, res) => {
  res.send(`<!DOCTYPE html>
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
  <h3>4. Contact Us</h3>
  <p>If you have any questions about this Privacy Policy, please contact our support team.</p>
</body>
</html>`);
});

// Terms of Service
app.get("/terms", (req, res) => {
  res.send(`<!DOCTYPE html>
<html>
<head><title>Terms of Service - Dikhan Care Bot</title><meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body style="font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6;">
  <h1>Terms of Service</h1>
  <p>By using this WhatsApp service, you agree to place orders legitimately and provide accurate delivery information.</p>
</body>
</html>`);
});

// ─────────────────────────────────────────────
// Webhook Verification (GET)
// Meta sends a GET request to verify the webhook
// ─────────────────────────────────────────────
app.get("/webhook", (req, res) => {
  const mode = req.query["hub.mode"];
  const token = req.query["hub.verify_token"];
  const challenge = req.query["hub.challenge"];

  if (mode === "subscribe" && token === WEBHOOK_VERIFY_TOKEN) {
    console.log("✅ Webhook verified successfully!");
    return res.status(200).send(challenge);
  }

  console.log("❌ Webhook verification failed.");
  return res.sendStatus(403);
});

// ─────────────────────────────────────────────
// Webhook Handler (POST)
// Receives incoming WhatsApp messages
// ─────────────────────────────────────────────
app.post("/webhook", async (req, res) => {
  // Always respond 200 quickly to Meta
  res.sendStatus(200);

  try {
    const body = req.body;

    // Validate the webhook payload structure
    if (
      !body.object ||
      !body.entry ||
      !body.entry[0]?.changes ||
      !body.entry[0]?.changes[0]?.value?.messages
    ) {
      return;
    }

    const changes = body.entry[0].changes[0];
    const messages = changes.value.messages;

    if (!messages || messages.length === 0) return;

    for (const message of messages) {
      // Mark message as read (gives user blue ticks)
      await markAsRead(message.id);

      // Only handle text messages for now
      if (message.type !== "text") {
        await sendWhatsAppMessage(
          message.from,
          "🤖 Sorry, I can only understand text messages right now.\n\nPlease type *hi* to get started!"
        );
        continue;
      }

      const phoneNumber = message.from;
      const incomingText = message.text.body;

      console.log(`📩 Message from ${phoneNumber}: "${incomingText}"`);

      // Process through AI conversation engine
      const reply = await processMessage(phoneNumber, incomingText);

      console.log(`📤 Reply to ${phoneNumber}: "${reply.substring(0, 80)}..."`);

      // Send reply back via WhatsApp API
      await sendWhatsAppMessage(phoneNumber, reply);
    }
  } catch (error) {
    console.error("❌ Error processing webhook:", error.message);
  }
});

// ─────────────────────────────────────────────
// Send Message via WhatsApp Cloud API
// ─────────────────────────────────────────────
async function sendWhatsAppMessage(to, text) {
  try {
    const url = `https://graph.facebook.com/v21.0/${WHATSAPP_PHONE_NUMBER_ID}/messages`;

    const response = await axios.post(
      url,
      {
        messaging_product: "whatsapp",
        to: to,
        type: "text",
        text: { body: text },
      },
      {
        headers: {
          Authorization: `Bearer ${WHATSAPP_ACCESS_TOKEN}`,
          "Content-Type": "application/json",
        },
      }
    );

    console.log(`✅ Message sent to ${to}`);
    return response.data;
  } catch (error) {
    console.error(
      "❌ Failed to send message:",
      error.response?.data || error.message
    );
    throw error;
  }
}

// Mark incoming message as read (blue ticks)
async function markAsRead(messageId) {
  try {
    await axios.post(
      `https://graph.facebook.com/v21.0/${WHATSAPP_PHONE_NUMBER_ID}/messages`,
      {
        messaging_product: "whatsapp",
        status: "read",
        message_id: messageId,
      },
      {
        headers: {
          Authorization: `Bearer ${WHATSAPP_ACCESS_TOKEN}`,
          "Content-Type": "application/json",
        },
      }
    );
  } catch (e) {
    // Non-critical, don't break flow
  }
}

// ─────────────────────────────────────────────
// Start Server
// ─────────────────────────────────────────────
app.listen(PORT, () => {
  console.log(`\n🍕 Food Delivery Bot is running!`);
  console.log(`📡 Server: http://localhost:${PORT}`);
  console.log(`🔗 Webhook: http://localhost:${PORT}/webhook`);
  console.log(`\n⚙️  Make sure to:`);
  console.log(`   1. Set up ngrok or a public URL`);
  console.log(`   2. Configure webhook in Meta Developer Dashboard`);
  console.log(`   3. Fill in your .env file with API credentials\n`);
});
