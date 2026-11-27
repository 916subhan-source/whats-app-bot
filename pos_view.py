# ============================================
# 🍕 Cherry Peri Fast Food - POS & Sales Management HTML View
# Modern, Elegant, Simple & Attractive UI (Light & Dark Mode)
# ============================================

def render_pos_html() -> str:
    return """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cherry Peri — POS & Sales Management</title>
    <!-- Prevent Theme Flash -->
    <script>
        const savedTheme = localStorage.getItem('cherry_theme');
        if (savedTheme === 'light') {
            document.documentElement.classList.remove('dark');
        } else {
            document.documentElement.classList.add('dark');
        }
    </script>
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
                            200: '#fecdd3',
                            300: '#fda4af',
                            400: '#fb7185',
                            500: '#f43f5e',
                            600: '#e11d48',
                            700: '#be123c',
                            800: '#9f1239',
                            900: '#881337',
                        },
                        darkslate: {
                            700: '#334155',
                            800: '#1e293b',
                            850: '#141e33',
                            900: '#0f172a',
                            950: '#080d1a',
                        }
                    },
                    boxShadow: {
                        'glow-cherry': '0 4px 20px -2px rgba(225, 29, 72, 0.35)',
                        'glow-emerald': '0 4px 20px -2px rgba(16, 185, 129, 0.3)',
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
            transition: background-color 0.25s ease, color 0.25s ease;
        }
        html.dark body {
            background-color: #080d1a;
            color: #f1f5f9;
        }
        html:not(.dark) body {
            background-color: #f8fafc;
            color: #0f172a;
        }
        .font-mono-num {
            font-family: 'JetBrains Mono', monospace;
            font-feature-settings: "tnum";
            font-variant-numeric: tabular-nums;
        }
        /* Custom Smooth Scrollbars */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        html.dark ::-webkit-scrollbar-track {
            background: #0f172a;
        }
        html.dark ::-webkit-scrollbar-thumb {
            background: #334155;
            border-radius: 9999px;
        }
        html.dark ::-webkit-scrollbar-thumb:hover {
            background: #475569;
        }
        html:not(.dark) ::-webkit-scrollbar-track {
            background: #f1f5f9;
        }
        html:not(.dark) ::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 9999px;
        }
        html:not(.dark) ::-webkit-scrollbar-thumb:hover {
            background: #94a3b8;
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

        /* Interactive Tab Controls */
        .tab-btn.active {
            background: linear-gradient(135deg, #e11d48, #be123c);
            color: #ffffff !important;
            box-shadow: 0 4px 15px rgba(225, 29, 72, 0.4);
        }
        .cat-pill.active {
            background: linear-gradient(135deg, #e11d48, #be123c);
            color: #ffffff !important;
            box-shadow: 0 2px 10px rgba(225, 29, 72, 0.35);
        }
        .order-type-btn.active {
            background: linear-gradient(135deg, #e11d48, #be123c);
            color: #ffffff !important;
            box-shadow: 0 2px 8px rgba(225, 29, 72, 0.35);
            border-color: transparent !important;
        }
    </style>
</head>
<body class="min-h-screen flex flex-col antialiased selection:bg-rose-500 selection:text-white">

    <!-- ───────────────────────────────────────────── -->
    <!-- 🔝 Top Navbar & Header -->
    <!-- ───────────────────────────────────────────── -->
    <header class="bg-white/80 dark:bg-darkslate-900/80 backdrop-blur-xl border-b border-slate-200/80 dark:border-slate-800 sticky top-0 z-40 px-4 sm:px-6 py-3 shadow-sm transition-colors">
        <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3.5">
            <!-- Brand -->
            <div class="flex items-center space-x-3.5">
                <div class="w-11 h-11 rounded-2xl bg-gradient-to-tr from-rose-600 via-rose-500 to-amber-400 flex items-center justify-center text-2xl shadow-glow-cherry border border-rose-400/25 shrink-0 transform hover:scale-105 transition-transform duration-200">
                    🍕
                </div>
                <div>
                    <div class="flex items-center space-x-2">
                        <h1 class="text-lg sm:text-xl font-black tracking-tight text-slate-900 dark:text-white">CHERRY PERI</h1>
                        <span class="bg-rose-500/10 text-rose-600 dark:text-rose-400 text-[11px] px-2.5 py-0.5 rounded-full font-extrabold border border-rose-500/20 tracking-wide">
                            POS & SALES
                        </span>
                    </div>
                    <p class="text-xs text-slate-500 dark:text-slate-400 font-medium">Opp. Stylo, Circular Road, Dera Ismail Khan</p>
                </div>
            </div>

            <!-- Tab Navigation (Segmented Dock) -->
            <nav class="flex items-center bg-slate-100/90 dark:bg-darkslate-850 p-1.5 rounded-2xl border border-slate-200/80 dark:border-slate-800 space-x-1 shadow-inner">
                <button onclick="switchTab('pos')" id="btn-tab-pos" class="tab-btn active px-4 py-2 rounded-xl text-xs sm:text-sm font-bold text-slate-600 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white transition-all flex items-center space-x-2">
                    <span>🛒</span>
                    <span>POS Terminal</span>
                </button>
                <button onclick="switchTab('sales')" id="btn-tab-sales" class="tab-btn px-4 py-2 rounded-xl text-xs sm:text-sm font-bold text-slate-600 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white transition-all flex items-center space-x-2">
                    <span>📊</span>
                    <span>Sales & Analytics</span>
                </button>
                <button onclick="switchTab('orders')" id="btn-tab-orders" class="tab-btn px-4 py-2 rounded-xl text-xs sm:text-sm font-bold text-slate-600 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white transition-all flex items-center space-x-2">
                    <span>🍳</span>
                    <span>Kitchen Pipeline</span>
                    <span id="badge-active-count" class="bg-emerald-500 text-white font-black text-[11px] px-2 py-0.5 rounded-full shadow-sm hidden">0</span>
                </button>
            </nav>

            <!-- Quick Actions & Theme Switcher -->
            <div class="flex items-center space-x-2.5">
                <!-- Theme Toggle Button -->
                <button onclick="toggleTheme()" class="bg-slate-100 hover:bg-slate-200 dark:bg-darkslate-850 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-700/80 px-3 py-2 rounded-xl text-xs font-bold text-slate-700 dark:text-slate-200 flex items-center space-x-1.5 transition shadow-sm active:scale-95" title="Toggle Light / Dark Mode">
                    <span id="theme-toggle-icon" class="text-base">☀️</span>
                    <span id="theme-toggle-text" class="hidden md:inline">Theme</span>
                </button>

                <!-- Live digital clock -->
                <div class="text-right hidden lg:block bg-slate-50 dark:bg-darkslate-950 px-3 py-1.5 rounded-xl border border-slate-200/70 dark:border-slate-800">
                    <div id="live-clock" class="text-xs font-mono-num font-extrabold text-slate-800 dark:text-slate-200">--:--:--</div>
                    <div id="live-date" class="text-[10px] text-slate-500 dark:text-slate-400 font-semibold">PKT (UTC+5)</div>
                </div>

                <!-- Live Auto-Sync Status -->
                <div class="flex items-center space-x-2 bg-emerald-500/10 border border-emerald-500/25 text-emerald-600 dark:text-emerald-400 px-3 py-2 rounded-xl text-xs font-bold">
                    <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse shadow-glow-emerald"></span>
                    <span class="hidden sm:inline">Live Sync</span>
                </div>

                <!-- Export CSV -->
                <a href="/api/sales/export" download class="bg-slate-100 hover:bg-slate-200 dark:bg-darkslate-850 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-700/80 text-slate-700 dark:text-slate-200 px-3 py-2 rounded-xl text-xs font-bold flex items-center space-x-1.5 transition shadow-sm active:scale-95">
                    <span>📥</span>
                    <span class="hidden sm:inline">Export</span>
                </a>
            </div>
        </div>
    </header>

    <!-- ───────────────────────────────────────────── -->
    <!-- 💰 Smart KPI Cards with Trend Indicators -->
    <!-- ───────────────────────────────────────────── -->
    <div class="bg-slate-100/60 dark:bg-darkslate-900/60 border-b border-slate-200/80 dark:border-slate-800/80 px-4 sm:px-6 py-3.5 transition-colors">
        <div class="max-w-7xl mx-auto grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">

            <!-- Today's Revenue with Trend -->
            <div class="bg-white dark:bg-darkslate-850 border border-emerald-500/20 dark:border-emerald-500/25 rounded-2xl p-3.5 flex flex-col justify-between shadow-sm hover:shadow-md transition-all duration-200 col-span-1">
                <div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-1 font-semibold">
                    <span class="flex items-center space-x-1.5">
                        <span class="text-sm">💰</span>
                        <span class="uppercase tracking-wider text-[11px]">Today</span>
                    </span>
                    <span id="kpi-today-orders" class="bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 font-bold px-2 py-0.5 rounded-md font-mono-num text-[11px]">0 orders</span>
                </div>
                <div class="text-lg sm:text-xl font-black text-emerald-600 dark:text-emerald-400 font-mono-num tracking-tight" id="kpi-today-rev">Rs. 0</div>
                <div class="flex items-center justify-between mt-1">
                    <span class="text-[10px] text-slate-500 dark:text-slate-400">vs yesterday</span>
                    <span id="kpi-today-trend" class="text-[11px] font-bold"></span>
                </div>
            </div>

            <!-- Yesterday -->
            <div class="bg-white dark:bg-darkslate-850 border border-slate-200/80 dark:border-slate-800 rounded-2xl p-3.5 flex flex-col justify-between shadow-sm hover:shadow-md transition-all duration-200">
                <div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-1 font-semibold">
                    <span class="flex items-center space-x-1.5">
                        <span class="text-sm">📆</span>
                        <span class="uppercase tracking-wider text-[11px]">Yesterday</span>
                    </span>
                    <span id="kpi-yest-orders" class="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 font-bold px-2 py-0.5 rounded-md font-mono-num text-[11px]">0 orders</span>
                </div>
                <div class="text-lg sm:text-xl font-black text-slate-700 dark:text-slate-300 font-mono-num tracking-tight" id="kpi-yest-rev">Rs. 0</div>
                <div class="text-[10px] text-slate-400 dark:text-slate-500 mt-1">Previous Day</div>
            </div>

            <!-- This Week with Trend -->
            <div class="bg-white dark:bg-darkslate-850 border border-violet-500/20 dark:border-violet-500/25 rounded-2xl p-3.5 flex flex-col justify-between shadow-sm hover:shadow-md transition-all duration-200">
                <div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-1 font-semibold">
                    <span class="flex items-center space-x-1.5">
                        <span class="text-sm">📊</span>
                        <span class="uppercase tracking-wider text-[11px]">This Week</span>
                    </span>
                    <span id="kpi-week-orders" class="bg-violet-500/10 text-violet-700 dark:text-violet-300 font-bold px-2 py-0.5 rounded-md font-mono-num text-[11px]">0 orders</span>
                </div>
                <div class="text-lg sm:text-xl font-black text-violet-600 dark:text-violet-400 font-mono-num tracking-tight" id="kpi-week-rev">Rs. 0</div>
                <div class="flex items-center justify-between mt-1">
                    <span class="text-[10px] text-slate-500 dark:text-slate-400">vs last week</span>
                    <span id="kpi-week-trend" class="text-[11px] font-bold"></span>
                </div>
            </div>

            <!-- This Month with Trend -->
            <div class="bg-white dark:bg-darkslate-850 border border-amber-500/20 dark:border-amber-500/25 rounded-2xl p-3.5 flex flex-col justify-between shadow-sm hover:shadow-md transition-all duration-200">
                <div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-1 font-semibold">
                    <span class="flex items-center space-x-1.5">
                        <span class="text-sm">📅</span>
                        <span class="uppercase tracking-wider text-[11px]">This Month</span>
                    </span>
                    <span id="kpi-month-orders" class="bg-amber-500/10 text-amber-700 dark:text-amber-300 font-bold px-2 py-0.5 rounded-md font-mono-num text-[11px]">0 orders</span>
                </div>
                <div class="text-lg sm:text-xl font-black text-amber-600 dark:text-amber-400 font-mono-num tracking-tight" id="kpi-month-rev">Rs. 0</div>
                <div class="flex items-center justify-between mt-1">
                    <span class="text-[10px] text-slate-500 dark:text-slate-400">vs last month</span>
                    <span id="kpi-month-trend" class="text-[11px] font-bold"></span>
                </div>
            </div>

            <!-- Total All-Time Revenue -->
            <div class="bg-white dark:bg-darkslate-850 border border-sky-500/20 dark:border-sky-500/25 rounded-2xl p-3.5 flex flex-col justify-between shadow-sm hover:shadow-md transition-all duration-200">
                <div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-1 font-semibold">
                    <span class="flex items-center space-x-1.5">
                        <span class="text-sm">🏆</span>
                        <span class="uppercase tracking-wider text-[11px]">All-Time</span>
                    </span>
                    <span id="kpi-total-orders" class="bg-sky-500/10 text-sky-700 dark:text-sky-300 font-bold px-2 py-0.5 rounded-md font-mono-num text-[11px]">0 total</span>
                </div>
                <div class="text-lg sm:text-xl font-black text-sky-600 dark:text-sky-400 font-mono-num tracking-tight" id="kpi-total-rev">Rs. 0</div>
                <div class="text-[10px] text-slate-400 dark:text-slate-500 mt-1">WhatsApp + Counter</div>
            </div>

            <!-- AOV -->
            <div class="bg-white dark:bg-darkslate-850 border border-rose-500/20 dark:border-rose-500/25 rounded-2xl p-3.5 flex flex-col justify-between shadow-sm hover:shadow-md transition-all duration-200">
                <div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-1 font-semibold">
                    <span class="flex items-center space-x-1.5">
                        <span class="text-sm">📈</span>
                        <span class="uppercase tracking-wider text-[11px]">Avg Order</span>
                    </span>
                    <span class="bg-rose-500/10 text-rose-700 dark:text-rose-300 font-bold px-2 py-0.5 rounded-md text-[11px]">AOV</span>
                </div>
                <div class="text-lg sm:text-xl font-black text-rose-600 dark:text-rose-400 font-mono-num tracking-tight" id="kpi-avg-order">Rs. 0</div>
                <div class="flex items-center space-x-1 mt-1">
                    <span class="text-[10px] text-slate-400 dark:text-slate-500">per ticket</span>
                    <span class="text-[10px] text-slate-300 dark:text-slate-600">|</span>
                    <span id="kpi-delivery-rev" class="text-[10px] text-emerald-600 dark:text-emerald-400 font-bold font-mono-num">🛵 Rs. 0</span>
                </div>
            </div>

        </div>
        <!-- Cancelled Orders Disclaimer -->
        <div class="max-w-7xl mx-auto mt-2">
            <p class="text-[10px] text-slate-400 dark:text-slate-600 font-medium flex items-center space-x-1.5">
                <span>⚠️</span>
                <span>All revenue figures exclude cancelled orders. Trend arrows compare current vs previous period.</span>
            </p>
        </div>
    </div>

    <!-- ───────────────────────────────────────────── -->
    <!-- 🖥️ MAIN VIEW CONTAINER -->
    <!-- ───────────────────────────────────────────── -->
    <main class="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6">

        <!-- ───────────────────────────────────────────── -->
        <!-- 🛒 TAB 1: POS TERMINAL -->
        <!-- ───────────────────────────────────────────── -->
        <div id="tab-content-pos" class="space-y-5">
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-5 sm:gap-6">

                <!-- Left Column: Menu Items & Catalog (8 cols) -->
                <div class="lg:col-span-7 xl:col-span-8 space-y-4">

                    <!-- Search and Category Filters -->
                    <div class="bg-white dark:bg-darkslate-850 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-4 sm:p-5 shadow-sm space-y-3.5 transition-colors">
                        <div class="flex items-center gap-2.5">
                            <div class="relative flex-1">
                                <span class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-sm">🔍</span>
                                <input type="text" id="pos-search-input" oninput="filterMenuItems()" placeholder="Search menu (e.g. Deal 20, Zinger, Tikka, Shawarma)..."
                                       class="w-full bg-slate-50 dark:bg-darkslate-950 border border-slate-200 dark:border-slate-700/80 rounded-2xl pl-10 pr-4 py-2.5 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-rose-500 focus:ring-2 focus:ring-rose-500/20 transition shadow-inner">
                            </div>
                            <button onclick="clearSearch()" class="px-4 py-2.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-bold rounded-2xl transition active:scale-95">
                                Reset
                            </button>
                        </div>

                        <!-- Category Filter Buttons -->
                        <div class="flex items-center gap-2 overflow-x-auto pb-1.5 scrollbar-thin" id="category-pills">
                            <button onclick="filterCategory('all')" class="cat-pill active px-3.5 py-1.5 rounded-full text-xs font-bold whitespace-nowrap transition-all">
                                🌟 All Items
                            </button>
                            <button onclick="filterCategory('deals')" class="cat-pill px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-full text-xs font-bold whitespace-nowrap transition-all">
                                🌟 Deals (1-26)
                            </button>
                            <button onclick="filterCategory('pizza_regular')" class="cat-pill px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-full text-xs font-bold whitespace-nowrap transition-all">
                                🍕 Regular Pizzas
                            </button>
                            <button onclick="filterCategory('pizza_special')" class="cat-pill px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-full text-xs font-bold whitespace-nowrap transition-all">
                                🍕 Special Pizzas
                            </button>
                            <button onclick="filterCategory('burgers')" class="cat-pill px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-full text-xs font-bold whitespace-nowrap transition-all">
                                🍔 Burgers
                            </button>
                            <button onclick="filterCategory('shawarma')" class="cat-pill px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-full text-xs font-bold whitespace-nowrap transition-all">
                                🌯 Shawarma
                            </button>
                            <button onclick="filterCategory('paratha_rolls')" class="cat-pill px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-full text-xs font-bold whitespace-nowrap transition-all">
                                🌯 Paratha Rolls
                            </button>
                            <button onclick="filterCategory('fries')" class="cat-pill px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-full text-xs font-bold whitespace-nowrap transition-all">
                                🍟 Fries & Sides
                            </button>
                            <button onclick="filterCategory('drinks')" class="cat-pill px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-full text-xs font-bold whitespace-nowrap transition-all">
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
                    <div class="bg-white dark:bg-darkslate-850 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-5 shadow-lg sticky top-20 flex flex-col h-[760px] transition-colors">
                        <!-- Cart Header -->
                        <div class="flex items-center justify-between pb-3.5 border-b border-slate-200/80 dark:border-slate-800">
                            <div class="flex items-center space-x-2.5">
                                <span class="text-xl">🧾</span>
                                <div>
                                    <h3 class="font-extrabold text-slate-900 dark:text-white text-sm">Order Terminal</h3>
                                    <p class="text-[11px] text-slate-500 dark:text-slate-400">Cashier Billing Slip</p>
                                </div>
                            </div>
                            <button onclick="clearCart()" class="text-xs text-rose-600 dark:text-rose-400 hover:text-rose-700 dark:hover:text-rose-300 font-bold px-2.5 py-1 rounded-xl hover:bg-rose-50 dark:hover:bg-rose-950/30 transition">
                                Clear
                            </button>
                        </div>

                        <!-- Customer & Order Meta Inputs -->
                        <div class="py-3.5 space-y-2.5 border-b border-slate-200/80 dark:border-slate-800 text-xs">
                            <!-- Order Type Interactive Segmented Pills -->
                            <div>
                                <label class="text-[11px] text-slate-600 dark:text-slate-400 font-semibold block mb-1">Order Type</label>
                                <div class="grid grid-cols-3 gap-1.5 p-1 bg-slate-100 dark:bg-darkslate-950 rounded-2xl border border-slate-200/80 dark:border-slate-800">
                                    <button type="button" onclick="selectOrderType('counter')" id="type-pill-counter" class="order-type-btn active py-1.5 rounded-xl text-[11px] font-bold text-center transition-all">
                                        🛍️ Counter
                                    </button>
                                    <button type="button" onclick="selectOrderType('dine_in')" id="type-pill-dine_in" class="order-type-btn py-1.5 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white rounded-xl text-[11px] font-bold text-center transition-all">
                                        🍽️ Dine-in
                                    </button>
                                    <button type="button" onclick="selectOrderType('delivery')" id="type-pill-delivery" class="order-type-btn py-1.5 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white rounded-xl text-[11px] font-bold text-center transition-all">
                                        🛵 Delivery
                                    </button>
                                </div>
                                <!-- Hidden select to maintain full compatibility -->
                                <select id="cart-order-type" onchange="handleOrderTypeChange()" class="hidden">
                                    <option value="counter" selected>Counter</option>
                                    <option value="dine_in">Dine-in</option>
                                    <option value="delivery">Delivery</option>
                                </select>
                            </div>

                            <div class="grid grid-cols-2 gap-2">
                                <div>
                                    <label class="text-[11px] text-slate-600 dark:text-slate-400 font-semibold block mb-0.5">Customer Name</label>
                                    <input type="text" id="cart-customer-name" placeholder="Walk-in Customer"
                                           class="w-full bg-slate-50 dark:bg-darkslate-950 border border-slate-200 dark:border-slate-700/80 rounded-xl px-3 py-1.5 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-rose-500 focus:ring-1 focus:ring-rose-500/20">
                                </div>
                                <div>
                                    <label class="text-[11px] text-slate-600 dark:text-slate-400 font-semibold block mb-0.5">Phone Number</label>
                                    <input type="text" id="cart-customer-phone" placeholder="0300-1234567"
                                           class="w-full bg-slate-50 dark:bg-darkslate-950 border border-slate-200 dark:border-slate-700/80 rounded-xl px-3 py-1.5 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-rose-500 focus:ring-1 focus:ring-rose-500/20">
                                </div>
                            </div>

                            <div>
                                <label class="text-[11px] text-slate-600 dark:text-slate-400 font-semibold block mb-0.5" id="label-cart-address">Location / Table / Address</label>
                                <input type="text" id="cart-address" placeholder="Counter Takeaway"
                                       class="w-full bg-slate-50 dark:bg-darkslate-950 border border-slate-200 dark:border-slate-700/80 rounded-xl px-3 py-1.5 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-rose-500 focus:ring-1 focus:ring-rose-500/20">
                            </div>

                            <div>
                                <label class="text-[11px] text-amber-700 dark:text-amber-400 font-semibold block mb-0.5">📝 Special Customer Note</label>
                                <input type="text" id="cart-special-notes" placeholder="e.g. Cheese kam, Extra spicy, Kam sauce"
                                       class="w-full bg-amber-50/50 dark:bg-darkslate-950 border border-amber-500/30 dark:border-amber-500/40 rounded-xl px-3 py-1.5 text-xs text-amber-900 dark:text-amber-200 placeholder-amber-400/60 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500/20">
                            </div>
                        </div>

                        <!-- Cart Items Scroll Area -->
                        <div id="cart-items-container" class="flex-1 overflow-y-auto py-2.5 space-y-2 pr-1">
                            <div class="text-center py-16 text-slate-400 dark:text-slate-500 text-xs font-medium">
                                <span class="text-3xl block mb-2">🛒</span>
                                Cart is empty.<br>Click any item from the catalog to add!
                            </div>
                        </div>

                        <!-- Cart Totals & Place Order -->
                        <div class="pt-3 border-t border-slate-200/80 dark:border-slate-800 space-y-2">
                            <div class="flex justify-between text-xs text-slate-600 dark:text-slate-400 font-medium">
                                <span>Food Subtotal</span>
                                <span class="font-mono-num font-bold text-slate-800 dark:text-slate-200" id="cart-subtotal">Rs. 0</span>
                            </div>
                            <div class="flex justify-between text-xs text-slate-600 dark:text-slate-400 items-center font-medium">
                                <span>Delivery Fee (Rs.)</span>
                                <input type="number" id="cart-delivery-fee" value="0" min="0" oninput="calculateCartTotal()"
                                       class="w-20 bg-slate-50 dark:bg-darkslate-950 border border-slate-300 dark:border-slate-700 text-right px-2 py-0.5 rounded-lg text-xs text-slate-900 dark:text-slate-200 font-mono-num font-bold">
                            </div>
                            <div class="flex justify-between text-xs text-slate-600 dark:text-slate-400 items-center font-medium">
                                <span>Discount (Rs.)</span>
                                <input type="number" id="cart-discount" value="0" min="0" oninput="calculateCartTotal()"
                                       class="w-20 bg-slate-50 dark:bg-darkslate-950 border border-slate-300 dark:border-slate-700 text-right px-2 py-0.5 rounded-lg text-xs text-slate-900 dark:text-slate-200 font-mono-num font-bold">
                            </div>
                            <div class="flex justify-between items-center text-sm font-bold text-slate-900 dark:text-white pt-2 border-t border-slate-200/80 dark:border-slate-800">
                                <span class="text-slate-600 dark:text-slate-300">Net Total Bill:</span>
                                <span class="text-2xl font-black text-emerald-600 dark:text-emerald-400 font-mono-num" id="cart-net-total">Rs. 0</span>
                            </div>

                            <!-- Actions -->
                            <div class="grid grid-cols-2 gap-2.5 pt-2">
                                <button onclick="submitPosOrder(false)" class="bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 font-bold py-2.5 px-3 rounded-2xl text-xs transition-all flex items-center justify-center space-x-1.5 shadow-sm active:scale-95">
                                    <span>💾</span>
                                    <span>Record Order</span>
                                </button>
                                <button onclick="submitPosOrder(true)" class="bg-gradient-to-r from-rose-600 via-rose-600 to-rose-700 hover:from-rose-500 hover:to-rose-600 text-white font-black py-2.5 px-3 rounded-2xl text-xs transition-all shadow-glow-cherry flex items-center justify-center space-x-1.5 active:scale-95">
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
        <!-- 📊 TAB 2: SALES & INCOME ANALYTICS (Modern) -->
        <!-- ───────────────────────────────────────────── -->
        <div id="tab-content-sales" class="hidden space-y-5">

            <!-- Row 1: Summary Cards with Trend -->
            <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <!-- Gross Income -->
                <div class="bg-white dark:bg-darkslate-850 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-5 shadow-sm flex items-center space-x-4 transition-all hover:shadow-md">
                    <div class="w-12 h-12 rounded-2xl bg-emerald-500/10 dark:bg-emerald-500/15 text-2xl flex items-center justify-center border border-emerald-500/20 shrink-0">💰</div>
                    <div>
                        <div class="text-[11px] uppercase font-bold text-slate-500 dark:text-slate-400 tracking-wider">Gross Income</div>
                        <div class="text-xl font-black text-emerald-600 dark:text-emerald-400 font-mono-num" id="analytics-total-rev">Rs. 0</div>
                        <div class="text-[11px] text-slate-500 dark:text-slate-400">Cancelled orders excluded</div>
                    </div>
                </div>
                <!-- Delivery Channel -->
                <div class="bg-white dark:bg-darkslate-850 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-5 shadow-sm flex items-center space-x-4 transition-all hover:shadow-md">
                    <div class="w-12 h-12 rounded-2xl bg-green-500/10 dark:bg-green-500/15 text-2xl flex items-center justify-center border border-green-500/20 shrink-0">🛵</div>
                    <div>
                        <div class="text-[11px] uppercase font-bold text-slate-500 dark:text-slate-400 tracking-wider">WhatsApp</div>
                        <div class="text-xl font-black text-green-600 dark:text-green-400 font-mono-num" id="analytics-wa-rev">Rs. 0</div>
                        <div class="text-[11px] text-slate-500 dark:text-slate-400" id="analytics-wa-orders">0 orders</div>
                    </div>
                </div>
                <!-- Counter Channel -->
                <div class="bg-white dark:bg-darkslate-850 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-5 shadow-sm flex items-center space-x-4 transition-all hover:shadow-md">
                    <div class="w-12 h-12 rounded-2xl bg-sky-500/10 dark:bg-sky-500/15 text-2xl flex items-center justify-center border border-sky-500/20 shrink-0">🛍️</div>
                    <div>
                        <div class="text-[11px] uppercase font-bold text-slate-500 dark:text-slate-400 tracking-wider">Counter/Dine-in</div>
                        <div class="text-xl font-black text-sky-600 dark:text-sky-400 font-mono-num" id="analytics-counter-rev">Rs. 0</div>
                        <div class="text-[11px] text-slate-500 dark:text-slate-400" id="analytics-counter-orders">0 orders</div>
                    </div>
                </div>
                <!-- Completion Rate -->
                <div class="bg-white dark:bg-darkslate-850 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-5 shadow-sm flex items-center space-x-4 transition-all hover:shadow-md">
                    <div class="w-12 h-12 rounded-2xl bg-amber-500/10 dark:bg-amber-500/15 text-2xl flex items-center justify-center border border-amber-500/20 shrink-0">🎯</div>
                    <div>
                        <div class="text-[11px] uppercase font-bold text-slate-500 dark:text-slate-400 tracking-wider">Success Rate</div>
                        <div class="text-xl font-black text-amber-600 dark:text-amber-400 font-mono-num" id="analytics-completion-rate">100%</div>
                        <div class="text-[11px] text-slate-500 dark:text-slate-400" id="analytics-active-ratio">0 active</div>
                    </div>
                </div>
            </div>

            <!-- Row 2: Main 30-day Revenue Chart + Channel Donut -->
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
                <!-- 30-Day Area+Bar Revenue -->
                <div class="lg:col-span-8 bg-white dark:bg-darkslate-850 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-5 shadow-sm space-y-3 transition-colors">
                    <div class="flex flex-wrap items-center justify-between gap-2">
                        <div>
                            <h3 class="font-extrabold text-slate-900 dark:text-white text-sm flex items-center space-x-2">
                                <span>📈</span><span>30-Day Revenue & Orders Trend</span>
                            </h3>
                            <p class="text-xs text-slate-500 dark:text-slate-400">Daily PKR revenue (bars) + order count line — cancelled excluded</p>
                        </div>
                        <span class="text-xs text-rose-600 dark:text-rose-400 bg-rose-500/10 border border-rose-500/20 px-3 py-1 rounded-xl font-bold">🔴 Live</span>
                    </div>
                    <div class="h-72 w-full"><canvas id="salesTrendChart"></canvas></div>
                </div>
                <!-- Channel Donut -->
                <div class="lg:col-span-4 bg-white dark:bg-darkslate-850 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-5 shadow-sm space-y-3 flex flex-col transition-colors">
                    <div>
                        <h3 class="font-extrabold text-slate-900 dark:text-white text-sm flex items-center space-x-2">
                            <span>🥧</span><span>Revenue by Channel</span>
                        </h3>
                        <p class="text-xs text-slate-500 dark:text-slate-400">WhatsApp vs Counter vs Dine-in</p>
                    </div>
                    <div class="flex-1 flex items-center justify-center min-h-[180px]">
                        <canvas id="channelDonutChart"></canvas>
                    </div>
                    <div id="channel-donut-legend" class="grid grid-cols-1 gap-1.5 text-xs pt-2 border-t border-slate-200/80 dark:border-slate-800"></div>
                </div>
            </div>

            <!-- Row 3: Hourly Peak + This Week vs Last Week -->
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
                <!-- Today's Hourly Orders (Peak Hours) -->
                <div class="lg:col-span-5 bg-white dark:bg-darkslate-850 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-5 shadow-sm space-y-3 transition-colors">
                    <div>
                        <h3 class="font-extrabold text-slate-900 dark:text-white text-sm flex items-center space-x-2">
                            <span>⏰</span><span>Today's Peak Hours</span>
                        </h3>
                        <p class="text-xs text-slate-500 dark:text-slate-400">Orders by hour today (PKT) — find your busiest times</p>
                    </div>
                    <div class="h-52 w-full"><canvas id="hourlyChart"></canvas></div>
                </div>
                <!-- This Week vs Last Week Comparison -->
                <div class="lg:col-span-7 bg-white dark:bg-darkslate-850 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-5 shadow-sm space-y-3 transition-colors">
                    <div>
                        <h3 class="font-extrabold text-slate-900 dark:text-white text-sm flex items-center space-x-2">
                            <span>📊</span><span>This Week vs Last Week</span>
                        </h3>
                        <p class="text-xs text-slate-500 dark:text-slate-400">Day-by-day revenue comparison — green = this week, blue = last week</p>
                    </div>
                    <div class="h-52 w-full"><canvas id="weekCompareChart"></canvas></div>
                </div>
            </div>

            <!-- Row 4: Order Status Donut + Top Items Leaderboard -->
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
                <!-- Order Status Distribution -->
                <div class="lg:col-span-5 bg-white dark:bg-darkslate-850 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-5 shadow-sm space-y-3 transition-colors">
                    <div>
                        <h3 class="font-extrabold text-slate-900 dark:text-white text-sm flex items-center space-x-2">
                            <span>🍳</span><span>Order Status Breakdown</span>
                        </h3>
                        <p class="text-xs text-slate-500 dark:text-slate-400">Pipeline flow — completed, preparing, pending, cancelled</p>
                    </div>
                    <div class="h-44 w-full flex items-center justify-center">
                        <canvas id="statusDonutChart"></canvas>
                    </div>
                    <div id="status-bars-container" class="space-y-2 text-xs"></div>
                </div>

                <!-- Top 10 Items Leaderboard -->
                <div class="lg:col-span-7 bg-white dark:bg-darkslate-850 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-5 shadow-sm space-y-3 transition-colors">
                    <div class="flex items-center justify-between">
                        <div>
                            <h3 class="font-extrabold text-slate-900 dark:text-white text-sm flex items-center space-x-2">
                                <span>🏆</span><span>Top Selling Items</span>
                            </h3>
                            <p class="text-xs text-slate-500 dark:text-slate-400">Best-performing menu items by quantity sold</p>
                        </div>
                        <span class="text-xs text-slate-500 dark:text-slate-400 font-semibold">Rank by Qty</span>
                    </div>
                    <div class="space-y-2 max-h-72 overflow-y-auto pr-1" id="top-items-container"></div>
                </div>
            </div>

            <!-- Row 5: Sales Ledger Table -->
            <div class="bg-white dark:bg-darkslate-850 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-5 shadow-sm space-y-3.5 transition-colors">
                <div class="flex items-center justify-between flex-wrap gap-2">
                    <div>
                        <h3 class="font-extrabold text-slate-900 dark:text-white text-sm flex items-center space-x-2">
                            <span>📑</span><span>Sales Ledger — All Transactions</span>
                        </h3>
                        <p class="text-xs text-slate-500 dark:text-slate-400">Last 50 orders — <span class="text-rose-500 font-bold">cancelled orders shown in red, excluded from totals</span></p>
                    </div>
                    <a href="/api/sales/export" download class="bg-emerald-600 hover:bg-emerald-700 text-white font-black py-2 px-4 rounded-xl text-xs flex items-center space-x-1.5 transition shadow-md active:scale-95">
                        <span>📥</span><span>Export CSV</span>
                    </a>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs">
                        <thead>
                            <tr class="text-slate-500 dark:text-slate-400 border-b border-slate-200/80 dark:border-slate-800 font-bold uppercase tracking-wider text-[11px]">
                                <th class="py-2.5 px-2">Order ID</th>
                                <th class="py-2.5 px-2">Time</th>
                                <th class="py-2.5 px-2">Customer</th>
                                <th class="py-2.5 px-2">Channel</th>
                                <th class="py-2.5 px-2">Items</th>
                                <th class="py-2.5 px-2 text-right">Total</th>
                                <th class="py-2.5 px-2 text-center">Status</th>
                            </tr>
                        </thead>
                        <tbody id="sales-ledger-tbody" class="divide-y divide-slate-200/80 dark:divide-slate-800/60 font-medium"></tbody>
                    </table>
                </div>
            </div>

        </div>

        <!-- ───────────────────────────────────────────── -->
        <!-- 🍳 TAB 3: KITCHEN & ORDERS PIPELINE -->
        <!-- ───────────────────────────────────────────── -->
        <div id="tab-content-orders" class="hidden space-y-4">

            <!-- Filter Status Bar -->
            <div class="bg-white dark:bg-darkslate-850 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-3 sm:p-4 flex flex-wrap items-center justify-between gap-3 shadow-sm transition-colors">
                <div class="flex items-center space-x-2 overflow-x-auto pb-1" id="order-status-filters">
                    <button onclick="filterOrderStatus('all')" class="status-filter-btn active px-3.5 py-1.5 bg-rose-600 text-white rounded-full text-xs font-bold whitespace-nowrap shadow-sm">
                        All Orders
                    </button>
                    <button onclick="filterOrderStatus('pending')" class="status-filter-btn px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-amber-700 dark:text-amber-400 rounded-full text-xs font-bold whitespace-nowrap transition">
                        🟡 Pending
                    </button>
                    <button onclick="filterOrderStatus('preparing')" class="status-filter-btn px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-sky-700 dark:text-sky-400 rounded-full text-xs font-bold whitespace-nowrap transition">
                        🔵 Preparing
                    </button>
                    <button onclick="filterOrderStatus('out_for_delivery')" class="status-filter-btn px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-purple-700 dark:text-purple-400 rounded-full text-xs font-bold whitespace-nowrap transition">
                        🟣 Out for Delivery
                    </button>
                    <button onclick="filterOrderStatus('completed')" class="status-filter-btn px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-emerald-700 dark:text-emerald-400 rounded-full text-xs font-bold whitespace-nowrap transition">
                        🟢 Completed
                    </button>
                    <button onclick="filterOrderStatus('cancelled')" class="status-filter-btn px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-rose-700 dark:text-rose-400 rounded-full text-xs font-bold whitespace-nowrap transition">
                        🔴 Cancelled
                    </button>
                </div>

                <div class="text-xs text-slate-500 dark:text-slate-400 font-semibold">
                    Showing <span id="orders-count-label" class="text-slate-900 dark:text-white font-bold font-mono-num">0</span> orders
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
        <div class="bg-white text-slate-900 rounded-3xl max-w-sm w-full p-6 shadow-2xl relative space-y-4 max-h-[90vh] overflow-y-auto">
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
                <button onclick="closeReceiptModal()" class="flex-1 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded-xl transition">
                    Close
                </button>
                <button onclick="window.print()" class="flex-1 py-2.5 bg-rose-600 hover:bg-rose-700 text-white font-black text-xs rounded-xl shadow-md transition flex items-center justify-center space-x-1.5 active:scale-95">
                    <span>🖨️</span>
                    <span>Print Receipt</span>
                </button>
            </div>
        </div>
    </div>

    <!-- ───────────────────────────────────────────── -->
    <!-- ⚡ JAVASCRIPT LOGIC & THEME SWITCHER -->
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
            initTheme();
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

        // ─────────────────────────────────────────────
        // ☀️ / 🌙 Theme Toggle & Persistence
        // ─────────────────────────────────────────────
        function initTheme() {
            const saved = localStorage.getItem('cherry_theme');
            const isDark = saved !== 'light';
            updateThemeUI(isDark);
        }

        function toggleTheme() {
            const isDark = document.documentElement.classList.contains('dark');
            const nextDark = !isDark;
            if (nextDark) {
                document.documentElement.classList.add('dark');
                localStorage.setItem('cherry_theme', 'dark');
            } else {
                document.documentElement.classList.remove('dark');
                localStorage.setItem('cherry_theme', 'light');
            }
            updateThemeUI(nextDark);
            if (!document.getElementById('tab-content-sales').classList.contains('hidden')) {
                renderSalesCharts();
            }
        }

        function updateThemeUI(isDark) {
            const icon = document.getElementById('theme-toggle-icon');
            const text = document.getElementById('theme-toggle-text');
            if (icon) icon.innerText = isDark ? '🌙' : '☀️';
            if (text) text.innerText = isDark ? 'Dark' : 'Light';
        }

        // ─────────────────────────────────────────────
        // 🕒 Live Digital Clock
        // ─────────────────────────────────────────────
        function formatPakistanTime(dateOrStr) {
            if (!dateOrStr) return '-';
            let d = new Date(dateOrStr);
            if (isNaN(d.getTime())) {
                let isoStr = String(dateOrStr).trim().replace(' ', 'T');
                if (!isoStr.endsWith('Z') && !isoStr.includes('+')) {
                    isoStr += 'Z';
                }
                d = new Date(isoStr);
            }
            if (!isNaN(d.getTime())) {
                return d.toLocaleString('en-US', {
                    timeZone: 'Asia/Karachi',
                    month: 'short',
                    day: 'numeric',
                    hour: 'numeric',
                    minute: '2-digit',
                    hour12: true
                });
            }
            return dateOrStr;
        }

        function startClock() {
            function update() {
                const now = new Date();
                const clockEl = document.getElementById('live-clock');
                const dateEl = document.getElementById('live-date');
                if (clockEl) {
                    clockEl.innerText = now.toLocaleTimeString('en-US', {
                        timeZone: 'Asia/Karachi',
                        hour: 'numeric',
                        minute: '2-digit',
                        second: '2-digit',
                        hour12: true
                    });
                }
                if (dateEl) {
                    dateEl.innerText = now.toLocaleDateString('en-US', {
                        timeZone: 'Asia/Karachi',
                        weekday: 'short',
                        month: 'short',
                        day: 'numeric'
                    }) + ' (PKT)';
                }
            }
            update();
            setInterval(update, 1000);
        }

        // ─────────────────────────────────────────────
        // 🗂️ Tab Switching Logic
        // ─────────────────────────────────────────────
        function switchTab(tab) {
            ['pos', 'sales', 'orders'].forEach(t => {
                const btn = document.getElementById(`btn-tab-${t}`);
                const content = document.getElementById(`tab-content-${t}`);
                if (t === tab) {
                    btn?.classList.add('active');
                    content?.classList.remove('hidden');
                } else {
                    btn?.classList.remove('active');
                    content?.classList.add('hidden');
                }
            });

            if (tab === 'sales') {
                setTimeout(renderSalesCharts, 100);
            }
        }

        // ─────────────────────────────────────────────
        // 🛍️ Order Type Selector
        // ─────────────────────────────────────────────
        function selectOrderType(type) {
            ['counter', 'dine_in', 'delivery'].forEach(t => {
                const btn = document.getElementById(`type-pill-${t}`);
                if (t === type) {
                    btn?.classList.add('active');
                    btn?.classList.remove('text-slate-600', 'dark:text-slate-400');
                } else {
                    btn?.classList.remove('active');
                    btn?.classList.add('text-slate-600', 'dark:text-slate-400');
                }
            });

            const sel = document.getElementById('cart-order-type');
            if (sel) sel.value = type;

            const addrInput = document.getElementById('cart-address');
            const addrLabel = document.getElementById('label-cart-address');
            if (type === 'dine_in') {
                addrLabel.innerText = 'Table Number';
                addrInput.placeholder = 'e.g. Table 4';
                if (!addrInput.value || addrInput.value === 'Counter Takeaway') addrInput.value = '';
            } else if (type === 'delivery') {
                addrLabel.innerText = 'Delivery Street / Mohalla';
                addrInput.placeholder = 'e.g. Circular Road / Stylo Center';
                if (!addrInput.value || addrInput.value === 'Counter Takeaway') addrInput.value = '';
            } else {
                addrLabel.innerText = 'Location / Table / Address';
                addrInput.placeholder = 'Counter Takeaway';
                if (!addrInput.value) addrInput.value = 'Counter Takeaway';
            }
        }

        function handleOrderTypeChange() {
            const sel = document.getElementById('cart-order-type');
            if (sel) selectOrderType(sel.value);
        }

        // ─────────────────────────────────────────────
        // 🍕 Menu Catalog & POS Logic
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
            document.querySelectorAll('#category-pills .cat-pill').forEach(b => {
                b.classList.remove('active');
            });
            event.target.classList.add('active');
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
            if (category && category.includes('pizza')) return '🍕';
            if (category === 'burgers') return '🍔';
            if (category === 'shawarma' || category === 'paratha_rolls') return '🌯';
            if (category === 'fries') return '🍟';
            if (category === 'drinks') return '🥤';
            return '🍽️';
        }

        function renderMenuItems() {
            const grid = document.getElementById('pos-items-grid');
            if (!grid) return;
            grid.innerHTML = '';

            let filtered = allMenuItems;
            if (currentCategory !== 'all') {
                filtered = filtered.filter(i => i.category === currentCategory);
            }
            if (currentSearch) {
                filtered = filtered.filter(i => i.name.toLowerCase().includes(currentSearch));
            }

            if (filtered.length === 0) {
                grid.innerHTML = `<div class="col-span-full py-20 text-center text-slate-400 dark:text-slate-500 text-sm font-medium">No items found matching "${currentSearch}".</div>`;
                return;
            }

            filtered.forEach(item => {
                const card = document.createElement('div');
                card.className = "bg-white dark:bg-darkslate-850 border border-slate-200/80 dark:border-slate-800 hover:border-rose-500/40 dark:hover:border-rose-500/40 rounded-2xl p-4 shadow-sm hover:shadow-md transition-all duration-200 flex flex-col justify-between group hover:-translate-y-0.5";

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
                        <div class="flex items-start justify-between gap-1.5 mb-1.5">
                            <div class="flex items-center space-x-2">
                                <span class="text-lg p-1.5 bg-slate-50 dark:bg-darkslate-950 rounded-xl border border-slate-200/60 dark:border-slate-800">${icon}</span>
                                <h4 class="text-xs font-bold text-slate-900 dark:text-slate-100 group-hover:text-rose-600 dark:group-hover:text-rose-400 transition-colors leading-snug">${title}</h4>
                            </div>
                        </div>
                        ${subtext ? `<p class="text-[11px] text-slate-500 dark:text-slate-400 mb-2 leading-tight">${subtext}</p>` : ''}
                        <span class="text-[10px] text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-slate-800/80 px-2.5 py-0.5 rounded-full font-semibold">${item.category_name || item.category}</span>
                    </div>
                    <div class="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between">
                        <span class="text-sm font-black text-emerald-600 dark:text-emerald-400 font-mono-num">Rs. ${item.price}</span>
                        <button onclick="addToCart('${item.id}', '${escapeHtml(item.name)}', ${item.price})"
                                class="bg-gradient-to-r from-rose-600 to-rose-700 hover:from-rose-500 hover:to-rose-600 active:scale-95 text-white font-extrabold text-xs px-3.5 py-1.5 rounded-xl transition-all shadow-sm flex items-center space-x-1">
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
            selectOrderType('counter');
            renderCart();
        }

        function renderCart() {
            const container = document.getElementById('cart-items-container');
            if (!container) return;
            container.innerHTML = '';

            if (cart.length === 0) {
                container.innerHTML = `
                    <div class="text-center py-16 text-slate-400 dark:text-slate-500 text-xs font-medium">
                        <span class="text-3xl block mb-2">🛒</span>
                        Cart is empty.<br>Click any item from the catalog to add!
                    </div>
                `;
                calculateCartTotal();
                return;
            }

            cart.forEach(item => {
                const row = document.createElement('div');
                row.className = "bg-slate-50 dark:bg-darkslate-950 border border-slate-200/80 dark:border-slate-800 rounded-2xl p-2.5 flex items-center justify-between text-xs";
                const totalItemPrice = item.price * item.qty;

                row.innerHTML = `
                    <div class="flex-1 pr-2 min-w-0">
                        <div class="font-bold text-slate-900 dark:text-slate-100 truncate">${item.name}</div>
                        <div class="text-[11px] text-slate-500 dark:text-slate-400 font-mono-num">Rs. ${item.price} × ${item.qty} = <span class="text-emerald-600 dark:text-emerald-400 font-bold">Rs. ${totalItemPrice}</span></div>
                    </div>
                    <div class="flex items-center space-x-1.5 shrink-0">
                        <button onclick="updateCartQty('${item.id}', -1)" class="w-6 h-6 rounded-lg bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 font-bold flex items-center justify-center transition">-</button>
                        <span class="font-mono-num font-bold text-xs w-4 text-center text-slate-900 dark:text-white">${item.qty}</span>
                        <button onclick="updateCartQty('${item.id}', 1)" class="w-6 h-6 rounded-lg bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 font-bold flex items-center justify-center transition">+</button>
                        <button onclick="removeCartItem('${item.id}')" class="text-rose-600 dark:text-rose-400 hover:text-rose-700 ml-1.5 font-bold text-sm">✕</button>
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

            document.getElementById('cart-subtotal').innerText = `Rs. ${subtotal.toLocaleString()}`;
            document.getElementById('cart-net-total').innerText = `Rs. ${net.toLocaleString()}`;
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

            const itemsList = cart.map(i => `• ${i.qty}x ${i.name} — Rs. ${i.price * i.qty}`).join(String.fromCharCode(10));

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

        function trendBadge(current, previous) {
            if (!previous || previous === 0) return '<span class="text-slate-400 text-[10px]">— new</span>';
            const pct = Math.round(((current - previous) / previous) * 100);
            const up = pct >= 0;
            const color = up ? 'text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 border-emerald-500/25' : 'text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/40 border-rose-500/25';
            const arrow = up ? '↑' : '↓';
            return `<span class="${color} text-[11px] font-extrabold px-2 py-0.5 rounded-full border inline-flex items-center space-x-0.5"><span>${arrow}</span><span>${Math.abs(pct)}%</span></span>`;
        }

        function updateKPICards(stats) {
            document.getElementById('kpi-today-rev').innerText = `Rs. ${(stats.today_revenue || 0).toLocaleString()}`;
            document.getElementById('kpi-today-orders').innerText = `${stats.today_orders || 0} orders`;
            const todayTrendEl = document.getElementById('kpi-today-trend');
            if (todayTrendEl) todayTrendEl.innerHTML = trendBadge(stats.today_revenue || 0, stats.yesterday_revenue || 0);

            document.getElementById('kpi-yest-rev').innerText = `Rs. ${(stats.yesterday_revenue || 0).toLocaleString()}`;
            document.getElementById('kpi-yest-orders').innerText = `${stats.yesterday_orders || 0} orders`;

            const weekRevEl = document.getElementById('kpi-week-rev');
            const weekOrdEl = document.getElementById('kpi-week-orders');
            const weekTrendEl = document.getElementById('kpi-week-trend');
            if (weekRevEl) weekRevEl.innerText = `Rs. ${(stats.week_revenue || 0).toLocaleString()}`;
            if (weekOrdEl) weekOrdEl.innerText = `${stats.week_orders || 0} orders`;
            if (weekTrendEl) weekTrendEl.innerHTML = trendBadge(stats.week_revenue || 0, stats.last_week_revenue || 0);

            document.getElementById('kpi-month-rev').innerText = `Rs. ${(stats.month_revenue || 0).toLocaleString()}`;
            document.getElementById('kpi-month-orders').innerText = `${stats.month_orders || 0} orders`;
            const monthTrendEl = document.getElementById('kpi-month-trend');
            if (monthTrendEl) monthTrendEl.innerHTML = trendBadge(stats.month_revenue || 0, stats.last_month_revenue || 0);

            document.getElementById('kpi-total-rev').innerText = `Rs. ${(stats.total_revenue || 0).toLocaleString()}`;
            document.getElementById('kpi-total-orders').innerText = `${stats.total_orders || 0} total`;

            document.getElementById('kpi-avg-order').innerText = `Rs. ${(stats.avg_order_value || 0).toLocaleString()}`;

            // Channel Breakdown
            const ch = stats.channel_stats || {};
            const delRev = ch.delivery?.revenue || 0;
            const counterRev = (ch.counter?.revenue || 0) + (ch.dine_in?.revenue || 0);
            const kpiDelEl = document.getElementById('kpi-delivery-rev');
            const kpiCtrEl = document.getElementById('kpi-counter-rev');
            if (kpiDelEl) kpiDelEl.innerText = `🛵 Rs. ${delRev.toLocaleString()}`;
            if (kpiCtrEl) kpiCtrEl.innerText = `Rs. ${counterRev.toLocaleString()}`;

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

            // Top items leaderboard
            const topContainer = document.getElementById('top-items-container');
            topContainer.innerHTML = '';
            const topList = stats.top_items || [];
            if (topList.length === 0) {
                topContainer.innerHTML = `<div class="py-6 text-center text-slate-400 dark:text-slate-500 text-xs">No item sales recorded yet.</div>`;
            } else {
                const maxCount = Math.max(...topList.map(t => t.count), 1);
                topList.forEach((it, idx) => {
                    const pct = Math.round((it.count / maxCount) * 100);
                    const medal = idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : `#${idx + 1}`;
                    const row = document.createElement('div');
                    row.className = "bg-slate-50 dark:bg-darkslate-950 p-3 rounded-2xl border border-slate-200/80 dark:border-slate-800 space-y-1.5";
                    row.innerHTML = `
                        <div class="flex items-center justify-between text-xs font-semibold">
                            <span class="flex items-center space-x-2 text-slate-800 dark:text-slate-200">
                                <span class="font-extrabold text-amber-500 w-5 text-center">${medal}</span>
                                <span>${it.name}</span>
                            </span>
                            <span class="font-bold text-emerald-600 dark:text-emerald-400 font-mono-num">${it.count} sold</span>
                        </div>
                        <div class="w-full bg-slate-200 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
                            <div class="bg-gradient-to-r from-rose-500 to-amber-400 h-full rounded-full transition-all duration-500" style="width: ${pct}%"></div>
                        </div>
                    `;
                    topContainer.appendChild(row);
                });
            }

            // Status Progress Bars
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
                el.className = "space-y-1.5";
                el.innerHTML = `
                    <div class="flex justify-between text-xs font-semibold">
                        <span class="text-slate-700 dark:text-slate-300">${sm.label}</span>
                        <span class="font-mono-num text-slate-900 dark:text-slate-200 font-bold">${sm.count} (${pct}%)</span>
                    </div>
                    <div class="w-full bg-slate-200 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div class="bg-gradient-to-r ${sm.color} h-full rounded-full transition-all duration-500" style="width: ${pct}%"></div>
                    </div>
                `;
                statusContainer.appendChild(el);
            });

            // Sales Ledger Table
            const tbody = document.getElementById('sales-ledger-tbody');
            tbody.innerHTML = '';
            (allOrders || []).slice(0, 30).forEach(order => {
                const tr = document.createElement('tr');
                tr.className = "hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors";
                const channelBadge = {
                    delivery: '<span class="text-emerald-600 dark:text-emerald-400 font-bold">🛵 WhatsApp</span>',
                    counter: '<span class="text-blue-600 dark:text-blue-400 font-bold">🛍️ Counter</span>',
                    dine_in: '<span class="text-amber-600 dark:text-amber-400 font-bold">🍽️ Dine-in</span>'
                }[order.order_type] || order.order_type;

                const statusColor = {
                    completed: 'text-emerald-700 dark:text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
                    preparing: 'text-sky-700 dark:text-sky-400 bg-sky-500/10 border-sky-500/20',
                    pending: 'text-amber-700 dark:text-amber-400 bg-amber-500/10 border-amber-500/20',
                    out_for_delivery: 'text-purple-700 dark:text-purple-400 bg-purple-500/10 border-purple-500/20',
                    cancelled: 'text-rose-700 dark:text-rose-400 bg-rose-500/10 border-rose-500/20'
                }[order.status] || 'text-slate-500';

                const rawItems = order.items_list || order.slip || '';
                const itemsSummary = rawItems
                    .split(String.fromCharCode(10)).join(', ')
                    .replace(/•/g, '')
                    .replace(/— Rs[^,]*/g, '')
                    .trim();

                tr.innerHTML = `
                    <td class="py-3 px-2 font-mono-num font-bold text-sky-600 dark:text-sky-400">${order.order_id}</td>
                    <td class="py-3 px-2 text-slate-500 dark:text-slate-400 text-[11px] font-mono-num">${formatPakistanTime(order.formatted_time || order.timestamp)}</td>
                    <td class="py-3 px-2 text-slate-900 dark:text-slate-200 font-semibold">${order.customer_name}</td>
                    <td class="py-3 px-2 text-[11px] font-semibold">${channelBadge}</td>
                    <td class="py-3 px-2 text-slate-600 dark:text-slate-300 max-w-xs truncate">${itemsSummary || 'Order Items'}</td>
                    <td class="py-3 px-2 text-right font-mono-num font-extrabold text-emerald-600 dark:text-emerald-400">Rs. ${order.total}</td>
                    <td class="py-3 px-2 text-center">
                        <span class="text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${statusColor}">
                            ${order.status}
                        </span>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        // Chart instances
        let hourlyChartInstance = null;
        let weekCompareChartInstance = null;
        let channelDonutChartInstance = null;
        let statusDonutChartInstance = null;

        function mkTooltip(isDark) {
            return {
                backgroundColor: isDark ? '#0f172a' : '#ffffff',
                titleColor: isDark ? '#ffffff' : '#0f172a',
                bodyColor: isDark ? '#cbd5e1' : '#334155',
                borderColor: isDark ? '#334155' : '#cbd5e1',
                borderWidth: 1,
                padding: 10,
                cornerRadius: 8
            };
        }

        function renderSalesCharts() {
            if (!salesStats) return;

            const isDark = document.documentElement.classList.contains('dark');
            const gridColor = isDark ? 'rgba(51,65,85,0.25)' : 'rgba(203,213,225,0.5)';
            const tickColor = isDark ? '#94a3b8' : '#475569';
            const legendColor = isDark ? '#f1f5f9' : '#0f172a';
            const bgPanel = isDark ? '#0f172a' : '#ffffff';

            // ── 1. 30-Day Revenue Area+Bar Chart ─────────────────────────
            const trendCtx = document.getElementById('salesTrendChart')?.getContext('2d');
            if (trendCtx && salesStats.daily_breakdown) {
                const labels = (salesStats.daily_breakdown || []).map(d => {
                    const parts = (d.sale_date || d.date || '').split('-');
                    return parts.length >= 3 ? `${parts[2]}/${parts[1]}` : (d.sale_date || d.date || '');
                });
                const revenues = (salesStats.daily_breakdown || []).map(d => d.revenue || 0);
                const orders = (salesStats.daily_breakdown || []).map(d => d.order_count || 0);

                if (salesChartInstance) salesChartInstance.destroy();

                const grad = trendCtx.createLinearGradient(0, 0, 0, 280);
                grad.addColorStop(0, isDark ? 'rgba(225,29,72,0.5)' : 'rgba(225,29,72,0.3)');
                grad.addColorStop(1, 'rgba(225,29,72,0)');

                salesChartInstance = new Chart(trendCtx, {
                    type: 'bar',
                    data: {
                        labels,
                        datasets: [
                            {
                                label: 'Revenue (Rs.)',
                                data: revenues,
                                backgroundColor: grad,
                                borderColor: '#e11d48',
                                borderWidth: 2,
                                borderRadius: 6,
                                yAxisID: 'y'
                            },
                            {
                                label: 'Orders',
                                data: orders,
                                type: 'line',
                                borderColor: '#10b981',
                                backgroundColor: '#10b981',
                                tension: 0.4,
                                pointRadius: 3,
                                pointHoverRadius: 6,
                                borderWidth: 2.5,
                                fill: false,
                                yAxisID: 'y1'
                            }
                        ]
                    },
                    options: {
                        responsive: true, maintainAspectRatio: false,
                        interaction: { mode: 'index', intersect: false },
                        scales: {
                            x: { grid: { color: gridColor }, ticks: { color: tickColor, font: { size: 10, weight: '600' }, maxTicksLimit: 15 } },
                            y: {
                                position: 'left', grid: { color: gridColor },
                                ticks: { color: tickColor, font: { size: 10, family: 'JetBrains Mono', weight: '700' }, callback: v => 'Rs.' + (v >= 1000 ? (v/1000).toFixed(1)+'k' : v) }
                            },
                            y1: {
                                position: 'right', grid: { drawOnChartArea: false },
                                ticks: { color: '#10b981', font: { size: 10, weight: '700' }, stepSize: 1 }
                            }
                        },
                        plugins: {
                            legend: { labels: { color: legendColor, font: { size: 11, weight: '700' }, boxWidth: 12, padding: 16 } },
                            tooltip: { ...mkTooltip(isDark), callbacks: {
                                label: ctx => ctx.dataset.yAxisID === 'y' ? ` Revenue: Rs. ${ctx.parsed.y.toLocaleString()}` : ` Orders: ${ctx.parsed.y}`
                            }}
                        }
                    }
                });
            }

            // ── 2. Channel Donut ──────────────────────────────────────────
            const chCtx = document.getElementById('channelDonutChart')?.getContext('2d');
            if (chCtx) {
                const ch = salesStats.channel_stats || {};
                const chLabels = ['🛵 Delivery', '🛍️ Counter', '🍽️ Dine-in'];
                const chValues = [ch.delivery?.revenue || 0, ch.counter?.revenue || 0, ch.dine_in?.revenue || 0];
                const chColors = ['#10b981', '#38bdf8', '#f59e0b'];
                if (channelDonutChartInstance) channelDonutChartInstance.destroy();
                channelDonutChartInstance = new Chart(chCtx, {
                    type: 'doughnut',
                    data: { labels: chLabels, datasets: [{ data: chValues, backgroundColor: chColors, borderColor: isDark ? '#0f172a' : '#fff', borderWidth: 3, hoverOffset: 8 }] },
                    options: { responsive: true, maintainAspectRatio: false, cutout: '70%',
                        plugins: { legend: { display: false }, tooltip: { ...mkTooltip(isDark), callbacks: { label: ctx => ` Rs. ${ctx.parsed.toLocaleString()}` } } }
                    }
                });
                const legEl = document.getElementById('channel-donut-legend');
                if (legEl) {
                    legEl.innerHTML = '';
                    chLabels.forEach((lb, i) => {
                        const pct = chValues.reduce((a,b) => a+b, 0) > 0 ? Math.round((chValues[i] / chValues.reduce((a,b) => a+b, 0)) * 100) : 0;
                        legEl.innerHTML += `<div class="flex items-center justify-between bg-slate-50 dark:bg-darkslate-950 px-3 py-2 rounded-xl border border-slate-200/80 dark:border-slate-800"><span class="flex items-center space-x-2"><span class="w-2.5 h-2.5 rounded-full" style="background:${chColors[i]}"></span><span class="text-slate-700 dark:text-slate-300 font-semibold">${lb}</span></span><span class="font-extrabold text-slate-900 dark:text-white font-mono-num">Rs. ${chValues[i].toLocaleString()} <span class="text-slate-400 font-normal">(${pct}%)</span></span></div>`;
                    });
                }
            }

            // ── 3. Today's Hourly Peak Chart ─────────────────────────────
            const hourCtx = document.getElementById('hourlyChart')?.getContext('2d');
            if (hourCtx) {
                const hourly = salesStats.hourly_breakdown || [];
                const hourLabels = Array.from({length: 24}, (_, i) => { const h = i % 12 || 12; return `${h}${i < 12 ? 'am' : 'pm'}`; });
                const hourOrders = Array(24).fill(0);
                hourly.forEach(h => { if (h.hour >= 0 && h.hour < 24) hourOrders[h.hour] = h.order_count; });
                const maxH = Math.max(...hourOrders, 1);
                const hourColors = hourOrders.map(v => v === maxH && maxH > 0 ? '#e11d48' : (isDark ? 'rgba(148,163,184,0.5)' : 'rgba(148,163,184,0.6)'));
                if (hourlyChartInstance) hourlyChartInstance.destroy();
                hourlyChartInstance = new Chart(hourCtx, {
                    type: 'bar',
                    data: { labels: hourLabels, datasets: [{ label: 'Orders', data: hourOrders, backgroundColor: hourColors, borderRadius: 4 }] },
                    options: {
                        responsive: true, maintainAspectRatio: false,
                        scales: {
                            x: { grid: { display: false }, ticks: { color: tickColor, font: { size: 9, weight: '600' }, maxRotation: 0 } },
                            y: { grid: { color: gridColor }, ticks: { color: tickColor, font: { size: 10 }, stepSize: 1 }, beginAtZero: true }
                        },
                        plugins: {
                            legend: { display: false },
                            tooltip: { ...mkTooltip(isDark), callbacks: { title: ctx => `Hour: ${ctx[0].label}`, label: ctx => ` ${ctx.parsed.y} orders` } }
                        }
                    }
                });
            }

            // ── 4. This Week vs Last Week Comparison ──────────────────────
            const weekCtx = document.getElementById('weekCompareChart')?.getContext('2d');
            if (weekCtx) {
                const weeklyData = salesStats.weekly_breakdown || [];
                const today = new Date();
                const thisWeek = [], lastWeek = [], dayLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

                for (let i = 6; i >= 0; i--) {
                    const d = new Date(today);
                    d.setDate(d.getDate() - i);
                    const dateStr = d.toISOString().split('T')[0];
                    const found = weeklyData.find(r => r.sale_date === dateStr);
                    thisWeek.push(found ? found.revenue : 0);
                }
                for (let i = 13; i >= 7; i--) {
                    const d = new Date(today);
                    d.setDate(d.getDate() - i);
                    const dateStr = d.toISOString().split('T')[0];
                    const found = weeklyData.find(r => r.sale_date === dateStr);
                    lastWeek.push(found ? found.revenue : 0);
                }

                if (weekCompareChartInstance) weekCompareChartInstance.destroy();
                weekCompareChartInstance = new Chart(weekCtx, {
                    type: 'bar',
                    data: {
                        labels: dayLabels,
                        datasets: [
                            { label: 'This Week', data: thisWeek, backgroundColor: isDark ? 'rgba(16,185,129,0.75)' : 'rgba(16,185,129,0.65)', borderColor: '#10b981', borderWidth: 1.5, borderRadius: 5 },
                            { label: 'Last Week', data: lastWeek, backgroundColor: isDark ? 'rgba(56,189,248,0.5)' : 'rgba(56,189,248,0.4)', borderColor: '#38bdf8', borderWidth: 1.5, borderRadius: 5 }
                        ]
                    },
                    options: {
                        responsive: true, maintainAspectRatio: false,
                        interaction: { mode: 'index', intersect: false },
                        scales: {
                            x: { grid: { display: false }, ticks: { color: tickColor, font: { size: 11, weight: '600' } } },
                            y: { grid: { color: gridColor }, ticks: { color: tickColor, font: { size: 10, family: 'JetBrains Mono' }, callback: v => 'Rs.' + (v >= 1000 ? (v/1000).toFixed(1)+'k' : v) }, beginAtZero: true }
                        },
                        plugins: {
                            legend: { labels: { color: legendColor, font: { size: 11, weight: '700' }, boxWidth: 12, padding: 16 } },
                            tooltip: { ...mkTooltip(isDark), callbacks: { label: ctx => ` ${ctx.dataset.label}: Rs. ${ctx.parsed.y.toLocaleString()}` } }
                        }
                    }
                });
            }

            // ── 5. Status Donut Chart ────────────────────────────────────
            const sdCtx = document.getElementById('statusDonutChart')?.getContext('2d');
            if (sdCtx) {
                const sc = salesStats.status_counts || {};
                const sdLabels = ['Completed', 'Preparing', 'Pending', 'Out for Delivery', 'Cancelled'];
                const sdValues = [sc.completed || 0, sc.preparing || 0, sc.pending || 0, sc.out_for_delivery || 0, sc.cancelled || 0];
                const sdColors = ['#10b981', '#38bdf8', '#f59e0b', '#a855f7', '#e11d48'];
                if (statusDonutChartInstance) statusDonutChartInstance.destroy();
                statusDonutChartInstance = new Chart(sdCtx, {
                    type: 'doughnut',
                    data: { labels: sdLabels, datasets: [{ data: sdValues, backgroundColor: sdColors, borderColor: isDark ? '#0f172a' : '#fff', borderWidth: 2, hoverOffset: 6 }] },
                    options: {
                        responsive: true, maintainAspectRatio: false, cutout: '65%',
                        plugins: {
                            legend: { display: false },
                            tooltip: { ...mkTooltip(isDark), callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed} orders` } }
                        }
                    }
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
                b.classList.add('bg-slate-100', 'dark:bg-slate-800', 'text-slate-700', 'dark:text-slate-300');
            });
            event.target.classList.add('active', 'bg-rose-600', 'text-white');
            event.target.classList.remove('bg-slate-100', 'dark:bg-slate-800', 'text-slate-700', 'dark:text-slate-300');
            renderOrdersPipeline();
        }

        function renderOrdersPipeline() {
            const grid = document.getElementById('orders-pipeline-grid');
            if (!grid) return;
            grid.innerHTML = '';

            let filtered = allOrders;
            if (activeOrderStatusFilter !== 'all') {
                filtered = filtered.filter(o => o.status === activeOrderStatusFilter);
            }

            document.getElementById('orders-count-label').innerText = filtered.length;

            if (filtered.length === 0) {
                grid.innerHTML = `<div class="col-span-full py-20 text-center text-slate-400 dark:text-slate-500 text-sm font-medium">No orders found in this category.</div>`;
                return;
            }

            filtered.forEach(order => {
                const card = document.createElement('div');
                const statusBorder = {
                    pending: 'border-l-4 border-l-amber-500',
                    preparing: 'border-l-4 border-l-sky-500',
                    out_for_delivery: 'border-l-4 border-l-purple-500',
                    completed: 'border-l-4 border-l-emerald-500',
                    cancelled: 'border-l-4 border-l-rose-500'
                }[order.status] || 'border-l-4 border-l-slate-400';

                const statusBadge = {
                    pending: '<span class="bg-amber-500/10 text-amber-700 dark:text-amber-300 border border-amber-500/30 text-[10px] font-bold px-2 py-0.5 rounded-full">🟡 Pending</span>',
                    preparing: '<span class="bg-sky-500/10 text-sky-700 dark:text-sky-300 border border-sky-500/30 text-[10px] font-bold px-2 py-0.5 rounded-full">🔵 Preparing</span>',
                    out_for_delivery: '<span class="bg-purple-500/10 text-purple-700 dark:text-purple-300 border border-purple-500/30 text-[10px] font-bold px-2 py-0.5 rounded-full">🟣 Out for Delivery</span>',
                    completed: '<span class="bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 border border-emerald-500/30 text-[10px] font-bold px-2 py-0.5 rounded-full">🟢 Completed</span>',
                    cancelled: '<span class="bg-rose-500/10 text-rose-700 dark:text-rose-300 border border-rose-500/30 text-[10px] font-bold px-2 py-0.5 rounded-full">🔴 Cancelled</span>'
                }[order.status] || `<span class="bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-slate-300 text-[10px] px-2 py-0.5 rounded">${order.status}</span>`;

                const typeBadge = {
                    delivery: '<span class="bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 border border-emerald-500/30 text-[10px] px-2 py-0.5 rounded-lg font-bold">🛵 WhatsApp</span>',
                    counter: '<span class="bg-blue-500/10 text-blue-700 dark:text-blue-300 border border-blue-500/30 text-[10px] px-2 py-0.5 rounded-lg font-bold">🛍️ Counter</span>',
                    dine_in: '<span class="bg-amber-500/10 text-amber-700 dark:text-amber-300 border border-amber-500/30 text-[10px] px-2 py-0.5 rounded-lg font-bold">🍽️ Dine-in</span>'
                }[order.order_type] || '';

                const noteHtml = order.special_notes ? `
                    <div class="bg-amber-500/10 border border-amber-500/30 rounded-2xl p-2.5 text-xs text-amber-900 dark:text-amber-200">
                        <strong>📝 Special Note:</strong> ${order.special_notes}
                    </div>
                ` : '';

                card.className = `bg-white dark:bg-darkslate-850 border border-slate-200/80 dark:border-slate-800 ${statusBorder} rounded-3xl p-5 shadow-sm hover:shadow-md transition-all duration-200 space-y-3.5 flex flex-col justify-between`;

                card.innerHTML = `
                    <div class="space-y-3">
                        <div class="flex items-center justify-between">
                            <span class="font-extrabold text-sm text-sky-600 dark:text-sky-400 font-mono-num">${order.order_id}</span>
                            <div class="flex items-center space-x-1.5">
                                ${typeBadge}
                                ${statusBadge}
                            </div>
                        </div>

                        <div class="text-xs text-slate-600 dark:text-slate-300 space-y-1">
                            <div><strong>👤 Customer:</strong> <span class="text-slate-900 dark:text-white font-semibold">${order.customer_name}</span> &nbsp;|&nbsp; <strong>📞</strong> <a href="https://wa.me/${(order.customer_phone || '').replace(/[^0-9]/g, '')}" target="_blank" class="text-emerald-600 dark:text-emerald-400 hover:underline font-mono-num font-bold">${order.customer_phone}</a></div>
                            <div><strong>📍 Location / Table:</strong> ${order.address}</div>
                            <div class="text-[11px] text-slate-500 dark:text-slate-400">🕒 ${formatPakistanTime(order.formatted_time || order.timestamp)}</div>
                        </div>

                        <!-- Items list -->
                        <div class="bg-slate-50 dark:bg-darkslate-950 p-3 rounded-2xl border border-slate-200/80 dark:border-slate-800 text-xs text-slate-800 dark:text-slate-200 whitespace-pre-wrap font-sans leading-relaxed">
${order.items_list || order.slip || 'Order items'}
                        </div>

                        ${noteHtml}
                    </div>

                    <div class="pt-3 border-t border-slate-200/80 dark:border-slate-800 flex items-center justify-between">
                        <div>
                            <span class="text-xs text-slate-500 dark:text-slate-400">Total:</span>
                            <span class="text-lg font-black text-emerald-600 dark:text-emerald-400 font-mono-num ml-1">Rs. ${order.total}</span>
                        </div>
                        <div class="flex items-center space-x-2">
                            <button onclick="openReceiptModalByOrderId('${order.order_id}')" class="px-2.5 py-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-bold rounded-xl transition" title="Print 80mm Receipt">
                                🖨️
                            </button>
                            <select onchange="updateOrderStatus('${order.order_id}', this.value)" class="bg-slate-50 dark:bg-darkslate-950 border border-slate-300 dark:border-slate-700 text-slate-800 dark:text-slate-200 rounded-xl text-xs px-2.5 py-1.5 font-semibold focus:outline-none focus:border-rose-500">
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
                    <div><strong>DATE:</strong> ${formatPakistanTime(order.timestamp || new Date())}</div>
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
