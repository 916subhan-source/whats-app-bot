# ============================================
# 🍕 Cherry Peri Fast Food - POS & Sales Management HTML View
# Enhanced, High-Contrast, Easily Readable Analytics & POS Terminal
# ============================================

def render_pos_html() -> str:
    return """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cherry Peri — POS & Sales Management System</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        cherry: {
                            50: '#fff1f2',
                            100: '#ffe4e6',
                            400: '#fb7185',
                            500: '#f43f5e',
                            600: '#e11d48',
                            700: '#be123c',
                            800: '#9f1239',
                            900: '#881337',
                        },
                        darkslate: {
                            800: '#1e293b',
                            850: '#141e33',
                            900: '#0f172a',
                            950: '#080d1a',
                        }
                    }
                }
            }
        }
    </script>
    <!-- Google Fonts: Plus Jakarta Sans & JetBrains Mono -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;600;700;800&display=swap" rel="stylesheet">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <style>
        body {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: #080d1a;
            color: #f1f5f9;
        }
        .font-mono-num {
            font-family: 'JetBrains Mono', monospace;
        }
        /* High-Contrast Scrollbars */
        ::-webkit-scrollbar {
            width: 7px;
            height: 7px;
        }
        ::-webkit-scrollbar-track {
            background: #0f172a;
        }
        ::-webkit-scrollbar-thumb {
            background: #334155;
            border-radius: 6px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #475569;
        }
        /* Thermal Receipt Printing (80mm standard format) */
        @media print {
            body * {
                visibility: hidden !important;
            }
            #thermal-receipt-modal, #thermal-receipt-modal * {
                visibility: visible !important;
            }
            #thermal-receipt-modal {
                position: absolute !important;
                left: 0 !important;
                top: 0 !important;
                width: 80mm !important;
                margin: 0 !important;
                padding: 4mm !important;
                background: white !important;
                color: black !important;
                font-family: 'Courier New', Courier, monospace !important;
                font-size: 11pt !important;
                box-shadow: none !important;
            }
            .no-print {
                display: none !important;
            }
        }
        .tab-btn.active {
            background: linear-gradient(135deg, #e11d48, #be123c);
            color: #ffffff;
            box-shadow: 0 4px 14px rgba(225, 29, 72, 0.45);
        }
    </style>
</head>
<body class="min-h-screen flex flex-col bg-darkslate-950 text-slate-100 antialiased">

    <!-- ───────────────────────────────────────────── -->
    <!-- 🔝 Top Navbar & Header -->
    <!-- ───────────────────────────────────────────── -->
    <header class="bg-darkslate-900/90 backdrop-blur-md border-b border-slate-800 sticky top-0 z-40 px-4 py-3 shadow-lg">
        <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
            <!-- Brand -->
            <div class="flex items-center space-x-3.5">
                <div class="w-11 h-11 rounded-2xl bg-gradient-to-tr from-cherry-700 via-rose-600 to-amber-500 flex items-center justify-center text-2xl shadow-lg shadow-cherry-700/40 border border-rose-400/20">
                    🍕
                </div>
                <div>
                    <div class="flex items-center space-x-2">
                        <h1 class="text-xl font-black tracking-tight text-white">CHERRY PERI</h1>
                        <span class="bg-gradient-to-r from-rose-500/20 to-amber-500/20 text-rose-300 text-xs px-2.5 py-0.5 rounded-full font-bold border border-rose-500/30">
                            POS & SALES
                        </span>
                    </div>
                    <p class="text-xs text-slate-400 font-medium">Opp. Stylo, Circular Road, Dera Ismail Khan</p>
                </div>
            </div>

            <!-- Tab Buttons -->
            <nav class="flex items-center bg-darkslate-850 p-1.5 rounded-2xl border border-slate-800 space-x-1.5 shadow-inner">
                <button onclick="switchTab('pos')" id="btn-tab-pos" class="tab-btn active px-4 py-2 rounded-xl text-sm font-bold text-slate-300 hover:text-white transition flex items-center space-x-2">
                    <span class="text-base">🛒</span>
                    <span>POS Terminal</span>
                </button>
                <button onclick="switchTab('sales')" id="btn-tab-sales" class="tab-btn px-4 py-2 rounded-xl text-sm font-bold text-slate-300 hover:text-white transition flex items-center space-x-2">
                    <span class="text-base">📊</span>
                    <span>Sales & Analytics</span>
                </button>
                <button onclick="switchTab('orders')" id="btn-tab-orders" class="tab-btn px-4 py-2 rounded-xl text-sm font-bold text-slate-300 hover:text-white transition flex items-center space-x-2">
                    <span class="text-base">🍳</span>
                    <span>Kitchen Pipeline</span>
                    <span id="badge-active-count" class="bg-emerald-500 text-slate-950 font-black text-xs px-2 py-0.5 rounded-full hidden">0</span>
                </button>
            </nav>

            <!-- Actions & Clock -->
            <div class="flex items-center space-x-3">
                <div class="text-right hidden sm:block">
                    <div id="live-clock" class="text-xs font-mono-num font-extrabold text-slate-200">12:00:00 PM</div>
                    <div id="live-date" class="text-[11px] text-slate-400 font-semibold">Today</div>
                </div>
                <div class="h-7 w-px bg-slate-800 hidden sm:block"></div>
                <!-- Live status indicator -->
                <div class="flex items-center space-x-2 bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 px-3 py-1.5 rounded-xl text-xs font-bold">
                    <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse shadow-sm shadow-emerald-400"></span>
                    <span class="hidden md:inline">Live Auto-Sync (15s)</span>
                </div>
                <!-- Export to CSV -->
                <a href="/api/sales/export" download class="bg-darkslate-850 hover:bg-slate-800 border border-slate-700 hover:border-slate-600 text-slate-200 px-3.5 py-1.5 rounded-xl text-xs font-bold flex items-center space-x-1.5 transition shadow-sm">
                    <span>📥</span>
                    <span>Export CSV</span>
                </a>
            </div>
        </div>
    </header>

    <!-- ───────────────────────────────────────────── -->
    <!-- 💰 High-Contrast KPI Cards Bar (Always Visible) -->
    <!-- ───────────────────────────────────────────── -->
    <div class="bg-darkslate-900/80 border-b border-slate-800/90 px-4 py-3.5">
        <div class="max-w-7xl mx-auto grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-5 gap-3.5">

            <!-- Today's Revenue -->
            <div class="bg-gradient-to-b from-darkslate-850 to-darkslate-900 border border-emerald-500/25 hover:border-emerald-500/50 rounded-2xl p-3.5 flex flex-col justify-between shadow-sm transition">
                <div class="flex items-center justify-between text-xs text-slate-400 mb-1 font-semibold">
                    <span class="flex items-center space-x-1.5">
                        <span class="text-emerald-400">💰</span>
                        <span class="uppercase tracking-wider">Today's Sales</span>
                    </span>
                    <span id="kpi-today-orders" class="bg-emerald-500/15 text-emerald-300 font-bold px-2 py-0.5 rounded-md font-mono-num text-[11px]">
                        0 orders
                    </span>
                </div>
                <div class="text-2xl font-black text-emerald-400 font-mono-num tracking-tight" id="kpi-today-rev">
                    Rs. 0
                </div>
                <div class="text-[11px] text-slate-400 mt-1 flex items-center justify-between">
                    <span>Yesterday: <strong id="kpi-yest-rev" class="text-slate-300 font-mono-num font-bold">Rs. 0</strong></span>
                    <span id="kpi-yest-orders" class="text-slate-400 font-mono-num">(0)</span>
                </div>
            </div>

            <!-- This Month's Revenue -->
            <div class="bg-gradient-to-b from-darkslate-850 to-darkslate-900 border border-amber-500/25 hover:border-amber-500/50 rounded-2xl p-3.5 flex flex-col justify-between shadow-sm transition">
                <div class="flex items-center justify-between text-xs text-slate-400 mb-1 font-semibold">
                    <span class="flex items-center space-x-1.5">
                        <span class="text-amber-400">📅</span>
                        <span class="uppercase tracking-wider">This Month</span>
                    </span>
                    <span id="kpi-month-orders" class="bg-amber-500/15 text-amber-300 font-bold px-2 py-0.5 rounded-md font-mono-num text-[11px]">
                        0 orders
                    </span>
                </div>
                <div class="text-2xl font-black text-amber-400 font-mono-num tracking-tight" id="kpi-month-rev">
                    Rs. 0
                </div>
                <div class="text-[11px] text-slate-400 mt-1">
                    Current Calendar Month
                </div>
            </div>

            <!-- Total All-Time Revenue -->
            <div class="bg-gradient-to-b from-darkslate-850 to-darkslate-900 border border-sky-500/25 hover:border-sky-500/50 rounded-2xl p-3.5 flex flex-col justify-between shadow-sm transition">
                <div class="flex items-center justify-between text-xs text-slate-400 mb-1 font-semibold">
                    <span class="flex items-center space-x-1.5">
                        <span class="text-sky-400">🏆</span>
                        <span class="uppercase tracking-wider">Total Sales</span>
                    </span>
                    <span id="kpi-total-orders" class="bg-sky-500/15 text-sky-300 font-bold px-2 py-0.5 rounded-md font-mono-num text-[11px]">
                        0 total
                    </span>
                </div>
                <div class="text-2xl font-black text-sky-400 font-mono-num tracking-tight" id="kpi-total-rev">
                    Rs. 0
                </div>
                <div class="text-[11px] text-slate-400 mt-1">
                    WhatsApp + Counter Combined
                </div>
            </div>

            <!-- Average Order Value (AOV) -->
            <div class="bg-gradient-to-b from-darkslate-850 to-darkslate-900 border border-rose-500/25 hover:border-rose-500/50 rounded-2xl p-3.5 flex flex-col justify-between shadow-sm transition">
                <div class="flex items-center justify-between text-xs text-slate-400 mb-1 font-semibold">
                    <span class="flex items-center space-x-1.5">
                        <span class="text-rose-400">📈</span>
                        <span class="uppercase tracking-wider">Avg Order (AOV)</span>
                    </span>
                    <span class="bg-rose-500/15 text-rose-300 font-bold px-2 py-0.5 rounded-md text-[11px]">
                        Per Ticket
                    </span>
                </div>
                <div class="text-2xl font-black text-rose-400 font-mono-num tracking-tight" id="kpi-avg-order">
                    Rs. 0
                </div>
                <div class="text-[11px] text-slate-400 mt-1">
                    Average revenue per customer
                </div>
            </div>

            <!-- Sales Channel Quick Split -->
            <div class="bg-gradient-to-b from-darkslate-850 to-darkslate-900 border border-purple-500/25 hover:border-purple-500/50 rounded-2xl p-3.5 col-span-2 sm:col-span-1 flex flex-col justify-between shadow-sm transition">
                <div class="flex items-center justify-between text-xs text-slate-400 mb-1 font-semibold">
                    <span class="flex items-center space-x-1.5">
                        <span class="text-purple-400">🛵</span>
                        <span class="uppercase tracking-wider">Channels</span>
                    </span>
                    <span class="text-slate-400 text-[11px]">Breakdown</span>
                </div>
                <div class="space-y-1 mt-1 text-xs font-mono-num">
                    <div class="flex justify-between items-center text-slate-300">
                        <span class="text-slate-400">Delivery:</span>
                        <span id="kpi-delivery-rev" class="font-bold text-emerald-400">Rs. 0</span>
                    </div>
                    <div class="flex justify-between items-center text-slate-300">
                        <span class="text-slate-400">Counter:</span>
                        <span id="kpi-counter-rev" class="font-bold text-blue-400">Rs. 0</span>
                    </div>
                </div>
            </div>

        </div>
    </div>

    <!-- ───────────────────────────────────────────── -->
    <!-- 🖥️ MAIN VIEW CONTAINER -->
    <!-- ───────────────────────────────────────────── -->
    <main class="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-5">

        <!-- ───────────────────────────────────────────── -->
        <!-- 🛒 TAB 1: POS TERMINAL -->
        <!-- ───────────────────────────────────────────── -->
        <div id="tab-content-pos" class="space-y-4">
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">

                <!-- Left Column: Menu Items & Catalog (8 cols) -->
                <div class="lg:col-span-7 xl:col-span-8 space-y-4">

                    <!-- Search and Category Filters -->
                    <div class="bg-darkslate-900 border border-slate-800 rounded-2xl p-4 shadow-md space-y-3.5">
                        <div class="flex flex-wrap items-center gap-2.5">
                            <div class="relative flex-1 min-w-[220px]">
                                <input type="text" id="pos-search-input" oninput="filterMenuItems()" placeholder="🔍 Search menu (e.g. Deal 20, Zinger, Tikka, Shawarma)..."
                                       class="w-full bg-darkslate-950 border border-slate-700/80 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-rose-500 transition shadow-inner">
                            </div>
                            <button onclick="clearSearch()" class="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold rounded-xl transition">
                                Reset
                            </button>
                        </div>

                        <!-- Category Filter Buttons -->
                        <div class="flex items-center gap-2 overflow-x-auto pb-1" id="category-pills">
                            <button onclick="filterCategory('all')" class="cat-pill active px-3.5 py-1.5 bg-rose-600 text-white rounded-xl text-xs font-bold whitespace-nowrap shadow-sm">
                                🌟 All Items
                            </button>
                            <button onclick="filterCategory('deals')" class="cat-pill px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-bold whitespace-nowrap transition">
                                🌟 Deals (1-26)
                            </button>
                            <button onclick="filterCategory('pizza_regular')" class="cat-pill px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-bold whitespace-nowrap transition">
                                🍕 Regular Pizzas
                            </button>
                            <button onclick="filterCategory('pizza_special')" class="cat-pill px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-bold whitespace-nowrap transition">
                                🍕 Special Pizzas
                            </button>
                            <button onclick="filterCategory('burgers')" class="cat-pill px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-bold whitespace-nowrap transition">
                                🍔 Burgers
                            </button>
                            <button onclick="filterCategory('shawarma')" class="cat-pill px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-bold whitespace-nowrap transition">
                                🌯 Shawarma
                            </button>
                            <button onclick="filterCategory('paratha_rolls')" class="cat-pill px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-bold whitespace-nowrap transition">
                                🌯 Paratha Rolls
                            </button>
                            <button onclick="filterCategory('fries')" class="cat-pill px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-bold whitespace-nowrap transition">
                                🍟 Fries & Sides
                            </button>
                            <button onclick="filterCategory('drinks')" class="cat-pill px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-bold whitespace-nowrap transition">
                                🥤 Drinks
                            </button>
                        </div>
                    </div>

                    <!-- Items Grid -->
                    <div id="pos-items-grid" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3.5 max-h-[660px] overflow-y-auto pr-1">
                        <!-- Populated by JS -->
                    </div>
                </div>

                <!-- Right Column: Current POS Order Cart (4 cols) -->
                <div class="lg:col-span-5 xl:col-span-4 space-y-4">
                    <div class="bg-darkslate-900 border border-slate-800 rounded-2xl p-4 shadow-xl sticky top-20 flex flex-col h-[750px]">
                        <!-- Cart Header -->
                        <div class="flex items-center justify-between pb-3 border-b border-slate-800">
                            <div class="flex items-center space-x-2">
                                <span class="text-xl">🧾</span>
                                <div>
                                    <h3 class="font-bold text-white text-sm">Order Terminal</h3>
                                    <p class="text-[11px] text-slate-400">Cashier Billing Slip</p>
                                </div>
                            </div>
                            <button onclick="clearCart()" class="text-xs text-rose-400 hover:text-rose-300 font-bold px-2.5 py-1 rounded-lg hover:bg-rose-950/30 transition">
                                Clear Cart
                            </button>
                        </div>

                        <!-- Customer & Order Meta Inputs -->
                        <div class="py-3 space-y-2.5 border-b border-slate-800/90 text-xs">
                            <div class="grid grid-cols-2 gap-2">
                                <div>
                                    <label class="text-[11px] text-slate-400 font-semibold block mb-0.5">Customer Name</label>
                                    <input type="text" id="cart-customer-name" placeholder="Walk-in Customer"
                                           class="w-full bg-darkslate-950 border border-slate-700/80 rounded-xl px-3 py-1.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-rose-500">
                                </div>
                                <div>
                                    <label class="text-[11px] text-slate-400 font-semibold block mb-0.5">Phone Number</label>
                                    <input type="text" id="cart-customer-phone" placeholder="0300-1234567"
                                           class="w-full bg-darkslate-950 border border-slate-700/80 rounded-xl px-3 py-1.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-rose-500">
                                </div>
                            </div>

                            <div class="grid grid-cols-2 gap-2">
                                <div>
                                    <label class="text-[11px] text-slate-400 font-semibold block mb-0.5">Order Type</label>
                                    <select id="cart-order-type" onchange="handleOrderTypeChange()"
                                            class="w-full bg-darkslate-950 border border-slate-700/80 rounded-xl px-2.5 py-1.5 text-xs text-slate-100 font-semibold focus:outline-none focus:border-rose-500">
                                        <option value="counter">🛍️ Counter / Takeaway</option>
                                        <option value="dine_in">🍽️ Dine-in (Table)</option>
                                        <option value="delivery">🛵 WhatsApp Delivery</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="text-[11px] text-slate-400 font-semibold block mb-0.5">Location / Table</label>
                                    <input type="text" id="cart-address" placeholder="Table # / Address"
                                           class="w-full bg-darkslate-950 border border-slate-700/80 rounded-xl px-3 py-1.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-rose-500">
                                </div>
                            </div>

                            <div>
                                <label class="text-[11px] text-amber-300 font-semibold block mb-0.5">📝 Special Customer Note</label>
                                <input type="text" id="cart-special-notes" placeholder="e.g. Cheese kam, Extra spicy, Kam sauce"
                                       class="w-full bg-darkslate-950 border border-amber-500/40 rounded-xl px-3 py-1.5 text-xs text-amber-200 placeholder-amber-400/40 focus:outline-none focus:border-amber-400">
                            </div>
                        </div>

                        <!-- Cart Items Scroll Area -->
                        <div id="cart-items-container" class="flex-1 overflow-y-auto py-2.5 space-y-2 pr-1">
                            <div class="text-center py-16 text-slate-500 text-xs font-medium">
                                Cart is empty.<br>Click any item from the menu catalog to add!
                            </div>
                        </div>

                        <!-- Cart Totals & Place Order -->
                        <div class="pt-3 border-t border-slate-800 space-y-2">
                            <div class="flex justify-between text-xs text-slate-400 font-medium">
                                <span>Food Subtotal</span>
                                <span class="font-mono-num font-bold text-slate-200" id="cart-subtotal">Rs. 0</span>
                            </div>
                            <div class="flex justify-between text-xs text-slate-400 items-center font-medium">
                                <span>Delivery Fee (Rs.)</span>
                                <input type="number" id="cart-delivery-fee" value="0" min="0" oninput="calculateCartTotal()"
                                       class="w-20 bg-darkslate-950 border border-slate-700 text-right px-2 py-0.5 rounded-lg text-xs text-slate-200 font-mono-num font-bold">
                            </div>
                            <div class="flex justify-between text-xs text-slate-400 items-center font-medium">
                                <span>Discount (Rs.)</span>
                                <input type="number" id="cart-discount" value="0" min="0" oninput="calculateCartTotal()"
                                       class="w-20 bg-darkslate-950 border border-slate-700 text-right px-2 py-0.5 rounded-lg text-xs text-slate-200 font-mono-num font-bold">
                            </div>
                            <div class="flex justify-between items-center text-sm font-bold text-white pt-2.5 border-t border-slate-800/80">
                                <span class="text-slate-300">Net Total Bill:</span>
                                <span class="text-2xl font-black text-emerald-400 font-mono-num" id="cart-net-total">Rs. 0</span>
                            </div>

                            <!-- Actions -->
                            <div class="grid grid-cols-2 gap-2.5 pt-2">
                                <button onclick="submitPosOrder(false)" class="bg-slate-800 hover:bg-slate-700 text-slate-200 font-extrabold py-2.5 px-3 rounded-xl text-xs transition flex items-center justify-center space-x-1.5 shadow-sm">
                                    <span>💾</span>
                                    <span>Record Order</span>
                                </button>
                                <button onclick="submitPosOrder(true)" class="bg-gradient-to-r from-rose-600 via-rose-600 to-rose-700 hover:from-rose-500 hover:to-rose-600 text-white font-black py-2.5 px-3 rounded-xl text-xs transition shadow-lg shadow-rose-900/50 flex items-center justify-center space-x-1.5">
                                    <span>🖨️</span>
                                    <span>Place & Print</span>
                                </button>
                            </div>
                        </div>

                    </div>
                </div>

            </div>
        </div>

        <!-- ───────────────────────────────────────────── -->
        <!-- 📊 TAB 2: SALES & INCOME ANALYTICS (EASY READABLE) -->
        <!-- ───────────────────────────────────────────── -->
        <div id="tab-content-sales" class="hidden space-y-6">

            <!-- Financial Health Summary Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <!-- Net Revenue -->
                <div class="bg-darkslate-900 border border-slate-800 rounded-2xl p-4 shadow-sm flex items-center space-x-3.5">
                    <div class="w-12 h-12 rounded-2xl bg-emerald-500/15 text-emerald-400 flex items-center justify-center text-2xl border border-emerald-500/25">
                        💰
                    </div>
                    <div>
                        <div class="text-xs uppercase font-bold text-slate-400 tracking-wider">Gross Income</div>
                        <div class="text-xl font-black text-emerald-400 font-mono-num" id="analytics-total-rev">Rs. 0</div>
                        <div class="text-[11px] text-slate-400">All Completed Orders</div>
                    </div>
                </div>

                <!-- WhatsApp Orders Revenue -->
                <div class="bg-darkslate-900 border border-slate-800 rounded-2xl p-4 shadow-sm flex items-center space-x-3.5">
                    <div class="w-12 h-12 rounded-2xl bg-emerald-500/15 text-emerald-300 flex items-center justify-center text-2xl border border-emerald-500/25">
                        🛵
                    </div>
                    <div>
                        <div class="text-xs uppercase font-bold text-slate-400 tracking-wider">WhatsApp Delivery</div>
                        <div class="text-xl font-black text-emerald-300 font-mono-num" id="analytics-wa-rev">Rs. 0</div>
                        <div class="text-[11px] text-slate-400" id="analytics-wa-orders">0 orders</div>
                    </div>
                </div>

                <!-- Counter & Dine-in Revenue -->
                <div class="bg-darkslate-900 border border-slate-800 rounded-2xl p-4 shadow-sm flex items-center space-x-3.5">
                    <div class="w-12 h-12 rounded-2xl bg-sky-500/15 text-sky-400 flex items-center justify-center text-2xl border border-sky-500/25">
                        🛍️
                    </div>
                    <div>
                        <div class="text-xs uppercase font-bold text-slate-400 tracking-wider">Counter & Dine-in</div>
                        <div class="text-xl font-black text-sky-400 font-mono-num" id="analytics-counter-rev">Rs. 0</div>
                        <div class="text-[11px] text-slate-400" id="analytics-counter-orders">0 orders</div>
                    </div>
                </div>

                <!-- Success Rate -->
                <div class="bg-darkslate-900 border border-slate-800 rounded-2xl p-4 shadow-sm flex items-center space-x-3.5">
                    <div class="w-12 h-12 rounded-2xl bg-amber-500/15 text-amber-400 flex items-center justify-center text-2xl border border-amber-500/25">
                        🎯
                    </div>
                    <div>
                        <div class="text-xs uppercase font-bold text-slate-400 tracking-wider">Order Completion</div>
                        <div class="text-xl font-black text-amber-400 font-mono-num" id="analytics-completion-rate">100%</div>
                        <div class="text-[11px] text-slate-400" id="analytics-active-ratio">0 active now</div>
                    </div>
                </div>
            </div>

            <!-- Charts Row -->
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
                <!-- Daily Sales Bar/Area Chart (30 Days) -->
                <div class="lg:col-span-8 bg-darkslate-900 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-4">
                    <div class="flex flex-wrap items-center justify-between gap-2">
                        <div>
                            <h3 class="font-extrabold text-white text-base flex items-center space-x-2">
                                <span>📈</span>
                                <span>Daily Sales Revenue & Volume Trend</span>
                            </h3>
                            <p class="text-xs text-slate-400">Interactive revenue (PKR) and order count over the last 30 days</p>
                        </div>
                        <span class="text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 rounded-xl font-mono-num font-bold">
                            ● Unified Daily Tracking
                        </span>
                    </div>
                    <div class="h-80 w-full pt-2">
                        <canvas id="salesTrendChart"></canvas>
                    </div>
                </div>

                <!-- Channel & Order Distribution Doughnut Chart -->
                <div class="lg:col-span-4 bg-darkslate-900 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-4 flex flex-col justify-between">
                    <div>
                        <h3 class="font-extrabold text-white text-base flex items-center space-x-2">
                            <span>🥧</span>
                            <span>Sales by Channel & Status</span>
                        </h3>
                        <p class="text-xs text-slate-400">Where revenue comes from</p>
                    </div>
                    <div class="h-56 flex items-center justify-center relative">
                        <canvas id="statusChart"></canvas>
                    </div>
                    <div id="status-legend" class="grid grid-cols-2 gap-2 text-xs pt-2 border-t border-slate-800/80">
                        <!-- Populated by JS -->
                    </div>
                </div>
            </div>

            <!-- Leaderboard & Pipeline Breakdown -->
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
                <!-- Top 10 Selling Items Leaderboard -->
                <div class="lg:col-span-6 bg-darkslate-900 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-4">
                    <div class="flex items-center justify-between">
                        <div>
                            <h3 class="font-extrabold text-white text-base flex items-center space-x-2">
                                <span>🏆</span>
                                <span>Top Selling Menu Items</span>
                            </h3>
                            <p class="text-xs text-slate-400">Most ordered deals & food items</p>
                        </div>
                        <span class="text-xs text-slate-400 font-semibold">Rank by Qty</span>
                    </div>

                    <div class="space-y-3" id="top-items-container">
                        <!-- Populated with progress bars by JS -->
                    </div>
                </div>

                <!-- Pipeline Status Progress & Accounting Info -->
                <div class="lg:col-span-6 bg-darkslate-900 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-4 flex flex-col justify-between">
                    <div class="space-y-4">
                        <div>
                            <h3 class="font-extrabold text-white text-base flex items-center space-x-2">
                                <span>🍳</span>
                                <span>Kitchen Pipeline Status</span>
                            </h3>
                            <p class="text-xs text-slate-400">Current workflow breakdown</p>
                        </div>

                        <div class="space-y-2.5 text-xs" id="status-bars-container">
                            <!-- Populated with colored progress bars by JS -->
                        </div>
                    </div>

                    <!-- Direct Excel / CSV Export Banner -->
                    <div class="bg-darkslate-950 p-4 rounded-xl border border-slate-800 space-y-2 mt-4">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-bold text-slate-200">Financial Reporting & Accounting</span>
                            <span class="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono-num font-bold">CSV / Excel</span>
                        </div>
                        <p class="text-[11px] text-slate-400 leading-relaxed">
                            Export every single recorded order with timestamps, customer names, phone numbers, items, special notes, and amounts.
                        </p>
                        <a href="/api/sales/export" download class="w-full bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-500 hover:to-emerald-600 text-white font-black py-2.5 px-4 rounded-xl text-xs flex items-center justify-center space-x-2 transition shadow-lg shadow-emerald-950">
                            <span>📥</span>
                            <span>Download All Sales History (.CSV)</span>
                        </a>
                    </div>
                </div>
            </div>

            <!-- Recent Completed Sales Ledger Table -->
            <div class="bg-darkslate-900 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-3">
                <div class="flex items-center justify-between">
                    <div>
                        <h3 class="font-extrabold text-white text-base flex items-center space-x-2">
                            <span>📑</span>
                            <span>Recent Sales Transactions Ledger</span>
                        </h3>
                        <p class="text-xs text-slate-400">Last 50 customer orders</p>
                    </div>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs">
                        <thead>
                            <tr class="text-slate-400 border-b border-slate-800 font-bold uppercase tracking-wider text-[11px]">
                                <th class="py-2.5 px-2">Order ID</th>
                                <th class="py-2.5 px-2">Time</th>
                                <th class="py-2.5 px-2">Customer</th>
                                <th class="py-2.5 px-2">Channel</th>
                                <th class="py-2.5 px-2">Items Summary</th>
                                <th class="py-2.5 px-2 text-right">Total Bill</th>
                                <th class="py-2.5 px-2 text-center">Status</th>
                            </tr>
                        </thead>
                        <tbody id="sales-ledger-tbody" class="divide-y divide-slate-800/60 font-medium">
                            <!-- Populated by JS -->
                        </tbody>
                    </table>
                </div>
            </div>

        </div>

        <!-- ───────────────────────────────────────────── -->
        <!-- 🍳 TAB 3: KITCHEN & ORDERS PIPELINE -->
        <!-- ───────────────────────────────────────────── -->
        <div id="tab-content-orders" class="hidden space-y-4">

            <!-- Filter Status Bar -->
            <div class="bg-darkslate-900 border border-slate-800 rounded-2xl p-3 flex flex-wrap items-center justify-between gap-3 shadow-md">
                <div class="flex items-center space-x-2 overflow-x-auto pb-1" id="order-status-filters">
                    <button onclick="filterOrderStatus('all')" class="status-filter-btn active px-3.5 py-1.5 bg-rose-600 text-white rounded-xl text-xs font-bold whitespace-nowrap shadow-sm">
                        All Orders
                    </button>
                    <button onclick="filterOrderStatus('pending')" class="status-filter-btn px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-amber-400 rounded-xl text-xs font-bold whitespace-nowrap transition">
                        🟡 Pending
                    </button>
                    <button onclick="filterOrderStatus('preparing')" class="status-filter-btn px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-sky-400 rounded-xl text-xs font-bold whitespace-nowrap transition">
                        🔵 Preparing
                    </button>
                    <button onclick="filterOrderStatus('out_for_delivery')" class="status-filter-btn px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-purple-400 rounded-xl text-xs font-bold whitespace-nowrap transition">
                        🟣 Out for Delivery
                    </button>
                    <button onclick="filterOrderStatus('completed')" class="status-filter-btn px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-emerald-400 rounded-xl text-xs font-bold whitespace-nowrap transition">
                        🟢 Completed
                    </button>
                    <button onclick="filterOrderStatus('cancelled')" class="status-filter-btn px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-rose-400 rounded-xl text-xs font-bold whitespace-nowrap transition">
                        🔴 Cancelled
                    </button>
                </div>

                <div class="text-xs text-slate-400 font-semibold">
                    Showing <span id="orders-count-label" class="text-white font-bold font-mono-num">0</span> orders
                </div>
            </div>

            <!-- Orders Pipeline Grid -->
            <div id="orders-pipeline-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <!-- Populated by JS -->
            </div>

        </div>

    </main>

    <!-- ───────────────────────────────────────────── -->
    <!-- 🖨️ 80mm THERMAL RECEIPT MODAL -->
    <!-- ───────────────────────────────────────────── -->
    <div id="receipt-modal-backdrop" class="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-white text-slate-900 rounded-2xl max-w-sm w-full p-5 shadow-2xl relative space-y-4 max-h-[90vh] overflow-y-auto">
            <!-- Modal Header -->
            <div class="flex items-center justify-between no-print border-b border-slate-200 pb-3">
                <span class="font-extrabold text-sm text-slate-800">Print Preview (80mm Thermal)</span>
                <button onclick="closeReceiptModal()" class="text-slate-400 hover:text-slate-600 text-lg font-bold">✕</button>
            </div>

            <!-- Printable Slip Content -->
            <div id="thermal-receipt-modal" class="font-mono text-xs leading-relaxed">
                <!-- Injected by JS -->
            </div>

            <!-- Modal Actions -->
            <div class="flex space-x-2 pt-2 border-t border-slate-200 no-print">
                <button onclick="closeReceiptModal()" class="flex-1 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded-xl transition">
                    Close
                </button>
                <button onclick="window.print()" class="flex-1 py-2 bg-rose-600 hover:bg-rose-700 text-white font-black text-xs rounded-xl shadow-md transition flex items-center justify-center space-x-1.5">
                    <span>🖨️</span>
                    <span>Print Receipt</span>
                </button>
            </div>
        </div>
    </div>

    <!-- ───────────────────────────────────────────── -->
    <!-- ⚡ JAVASCRIPT LOGIC & VISUAL DATA BINDING -->
    <!-- ───────────────────────────────────────────── -->
    <script>
        // State
        let allMenuItems = [];
        let currentCategory = 'all';
        let currentSearch = '';
        let cart = []; // [{id, name, price, qty}]
        let allOrders = [];
        let salesStats = {};
        let activeOrderStatusFilter = 'all';
        let salesChartInstance = null;
        let statusChartInstance = null;

        function initApp() {
            startClock();
            fetchMenuData();
            fetchSalesStatsAndOrders();
            setInterval(fetchSalesStatsAndOrders, 15000);
        }

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initApp);
        } else {
            initApp();
        }

        function startClock() {
            function update() {
                const now = new Date();
                const clockEl = document.getElementById('live-clock');
                const dateEl = document.getElementById('live-date');
                if (clockEl) {
                    clockEl.innerText = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
                }
                if (dateEl) {
                    dateEl.innerText = now.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });
                }
            }
            update();
            setInterval(update, 1000);
        }

        function switchTab(tab) {
            ['pos', 'sales', 'orders'].forEach(t => {
                document.getElementById(`tab-content-${t}`).classList.add('hidden');
                document.getElementById(`btn-tab-${t}`).classList.remove('active');
            });
            document.getElementById(`tab-content-${tab}`).classList.remove('hidden');
            document.getElementById(`btn-tab-${tab}`).classList.add('active');

            if (tab === 'sales') {
                renderSalesCharts();
            }
        }

        // ─────────────────────────────────────────────
        // 🍕 Menu Catalog & POS Terminal
        // ─────────────────────────────────────────────
        async function fetchMenuData() {
            try {
                const res = await fetch('/api/menu');
                const data = await res.json();
                allMenuItems = data.items || [];
                renderMenuItems();
            } catch (err) {
                console.error('Error fetching menu items:', err);
            }
        }

        function filterCategory(cat) {
            currentCategory = cat;
            document.querySelectorAll('#category-pills button').forEach(b => {
                b.classList.remove('active', 'bg-rose-600', 'text-white');
                b.classList.add('bg-slate-800', 'text-slate-300');
            });
            event.target.classList.add('active', 'bg-rose-600', 'text-white');
            event.target.classList.remove('bg-slate-800', 'text-slate-300');
            renderMenuItems();
        }

        function filterMenuItems() {
            currentSearch = document.getElementById('pos-search-input').value.toLowerCase().trim();
            renderMenuItems();
        }

        function clearSearch() {
            document.getElementById('pos-search-input').value = '';
            currentSearch = '';
            renderMenuItems();
        }

        function getItemIcon(category) {
            if (category === 'deals') return '🌟';
            if (category.includes('pizza')) return '🍕';
            if (category === 'burgers') return '🍔';
            if (category === 'shawarma' || category === 'paratha_rolls') return '🌯';
            if (category === 'fries') return '🍟';
            if (category === 'drinks') return '🥤';
            return '🍽️';
        }

        function renderMenuItems() {
            const grid = document.getElementById('pos-items-grid');
            grid.innerHTML = '';

            let filtered = allMenuItems;
            if (currentCategory !== 'all') {
                filtered = filtered.filter(i => i.category === currentCategory);
            }
            if (currentSearch) {
                filtered = filtered.filter(i => i.name.toLowerCase().includes(currentSearch));
            }

            if (filtered.length === 0) {
                grid.innerHTML = `<div class="col-span-full py-16 text-center text-slate-500 text-sm">No items found matching "${currentSearch}".</div>`;
                return;
            }

            filtered.forEach(item => {
                const card = document.createElement('div');
                card.className = "bg-darkslate-900 border border-slate-800 hover:border-slate-700 rounded-2xl p-3.5 shadow-sm hover:shadow-md transition flex flex-col justify-between group";

                // Split title if parenthetical components exist (e.g. Deal 1 (1 Small Pizza + 1 Zinger...))
                let title = item.name;
                let subtext = "";
                if (item.name.indexOf('(') !== -1 && item.name.indexOf(')') !== -1) {
                    const firstParen = item.name.indexOf('(');
                    const lastParen = item.name.lastIndexOf(')');
                    title = item.name.substring(0, firstParen).trim();
                    subtext = item.name.substring(firstParen + 1, lastParen).trim();
                }

                const icon = getItemIcon(item.category);

                card.innerHTML = `
                    <div>
                        <div class="flex items-start justify-between gap-1 mb-1.5">
                            <div class="flex items-center space-x-1.5">
                                <span class="text-base">${icon}</span>
                                <h4 class="text-xs font-bold text-slate-100 group-hover:text-rose-400 transition leading-snug">${title}</h4>
                            </div>
                        </div>
                        ${subtext ? `<p class="text-[11px] text-slate-400 mb-2 leading-tight">${subtext}</p>` : ''}
                        <span class="text-[10px] text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded-md font-medium">${item.category_name || item.category}</span>
                    </div>
                    <div class="mt-3.5 pt-2.5 border-t border-slate-800/80 flex items-center justify-between">
                        <span class="text-sm font-black text-emerald-400 font-mono-num">Rs. ${item.price}</span>
                        <button onclick="addToCart('${item.id}', '${escapeHtml(item.name)}', ${item.price})"
                                class="bg-rose-600 hover:bg-rose-500 active:scale-95 text-white font-extrabold text-xs px-3 py-1.5 rounded-xl transition shadow-md shadow-rose-950 flex items-center space-x-1">
                            <span>+ Add</span>
                        </button>
                    </div>
                `;
                grid.appendChild(card);
            });
        }

        function escapeHtml(str) {
            return str.replace(/'/g, "\\'").replace(/"/g, '&quot;');
        }

        function addToCart(id, name, price) {
            const existing = cart.find(i => i.id === id);
            if (existing) {
                existing.qty += 1;
            } else {
                cart.push({ id, name, price, qty: 1 });
            }
            renderCart();
        }

        function updateCartQty(id, delta) {
            const item = cart.find(i => i.id === id);
            if (item) {
                item.qty += delta;
                if (item.qty <= 0) {
                    cart = cart.filter(i => i.id !== id);
                }
            }
            renderCart();
        }

        function removeCartItem(id) {
            cart = cart.filter(i => i.id !== id);
            renderCart();
        }

        function clearCart() {
            cart = [];
            document.getElementById('cart-customer-name').value = '';
            document.getElementById('cart-customer-phone').value = '';
            document.getElementById('cart-address').value = '';
            document.getElementById('cart-special-notes').value = '';
            document.getElementById('cart-delivery-fee').value = '0';
            document.getElementById('cart-discount').value = '0';
            renderCart();
        }

        function handleOrderTypeChange() {
            const type = document.getElementById('cart-order-type').value;
            const addrInput = document.getElementById('cart-address');
            if (type === 'dine_in') {
                addrInput.placeholder = 'Table Number (e.g. Table 4)';
            } else if (type === 'delivery') {
                addrInput.placeholder = 'Delivery Street / Mohalla';
            } else {
                addrInput.placeholder = 'Counter / Takeaway';
            }
        }

        function renderCart() {
            const container = document.getElementById('cart-items-container');
            container.innerHTML = '';

            if (cart.length === 0) {
                container.innerHTML = `<div class="text-center py-16 text-slate-500 text-xs font-medium">Cart is empty.<br>Click any item from the menu catalog to add!</div>`;
                calculateCartTotal();
                return;
            }

            cart.forEach(item => {
                const row = document.createElement('div');
                row.className = "bg-darkslate-950 border border-slate-800 rounded-xl p-2.5 flex items-center justify-between text-xs";
                const totalItemPrice = item.price * item.qty;

                row.innerHTML = `
                    <div class="flex-1 pr-2 min-w-0">
                        <div class="font-bold text-slate-100 truncate">${item.name}</div>
                        <div class="text-[11px] text-slate-400 font-mono-num">Rs. ${item.price} × ${item.qty} = <span class="text-emerald-400 font-bold">Rs. ${totalItemPrice}</span></div>
                    </div>
                    <div class="flex items-center space-x-1.5 shrink-0">
                        <button onclick="updateCartQty('${item.id}', -1)" class="w-6 h-6 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold flex items-center justify-center">-</button>
                        <span class="font-mono-num font-bold text-xs w-4 text-center text-white">${item.qty}</span>
                        <button onclick="updateCartQty('${item.id}', 1)" class="w-6 h-6 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold flex items-center justify-center">+</button>
                        <button onclick="removeCartItem('${item.id}')" class="text-rose-400 hover:text-rose-300 ml-1.5 font-bold text-sm">✕</button>
                    </div>
                `;
                container.appendChild(row);
            });

            calculateCartTotal();
        }

        function calculateCartTotal() {
            const subtotal = cart.reduce((sum, item) => sum + (item.price * item.qty), 0);
            const delivery = parseInt(document.getElementById('cart-delivery-fee').value) || 0;
            const discount = parseInt(document.getElementById('cart-discount').value) || 0;
            const net = Math.max(0, subtotal + delivery - discount);

            document.getElementById('cart-subtotal').innerText = `Rs. ${subtotal}`;
            document.getElementById('cart-net-total').innerText = `Rs. ${net}`;
            return { subtotal, delivery, discount, net };
        }

        async function submitPosOrder(andPrint = false) {
            if (cart.length === 0) {
                alert('Please add at least one item to cart!');
                return;
            }

            const { subtotal, delivery, discount, net } = calculateCartTotal();
            const customerName = document.getElementById('cart-customer-name').value.trim() || 'Walk-in Customer';
            const customerPhone = document.getElementById('cart-customer-phone').value.trim() || '-';
            const orderType = document.getElementById('cart-order-type').value;
            const address = document.getElementById('cart-address').value.trim() || (orderType === 'dine_in' ? 'Dine-in Table' : 'Counter Takeaway');
            const specialNotes = document.getElementById('cart-special-notes').value.trim();

            const itemsList = cart.map(i => `• ${i.qty}x ${i.name} — Rs. ${i.price * i.qty}`).join('\\n');

            const payload = {
                customer_name: customerName,
                customer_phone: customerPhone,
                order_type: orderType,
                address: address,
                items_list: itemsList,
                subtotal: subtotal,
                delivery_fee: delivery,
                total: net,
                special_notes: specialNotes,
                status: 'completed'
            };

            try {
                const res = await fetch('/api/pos/order', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (data.status === 'ok' || data.order_id) {
                    if (andPrint) {
                        openReceiptModal(data.order || { ...payload, order_id: data.order_id, timestamp: 'Just now' });
                    } else {
                        alert(`Order ${data.order_id} recorded successfully! Total: Rs. ${net}`);
                    }
                    clearCart();
                    fetchSalesStatsAndOrders();
                } else {
                    alert('Error creating order: ' + JSON.stringify(data));
                }
            } catch (err) {
                console.error('POS order submission error:', err);
                alert('Network error while saving order: ' + err.message);
            }
        }

        // ─────────────────────────────────────────────
        // 📊 Enhanced Visual Sales Analytics Logic
        // ─────────────────────────────────────────────
        async function fetchSalesStatsAndOrders() {
            try {
                const res = await fetch('/api/sales/stats');
                const data = await res.json();
                salesStats = data;
                allOrders = data.recent_orders || [];

                updateKPICards(data);
                renderAnalyticsView(data);
                renderOrdersPipeline();

                if (!document.getElementById('tab-content-sales').classList.contains('hidden')) {
                    renderSalesCharts();
                }
            } catch (err) {
                console.error('Error fetching sales analytics:', err);
            }
        }

        function updateKPICards(stats) {
            document.getElementById('kpi-today-rev').innerText = `Rs. ${(stats.today_revenue || 0).toLocaleString()}`;
            document.getElementById('kpi-today-orders').innerText = `${stats.today_orders || 0} orders`;

            document.getElementById('kpi-yest-rev').innerText = `Rs. ${(stats.yesterday_revenue || 0).toLocaleString()}`;
            document.getElementById('kpi-yest-orders').innerText = `(${stats.yesterday_orders || 0})`;

            document.getElementById('kpi-month-rev').innerText = `Rs. ${(stats.month_revenue || 0).toLocaleString()}`;
            document.getElementById('kpi-month-orders').innerText = `${stats.month_orders || 0} orders`;

            document.getElementById('kpi-total-rev').innerText = `Rs. ${(stats.total_revenue || 0).toLocaleString()}`;
            document.getElementById('kpi-total-orders').innerText = `${stats.total_orders || 0} total`;

            document.getElementById('kpi-avg-order').innerText = `Rs. ${(stats.avg_order_value || 0).toLocaleString()}`;

            // Channel Breakdown pill
            const ch = stats.channel_stats || {};
            const delRev = (ch.delivery?.revenue || 0).toLocaleString();
            const counterRev = ((ch.counter?.revenue || 0) + (ch.dine_in?.revenue || 0)).toLocaleString();
            document.getElementById('kpi-delivery-rev').innerText = `Rs. ${delRev}`;
            document.getElementById('kpi-counter-rev').innerText = `Rs. ${counterRev}`;

            // Active orders badge
            const activeCount = (allOrders || []).filter(o => ['pending', 'preparing', 'out_for_delivery'].includes(o.status)).length;
            const badge = document.getElementById('badge-active-count');
            if (activeCount > 0) {
                badge.innerText = activeCount;
                badge.classList.remove('hidden');
            } else {
                badge.classList.add('hidden');
            }
        }

        function renderAnalyticsView(stats) {
            // 1. Financial cards
            const tot = stats.total_revenue || 0;
            const ch = stats.channel_stats || {};
            const delData = ch.delivery || { count: 0, revenue: 0 };
            const countData = ch.counter || { count: 0, revenue: 0 };
            const dineData = ch.dine_in || { count: 0, revenue: 0 };

            const walkinRev = countData.revenue + dineData.revenue;
            const walkinCount = countData.count + dineData.count;

            document.getElementById('analytics-total-rev').innerText = `Rs. ${tot.toLocaleString()}`;
            document.getElementById('analytics-wa-rev').innerText = `Rs. ${delData.revenue.toLocaleString()}`;
            document.getElementById('analytics-wa-orders').innerText = `${delData.count} WhatsApp bot orders`;

            document.getElementById('analytics-counter-rev').innerText = `Rs. ${walkinRev.toLocaleString()}`;
            document.getElementById('analytics-counter-orders').innerText = `${walkinCount} counter/dine-in orders`;

            const sc = stats.status_counts || {};
            const comp = sc.completed || 0;
            const canc = sc.cancelled || 0;
            const active = (sc.pending || 0) + (sc.preparing || 0) + (sc.out_for_delivery || 0);
            const totalOrders = stats.total_orders || (comp + canc + active);
            const rate = totalOrders > 0 ? Math.round((comp / totalOrders) * 100) : 100;

            document.getElementById('analytics-completion-rate').innerText = `${rate}%`;
            document.getElementById('analytics-active-ratio').innerText = `${active} orders active now`;

            // 2. Leaderboard with visual ranking and progress bars
            const topContainer = document.getElementById('top-items-container');
            topContainer.innerHTML = '';
            const topList = stats.top_items || [];
            if (topList.length === 0) {
                topContainer.innerHTML = `<div class="py-6 text-center text-slate-500 text-xs">No item sales recorded yet.</div>`;
            } else {
                const maxCount = Math.max(...topList.map(t => t.count), 1);
                topList.forEach((it, idx) => {
                    const pct = Math.round((it.count / maxCount) * 100);
                    const medal = idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : `#${idx + 1}`;
                    const row = document.createElement('div');
                    row.className = "bg-darkslate-950 p-2.5 rounded-xl border border-slate-800 space-y-1.5";
                    row.innerHTML = `
                        <div class="flex items-center justify-between text-xs font-semibold">
                            <span class="flex items-center space-x-2 text-slate-200">
                                <span class="font-extrabold text-amber-400 w-5 text-center">${medal}</span>
                                <span>${it.name}</span>
                            </span>
                            <span class="font-bold text-emerald-400 font-mono-num">${it.count} sold</span>
                        </div>
                        <div class="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                            <div class="bg-gradient-to-r from-rose-500 to-amber-400 h-full rounded-full" style="width: ${pct}%"></div>
                        </div>
                    `;
                    topContainer.appendChild(row);
                });
            }

            // 3. Status Progress Bars
            const statusContainer = document.getElementById('status-bars-container');
            statusContainer.innerHTML = '';
            const statusMeta = [
                { key: 'completed', label: '🟢 Completed', color: 'from-emerald-500 to-teal-400', count: sc.completed || 0 },
                { key: 'preparing', label: '🔵 Preparing', color: 'from-sky-500 to-blue-400', count: sc.preparing || 0 },
                { key: 'pending', label: '🟡 Pending', color: 'from-amber-500 to-yellow-400', count: sc.pending || 0 },
                { key: 'out_for_delivery', label: '🟣 Out for Delivery', color: 'from-purple-500 to-pink-400', count: sc.out_for_delivery || 0 },
                { key: 'cancelled', label: '🔴 Cancelled', color: 'from-rose-500 to-red-600', count: sc.cancelled || 0 },
            ];
            const sumOrders = statusMeta.reduce((s, m) => s + m.count, 0) || 1;
            statusMeta.forEach(sm => {
                const pct = Math.round((sm.count / sumOrders) * 100);
                const el = document.createElement('div');
                el.className = "space-y-1";
                el.innerHTML = `
                    <div class="flex justify-between text-xs font-semibold">
                        <span class="text-slate-300">${sm.label}</span>
                        <span class="font-mono-num text-slate-200 font-bold">${sm.count} (${pct}%)</span>
                    </div>
                    <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div class="bg-gradient-to-r ${sm.color} h-full rounded-full" style="width: ${pct}%"></div>
                    </div>
                `;
                statusContainer.appendChild(el);
            });

            // 4. Sales Ledger Table
            const tbody = document.getElementById('sales-ledger-tbody');
            tbody.innerHTML = '';
            (allOrders || []).slice(0, 30).forEach(order => {
                const tr = document.createElement('tr');
                tr.className = "hover:bg-slate-800/40 transition";
                const channelBadge = {
                    delivery: '<span class="text-emerald-400">🛵 WhatsApp</span>',
                    counter: '<span class="text-blue-400">🛍️ Counter</span>',
                    dine_in: '<span class="text-amber-400">🍽️ Dine-in</span>'
                }[order.order_type] || order.order_type;

                const statusColor = {
                    completed: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
                    preparing: 'text-sky-400 bg-sky-500/10 border-sky-500/20',
                    pending: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
                    out_for_delivery: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
                    cancelled: 'text-rose-400 bg-rose-500/10 border-rose-500/20'
                }[order.status] || 'text-slate-300';

                // Truncate item text for clean table presentation
                const rawItems = order.items_list || order.slip || '';
                const itemsSummary = rawItems
                    .split(String.fromCharCode(10)).join(', ')
                    .replace(/•/g, '')
                    .replace(/— Rs[^,]*/g, '')
                    .trim();

                tr.innerHTML = `
                    <td class="py-2.5 px-2 font-mono-num font-bold text-sky-400">${order.order_id}</td>
                    <td class="py-2.5 px-2 text-slate-400 text-[11px] font-mono-num">${order.formatted_time || order.timestamp || '-'}</td>
                    <td class="py-2.5 px-2 text-slate-200 font-semibold">${order.customer_name}</td>
                    <td class="py-2.5 px-2 text-[11px] font-semibold">${channelBadge}</td>
                    <td class="py-2.5 px-2 text-slate-300 max-w-xs truncate">${itemsSummary || 'Order Items'}</td>
                    <td class="py-2.5 px-2 text-right font-mono-num font-extrabold text-emerald-400">Rs. ${order.total}</td>
                    <td class="py-2.5 px-2 text-center">
                        <span class="text-[10px] font-bold px-2 py-0.5 rounded-full border ${statusColor}">
                            ${order.status}
                        </span>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        function renderSalesCharts() {
            if (!salesStats || !salesStats.daily_breakdown) return;

            // 1. Enhanced Daily Sales Area & Bar Chart
            const trendCtx = document.getElementById('salesTrendChart')?.getContext('2d');
            if (trendCtx) {
                const labels = salesStats.daily_breakdown.map(d => {
                    const parts = d.date.split('-');
                    return parts.length >= 3 ? `${parts[2]}/${parts[1]}` : d.date;
                });
                const revenues = salesStats.daily_breakdown.map(d => d.revenue || d.total_revenue || 0);
                const orders = salesStats.daily_breakdown.map(d => d.order_count || d.orders_count || 0);

                if (salesChartInstance) salesChartInstance.destroy();

                const gradientRev = trendCtx.createLinearGradient(0, 0, 0, 300);
                gradientRev.addColorStop(0, 'rgba(225, 29, 72, 0.45)');
                gradientRev.addColorStop(1, 'rgba(225, 29, 72, 0.0)');

                salesChartInstance = new Chart(trendCtx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [
                            {
                                label: 'Daily Revenue (Rs.)',
                                data: revenues,
                                backgroundColor: gradientRev,
                                borderColor: '#f43f5e',
                                borderWidth: 2,
                                borderRadius: 6,
                                fill: true,
                                yAxisID: 'y'
                            },
                            {
                                label: 'Orders Count',
                                data: orders,
                                type: 'line',
                                borderColor: '#10b981',
                                backgroundColor: '#10b981',
                                tension: 0.35,
                                pointRadius: 4,
                                pointHoverRadius: 6,
                                borderWidth: 3,
                                yAxisID: 'y1'
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: { mode: 'index', intersect: false },
                        scales: {
                            x: {
                                grid: { color: 'rgba(51, 65, 85, 0.25)' },
                                ticks: { color: '#94a3b8', font: { size: 11, weight: '600' } }
                            },
                            y: {
                                type: 'linear',
                                display: true,
                                position: 'left',
                                grid: { color: 'rgba(51, 65, 85, 0.25)' },
                                ticks: {
                                    color: '#cbd5e1',
                                    font: { size: 11, family: 'JetBrains Mono', weight: '700' },
                                    callback: v => 'Rs. ' + v.toLocaleString()
                                }
                            },
                            y1: {
                                type: 'linear',
                                display: true,
                                position: 'right',
                                grid: { drawOnChartArea: false },
                                ticks: {
                                    color: '#10b981',
                                    font: { size: 11, family: 'JetBrains Mono', weight: '700' },
                                    stepSize: 1
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                labels: { color: '#f1f5f9', font: { size: 12, weight: '700' } }
                            },
                            tooltip: {
                                backgroundColor: '#0f172a',
                                titleColor: '#ffffff',
                                bodyColor: '#cbd5e1',
                                borderColor: '#334155',
                                borderWidth: 1,
                                padding: 10,
                                callbacks: {
                                    label: function(context) {
                                        if (context.dataset.yAxisID === 'y') {
                                            return ` Revenue: Rs. ${context.parsed.y.toLocaleString()}`;
                                        }
                                        return ` Orders: ${context.parsed.y}`;
                                    }
                                }
                            }
                        }
                    }
                });
            }

            // 2. Channel Distribution Doughnut Chart
            const statusCtx = document.getElementById('statusChart')?.getContext('2d');
            if (statusCtx) {
                const ch = salesStats.channel_stats || {};
                const delRev = ch.delivery?.revenue || 0;
                const counterRev = (ch.counter?.revenue || 0) + (ch.dine_in?.revenue || 0);

                const chLabels = ['WhatsApp Delivery', 'Counter & Dine-in'];
                const chValues = [delRev, counterRev];
                const chColors = ['#10b981', '#38bdf8'];

                if (statusChartInstance) statusChartInstance.destroy();

                statusChartInstance = new Chart(statusCtx, {
                    type: 'doughnut',
                    data: {
                        labels: chLabels,
                        datasets: [{
                            data: chValues,
                            backgroundColor: chColors,
                            borderColor: '#0f172a',
                            borderWidth: 3,
                            hoverOffset: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false }
                        },
                        cutout: '72%'
                    }
                });

                // Status Legend HTML
                const legendEl = document.getElementById('status-legend');
                legendEl.innerHTML = '';
                chLabels.forEach((label, idx) => {
                    const rev = chValues[idx];
                    legendEl.innerHTML += `
                        <div class="bg-darkslate-950 p-2 rounded-xl border border-slate-800 flex items-center space-x-2">
                            <span class="w-3 h-3 rounded-full shrink-0" style="background-color: ${chColors[idx]}"></span>
                            <div class="min-w-0">
                                <span class="text-slate-300 block text-[11px] font-semibold truncate">${label}</span>
                                <span class="font-extrabold text-white font-mono-num text-xs">Rs. ${rev.toLocaleString()}</span>
                            </div>
                        </div>
                    `;
                });
            }
        }

        // ─────────────────────────────────────────────
        // 🍳 Kitchen & Orders Pipeline Logic
        // ─────────────────────────────────────────────
        function filterOrderStatus(status) {
            activeOrderStatusFilter = status;
            document.querySelectorAll('.status-filter-btn').forEach(b => {
                b.classList.remove('active', 'bg-rose-600', 'text-white');
                b.classList.add('bg-slate-800', 'text-slate-300');
            });
            event.target.classList.add('active', 'bg-rose-600', 'text-white');
            event.target.classList.remove('bg-slate-800', 'text-slate-300');
            renderOrdersPipeline();
        }

        function renderOrdersPipeline() {
            const grid = document.getElementById('orders-pipeline-grid');
            grid.innerHTML = '';

            let filtered = allOrders;
            if (activeOrderStatusFilter !== 'all') {
                filtered = filtered.filter(o => o.status === activeOrderStatusFilter);
            }

            document.getElementById('orders-count-label').innerText = filtered.length;

            if (filtered.length === 0) {
                grid.innerHTML = `<div class="col-span-full py-20 text-center text-slate-500 text-sm">No orders found in this category.</div>`;
                return;
            }

            filtered.forEach(order => {
                const card = document.createElement('div');
                const statusBorder = {
                    pending: 'border-l-4 border-l-amber-400',
                    preparing: 'border-l-4 border-l-sky-400',
                    out_for_delivery: 'border-l-4 border-l-purple-400',
                    completed: 'border-l-4 border-l-emerald-400',
                    cancelled: 'border-l-4 border-l-rose-500'
                }[order.status] || 'border-l-4 border-l-slate-600';

                const statusBadge = {
                    pending: '<span class="bg-amber-400/15 text-amber-300 border border-amber-400/30 text-[10px] font-bold px-2 py-0.5 rounded-full">🟡 Pending</span>',
                    preparing: '<span class="bg-sky-400/15 text-sky-300 border border-sky-400/30 text-[10px] font-bold px-2 py-0.5 rounded-full">🔵 Preparing</span>',
                    out_for_delivery: '<span class="bg-purple-400/15 text-purple-300 border border-purple-400/30 text-[10px] font-bold px-2 py-0.5 rounded-full">🟣 Out for Delivery</span>',
                    completed: '<span class="bg-emerald-400/15 text-emerald-300 border border-emerald-400/30 text-[10px] font-bold px-2 py-0.5 rounded-full">🟢 Completed</span>',
                    cancelled: '<span class="bg-rose-500/15 text-rose-300 border border-rose-500/30 text-[10px] font-bold px-2 py-0.5 rounded-full">🔴 Cancelled</span>'
                }[order.status] || `<span class="bg-slate-700 text-slate-300 text-[10px] px-2 py-0.5 rounded">${order.status}</span>`;

                const typeBadge = {
                    delivery: '<span class="bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 text-[10px] px-2 py-0.5 rounded-lg font-bold">🛵 WhatsApp</span>',
                    counter: '<span class="bg-blue-500/15 text-blue-300 border border-blue-500/30 text-[10px] px-2 py-0.5 rounded-lg font-bold">🛍️ Counter</span>',
                    dine_in: '<span class="bg-amber-500/15 text-amber-300 border border-amber-500/30 text-[10px] px-2 py-0.5 rounded-lg font-bold">🍽️ Dine-in</span>'
                }[order.order_type] || '';

                const noteHtml = order.special_notes ? `
                    <div class="bg-amber-500/15 border border-amber-500/40 rounded-xl p-2.5 text-xs text-amber-200">
                        <strong>📝 Special Note:</strong> ${order.special_notes}
                    </div>
                ` : '';

                card.className = `bg-darkslate-900 border border-slate-800 ${statusBorder} rounded-2xl p-4 shadow-md space-y-3 flex flex-col justify-between`;

                card.innerHTML = `
                    <div class="space-y-2.5">
                        <div class="flex items-center justify-between">
                            <span class="font-extrabold text-sm text-sky-400 font-mono-num">${order.order_id}</span>
                            <div class="flex items-center space-x-1.5">
                                ${typeBadge}
                                ${statusBadge}
                            </div>
                        </div>

                        <div class="text-xs text-slate-300 space-y-1">
                            <div><strong>👤 Customer:</strong> ${order.customer_name} &nbsp;|&nbsp; <strong>📞</strong> <a href="https://wa.me/${(order.customer_phone || '').replace(/[^0-9]/g, '')}" target="_blank" class="text-emerald-400 hover:underline font-mono-num font-bold">${order.customer_phone}</a></div>
                            <div><strong>📍 Location / Table:</strong> ${order.address}</div>
                            <div class="text-[11px] text-slate-400">🕒 ${order.formatted_time || order.timestamp}</div>
                        </div>

                        <!-- Items list -->
                        <div class="bg-darkslate-950 p-3 rounded-xl border border-slate-800 text-xs text-slate-200 whitespace-pre-wrap font-sans leading-relaxed">
${order.items_list || order.slip || 'Order items'}
                        </div>

                        ${noteHtml}
                    </div>

                    <div class="pt-3 border-t border-slate-800 flex items-center justify-between">
                        <div>
                            <span class="text-xs text-slate-400">Total:</span>
                            <span class="text-lg font-black text-emerald-400 font-mono-num ml-1">Rs. ${order.total}</span>
                        </div>
                        <div class="flex items-center space-x-2">
                            <button onclick="openReceiptModalByOrderId('${order.order_id}')" class="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold rounded-xl transition" title="Print 80mm Receipt">
                                🖨️
                            </button>
                            <select onchange="updateOrderStatus('${order.order_id}', this.value)" class="bg-darkslate-950 border border-slate-700 text-slate-200 rounded-xl text-xs px-2.5 py-1.5 font-semibold focus:outline-none focus:border-rose-500">
                                <option value="" disabled selected>Status...</option>
                                <option value="pending">🟡 Pending</option>
                                <option value="preparing">🔵 Preparing</option>
                                <option value="out_for_delivery">🟣 Out for Delivery</option>
                                <option value="completed">🟢 Completed</option>
                                <option value="cancelled">🔴 Cancelled</option>
                            </select>
                        </div>
                    </div>
                `;
                grid.appendChild(card);
            });
        }

        async function updateOrderStatus(orderId, newStatus) {
            try {
                const res = await fetch(`/api/orders/${encodeURIComponent(orderId)}/status`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status: newStatus })
                });
                const data = await res.json();
                if (data.status === 'ok') {
                    fetchSalesStatsAndOrders();
                } else {
                    alert('Status update error: ' + JSON.stringify(data));
                }
            } catch (err) {
                console.error('Error updating order status:', err);
            }
        }

        // ─────────────────────────────────────────────
        // 🖨️ Thermal Receipt Printing Logic
        // ─────────────────────────────────────────────
        function openReceiptModalByOrderId(orderId) {
            const order = allOrders.find(o => o.order_id === orderId);
            if (order) {
                openReceiptModal(order);
            }
        }

        function openReceiptModal(order) {
            const container = document.getElementById('thermal-receipt-modal');
            const noteSection = order.special_notes ? `
                <div style="border-top: 1px dashed #000; margin-top: 6px; padding-top: 6px;">
                    <strong>NOTE:</strong> ${order.special_notes}
                </div>
            ` : '';

            container.innerHTML = `
                <div style="text-align: center; border-bottom: 1px dashed #000; padding-bottom: 8px; margin-bottom: 8px;">
                    <h2 style="font-size: 14pt; font-weight: bold; margin: 0;">CHERRY PERI FAST FOOD</h2>
                    <p style="margin: 2px 0; font-size: 9pt;">Circular Road, Opp. Stylo Center, D.I. Khan</p>
                    <p style="margin: 2px 0; font-size: 9pt;">Order Delivery: 0332-7247289</p>
                </div>

                <div style="font-size: 9pt; margin-bottom: 8px; border-bottom: 1px dashed #000; padding-bottom: 6px;">
                    <div><strong>RECEIPT:</strong> ${order.order_id}</div>
                    <div><strong>DATE:</strong> ${order.timestamp || new Date().toLocaleString()}</div>
                    <div><strong>TYPE:</strong> ${(order.order_type || 'Takeaway').toUpperCase()}</div>
                    <div><strong>CUSTOMER:</strong> ${order.customer_name || 'Walk-in'} (${order.customer_phone || '-'})</div>
                    <div><strong>LOCATION:</strong> ${order.address || 'Counter'}</div>
                </div>

                <div style="font-size: 10pt; line-height: 1.4; white-space: pre-wrap; margin-bottom: 8px;">
${order.items_list || order.slip || ''}
                </div>

                ${noteSection}

                <div style="border-top: 2px solid #000; padding-top: 6px; margin-top: 8px; display: flex; justify-content: space-between; font-size: 13pt; font-weight: bold;">
                    <span>NET TOTAL:</span>
                    <span>Rs. ${order.total}</span>
                </div>

                <div style="text-align: center; border-top: 1px dashed #000; margin-top: 12px; padding-top: 8px; font-size: 9pt;">
                    *** THANK YOU FOR DINING WITH US! ***<br>
                    Please visit again 🍕
                </div>
            `;

            document.getElementById('receipt-modal-backdrop').classList.remove('hidden');
        }

        function closeReceiptModal() {
            document.getElementById('receipt-modal-backdrop').classList.add('hidden');
        }
    </script>
</body>
</html>"""
