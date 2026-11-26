# ============================================
# 🍕 Cherry Peri Fast Food - POS & Sales Management HTML View
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
                            500: '#f43f5e',
                            600: '#e11d48',
                            700: '#be123c',
                            800: '#9f1239',
                            900: '#881337',
                        },
                        darkslate: {
                            800: '#1e293b',
                            850: '#172033',
                            900: '#0f172a',
                            950: '#0b1120',
                        }
                    }
                }
            }
        }
    </script>
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <style>
        body {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: #0b1120;
            color: #f8fafc;
        }
        .font-mono-num {
            font-family: 'JetBrains Mono', monospace;
        }
        /* Custom Scrollbars */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #0f172a;
        }
        ::-webkit-scrollbar-thumb {
            background: #334155;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #475569;
        }
        /* Receipt Printing Optimization (80mm standard thermal) */
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
            background-color: #e11d48;
            color: #ffffff;
            box-shadow: 0 4px 12px rgba(225, 29, 72, 0.35);
        }
    </style>
</head>
<body class="min-h-screen flex flex-col bg-darkslate-950 text-slate-100">

    <!-- ───────────────────────────────────────────── -->
    <!-- 🔝 Top Navbar & Brand Header -->
    <!-- ───────────────────────────────────────────── -->
    <header class="bg-darkslate-900 border-b border-slate-800 sticky top-0 z-40 px-4 py-3 shadow-md">
        <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
            <!-- Brand -->
            <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-cherry-700 to-rose-500 flex items-center justify-center text-xl shadow-lg shadow-cherry-700/30">
                    🍕
                </div>
                <div>
                    <div class="flex items-center space-x-2">
                        <h1 class="text-lg font-extrabold tracking-tight text-white">CHERRY PERI</h1>
                        <span class="bg-rose-500/20 text-rose-400 text-xs px-2 py-0.5 rounded-full font-bold border border-rose-500/30">POS & SALES</span>
                    </div>
                    <p class="text-xs text-slate-400">Opp. Stylo, Circular Road, D.I. Khan</p>
                </div>
            </div>

            <!-- Tab Buttons -->
            <nav class="flex items-center bg-darkslate-850 p-1 rounded-xl border border-slate-800 space-x-1">
                <button onclick="switchTab('pos')" id="btn-tab-pos" class="tab-btn active px-4 py-1.5 rounded-lg text-sm font-semibold text-slate-300 hover:text-white transition flex items-center space-x-2">
                    <span>🛒</span>
                    <span>POS Terminal</span>
                </button>
                <button onclick="switchTab('sales')" id="btn-tab-sales" class="tab-btn px-4 py-1.5 rounded-lg text-sm font-semibold text-slate-300 hover:text-white transition flex items-center space-x-2">
                    <span>📊</span>
                    <span>Sales & Income</span>
                </button>
                <button onclick="switchTab('orders')" id="btn-tab-orders" class="tab-btn px-4 py-1.5 rounded-lg text-sm font-semibold text-slate-300 hover:text-white transition flex items-center space-x-2">
                    <span>🍳</span>
                    <span>Orders Pipeline</span>
                    <span id="badge-active-count" class="bg-emerald-500 text-slate-950 font-bold text-xs px-1.5 py-0.2 rounded-full hidden">0</span>
                </button>
            </nav>

            <!-- Actions & Clock -->
            <div class="flex items-center space-x-3">
                <div class="text-right hidden sm:block">
                    <div id="live-clock" class="text-xs font-mono-num font-bold text-slate-200">12:00:00 PM</div>
                    <div id="live-date" class="text-[11px] text-slate-400">Today</div>
                </div>
                <div class="h-6 w-px bg-slate-800 hidden sm:block"></div>
                <!-- Live status indicator -->
                <div class="flex items-center space-x-1.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-2.5 py-1 rounded-lg text-xs font-medium">
                    <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    <span class="hidden md:inline">Live Sync</span>
                </div>
                <!-- Export to CSV -->
                <a href="/api/sales/export" download class="bg-slate-850 hover:bg-slate-800 border border-slate-700 text-slate-200 px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition">
                    <span>📥</span>
                    <span>Export CSV</span>
                </a>
            </div>
        </div>
    </header>

    <!-- ───────────────────────────────────────────── -->
    <!-- 💰 Quick Sales KPI Banner (Always Visible) -->
    <!-- ───────────────────────────────────────────── -->
    <div class="bg-darkslate-900/60 border-b border-slate-800/80 px-4 py-2.5">
        <div class="max-w-7xl mx-auto grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-5 gap-3">
            <!-- Today's Revenue -->
            <div class="bg-darkslate-850 border border-slate-800/80 rounded-xl p-3 flex items-center justify-between">
                <div>
                    <div class="text-[11px] uppercase tracking-wider text-slate-400 font-semibold">Today's Sales</div>
                    <div class="text-lg font-extrabold text-emerald-400 font-mono-num" id="kpi-today-rev">Rs. 0</div>
                </div>
                <div class="text-right">
                    <span id="kpi-today-orders" class="bg-slate-800 text-slate-300 text-xs px-2 py-0.5 rounded font-bold font-mono-num">0 orders</span>
                </div>
            </div>

            <!-- Yesterday's Revenue -->
            <div class="bg-darkslate-850 border border-slate-800/80 rounded-xl p-3 flex items-center justify-between">
                <div>
                    <div class="text-[11px] uppercase tracking-wider text-slate-400 font-semibold">Yesterday</div>
                    <div class="text-lg font-bold text-slate-200 font-mono-num" id="kpi-yest-rev">Rs. 0</div>
                </div>
                <div class="text-right">
                    <span id="kpi-yest-orders" class="bg-slate-800 text-slate-300 text-xs px-2 py-0.5 rounded font-bold font-mono-num">0 orders</span>
                </div>
            </div>

            <!-- This Month's Revenue -->
            <div class="bg-darkslate-850 border border-slate-800/80 rounded-xl p-3 flex items-center justify-between">
                <div>
                    <div class="text-[11px] uppercase tracking-wider text-slate-400 font-semibold">This Month</div>
                    <div class="text-lg font-extrabold text-amber-400 font-mono-num" id="kpi-month-rev">Rs. 0</div>
                </div>
                <div class="text-right">
                    <span id="kpi-month-orders" class="bg-slate-800 text-slate-300 text-xs px-2 py-0.5 rounded font-bold font-mono-num">0 orders</span>
                </div>
            </div>

            <!-- Total All-Time -->
            <div class="bg-darkslate-850 border border-slate-800/80 rounded-xl p-3 flex items-center justify-between">
                <div>
                    <div class="text-[11px] uppercase tracking-wider text-slate-400 font-semibold">Total Revenue</div>
                    <div class="text-lg font-bold text-sky-400 font-mono-num" id="kpi-total-rev">Rs. 0</div>
                </div>
                <div class="text-right">
                    <span id="kpi-total-orders" class="bg-slate-800 text-slate-300 text-xs px-2 py-0.5 rounded font-bold font-mono-num">0 total</span>
                </div>
            </div>

            <!-- Avg Order Value -->
            <div class="bg-darkslate-850 border border-slate-800/80 rounded-xl p-3 col-span-2 sm:col-span-1 flex items-center justify-between">
                <div>
                    <div class="text-[11px] uppercase tracking-wider text-slate-400 font-semibold">Avg Order (AOV)</div>
                    <div class="text-lg font-bold text-rose-400 font-mono-num" id="kpi-avg-order">Rs. 0</div>
                </div>
                <div class="text-right">
                    <span class="text-xs text-slate-400">per ticket</span>
                </div>
            </div>
        </div>
    </div>

    <!-- ───────────────────────────────────────────── -->
    <!-- 🖥️ MAIN VIEW CONTAINER -->
    <!-- ───────────────────────────────────────────── -->
    <main class="flex-1 max-w-7xl w-full mx-auto p-4">

        <!-- ───────────────────────────────────────────── -->
        <!-- 🛒 TAB 1: POS TERMINAL (Counter / Dine-In / Walk-in) -->
        <!-- ───────────────────────────────────────────── -->
        <div id="tab-content-pos" class="space-y-4">
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">

                <!-- Left Column: Menu Items & Catalog (8 cols) -->
                <div class="lg:col-span-7 xl:col-span-8 space-y-4">

                    <!-- Search and Category Filters -->
                    <div class="bg-darkslate-900 border border-slate-800 rounded-2xl p-4 shadow-sm space-y-3">
                        <div class="flex flex-wrap items-center gap-2">
                            <div class="relative flex-1 min-w-[200px]">
                                <input type="text" id="pos-search-input" oninput="filterMenuItems()" placeholder="🔍 Quick search items (e.g. Deal 1, Zinger, Tikka)..."
                                       class="w-full bg-darkslate-950 border border-slate-700/80 rounded-xl px-4 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-rose-500 transition">
                            </div>
                            <button onclick="clearSearch()" class="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium rounded-xl transition">
                                Clear
                            </button>
                        </div>

                        <!-- Category Filter Buttons -->
                        <div class="flex items-center gap-1.5 overflow-x-auto pb-1" id="category-pills">
                            <button onclick="filterCategory('all')" class="cat-pill active px-3 py-1.5 bg-rose-600 text-white rounded-lg text-xs font-semibold whitespace-nowrap shadow-sm">
                                🌟 All
                            </button>
                            <button onclick="filterCategory('deals')" class="cat-pill px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-semibold whitespace-nowrap transition">
                                🌟 Deals (1-26)
                            </button>
                            <button onclick="filterCategory('pizza_regular')" class="cat-pill px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-semibold whitespace-nowrap transition">
                                🍕 Regular Pizzas
                            </button>
                            <button onclick="filterCategory('pizza_special')" class="cat-pill px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-semibold whitespace-nowrap transition">
                                🍕 Special Pizzas
                            </button>
                            <button onclick="filterCategory('burgers')" class="cat-pill px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-semibold whitespace-nowrap transition">
                                🍔 Burgers
                            </button>
                            <button onclick="filterCategory('shawarma')" class="cat-pill px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-semibold whitespace-nowrap transition">
                                🌯 Shawarma
                            </button>
                            <button onclick="filterCategory('paratha_rolls')" class="cat-pill px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-semibold whitespace-nowrap transition">
                                🌯 Paratha Rolls
                            </button>
                            <button onclick="filterCategory('fries')" class="cat-pill px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-semibold whitespace-nowrap transition">
                                🍟 Fries & Pastas
                            </button>
                            <button onclick="filterCategory('drinks')" class="cat-pill px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-semibold whitespace-nowrap transition">
                                🥤 Drinks
                            </button>
                        </div>
                    </div>

                    <!-- Items Grid -->
                    <div id="pos-items-grid" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 max-h-[640px] overflow-y-auto pr-1">
                        <!-- Populated by JS -->
                    </div>
                </div>

                <!-- Right Column: Current POS Order / Bill Cart (4 cols) -->
                <div class="lg:col-span-5 xl:col-span-4 space-y-4">
                    <div class="bg-darkslate-900 border border-slate-800 rounded-2xl p-4 shadow-lg sticky top-20 flex flex-col h-[740px]">
                        <!-- Cart Header -->
                        <div class="flex items-center justify-between pb-3 border-b border-slate-800">
                            <div class="flex items-center space-x-2">
                                <span class="text-lg">🧾</span>
                                <h3 class="font-bold text-slate-100">Order Terminal</h3>
                            </div>
                            <button onclick="clearCart()" class="text-xs text-rose-400 hover:text-rose-300 font-semibold px-2 py-1 rounded hover:bg-rose-950/30 transition">
                                Clear Cart
                            </button>
                        </div>

                        <!-- Customer & Order Meta Inputs -->
                        <div class="py-3 space-y-2 border-b border-slate-800/80 text-xs">
                            <div class="grid grid-cols-2 gap-2">
                                <input type="text" id="cart-customer-name" placeholder="Customer Name"
                                       class="bg-darkslate-950 border border-slate-700/80 rounded-lg px-2.5 py-1.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-rose-500">
                                <input type="text" id="cart-customer-phone" placeholder="Phone (e.g. 0300-1234567)"
                                       class="bg-darkslate-950 border border-slate-700/80 rounded-lg px-2.5 py-1.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-rose-500">
                            </div>

                            <div class="grid grid-cols-2 gap-2">
                                <select id="cart-order-type" onchange="handleOrderTypeChange()"
                                        class="bg-darkslate-950 border border-slate-700/80 rounded-lg px-2.5 py-1.5 text-xs text-slate-100 focus:outline-none focus:border-rose-500">
                                    <option value="counter">Counter / Takeaway</option>
                                    <option value="dine_in">Dine-in (Table)</option>
                                    <option value="delivery">WhatsApp Delivery</option>
                                </select>
                                <input type="text" id="cart-address" placeholder="Table # / Delivery Address"
                                       class="bg-darkslate-950 border border-slate-700/80 rounded-lg px-2.5 py-1.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-rose-500">
                            </div>

                            <div>
                                <input type="text" id="cart-special-notes" placeholder="📝 Special Note (e.g. Cheese kam, Extra spicy)"
                                       class="w-full bg-darkslate-950 border border-amber-500/30 rounded-lg px-2.5 py-1.5 text-xs text-amber-200 placeholder-amber-400/40 focus:outline-none focus:border-amber-400">
                            </div>
                        </div>

                        <!-- Cart Items Scroll Area -->
                        <div id="cart-items-container" class="flex-1 overflow-y-auto py-2 space-y-2 pr-1">
                            <div class="text-center py-16 text-slate-500 text-xs">
                                Cart is empty.<br>Click any item from the left catalog to add!
                            </div>
                        </div>

                        <!-- Cart Totals & Place Order -->
                        <div class="pt-3 border-t border-slate-800 space-y-2">
                            <div class="flex justify-between text-xs text-slate-400">
                                <span>Subtotal</span>
                                <span class="font-mono-num font-semibold text-slate-200" id="cart-subtotal">Rs. 0</span>
                            </div>
                            <div class="flex justify-between text-xs text-slate-400 items-center">
                                <span>Delivery Fee (Rs.)</span>
                                <input type="number" id="cart-delivery-fee" value="0" min="0" oninput="calculateCartTotal()"
                                       class="w-16 bg-darkslate-950 border border-slate-700 text-right px-1.5 py-0.5 rounded text-xs text-slate-200 font-mono-num">
                            </div>
                            <div class="flex justify-between text-xs text-slate-400 items-center">
                                <span>Discount (Rs.)</span>
                                <input type="number" id="cart-discount" value="0" min="0" oninput="calculateCartTotal()"
                                       class="w-16 bg-darkslate-950 border border-slate-700 text-right px-1.5 py-0.5 rounded text-xs text-slate-200 font-mono-num">
                            </div>
                            <div class="flex justify-between items-center text-sm font-bold text-white pt-2 border-t border-slate-800/60">
                                <span>Net Total Payable:</span>
                                <span class="text-xl font-extrabold text-emerald-400 font-mono-num" id="cart-net-total">Rs. 0</span>
                            </div>

                            <!-- Actions -->
                            <div class="grid grid-cols-2 gap-2 pt-2">
                                <button onclick="submitPosOrder(false)" class="bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold py-2.5 px-3 rounded-xl text-xs transition flex items-center justify-center space-x-1.5">
                                    <span>💾</span>
                                    <span>Save Order</span>
                                </button>
                                <button onclick="submitPosOrder(true)" class="bg-gradient-to-r from-rose-600 to-rose-700 hover:from-rose-500 hover:to-rose-600 text-white font-extrabold py-2.5 px-3 rounded-xl text-xs transition shadow-lg shadow-rose-900/40 flex items-center justify-center space-x-1.5">
                                    <span>🖨️</span>
                                    <span>Order & Print</span>
                                </button>
                            </div>
                        </div>

                    </div>
                </div>

            </div>
        </div>

        <!-- ───────────────────────────────────────────── -->
        <!-- 📊 TAB 2: SALES & INCOME ANALYTICS -->
        <!-- ───────────────────────────────────────────── -->
        <div id="tab-content-sales" class="hidden space-y-6">

            <!-- Chart Row -->
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
                <!-- Daily Sales Bar Chart (30 Days) -->
                <div class="lg:col-span-8 bg-darkslate-900 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-4">
                    <div class="flex items-center justify-between">
                        <div>
                            <h3 class="font-bold text-white text-base">📈 Daily Sales & Income Trend (Last 30 Days)</h3>
                            <p class="text-xs text-slate-400">Total revenue and daily orders volume</p>
                        </div>
                        <span class="text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-lg font-mono-num font-semibold">
                            Unified Sales (WhatsApp + Counter)
                        </span>
                    </div>
                    <div class="h-72 w-full">
                        <canvas id="salesTrendChart"></canvas>
                    </div>
                </div>

                <!-- Order Status / Source Doughnut Chart -->
                <div class="lg:col-span-4 bg-darkslate-900 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-4">
                    <div>
                        <h3 class="font-bold text-white text-base">🥧 Orders by Status</h3>
                        <p class="text-xs text-slate-400">Active vs completed pipeline</p>
                    </div>
                    <div class="h-60 flex items-center justify-center">
                        <canvas id="statusChart"></canvas>
                    </div>
                    <div id="status-legend" class="grid grid-cols-2 gap-2 text-xs"></div>
                </div>
            </div>

            <!-- Top Selling Items & Breakdown -->
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
                <!-- Top Items Table -->
                <div class="lg:col-span-6 bg-darkslate-900 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-3">
                    <h3 class="font-bold text-white text-base flex items-center space-x-2">
                        <span>🏆</span>
                        <span>Top Selling Menu Items</span>
                    </h3>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs">
                            <thead>
                                <tr class="text-slate-400 border-b border-slate-800">
                                    <th class="py-2">Item Name</th>
                                    <th class="py-2 text-right">Qty Sold</th>
                                </tr>
                            </thead>
                            <tbody id="top-items-tbody" class="divide-y divide-slate-800/60">
                                <!-- Populated by JS -->
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Sales Summary Info Cards -->
                <div class="lg:col-span-6 bg-darkslate-900 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-4">
                    <h3 class="font-bold text-white text-base flex items-center space-x-2">
                        <span>📋</span>
                        <span>Income & Reporting Information</span>
                    </h3>
                    <div class="grid grid-cols-2 gap-3 text-xs">
                        <div class="bg-darkslate-950 p-3 rounded-xl border border-slate-800">
                            <span class="text-slate-400 block mb-1">Currency</span>
                            <span class="text-white font-bold text-sm">Pakistani Rupee (PKR)</span>
                        </div>
                        <div class="bg-darkslate-950 p-3 rounded-xl border border-slate-800">
                            <span class="text-slate-400 block mb-1">Sales Tracking</span>
                            <span class="text-emerald-400 font-bold text-sm">Daily + Monthly Auto</span>
                        </div>
                        <div class="bg-darkslate-950 p-3 rounded-xl border border-slate-800">
                            <span class="text-slate-400 block mb-1">WhatsApp Orders</span>
                            <span class="text-white font-bold text-sm">Auto-logged from Bot</span>
                        </div>
                        <div class="bg-darkslate-950 p-3 rounded-xl border border-slate-800">
                            <span class="text-slate-400 block mb-1">Counter / POS Sales</span>
                            <span class="text-white font-bold text-sm">Included in Income</span>
                        </div>
                    </div>
                    <div class="pt-2">
                        <a href="/api/sales/export" download class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-2.5 px-4 rounded-xl text-xs flex items-center justify-center space-x-2 transition shadow-md shadow-emerald-950">
                            <span>📥</span>
                            <span>Download Full Sales History (CSV / Excel)</span>
                        </a>
                    </div>
                </div>
            </div>

        </div>

        <!-- ───────────────────────────────────────────── -->
        <!-- 🍳 TAB 3: KITCHEN & ORDERS MANAGEMENT PIPELINE -->
        <!-- ───────────────────────────────────────────── -->
        <div id="tab-content-orders" class="hidden space-y-4">

            <!-- Filter Status Bar -->
            <div class="bg-darkslate-900 border border-slate-800 rounded-2xl p-3 flex flex-wrap items-center justify-between gap-3">
                <div class="flex items-center space-x-1.5 overflow-x-auto pb-1" id="order-status-filters">
                    <button onclick="filterOrderStatus('all')" class="status-filter-btn active px-3 py-1.5 bg-rose-600 text-white rounded-lg text-xs font-semibold whitespace-nowrap">
                        All Orders
                    </button>
                    <button onclick="filterOrderStatus('pending')" class="status-filter-btn px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-amber-400 rounded-lg text-xs font-semibold whitespace-nowrap">
                        🟡 Pending
                    </button>
                    <button onclick="filterOrderStatus('preparing')" class="status-filter-btn px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-sky-400 rounded-lg text-xs font-semibold whitespace-nowrap">
                        🔵 Preparing
                    </button>
                    <button onclick="filterOrderStatus('out_for_delivery')" class="status-filter-btn px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-purple-400 rounded-lg text-xs font-semibold whitespace-nowrap">
                        🟣 Out for Delivery
                    </button>
                    <button onclick="filterOrderStatus('completed')" class="status-filter-btn px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-emerald-400 rounded-lg text-xs font-semibold whitespace-nowrap">
                        🟢 Completed
                    </button>
                    <button onclick="filterOrderStatus('cancelled')" class="status-filter-btn px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-rose-400 rounded-lg text-xs font-semibold whitespace-nowrap">
                        🔴 Cancelled
                    </button>
                </div>

                <div class="text-xs text-slate-400 font-medium">
                    Showing <span id="orders-count-label" class="text-white font-bold">0</span> orders
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
    <div id="receipt-modal-backdrop" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-white text-slate-900 rounded-2xl max-w-sm w-full p-5 shadow-2xl relative space-y-4 max-h-[90vh] overflow-y-auto">
            <!-- Modal Header -->
            <div class="flex items-center justify-between no-print border-b border-slate-200 pb-3">
                <span class="font-bold text-sm text-slate-800">Print Preview (80mm Thermal)</span>
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
                <button onclick="window.print()" class="flex-1 py-2 bg-rose-600 hover:bg-rose-700 text-white font-extrabold text-xs rounded-xl shadow-md transition flex items-center justify-center space-x-1">
                    <span>🖨️</span>
                    <span>Print Receipt</span>
                </button>
            </div>
        </div>
    </div>

    <!-- ───────────────────────────────────────────── -->
    <!-- ⚡ FRONTEND INTERACTIVITY & API INTEGRATION -->
    <!-- ───────────────────────────────────────────── -->
    <script>
        // Global state
        let allMenuItems = [];
        let currentCategory = 'all';
        let currentSearch = '';
        let cart = []; // [{id, name, price, qty}]
        let allOrders = [];
        let salesStats = {};
        let activeOrderStatusFilter = 'all';
        let salesChartInstance = null;
        let statusChartInstance = null;

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', () => {
            startClock();
            fetchMenuData();
            fetchSalesStatsAndOrders();

            // Auto-refresh stats & orders every 15 seconds
            setInterval(fetchSalesStatsAndOrders, 15000);
        });

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
        // 🍕 Menu Catalog & POS Terminal Logic
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
                grid.innerHTML = `<div class="col-span-full py-16 text-center text-slate-500 text-sm">No items found matching your filter.</div>`;
                return;
            }

            filtered.forEach(item => {
                const card = document.createElement('div');
                card.className = "bg-darkslate-900 border border-slate-800 hover:border-slate-700 rounded-xl p-3 shadow-sm hover:shadow-md transition flex flex-col justify-between group";

                card.innerHTML = `
                    <div>
                        <div class="flex items-start justify-between gap-1 mb-1.5">
                            <h4 class="text-xs font-bold text-slate-100 group-hover:text-rose-400 transition leading-snug">${item.name}</h4>
                        </div>
                        <span class="text-[10px] text-slate-400 bg-slate-800/80 px-1.5 py-0.5 rounded font-medium">${item.category_name || item.category}</span>
                    </div>
                    <div class="mt-3 pt-2 border-t border-slate-800/70 flex items-center justify-between">
                        <span class="text-sm font-extrabold text-emerald-400 font-mono-num">Rs. ${item.price}</span>
                        <button onclick="addToCart('${item.id}', '${escapeHtml(item.name)}', ${item.price})"
                                class="bg-rose-600 hover:bg-rose-500 active:scale-95 text-white font-bold text-xs px-2.5 py-1.5 rounded-lg transition shadow-sm flex items-center space-x-1">
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
                container.innerHTML = `<div class="text-center py-16 text-slate-500 text-xs">Cart is empty.<br>Click any item from the left catalog to add!</div>`;
                calculateCartTotal();
                return;
            }

            cart.forEach(item => {
                const row = document.createElement('div');
                row.className = "bg-darkslate-950 border border-slate-800 rounded-lg p-2 flex items-center justify-between text-xs";
                const totalItemPrice = item.price * item.qty;

                row.innerHTML = `
                    <div class="flex-1 pr-2 min-w-0">
                        <div class="font-bold text-slate-100 truncate">${item.name}</div>
                        <div class="text-[11px] text-slate-400 font-mono-num">Rs. ${item.price} x ${item.qty} = <span class="text-emerald-400 font-semibold">Rs. ${totalItemPrice}</span></div>
                    </div>
                    <div class="flex items-center space-x-1.5 shrink-0">
                        <button onclick="updateCartQty('${item.id}', -1)" class="w-6 h-6 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold flex items-center justify-center">-</button>
                        <span class="font-mono-num font-bold text-xs w-4 text-center text-white">${item.qty}</span>
                        <button onclick="updateCartQty('${item.id}', 1)" class="w-6 h-6 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold flex items-center justify-center">+</button>
                        <button onclick="removeCartItem('${item.id}')" class="text-rose-400 hover:text-rose-300 ml-1 font-bold text-sm">✕</button>
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
        // 📊 Sales Analytics & Reporting Logic
        // ─────────────────────────────────────────────
        async function fetchSalesStatsAndOrders() {
            try {
                const res = await fetch('/api/sales/stats');
                const data = await res.json();
                salesStats = data;
                allOrders = data.recent_orders || [];

                updateKPICards(data);
                renderTopItems(data.top_items || []);
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
            document.getElementById('kpi-yest-orders').innerText = `${stats.yesterday_orders || 0} orders`;

            document.getElementById('kpi-month-rev').innerText = `Rs. ${(stats.month_revenue || 0).toLocaleString()}`;
            document.getElementById('kpi-month-orders').innerText = `${stats.month_orders || 0} orders`;

            document.getElementById('kpi-total-rev').innerText = `Rs. ${(stats.total_revenue || 0).toLocaleString()}`;
            document.getElementById('kpi-total-orders').innerText = `${stats.total_orders || 0} total`;

            document.getElementById('kpi-avg-order').innerText = `Rs. ${(stats.avg_order_value || 0).toLocaleString()}`;

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

        function renderSalesCharts() {
            if (!salesStats || !salesStats.daily_breakdown) return;

            // 1. Daily Trend Chart (Last 30 Days)
            const trendCtx = document.getElementById('salesTrendChart')?.getContext('2d');
            if (trendCtx) {
                const labels = salesStats.daily_breakdown.map(d => d.date.split('-').slice(1).join('/'));
                const revenues = salesStats.daily_breakdown.map(d => d.total_revenue);
                const orders = salesStats.daily_breakdown.map(d => d.orders_count);

                if (salesChartInstance) salesChartInstance.destroy();

                salesChartInstance = new Chart(trendCtx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [
                            {
                                label: 'Daily Revenue (Rs.)',
                                data: revenues,
                                backgroundColor: 'rgba(225, 29, 72, 0.7)',
                                borderColor: 'rgba(225, 29, 72, 1)',
                                borderWidth: 1,
                                borderRadius: 4,
                                yAxisID: 'y'
                            },
                            {
                                label: 'Orders Count',
                                data: orders,
                                type: 'line',
                                borderColor: '#10b981',
                                backgroundColor: '#10b981',
                                tension: 0.3,
                                borderWidth: 2,
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
                                grid: { color: 'rgba(51, 65, 85, 0.3)' },
                                ticks: { color: '#94a3b8', font: { size: 10 } }
                            },
                            y: {
                                type: 'linear',
                                display: true,
                                position: 'left',
                                grid: { color: 'rgba(51, 65, 85, 0.3)' },
                                ticks: {
                                    color: '#94a3b8',
                                    font: { size: 10 },
                                    callback: v => 'Rs. ' + v.toLocaleString()
                                }
                            },
                            y1: {
                                type: 'linear',
                                display: true,
                                position: 'right',
                                grid: { drawOnChartArea: false },
                                ticks: { color: '#10b981', font: { size: 10 } }
                            }
                        },
                        plugins: {
                            legend: { labels: { color: '#e2e8f0', font: { size: 11 } } }
                        }
                    }
                });
            }

            // 2. Status Doughnut Chart
            const statusCtx = document.getElementById('statusChart')?.getContext('2d');
            if (statusCtx && salesStats.status_counts) {
                const sc = salesStats.status_counts;
                const keys = Object.keys(sc);
                const values = Object.values(sc);

                if (statusChartInstance) statusChartInstance.destroy();

                const colorMap = {
                    completed: '#10b981',
                    preparing: '#38bdf8',
                    pending: '#f59e0b',
                    out_for_delivery: '#a855f7',
                    cancelled: '#ef4444'
                };
                const colors = keys.map(k => colorMap[k] || '#64748b');

                statusChartInstance = new Chart(statusCtx, {
                    type: 'doughnut',
                    data: {
                        labels: keys.map(k => k.replace(/_/g, ' ').toUpperCase()),
                        datasets: [{
                            data: values,
                            backgroundColor: colors,
                            borderWidth: 0
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false }
                        }
                    }
                });

                // Status Legend HTML
                const legendEl = document.getElementById('status-legend');
                legendEl.innerHTML = '';
                keys.forEach((k, idx) => {
                    legendEl.innerHTML += `
                        <div class="flex items-center space-x-1.5">
                            <span class="w-2.5 h-2.5 rounded-full" style="background-color: ${colors[idx]}"></span>
                            <span class="text-slate-300 capitalize">${k.replace(/_/g, ' ')}:</span>
                            <span class="font-bold text-white font-mono-num">${values[idx]}</span>
                        </div>
                    `;
                });
            }
        }

        function renderTopItems(items) {
            const tbody = document.getElementById('top-items-tbody');
            tbody.innerHTML = '';
            if (items.length === 0) {
                tbody.innerHTML = `<tr><td colspan="2" class="py-4 text-center text-slate-500">No sales recorded yet.</td></tr>`;
                return;
            }
            items.forEach((it, idx) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="py-2 text-slate-200">
                        <span class="font-bold text-rose-400 mr-2">#${idx + 1}</span>
                        ${it.name}
                    </td>
                    <td class="py-2 text-right font-bold text-emerald-400 font-mono-num">${it.count} sold</td>
                `;
                tbody.appendChild(tr);
            });
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
                    pending: '<span class="bg-amber-400/10 text-amber-300 border border-amber-400/20 text-[10px] font-bold px-2 py-0.5 rounded-full">🟡 Pending</span>',
                    preparing: '<span class="bg-sky-400/10 text-sky-300 border border-sky-400/20 text-[10px] font-bold px-2 py-0.5 rounded-full">🔵 Preparing</span>',
                    out_for_delivery: '<span class="bg-purple-400/10 text-purple-300 border border-purple-400/20 text-[10px] font-bold px-2 py-0.5 rounded-full">🟣 Out for Delivery</span>',
                    completed: '<span class="bg-emerald-400/10 text-emerald-300 border border-emerald-400/20 text-[10px] font-bold px-2 py-0.5 rounded-full">🟢 Completed</span>',
                    cancelled: '<span class="bg-rose-500/10 text-rose-300 border border-rose-500/20 text-[10px] font-bold px-2 py-0.5 rounded-full">🔴 Cancelled</span>'
                }[order.status] || `<span class="bg-slate-700 text-slate-300 text-[10px] px-2 py-0.5 rounded">${order.status}</span>`;

                const typeBadge = {
                    delivery: '<span class="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] px-1.5 py-0.5 rounded font-semibold">🛵 WhatsApp Delivery</span>',
                    counter: '<span class="bg-blue-500/10 text-blue-400 border border-blue-500/20 text-[10px] px-1.5 py-0.5 rounded font-semibold">🛍️ Counter / POS</span>',
                    dine_in: '<span class="bg-amber-500/10 text-amber-400 border border-amber-500/20 text-[10px] px-1.5 py-0.5 rounded font-semibold">🍽️ Dine-in Table</span>'
                }[order.order_type] || '';

                const noteHtml = order.special_notes ? `
                    <div class="bg-amber-500/10 border border-amber-500/30 rounded-lg p-2 text-xs text-amber-200">
                        <strong>📝 Special Note:</strong> ${order.special_notes}
                    </div>
                ` : '';

                card.className = `bg-darkslate-900 border border-slate-800 ${statusBorder} rounded-xl p-4 shadow-sm space-y-3 flex flex-col justify-between`;

                card.innerHTML = `
                    <div class="space-y-2">
                        <div class="flex items-center justify-between">
                            <span class="font-bold text-sm text-sky-400 font-mono-num">${order.order_id}</span>
                            <div class="flex items-center space-x-1.5">
                                ${typeBadge}
                                ${statusBadge}
                            </div>
                        </div>

                        <div class="text-xs text-slate-300 space-y-1">
                            <div><strong>👤 Customer:</strong> ${order.customer_name} &nbsp;|&nbsp; <strong>📞</strong> <a href="https://wa.me/${(order.customer_phone || '').replace(/[^0-9]/g, '')}" target="_blank" class="text-emerald-400 hover:underline font-mono-num">${order.customer_phone}</a></div>
                            <div><strong>📍 Address / Table:</strong> ${order.address}</div>
                            <div class="text-[11px] text-slate-400">🕒 ${order.timestamp}</div>
                        </div>

                        <!-- Items list -->
                        <div class="bg-darkslate-950 p-2.5 rounded-lg border border-slate-800/80 text-xs text-slate-200 whitespace-pre-wrap font-sans leading-relaxed">
                            ${order.items_list || 'Order items'}
                        </div>

                        ${noteHtml}
                    </div>

                    <div class="pt-2 border-t border-slate-800/80 flex items-center justify-between">
                        <div>
                            <span class="text-xs text-slate-400">Total:</span>
                            <span class="text-base font-extrabold text-emerald-400 font-mono-num ml-1">Rs. ${order.total}</span>
                        </div>
                        <div class="flex items-center space-x-1.5">
                            <button onclick="openReceiptModalByOrderId('${order.order_id}')" class="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg transition" title="Print 80mm Receipt">
                                🖨️
                            </button>
                            <select onchange="updateOrderStatus('${order.order_id}', this.value)" class="bg-darkslate-950 border border-slate-700 text-slate-200 rounded-lg text-xs px-2 py-1 focus:outline-none focus:border-rose-500">
                                <option value="" disabled selected>Change Status...</option>
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
