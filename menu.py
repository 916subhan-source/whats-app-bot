# ============================================
# 🍕 Cherry Peri Fast Food - Official Menu Data (Updated)
# ============================================

RESTAURANT_INFO = {
    "name": "Cherry Peri Fast Food",
    "tagline": "Delicious pizzas, zingers, deals & fast food delivered fresh in D.I. Khan!",
    "currency": "Rs.",
    "deliveryFee": 0,
    "estimatedTime": "30-45 mins",
    "address": "Opposite Stylo Shopping Center, Circular Road, Dera Ismail Khan",
    "phones": ["0332-7247289", "0341-5531083"]
}

MENU_PAGES = [
    {
        "id": "card_1_deals_pizza",
        "url": "https://whats-app-bot-jet.vercel.app/static/menu_card_1.jpg",
        "caption": "🍕 *Cherry Peri Deals & Pizzas* (Deals 1–26 & Fresh Pizzas)"
    },
    {
        "id": "card_2_fast_food",
        "url": "https://whats-app-bot-jet.vercel.app/static/menu_card_2.jpg",
        "caption": "🍔 *Burgers, Shawarmas, Paratha Rolls, Pastas, Wraps & Fries*"
    }
]

PIZZA_SIZES = {
    "small": {"name": "Small (6\")", "label": "Small"},
    "medium": {"name": "Medium (9\")", "label": "Medium"},
    "large": {"name": "Large (11\")", "label": "Large"},
    "family": {"name": "Family Pizza", "label": "Family"},
    "square": {"name": "Square Pizza", "label": "Square"},
}

PIZZA_CRUSTS = {
    "reg": {"name": "Regular Pan Crust", "short": "Regular", "extra": 0},
    "crown": {"name": "Peri Crown Crust", "short": "Peri Crown", "extra": 0},
    "cheese": {"name": "Cheese Stuffer Crust", "short": "Cheese Stuffer", "extra": 0},
    "kabab": {"name": "Kabab Stuffer Crust", "short": "Kabab Stuffer", "extra": 0},
}

MENU = {
    "deals": {
        "emoji": "🌟",
        "name": "Amazing Deals (1 to 26)",
        "items": [
            {"id": "deal_1", "name": "Deal 1 (1 Small Pizza + 1 Zinger Burger + 1L Drink)", "price": 800},
            {"id": "deal_2", "name": "Deal 2 (2 Chicken Shawarma + 2 Chicken Paratha Roll + 1L Drink)", "price": 820},
            {"id": "deal_3", "name": "Deal 3 (2 Zinger Burger + 2 Chicken Shawarma + 1L Drink)", "price": 900},
            {"id": "deal_4", "name": "Deal 4 (2 Zinger Burger + 1 Chicken Omelette Burger + 1 Chicken Shawarma + 1L Drink)", "price": 1000},
            {"id": "deal_5", "name": "Deal 5 (10 Hot Wings + 10 Nuggets + 1L Drink)", "price": 940},
            {"id": "deal_6", "name": "Deal 6 (1 Small Pizza + 2 Zinger Burger + 1 Zinger Shawarma + 1L Drink)", "price": 1000},
            {"id": "deal_7", "name": "Deal 7 (2 Small Pizza + 1L Drink)", "price": 950},
            {"id": "deal_8", "name": "Deal 8 (1 Medium Pizza + 1 Chapli Burger + 5 Nuggets + 1L Drink)", "price": 1200},
            {"id": "deal_9", "name": "Deal 9 (10 Nuggets + 2 Zinger Paratha + 2 Zinger Shawarma + 1L Drink)", "price": 1400},
            {"id": "deal_10", "name": "Deal 10 (1 Small Pizza + 1 Zinger Burger + 10 Hot Wings + 1L Drink)", "price": 1250},
            {"id": "deal_11", "name": "Deal 11 (5 Zinger Burger + 1.5L Drink)", "price": 1400},
            {"id": "deal_12", "name": "Deal 12 (3 Zinger Burger + 3 Zinger Shawarma + 1L Drink)", "price": 1500},
            {"id": "deal_13", "name": "Deal 13 (2 Small Pizza + 5 Hot Wings + 1.5L Drink)", "price": 1250},
            {"id": "deal_14", "name": "Deal 14 (1 Medium Pizza + 10 Hot Wings + 5 Nuggets + 1L Drink)", "price": 1450},
            {"id": "deal_15", "name": "Deal 15 (2 Small Pizza + 2 Zinger Burger + 1.5L Drink)", "price": 1520},
            {"id": "deal_16", "name": "Deal 16 (2 Medium Pizza + 1L Drink)", "price": 1550},
            {"id": "deal_17", "name": "Deal 17 (5 Zinger Burger + 10 Hot Wings + 1L Drink)", "price": 1850},
            {"id": "deal_18", "name": "Deal 18 (1 Large Pizza + 1 Zinger Burger + 1 Zinger Shawarma + 5 Hot Wings + 1.5L Drink)", "price": 1900},
            {"id": "deal_19", "name": "Deal 19 (1 Large Pizza + 1 Zinger Paratha + 10 Hot Wings + 1.5L Drink)", "price": 1900},
            {"id": "deal_20", "name": "Deal 20 (1 Large Pizza + 1 Medium Pizza + 1.5L Drink)", "price": 1900},
            {"id": "deal_21", "name": "Deal 21 (1 Zinger Burger + Fries + 1 Regular Drink)", "price": 400},
            {"id": "deal_22", "name": "Deal 22 (2 Large Pizza + 1.5L Drink)", "price": 2200},
            {"id": "deal_23", "name": "Deal 23 (1 Small Pizza + 1 Medium Pizza + 1.5L Drink)", "price": 1250},
            {"id": "deal_24", "name": "Deal 24 (1 Large Pizza + 10 Hot Wings + 10 Nuggets + 1.5L Drink)", "price": 2000},
            {"id": "deal_25", "name": "Deal 25 (5 Zinger Shawarma + 10 Wings + 1.5L Drink)", "price": 1600},
            {"id": "deal_26", "name": "Deal 26 (5 Zinger Shawarma + 1.5L Drink)", "price": 1180},
        ]
    },
    "pizza_regular": {
        "emoji": "🍕",
        "name": "Regular Pizzas (Any Flavor: Tikka, Fajita, Tandoori, BBQ, etc.)",
        "items": [
            {"id": "pz_reg_small", "name": "Regular Pizza (Small)", "price": 450},
            {"id": "pz_reg_med", "name": "Regular Pizza (Medium)", "price": 750},
            {"id": "pz_reg_large", "name": "Regular Pizza (Large)", "price": 1100},
            {"id": "pz_reg_family", "name": "Regular Pizza (Family)", "price": 1700},
            {"id": "pz_square", "name": "Square Pizza", "price": 1050},
        ]
    },
    "pizza_special": {
        "emoji": "🍕",
        "name": "Special Pizzas (Cherry Peri Special, Malai Boti, etc.)",
        "items": [
            {"id": "pz_sp_small", "name": "Special Pizza (Small)", "price": 600},
            {"id": "pz_sp_med", "name": "Special Pizza (Medium)", "price": 950},
            {"id": "pz_sp_large", "name": "Special Pizza (Large)", "price": 1300},
            {"id": "pz_sp_family", "name": "Special Pizza (Family)", "price": 2000},
        ]
    },
    "burgers": {
        "emoji": "🍔",
        "name": "Burgers",
        "items": [
            {"id": "b_anda_shami", "name": "Anda Shami Burger", "prices": {"regular": 200, "special": 150}},
            {"id": "b_double_anda", "name": "Double Anda Burger", "prices": {"regular": 270, "special": 220}},
            {"id": "b_chicken", "name": "Chicken Burger", "prices": {"regular": 270, "special": 220}},
            {"id": "b_chicken_anda", "name": "Chicken Anda Burger", "prices": {"regular": 320, "special": 260}},
            {"id": "b_chicken_omelette", "name": "Chicken Omelette Burger", "price": 260},
            {"id": "b_zinger", "name": "Zinger Burger", "prices": {"regular": 350, "special": 270}},
            {"id": "b_double_decker", "name": "Double Decker Zinger Burger", "prices": {"regular": 500, "special": 450}},
            {"id": "b_jaddah_special", "name": "Jaddah Special Zinger Burger", "price": 500},
            {"id": "b_sadah_band", "name": "Sadah Band Zinger Burger", "prices": {"regular": 350, "special": 300}},
            {"id": "b_pizza_burger", "name": "Pizza Burger", "prices": {"regular": 400, "special": 350}},
            {"id": "b_patty", "name": "Patty Burger", "prices": {"regular": 250, "special": 200}},
            {"id": "b_chapli", "name": "Chapli Burger", "prices": {"regular": 250, "special": 200}},
        ]
    },
    "shawarma": {
        "emoji": "🌯",
        "name": "Shawarma",
        "items": [
            {"id": "sh_chicken", "name": "Chicken Shawarma", "prices": {"regular": 200, "special": 150}},
            {"id": "sh_zinger", "name": "Zinger Shawarma", "prices": {"regular": 300, "special": 220}},
            {"id": "sh_single_kabab", "name": "Single Kabab Shawarma", "prices": {"regular": 190, "special": 140}},
            {"id": "sh_double_kabab", "name": "Double Kabab Shawarma", "prices": {"regular": 250, "special": 260}},
            {"id": "sh_kabab_chicken", "name": "Kabab Chicken Shawarma", "prices": {"regular": 250, "special": 200}},
            {"id": "sh_tikka", "name": "Tikka Shawarma", "prices": {"regular": 300, "special": 250}},
            {"id": "sh_malai_boti", "name": "Malai Boti Shawarma", "prices": {"regular": 300, "special": 250}},
            {"id": "sh_chicken_platter", "name": "Chicken Platter Shawarma", "price": 400},
            {"id": "sh_zinger_platter", "name": "Zinger Platter Shawarma", "price": 450},
            {"id": "sh_crunchy", "name": "Crunchy Shawarma", "price": 150},
        ]
    },
    "paratha_roll": {
        "emoji": "🌯",
        "name": "Paratha Rolls",
        "items": [
            {"id": "pr_chicken", "name": "Chicken Paratha Roll", "prices": {"regular": 300, "special": 230}},
            {"id": "pr_zinger", "name": "Zinger Paratha Roll", "prices": {"regular": 350, "special": 270}},
            {"id": "pr_kabab", "name": "Kabab Paratha Roll", "prices": {"regular": 300, "special": 250}},
            {"id": "pr_double_kabab", "name": "Double Kabab Paratha Roll", "prices": {"regular": 300, "special": 250}},
            {"id": "pr_tikka", "name": "Tikka Paratha Roll", "price": 320},
            {"id": "pr_malai_boti", "name": "Malai Boti Paratha Roll", "price": 350},
            {"id": "pr_shahi_shapata", "name": "Shapata / Shahi Roll", "prices": {"regular": 500, "special": 450}},
            {"id": "pr_jaddah", "name": "Jaddah Special Paratha Roll", "price": 500},
            {"id": "pr_pizza", "name": "Pizza Paratha", "price": 500},
        ]
    },
    "wraps": {
        "emoji": "🌯",
        "name": "Wraps",
        "items": [
            {"id": "wr_jaddah", "name": "Jaddah Special Wrap", "price": 500},
            {"id": "wr_cheese", "name": "Chicken Cheese Wrap", "price": 300},
            {"id": "wr_zinger", "name": "Zinger Wrap", "price": 350},
            {"id": "wr_tikka", "name": "Tikka Boti Wrap", "price": 400},
            {"id": "wr_malai", "name": "Malai Boti Wrap", "price": 400},
        ]
    },
    "pasta": {
        "emoji": "🍝",
        "name": "Pastas",
        "items": [
            {"id": "pas_cheese", "name": "Chicken Cheese Pasta", "prices": {"small": 400, "large": 500}},
            {"id": "pas_crunchy", "name": "Crunchy Pasta", "prices": {"small": 450, "large": 550}},
        ]
    },
    "sandwich": {
        "emoji": "🥪",
        "name": "Sandwiches",
        "items": [
            {"id": "sw_cheese", "name": "Chicken Cheese Sandwich", "price": 300},
            {"id": "sw_club", "name": "Chicken Club Sandwich", "price": 300},
            {"id": "sw_egg", "name": "Anda Sandwich", "price": 150},
            {"id": "sw_grill", "name": "Grill Sandwich", "price": 350},
        ]
    },
    "fries": {
        "emoji": "🍟",
        "name": "Fries",
        "items": [
            {"id": "fr_french", "name": "French Fries", "prices": {"small": 200, "large": 400}},
            {"id": "fr_masala", "name": "Masala Fries", "prices": {"small": 250, "large": 450}},
            {"id": "fr_loaded", "name": "Loaded Fries", "prices": {"small": 400, "large": 600}},
            {"id": "fr_cheese", "name": "Cheese Fries", "prices": {"small": 350, "large": 400}},
        ]
    },
    "wings_nuggets": {
        "emoji": "🍗",
        "name": "Wings & Nuggets",
        "items": [
            {"id": "w_hot_10", "name": "Hot Wings (10 Pcs)", "price": 460},
            {"id": "w_hot_5", "name": "Hot Wings (5 Pcs)", "price": 250},
            {"id": "ng_10", "name": "Nuggets (10 Pcs)", "price": 400},
            {"id": "ng_5", "name": "Nuggets (5 Pcs)", "price": 200},
            {"id": "b_zinger_piece", "name": "Zinger Piece", "price": 180},
        ]
    }
}
