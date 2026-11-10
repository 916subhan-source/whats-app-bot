# ============================================
# 🍕 Cherry Peri Fast Food - Official Menu Data
# ============================================

RESTAURANT_INFO = {
    "name": "Cherry Peri Fast Food",
    "tagline": "Delicious pizzas, zingers, broast & fast food delivered fresh in D.I. Khan!",
    "currency": "Rs.",
    "deliveryFee": 0,
    "estimatedTime": "30-45 mins",
    "address": "Opposite Stylo Shopping Center, Circular Road, Dera Ismail Khan",
    "phones": ["0332-7247289", "0341-5531083"]
}

MENU_PAGES = [
    {
        "id": "2205624197022076",
        "url": "https://whats-app-bot-beige.vercel.app/static/menu_page_1.jpg",
        "caption": "🍕 *Pizzas & Special Pizzas* — Cherry Peri"
    },
    {
        "id": "1425424989371303",
        "url": "https://whats-app-bot-beige.vercel.app/static/menu_page_2.jpg",
        "caption": "🍔 *Burgers, Pastas, Broast, Wings & Drinks* — Cherry Peri"
    },
    {
        "id": "1620610766411621",
        "url": "https://whats-app-bot-beige.vercel.app/static/menu_page_3.jpg",
        "caption": "🌟 *Special Deals (Student & Family)* — Cherry Peri"
    },
    {
        "id": "1144228828565454",
        "url": "https://whats-app-bot-beige.vercel.app/static/menu_page_4.jpg",
        "caption": "🌯 *Rolls, Loaded Fries, Shawarma & Wraps* — Cherry Peri"
    }
]

PIZZA_SIZES = {
    "personal": {"name": "Personal (6\")", "label": "Personal"},
    "medium": {"name": "Medium (9\")", "label": "Medium"},
    "large": {"name": "Large (13\")", "label": "Large"},
    "xlarge": {"name": "XL Family (17\")", "label": "XL Family"},
}

PIZZA_CRUSTS = {
    "reg": {"name": "Regular Pan Crust", "short": "Regular", "extra": 0},
    "crown": {"name": "Peri Crown Crust", "short": "Peri Crown", "extra": 0},
    "cheese": {"name": "Cheese Stuffer Crust", "short": "Cheese Stuffer", "extra": 0},
    "kabab": {"name": "Kabab Stuffer Crust", "short": "Kabab Stuffer", "extra": 0},
}

MENU = {
    "pizza": {
        "emoji": "🍕",
        "name": "Standard Pizzas",
        "desc": "Tandoori, Hot N Spicy, Supreme, Cheese Lover, Chicken Tikka, Fajita, BBQ",
        "items": [
            {"id": "p_tandoori", "name": "Tandoori Pizza", "prices": {"personal": 500, "medium": 800, "large": 1400, "xlarge": 1900}},
            {"id": "p_hotnspicy", "name": "Hot N Spicy Pizza", "prices": {"personal": 500, "medium": 800, "large": 1400, "xlarge": 1900}},
            {"id": "p_supreme", "name": "Supreme Pizza", "prices": {"personal": 500, "medium": 800, "large": 1400, "xlarge": 1900}},
            {"id": "p_cheeselover", "name": "Cheese Lover Pizza", "prices": {"personal": 500, "medium": 800, "large": 1400, "xlarge": 1900}},
            {"id": "p_chickentikka", "name": "Chicken Tikka Pizza", "prices": {"personal": 500, "medium": 800, "large": 1400, "xlarge": 1900}},
            {"id": "p_fajita", "name": "Fajita Pizza", "prices": {"personal": 500, "medium": 800, "large": 1400, "xlarge": 1900}},
            {"id": "p_bbq", "name": "BBQ Pizza", "prices": {"personal": 500, "medium": 800, "large": 1400, "xlarge": 1900}},
        ]
    },
    "special_pizza": {
        "emoji": "🍕",
        "name": "Special Pizzas",
        "desc": "Cherry Peri Special, Malai Boti, Bihari Kabab, Mughlai, Super Supreme",
        "items": [
            {"id": "sp_cherryperi", "name": "Cherry Peri Special Pizza", "prices": {"personal": 600, "medium": 950, "large": 1600, "xlarge": 2100}},
            {"id": "sp_malaiboti", "name": "Malai Boti Pizza", "prices": {"personal": 600, "medium": 950, "large": 1600, "xlarge": 2100}},
            {"id": "sp_biharikabab", "name": "Bihari Kabab Pizza", "prices": {"personal": 600, "medium": 950, "large": 1600, "xlarge": 2100}},
            {"id": "sp_mughlai", "name": "Mughlai Pizza", "prices": {"personal": 600, "medium": 950, "large": 1600, "xlarge": 2100}},
            {"id": "sp_supersupreme", "name": "Super Supreme Pizza", "prices": {"personal": 600, "medium": 950, "large": 1600, "xlarge": 2100}},
        ]
    },
    "premium_pizza": {
        "emoji": "👑",
        "name": "Premium Stuffed & Crown Pizzas",
        "items": [
            {"id": "pp_crown", "name": "Peri Crown Crust Pizza", "prices": {"medium": 1100, "large": 1700, "xlarge": 2300}},
            {"id": "pp_cheesestuff", "name": "Cheese Stuffer Pizza", "prices": {"medium": 1150, "large": 1800, "xlarge": 2400}},
            {"id": "pp_chickenstuff", "name": "Cheese Chicken Stuffer Pizza", "prices": {"medium": 1200, "large": 1900, "xlarge": 2500}},
            {"id": "pp_kababstuff", "name": "Kabab Stuffer Pizza", "prices": {"medium": 1200, "large": 1900, "xlarge": 2500}},
        ]
    },
    "deals": {
        "emoji": "🌟",
        "name": "Special Viral Deals (Fixed Sizes & Items — No Choice Needed)",
        "items": [
            {
                "id": "d1",
                "name": "Deal 1 — Student Viral (Fixed: 6\" Personal Pizza + Classic Zinger + Fries + 345ml Drink)",
                "price": 899,
                "desc": "Complete deal from menu card. Pizza size is fixed to 6\" Personal, Burger is Classic Zinger, Drink is 345ml. Never ask customer about pizza size or meal options for this deal."
            },
            {
                "id": "d2",
                "name": "Deal 2 — Family Viral King (Fixed: 9\" Medium Pizza + Half Broast 4 Pcs + Large Flavour Fries + 1.5Ltr Drink)",
                "price": 2499,
                "desc": "Complete deal from menu card. Pizza size is fixed to 9\" Medium, Broast is Half (4 Pcs), Fries are Large Flavour, Drink is 1.5Ltr. Never ask customer about pizza size or meal options for this deal."
            }
        ]
    },
    "zinger_burgers": {
        "emoji": "🍔",
        "name": "Zinger Burgers (with Fries)",
        "items": [
            {"id": "b_zinger_classic", "name": "Classic Zinger + Fries", "price": 450, "desc": "Crispy chicken fillet burger with fries"},
            {"id": "b_zinger_cheese", "name": "Cheese Zinger + Fries", "price": 500, "desc": "Zinger with melted cheese & fries"},
            {"id": "b_zinger_mighty", "name": "Mighty Zinger + Fries", "price": 600, "desc": "Double chicken fillet zinger & fries"},
        ]
    },
    "grill_burgers": {
        "emoji": "🔥",
        "name": "Grill Burgers (with Fries)",
        "items": [
            {"id": "b_grill", "name": "Chicken Grill Burger + Fries", "price": 550, "desc": "Juicy grilled chicken burger with fries"},
            {"id": "b_grill_special", "name": "Cherry Peri Special Grill + Fries", "price": 700, "desc": "Special peri grilled burger with fries"},
        ]
    },
    "simple_burgers": {
        "emoji": "🍔",
        "name": "Standard Burgers",
        "items": [
            {"id": "b_zinger_simple", "name": "Zinger Burger", "price": 250},
            {"id": "b_afghani", "name": "Afghani Burger", "price": 350},
            {"id": "b_zinger_ch_simple", "name": "Zinger Burger with Cheese", "price": 300},
        ]
    },
    "broast": {
        "emoji": "🍗",
        "name": "Crispy Chicken Broast",
        "items": [
            {"id": "br_quarter", "name": "Quarter Broast + Fries (2 Pcs)", "price": 550},
            {"id": "br_half", "name": "Half Broast + Fries (4 Pcs)", "price": 990},
            {"id": "br_full", "name": "Full Broast + 2 Fries (8 Pcs)", "price": 1850},
        ]
    },
    "wings": {
        "emoji": "🍗",
        "name": "Crispy & Flavored Wings",
        "items": [
            {"id": "w_crispy_6", "name": "Crispy Wings (6 Pcs)", "price": 400},
            {"id": "w_crispy_12", "name": "Crispy Wings (12 Pcs)", "price": 750},
            {"id": "w_flavor_6", "name": "Flavored Wings (6 Pcs - BBQ/Hot/Peri/Honey Garlic)", "price": 480},
            {"id": "w_flavor_12", "name": "Flavored Wings (12 Pcs - BBQ/Hot/Peri/Honey Garlic)", "price": 890},
        ]
    },
    "sandwiches": {
        "emoji": "🥪",
        "name": "Sandwiches (with Fries)",
        "items": [
            {"id": "sw_chicken", "name": "Chicken Sandwich + Fries", "price": 700},
            {"id": "sw_crunchy", "name": "Crunchy Sandwich + Fries", "price": 750},
            {"id": "sw_grill", "name": "Grill Sandwich + Fries", "price": 750},
            {"id": "sw_mexican", "name": "Mexican Sandwich + Fries", "price": 850},
            {"id": "sw_malaiboti", "name": "Malai Boti Sandwich + Fries", "price": 850},
            {"id": "sw_mughlai", "name": "Mughlai Sandwich + Fries", "price": 850},
            {"id": "sw_special", "name": "Cherry Peri Special Sandwich + Fries", "price": 900},
        ]
    },
    "spin_rolls": {
        "emoji": "🌯",
        "name": "Crunchy Spin Rolls",
        "items": [
            {"id": "sr_chicken_cheese", "name": "Chicken Cheese Spin Roll", "price": 500},
            {"id": "sr_peri", "name": "Peri Peri Spin Roll", "price": 550},
            {"id": "sr_bbq", "name": "BBQ Spin Roll", "price": 550},
            {"id": "sr_crunchy", "name": "Crunchy Chicken Spin Roll NEW", "price": 550},
            {"id": "sr_blast", "name": "Loaded Blast Spin Roll", "price": 550},
        ]
    },
    "shawarma_wraps": {
        "emoji": "🌯",
        "name": "Shawarma, Paratha & Wraps",
        "items": [
            {"id": "sh_small", "name": "Chicken Shawarma (Small)", "price": 120},
            {"id": "sh_large", "name": "Chicken Shawarma (Large)", "price": 150},
            {"id": "sh_zinger", "name": "Zinger Shawarma", "price": 200},
            {"id": "sh_achari", "name": "Chicken Achari Shawarma", "price": 200},
            {"id": "pr_malaiboti", "name": "Malai Boti Paratha Roll", "price": 300},
            {"id": "pr_kabab", "name": "Kabab Paratha Roll", "price": 250},
            {"id": "pr_zinger", "name": "Zinger Paratha Roll", "price": 250},
            {"id": "wr_afghani", "name": "Afghani Wrap", "price": 350},
            {"id": "wr_chicken", "name": "Chicken Wrap", "price": 350},
            {"id": "wr_zinger", "name": "Zinger Wrap", "price": 350},
        ]
    },
    "pastas": {
        "emoji": "🍝",
        "name": "Pastas",
        "items": [
            {"id": "pas_alfredo", "name": "Creamy Alfredo Pasta", "prices": {"small": 350, "large": 550}},
            {"id": "pas_peri", "name": "Spicy Peri Pasta", "prices": {"small": 400, "large": 600}},
            {"id": "pas_tikka", "name": "Chicken Tikka Pasta", "prices": {"small": 450, "large": 650}},
            {"id": "pas_cheese", "name": "Cheese Loaded Pasta", "prices": {"small": 500, "large": 700}},
        ]
    },
    "fries": {
        "emoji": "🍟",
        "name": "Fries & Loaded Fries",
        "items": [
            {"id": "fr_plain", "name": "Plain Fries", "prices": {"small": 250, "large": 350}},
            {"id": "fr_flavor", "name": "Flavour Fries (Peri Peri / BBQ / Cheese)", "prices": {"small": 300, "large": 400}},
            {"id": "fr_crunchy", "name": "Crunchy Fries", "prices": {"small": 400, "large": 550}},
            {"id": "fr_pizza", "name": "Pizza Fries", "prices": {"small": 400, "large": 550}},
            {"id": "fr_loaded", "name": "Loaded Cheese Fries", "prices": {"small": 400, "large": 550}},
            {"id": "fr_matka", "name": "Matka Pizza Fries", "price": 400},
        ]
    },
    "drinks": {
        "emoji": "🥤",
        "name": "Drinks",
        "items": [
            {"id": "dr_345", "name": "Cold Drink (345ml)", "price": 100},
            {"id": "dr_tin", "name": "Cold Drink (Tin Pack 250ml)", "price": 120},
            {"id": "dr_1ltr", "name": "Cold Drink (1 Litre)", "price": 180},
            {"id": "dr_15ltr", "name": "Cold Drink (1.5 Litre)", "price": 220},
        ]
    }
}
