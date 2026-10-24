const path = require("path");
require("dotenv").config({ path: path.resolve(__dirname, ".env"), override: true });
const https = require("https");
const { RESTAURANT_INFO, MENU } = require("./menu");

// In-memory conversation history & active cart per customer
const conversationHistory = new Map();
const userCarts = new Map();

function getHistory(phoneNumber) {
  if (!conversationHistory.has(phoneNumber)) {
    conversationHistory.set(phoneNumber, []);
  }
  return conversationHistory.get(phoneNumber);
}

function getCart(phoneNumber) {
  if (!userCarts.has(phoneNumber)) {
    userCarts.set(phoneNumber, { items: [], address: null });
  }
  return userCarts.get(phoneNumber);
}

// Prepare comprehensive restaurant & menu knowledge base
const menuKnowledgeBase = `
RESTAURANT DETAILS:
- Name: ${RESTAURANT_INFO.name}
- Tagline: ${RESTAURANT_INFO.tagline}
- Currency: ${RESTAURANT_INFO.currency}
- Standard Delivery Fee: ${RESTAURANT_INFO.currency} ${RESTAURANT_INFO.deliveryFee}
- Estimated Delivery Time: ${RESTAURANT_INFO.estimatedTime}

COMPLETE MENU ITEMS & PRICES:
${Object.values(MENU)
  .map(
    (cat) =>
      `Category: ${cat.name} (${cat.emoji})\n` +
      cat.items
        .map((item) => `  * ${item.name} -> ${RESTAURANT_INFO.currency} ${item.price}`)
        .join("\n")
  )
  .join("\n\n")}
`;

const SYSTEM_INSTRUCTION = `
You are the warm, friendly, intelligent, and human WhatsApp ordering assistant for "${RESTAURANT_INFO.name}".

PERSONALITY & LANGUAGE:
1. Talk like a friendly, helpful human employee answering on WhatsApp. Never sound like a robot or a numbered keypad menu.
2. Fluently speak and understand English, Urdu, and Roman Urdu (e.g., "bhai ek chicken zinger aur coke bhej do", "kya menu hai aapka?", "kitna time lagega delivery mein?").
3. Match the user's language and tone. If they speak Urdu, reply in sweet/polite Roman Urdu. If English, reply in English.

DUTIES:
1. Help customers choose what to eat, recommend popular items (like Chicken Zinger Burger, Pepperoni Pizza), explain items, and answer questions.
2. Keep calculations accurate based on the menu prices above.
3. When taking an order:
   - Keep track of what they want.
   - Ask for their delivery address if they haven't provided it.
   - Provide a clear breakdown: Items, Subtotal, Delivery Fee (${RESTAURANT_INFO.currency} ${RESTAURANT_INFO.deliveryFee}), and Total.
4. Format your messages nicely for WhatsApp with emojis, bullet points, and *bold* for prices.
5. If the order is confirmed with an address, give them an Order ID (like #FE-8892) and wish them a wonderful meal!

${menuKnowledgeBase}
`;

function callGeminiAI(userHistory, apiKey) {
  return new Promise((resolve, reject) => {
    const contents = [
      {
        role: "user",
        parts: [{ text: `System Instruction: ${SYSTEM_INSTRUCTION}` }],
      },
      {
        role: "model",
        parts: [{ text: "Understood! I am the friendly, human-like AI WhatsApp assistant for Foodie Express. I speak English, Urdu, and Roman Urdu fluently." }],
      },
      ...userHistory,
    ];

    const payload = JSON.stringify({
      contents: contents,
      generationConfig: {
        temperature: 0.7,
        maxOutputTokens: 600,
      },
    });

    const options = {
      hostname: "generativelanguage.googleapis.com",
      path: `/v1beta/models/gemini-3.8-flash:generateContent?key=${apiKey}`,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(payload),
      },
    };

    const req = https.request(options, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => {
        try {
          const json = JSON.parse(data);
          if (json.candidates && json.candidates[0]?.content?.parts) {
            const textPart = json.candidates[0].content.parts.find((p) => p.text && !p.thought);
            const finalText = textPart ? textPart.text : json.candidates[0].content.parts[0].text;
            resolve(finalText.trim());
          } else {
            reject(new Error("Empty response from Gemini"));
          }
        } catch (e) {
          reject(e);
        }
      });
    });

    // 6-second timeout so WhatsApp is always snappy
    req.setTimeout(6000, () => {
      req.destroy(new Error("Gemini API call timed out"));
    });

    req.on("error", reject);
    req.write(payload);
    req.end();
  });
}

// ─────────────────────────────────────────────
// Intelligent Local Fallback Engine (Zero failure guarantee)
// ─────────────────────────────────────────────
function generateIntelligentFallback(phoneNumber, messageText) {
  const text = messageText.toLowerCase().trim();
  const cart = getCart(phoneNumber);

  // 1. Menu request
  if (
    text.includes("menu") ||
    text.includes("kya hai") ||
    text.includes("list") ||
    text.includes("rates") ||
    text.includes("price") ||
    text.includes("cheezain")
  ) {
    let reply = `📋 *${RESTAURANT_INFO.name} — Menu*\n\n`;
    for (const cat of Object.values(MENU)) {
      reply += `${cat.emoji} *${cat.name}*\n`;
      for (const item of cat.items) {
        reply += `  • ${item.name} — *${RESTAURANT_INFO.currency} ${item.price}*\n`;
      }
      reply += "\n";
    }
    reply += `🛵 Delivery Fee: *${RESTAURANT_INFO.currency} ${RESTAURANT_INFO.deliveryFee}* (${RESTAURANT_INFO.estimatedTime})\n\n`;
    reply += `Order karne ke liye bas item ka naam likhein (e.g. *1 Zinger Burger aur 1 Coke*)!`;
    return reply;
  }

  // 2. Check for food items mentioned
  const foundItems = [];
  const ITEM_KEYWORDS = [
    { id: "b2", keywords: ["zinger", "chicken burger"], defaultQty: 1 },
    { id: "b1", keywords: ["beef burger", "beef"], defaultQty: 1 },
    { id: "b3", keywords: ["double cheese", "cheese burger"], defaultQty: 1 },
    { id: "b4", keywords: ["veggie burger"], defaultQty: 1 },
    { id: "p2", keywords: ["pepperoni"], defaultQty: 1 },
    { id: "p1", keywords: ["margherita"], defaultQty: 1 },
    { id: "p3", keywords: ["bbq chicken", "bbq pizza", "bbq"], defaultQty: 1 },
    { id: "p4", keywords: ["veggie supreme", "veggie pizza"], defaultQty: 1 },
    { id: "s1", keywords: ["fries", "finger chips", "french fries"], defaultQty: 1 },
    { id: "s2", keywords: ["nuggets", "chicken nuggets"], defaultQty: 1 },
    { id: "s3", keywords: ["garlic bread"], defaultQty: 1 },
    { id: "s4", keywords: ["coleslaw"], defaultQty: 1 },
    { id: "d1", keywords: ["coke", "coca cola", "cola", "cold drink"], defaultQty: 1 },
    { id: "d2", keywords: ["fresh lime", "lime"], defaultQty: 1 },
    { id: "d3", keywords: ["mango shake", "shake"], defaultQty: 1 },
    { id: "d4", keywords: ["water", "water bottle", "paani"], defaultQty: 1 },
  ];

  // Generic fallbacks if user just says "burger" or "pizza"
  if (text.includes("burger") && !ITEM_KEYWORDS.slice(0, 4).some(k => k.keywords.some(w => text.includes(w)))) {
    ITEM_KEYWORDS[0].matchedGeneric = true;
  }
  if (text.includes("pizza") && !ITEM_KEYWORDS.slice(4, 8).some(k => k.keywords.some(w => text.includes(w)))) {
    ITEM_KEYWORDS[4].matchedGeneric = true;
  }

  // Lookup table
  const allItemsMap = {};
  for (const cat of Object.values(MENU)) {
    for (const item of cat.items) {
      allItemsMap[item.id] = item;
    }
  }

  for (const entry of ITEM_KEYWORDS) {
    let matched = entry.matchedGeneric || entry.keywords.some((kw) => text.includes(kw));
    if (matched) {
      const item = allItemsMap[entry.id];
      if (item && !foundItems.some((f) => f.id === item.id)) {
        // Extract quantity if specified (e.g. "2 zinger", "3x coke", "ek zinger")
        let qty = 1;
        const kwRegex = entry.keywords.join("|");
        const numMatch = text.match(new RegExp(`(\\d+)\\s*(?:x\\s*)?(?:${kwRegex})`));
        if (numMatch) {
          qty = parseInt(numMatch[1]);
        } else if (text.includes("do ") || text.includes("2 ")) {
          qty = 2;
        } else if (text.includes("teen ") || text.includes("3 ")) {
          qty = 3;
        }
        foundItems.push({ ...item, quantity: qty });
      }
    }
  }

  if (foundItems.length > 0) {
    cart.items = foundItems;
    let subtotal = 0;
    let itemsList = "";
    for (const item of foundItems) {
      const itemTotal = item.price * item.quantity;
      subtotal += itemTotal;
      itemsList += `• ${item.quantity}x ${item.name} — *${RESTAURANT_INFO.currency} ${itemTotal}*\n`;
    }
    const total = subtotal + RESTAURANT_INFO.deliveryFee;

    return (
      `Wah, zabardast choice! 😋 Aapka order note ho gaya hai:\n\n` +
      `${itemsList}\n` +
      `Subtotal: *${RESTAURANT_INFO.currency} ${subtotal}*\n` +
      `Delivery Fee: *${RESTAURANT_INFO.currency} ${RESTAURANT_INFO.deliveryFee}*\n` +
      `*Total: ${RESTAURANT_INFO.currency} ${total}*\n\n` +
      `📍 Meharbani karke apna *Delivery Address* (Ghar / Mohalla / City) send kijiye taake rider foran rawana ho sake!`
    );
  }

  // 3. Address provided
  if (
    cart.items.length > 0 &&
    (text.includes("house") ||
      text.includes("street") ||
      text.includes("gali") ||
      text.includes("mohalla") ||
      text.includes("road") ||
      text.includes("near") ||
      text.includes("dikhan") ||
      text.includes("islamabad") ||
      text.includes("sector") ||
      text.split(" ").length >= 3)
  ) {
    cart.address = messageText;
    const orderId = "#FE-" + Math.floor(1000 + Math.random() * 9000);
    const orderedItems = [...cart.items];
    cart.items = []; // Reset cart after confirmation

    return (
      `🎉 *Order Confirmed!* (ID: *${orderId}*)\n\n` +
      `Aapka order kitchen mein tayaar ho raha hai aur *${RESTAURANT_INFO.estimatedTime}* mein pohnch jayega!\n\n` +
      `📍 *Delivery Address:* ${messageText}\n` +
      `💵 *Payment:* Cash on Delivery (COD)\n\n` +
      `Khana garma garam pohnchne tak intezar farmaiye. Shukriya for choosing *${RESTAURANT_INFO.name}*! ❤️`
    );
  }

  // 4. Default warm greeting / guidance
  return (
    `Assalam-o-Alaikum! 👋 Welcome to *${RESTAURANT_INFO.name}*! 🍕\n\n` +
    `Main aapka food ordering assistant hoon. Aaj kya khane ka mood hai?\n\n` +
    `• Hamara *Menu* dekhne ke liye likhein: *menu*\n` +
    `• Ya direct order karein, jaise: *1 Chicken Zinger Burger aur 1 Coke*\n\n` +
    `Bataiye aapke liye kya bhejoon? 😊`
  );
}

async function processMessage(phoneNumber, messageText) {
  const apiKey = process.env.GEMINI_API_KEY;

  if (apiKey) {
    try {
      const history = getHistory(phoneNumber);
      history.push({
        role: "user",
        parts: [{ text: messageText }],
      });

      const recentHistory = history.slice(-6);
      const aiReply = await callGeminiAI(recentHistory, apiKey);

      history.push({
        role: "model",
        parts: [{ text: aiReply }],
      });

      return aiReply;
    } catch (err) {
      console.log("ℹ️ Gemini AI fallback engaged:", err.message);
    }
  }

  // Seamless fallback ensuring instant response
  return generateIntelligentFallback(phoneNumber, messageText);
}

module.exports = { processMessage };
