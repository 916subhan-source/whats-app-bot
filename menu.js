// ============================================
// 🍕 WhatsApp Food Delivery Chatbot - Menu Data
// ============================================

const RESTAURANT_INFO = {
  name: "🍕 Foodie Express & Grill",
  tagline: "Delicious pizzas, burgers & charcoal grills delivered fresh!",
  currency: "Rs.",
  deliveryFee: 50,
  estimatedTime: "30-45 mins",
};

const MENU = {
  pizza: {
    emoji: "🍕",
    name: "Pizzas",
    items: [
      { id: "p1", name: "Margherita (Medium)", price: 600, desc: "Rich mozzarella cheese & tomato basil sauce" },
      { id: "p2", name: "Pepperoni (Medium)", price: 750, desc: "Loaded with spicy beef pepperoni slices" },
      { id: "p3", name: "BBQ Chicken (Medium)", price: 800, desc: "Smoky BBQ chicken chunks, onions & cheese" },
      { id: "p4", name: "Veggie Supreme (Medium)", price: 700, desc: "Olives, mushrooms, bell peppers & onions" },
    ],
  },
  grill: {
    emoji: "🍗",
    name: "Grill & BBQ",
    items: [
      { id: "g1", name: "Chicken Tikka (Leg/Breast)", price: 450, desc: "Charcoal grilled juicy chicken quarter" },
      { id: "g2", name: "Chicken Malai Boti (8 Pcs)", price: 650, desc: "Melt-in-mouth creamy boneless boti" },
      { id: "g3", name: "Beef Seekh Kabab (4 Pcs)", price: 550, desc: "Spiced minced beef grilled on skewers" },
      { id: "g4", name: "Grilled Fish Fillet", price: 850, desc: "Fresh seasoned fish grilled with lemon butter" },
    ],
  },
  burgers: {
    emoji: "🍔",
    name: "Burgers",
    items: [
      { id: "b1", name: "Classic Beef Burger", price: 350, desc: "Grilled beef patty with lettuce & secret sauce" },
      { id: "b2", name: "Chicken Zinger Burger", price: 400, desc: "Crispy fried chicken fillet with creamy mayo" },
      { id: "b3", name: "Double Cheese Burger", price: 500, desc: "Double patty topped with melted cheddar" },
      { id: "b4", name: "Veggie Burger", price: 300, desc: "Crispy vegetable patty with fresh greens" },
    ],
  },
  sides: {
    emoji: "🍟",
    name: "Sides",
    items: [
      { id: "s1", name: "French Fries (Regular)", price: 150, desc: "Golden crispy salted fries" },
      { id: "s2", name: "Chicken Nuggets (6pc)", price: 250, desc: "Crispy golden nuggets with dip sauce" },
      { id: "s3", name: "Garlic Bread (4pc)", price: 200, desc: "Toasted herb garlic butter bread" },
      { id: "s4", name: "Fresh Coleslaw", price: 100, desc: "Creamy chilled cabbage & carrot slaw" },
    ],
  },
  drinks: {
    emoji: "🥤",
    name: "Drinks",
    items: [
      { id: "d1", name: "Coca Cola (500ml)", price: 80, desc: "Chilled refreshing soft drink" },
      { id: "d2", name: "Fresh Mint Lemonade", price: 140, desc: "Zesty fresh mint & lemon cooler" },
      { id: "d3", name: "Mango Shake (Special)", price: 200, desc: "Thick creamy real mango shake" },
      { id: "d4", name: "Mineral Water (500ml)", price: 50, desc: "Clean bottled drinking water" },
    ],
  },
};

module.exports = { RESTAURANT_INFO, MENU };
