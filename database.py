"""
Database Layer for Cherry Peri WhatsApp Bot
Supports both SQLite (local/embedded) and PostgreSQL (cloud/Neon/Supabase/VPS).
Automatically initializes tables and seeds menu items.
"""

import os
import json
import sqlite3
import tempfile
from datetime import datetime
from typing import Optional, List, Dict, Any

# ─────────────────────────────────────────────
# 🔌 Database Configuration
# ─────────────────────────────────────────────
POSTGRES_URL = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL") or os.getenv("POSTGRESQL_URL")

# Fallback SQLite path
if os.getenv("VERCEL"):
    SQLITE_PATH = os.path.join(tempfile.gettempdir(), "cherry_peri.db")
else:
    SQLITE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cherry_peri.db")

def is_postgres() -> bool:
    return bool(POSTGRES_URL and ("postgres://" in POSTGRES_URL or "postgresql://" in POSTGRES_URL))

def get_pg_connection():
    import psycopg2
    from psycopg2.extras import RealDictCursor
    # Fix for postgres:// vs postgresql:// on newer drivers
    clean_url = POSTGRES_URL
    if clean_url.startswith("postgres://"):
        clean_url = clean_url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(clean_url, cursor_factory=RealDictCursor)

def get_sqlite_connection():
    conn = sqlite3.connect(SQLITE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# ─────────────────────────────────────────────
# 🏗️ Table Schemas
# ─────────────────────────────────────────────
def init_db():
    """Initializes tables in SQLite and (if configured) PostgreSQL."""
    # 1. Initialize SQLite
    conn = get_sqlite_connection()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            name TEXT NOT NULL,
            price INTEGER DEFAULT 0,
            prices_json TEXT,
            description TEXT,
            is_deal BOOLEAN DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            customer_name TEXT,
            customer_phone TEXT,
            address TEXT,
            items_list TEXT,
            subtotal INTEGER DEFAULT 0,
            delivery_fee INTEGER DEFAULT 0,
            total INTEGER DEFAULT 0,
            slip TEXT,
            status TEXT DEFAULT 'pending',
            order_type TEXT DEFAULT 'delivery',
            special_notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS customers (
            phone TEXT PRIMARY KEY,
            name TEXT,
            last_address TEXT,
            total_orders INTEGER DEFAULT 0,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS carts (
            phone TEXT PRIMARY KEY,
            cart_json TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Ensure schema migrations for SQLite
    for migration_sql in [
        "ALTER TABLE orders ADD COLUMN order_type TEXT DEFAULT 'delivery';",
        "ALTER TABLE orders ADD COLUMN special_notes TEXT DEFAULT '';"
    ]:
        try:
            cur.execute(migration_sql)
        except Exception:
            pass

    conn.commit()
    conn.close()

    # 2. Initialize PostgreSQL if configured
    if is_postgres():
        try:
            pg_conn = get_pg_connection()
            pg_cur = pg_conn.cursor()
            pg_cur.execute("""
                CREATE TABLE IF NOT EXISTS menu_items (
                    id VARCHAR(100) PRIMARY KEY,
                    category VARCHAR(100) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    price INTEGER DEFAULT 0,
                    prices_json TEXT,
                    description TEXT,
                    is_deal BOOLEAN DEFAULT FALSE,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS orders (
                    id VARCHAR(50) PRIMARY KEY,
                    customer_name VARCHAR(255),
                    customer_phone VARCHAR(50),
                    address TEXT,
                    items_list TEXT,
                    subtotal INTEGER DEFAULT 0,
                    delivery_fee INTEGER DEFAULT 0,
                    total INTEGER DEFAULT 0,
                    slip TEXT,
                    status VARCHAR(50) DEFAULT 'pending',
                    order_type VARCHAR(50) DEFAULT 'delivery',
                    special_notes TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                ALTER TABLE orders ADD COLUMN IF NOT EXISTS order_type VARCHAR(50) DEFAULT 'delivery';
                ALTER TABLE orders ADD COLUMN IF NOT EXISTS special_notes TEXT DEFAULT '';

                CREATE TABLE IF NOT EXISTS customers (
                    phone VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(255),
                    last_address TEXT,
                    total_orders INTEGER DEFAULT 0,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS carts (
                    phone VARCHAR(50) PRIMARY KEY,
                    cart_json TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            pg_conn.commit()
            pg_cur.close()
            pg_conn.close()
            print("[DB] PostgreSQL schemas verified successfully!")
        except Exception as pg_err:
            print(f"[DB WARN] PostgreSQL initialization failed: {pg_err}")

# ─────────────────────────────────────────────
# 🍕 Seed Menu Items into Database
# ─────────────────────────────────────────────
def seed_menu_items(menu_dict: dict):
    """Populates all menu items and Deals 1-26 into SQLite & PostgreSQL."""
    items_to_insert = []
    for cat_id, cat_info in menu_dict.items():
        cat_name = cat_info.get("name", cat_id)
        is_deal = (cat_id == "deals")
        for itm in cat_info.get("items", []):
            item_id = itm["id"]
            name = itm["name"]
            price = itm.get("price", 0)
            prices_json = json.dumps(itm.get("prices", {})) if "prices" in itm else None
            desc = itm.get("desc", "")
            items_to_insert.append((item_id, cat_name, name, price, prices_json, desc, is_deal))

    # Insert into SQLite
    conn = get_sqlite_connection()
    cur = conn.cursor()
    for row in items_to_insert:
        cur.execute("""
            INSERT INTO menu_items (id, category, name, price, prices_json, description, is_deal, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(id) DO UPDATE SET
                category=excluded.category,
                name=excluded.name,
                price=excluded.price,
                prices_json=excluded.prices_json,
                description=excluded.description,
                is_deal=excluded.is_deal,
                updated_at=CURRENT_TIMESTAMP;
        """, row)
    conn.commit()
    conn.close()

    # Insert into PostgreSQL if available
    if is_postgres():
        try:
            pg_conn = get_pg_connection()
            pg_cur = pg_conn.cursor()
            for row in items_to_insert:
                pg_cur.execute("""
                    INSERT INTO menu_items (id, category, name, price, prices_json, description, is_deal, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT(id) DO UPDATE SET
                        category=EXCLUDED.category,
                        name=EXCLUDED.name,
                        price=EXCLUDED.price,
                        prices_json=EXCLUDED.prices_json,
                        description=EXCLUDED.description,
                        is_deal=EXCLUDED.is_deal,
                        updated_at=CURRENT_TIMESTAMP;
                """, row)
            pg_conn.commit()
            pg_cur.close()
            pg_conn.close()
            print(f"[DB] Synced {len(items_to_insert)} menu items to PostgreSQL!")
        except Exception as e:
            print(f"[DB WARN] PostgreSQL seed error: {e}")

# ─────────────────────────────────────────────
# 📦 Orders CRUD
# ─────────────────────────────────────────────
def db_save_order(order_data: dict):
    """Saves a confirmed order and updates customer profile in SQLite and PostgreSQL."""
    oid = order_data.get("order_id", f"ORD-{int(datetime.now().timestamp())}")
    cname = order_data.get("customer_name", "Customer")
    cphone = order_data.get("customer_phone", "")
    addr = order_data.get("address", "")
    items_list = order_data.get("items_list", "")
    subtotal = int(order_data.get("subtotal", 0))
    delivery_fee = int(order_data.get("delivery_fee", 0))
    total = int(order_data.get("total", subtotal + delivery_fee))
    slip = order_data.get("slip", "")
    status = order_data.get("status", "pending")
    order_type = order_data.get("order_type", "delivery")
    special_notes = order_data.get("special_notes", "")

    # SQLite
    conn = get_sqlite_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO orders (id, customer_name, customer_phone, address, items_list, subtotal, delivery_fee, total, slip, status, order_type, special_notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(id) DO UPDATE SET
            address=excluded.address,
            total=excluded.total,
            slip=excluded.slip,
            status=excluded.status,
            order_type=excluded.order_type,
            special_notes=excluded.special_notes;
    """, (oid, cname, cphone, addr, items_list, subtotal, delivery_fee, total, slip, status, order_type, special_notes))

    # Update Customer
    cur.execute("""
        INSERT INTO customers (phone, name, last_address, total_orders, last_active)
        VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)
        ON CONFLICT(phone) DO UPDATE SET
            name=coalesce(excluded.name, customers.name),
            last_address=excluded.last_address,
            total_orders=customers.total_orders + 1,
            last_active=CURRENT_TIMESTAMP;
    """, (cphone, cname, addr))
    conn.commit()
    conn.close()

    # PostgreSQL
    if is_postgres():
        try:
            pg_conn = get_pg_connection()
            pg_cur = pg_conn.cursor()
            pg_cur.execute("""
                INSERT INTO orders (id, customer_name, customer_phone, address, items_list, subtotal, delivery_fee, total, slip, status, order_type, special_notes, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    address=EXCLUDED.address,
                    total=EXCLUDED.total,
                    slip=EXCLUDED.slip,
                    status=EXCLUDED.status,
                    order_type=EXCLUDED.order_type,
                    special_notes=EXCLUDED.special_notes;
            """, (oid, cname, cphone, addr, items_list, subtotal, delivery_fee, total, slip, status, order_type, special_notes))

            pg_cur.execute("""
                INSERT INTO customers (phone, name, last_address, total_orders, last_active)
                VALUES (%s, %s, %s, 1, CURRENT_TIMESTAMP)
                ON CONFLICT(phone) DO UPDATE SET
                    name=COALESCE(EXCLUDED.name, customers.name),
                    last_address=EXCLUDED.last_address,
                    total_orders=customers.total_orders + 1,
                    last_active=CURRENT_TIMESTAMP;
            """, (cphone, cname, addr))
            pg_conn.commit()
            pg_cur.close()
            pg_conn.close()
        except Exception as e:
            print(f"[DB WARN] PostgreSQL order save error: {e}")

def db_create_pos_order(order_data: dict) -> dict:
    """Creates a counter / POS order and records it in the sales system."""
    import random
    oid = order_data.get("order_id") or f"#POS-{random.randint(1000, 9999)}"
    cname = order_data.get("customer_name") or "Counter Customer"
    cphone = order_data.get("customer_phone") or "-"
    addr = order_data.get("address") or "Dine-in / Takeaway"
    items_list = order_data.get("items_list") or ""
    subtotal = int(order_data.get("subtotal", 0))
    delivery_fee = int(order_data.get("delivery_fee", 0))
    total = int(order_data.get("total", subtotal + delivery_fee))
    special_notes = order_data.get("special_notes", "")
    order_type = order_data.get("order_type", "counter")
    status = order_data.get("status", "completed")

    clean_slip = (
        f"*CHERRY PERI FAST FOOD (POS)*\n"
        f"Receipt {oid}\n"
        f"────────────────────\n"
        f"👤 Customer: {cname} | {cphone}\n"
        f"📍 Order Type: {order_type.title()} ({addr})\n\n"
        f"🍽️ Items:\n{items_list}\n"
    )
    if special_notes:
        clean_slip += f"📝 Note: {special_notes}\n"
    clean_slip += (
        f"\n💰 Total: Rs. {total}\n"
        f"────────────────────\n"
        f"Thank you for dining with us!"
    )

    full_order = {
        "order_id": oid,
        "customer_name": cname,
        "customer_phone": cphone,
        "address": addr,
        "items_list": items_list,
        "subtotal": subtotal,
        "delivery_fee": delivery_fee,
        "total": total,
        "slip": clean_slip,
        "status": status,
        "order_type": order_type,
        "special_notes": special_notes
    }
    db_save_order(full_order)
    return full_order

def db_update_order_status(order_id: str, new_status: str) -> bool:
    """Updates order status: pending, preparing, out_for_delivery, completed, cancelled."""
    oid = order_id if order_id.startswith("#") else f"#{order_id}"
    conn = get_sqlite_connection()
    cur = conn.cursor()
    cur.execute("UPDATE orders SET status = ? WHERE id = ? OR id = ?;", (new_status, order_id, oid))
    affected = cur.rowcount
    conn.commit()
    conn.close()

    if is_postgres():
        try:
            pg_conn = get_pg_connection()
            pg_cur = pg_conn.cursor()
            pg_cur.execute("UPDATE orders SET status = %s WHERE id = %s OR id = %s;", (new_status, order_id, oid))
            pg_conn.commit()
            pg_cur.close()
            pg_conn.close()
        except Exception:
            pass

    return affected > 0

def db_get_sales_analytics() -> dict:
    """Calculates daily, monthly, and overall sales metrics with daily trend charts."""
    init_db()
    conn = get_sqlite_connection()
    cur = conn.cursor()

    # Overall totals
    cur.execute("SELECT COUNT(*), COALESCE(SUM(total), 0), COALESCE(AVG(total), 0) FROM orders WHERE status != 'cancelled';")
    tot_row = cur.fetchone()
    tot_orders = tot_row[0] or 0
    tot_revenue = tot_row[1] or 0
    avg_order = int(tot_row[2] or 0)

    # Today's sales (Asia/Karachi UTC+5)
    cur.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM orders WHERE date(datetime(created_at, '+5 hours')) = date(datetime('now', '+5 hours')) AND status != 'cancelled';")
    tod_row = cur.fetchone()
    today_orders = tod_row[0] or 0
    today_revenue = tod_row[1] or 0

    # Yesterday's sales (Asia/Karachi UTC+5)
    cur.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM orders WHERE date(datetime(created_at, '+5 hours')) = date(datetime('now', '+5 hours', '-1 day')) AND status != 'cancelled';")
    yest_row = cur.fetchone()
    yest_orders = yest_row[0] or 0
    yest_revenue = yest_row[1] or 0

    # Current month's sales (Asia/Karachi UTC+5)
    cur.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM orders WHERE strftime('%Y-%m', datetime(created_at, '+5 hours')) = strftime('%Y-%m', datetime('now', '+5 hours')) AND status != 'cancelled';")
    mon_row = cur.fetchone()
    month_orders = mon_row[0] or 0
    month_revenue = mon_row[1] or 0

    # Daily breakdown for the last 30 days (Asia/Karachi UTC+5)
    cur.execute("""
        SELECT date(datetime(created_at, '+5 hours')) as sale_date, COUNT(*) as order_count, COALESCE(SUM(total), 0) as revenue
        FROM orders
        WHERE status != 'cancelled' AND datetime(created_at, '+5 hours') >= date(datetime('now', '+5 hours', '-30 days'))
        GROUP BY date(datetime(created_at, '+5 hours'))
        ORDER BY sale_date ASC;
    """)
    daily_rows = [dict(r) for r in cur.fetchall()]

    # Orders status breakdown
    cur.execute("SELECT status, COUNT(*) as count FROM orders GROUP BY status;")
    status_counts = {r["status"]: r["count"] for r in cur.fetchall()}

    # Channel / order_type breakdown (WhatsApp vs Counter vs Dine-in)
    cur.execute("""
        SELECT COALESCE(order_type, 'delivery') as otype, COUNT(*) as count, COALESCE(SUM(total), 0) as revenue
        FROM orders
        WHERE status != 'cancelled'
        GROUP BY COALESCE(order_type, 'delivery');
    """)
    channel_stats = {r["otype"]: {"count": r["count"], "revenue": int(r["revenue"])} for r in cur.fetchall()}

    # Recent orders
    cur.execute("""
        SELECT id as order_id, customer_name, customer_phone, address, items_list, total, status,
               coalesce(order_type, 'delivery') as order_type,
               coalesce(special_notes, '') as special_notes,
               strftime('%d %b, %H:%M', created_at) as formatted_time
        FROM orders
        ORDER BY created_at DESC
        LIMIT 100;
    """)
    recent_orders = [dict(r) for r in cur.fetchall()]

    # Top items breakdown
    item_counts = {}
    import re
    cur.execute("SELECT items_list FROM orders WHERE status != 'cancelled';")
    for r in cur.fetchall():
        txt = r[0] or ""
        for m in re.finditer(r"(?:•|\*|-)\s*(\d+)x\s*([^\n—–\-]+)", txt):
            qty = int(m.group(1))
            iname = m.group(2).strip().replace("*", "")
            item_counts[iname] = item_counts.get(iname, 0) + qty

    top_items = sorted([{"name": k, "count": v} for k, v in item_counts.items()], key=lambda x: x["count"], reverse=True)[:8]

    conn.close()

    return {
        "today_revenue": int(today_revenue),
        "today_orders": int(today_orders),
        "yesterday_revenue": int(yest_revenue),
        "yesterday_orders": int(yest_orders),
        "month_revenue": int(month_revenue),
        "month_orders": int(month_orders),
        "total_revenue": int(tot_revenue),
        "total_orders": int(tot_orders),
        "avg_order_value": avg_order,
        "daily_breakdown": daily_rows,
        "status_counts": status_counts,
        "channel_stats": channel_stats,
        "top_items": top_items,
        "recent_orders": recent_orders
    }

def db_seed_sample_orders():
    """Seeds initial sample orders if the table is empty so the POS dashboard shows rich sales data immediately."""
    init_db()
    conn = get_sqlite_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM orders;")
    count = cur.fetchone()[0]
    if count == 0:
        import random
        sample_data = [
            ("Ali Khan", "0300-1234567", "Circular Road, Opp Stylo", "• 1x Deal 1 (1 Small Pizza + 1 Zinger + 1L Drink) — Rs. 800", 800, "Cheese kam", "completed", "delivery", "date('now', '-4 days')"),
            ("Usman Tariq", "0333-9876543", "Cantt Area, D.I. Khan", "• 2x Zinger Burger (Regular) — Rs. 700\n• 1x Masala Fries — Rs. 250", 950, "Extra spicy", "completed", "delivery", "date('now', '-3 days')"),
            ("Hamza Shah", "0345-5551234", "Muryali Chowk", "• 1x Deal 22 (2 Large Pizza + 1.5L Drink) — Rs. 2200", 2200, "", "completed", "delivery", "date('now', '-2 days')"),
            ("Walk-in Customer", "-", "Table 4", "• 2x Zinger Burger (Special) — Rs. 540\n• 1x Loaded Fries — Rs. 600", 1140, "Garlic sauce", "completed", "dine_in", "date('now', '-1 day')"),
            ("Zahid Malik", "0312-3334455", "Topanwala Bazar", "• 1x Deal 3 (2 Zinger + 2 Shawarma + 1L Drink) — Rs. 900", 900, "Kam sauce", "completed", "delivery", "date('now', '-1 day')"),
            ("Subhan Sultan", "0332-5255879", "Naqshband Colony", "• 1x Deal 20 (1 Large Pizza + 1 Medium Pizza + 1.5L Drink) — Rs. 1900\n• 1x Chicken Paratha Roll — Rs. 300", 2200, "Kam sauce ke sath", "preparing", "delivery", "datetime('now', '-2 hours')"),
            ("Bilal Ahmed", "0321-4455667", "Bannu Road, Grid Station", "• 1x Medium Tikka Pizza (Special) — Rs. 950\n• 1x Hot Wings (10 Pcs) — Rs. 460", 1410, "Extra crispy", "pending", "delivery", "datetime('now', '-15 minutes')")
        ]
        for name, phone, addr, items, tot, note, status, otype, dt_expr in sample_data:
            oid = f"#FE-{random.randint(1000, 9999)}"
            cur.execute(f"""
                INSERT INTO orders (id, customer_name, customer_phone, address, items_list, subtotal, delivery_fee, total, slip, status, order_type, special_notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, {dt_expr});
            """, (oid, name, phone, addr, items, tot, tot, f"Order {oid}\n{items}\nTotal: Rs. {tot}", status, otype, note))
        conn.commit()
        print("[DB] Seeded initial sample orders for POS dashboard!")
    conn.close()

def db_get_recent_orders(limit: int = 50) -> List[Dict[str, Any]]:
    """Fetches recent orders for the live kitchen dashboard."""
    if is_postgres():
        try:
            pg_conn = get_pg_connection()
            pg_cur = pg_conn.cursor()
            pg_cur.execute("""
                SELECT id as order_id, customer_name, customer_phone, address,
                       items_list, subtotal, delivery_fee, total, slip, status,
                       coalesce(order_type, 'delivery') as order_type,
                       coalesce(special_notes, '') as special_notes,
                       to_char(created_at, 'DD Mon YYYY, HH:MI AM') as timestamp
                FROM orders
                ORDER BY created_at DESC
                LIMIT %s;
            """, (limit,))
            rows = pg_cur.fetchall()
            pg_cur.close()
            pg_conn.close()
            return [dict(r) for r in rows]
        except Exception as e:
            print(f"[DB WARN] PostgreSQL read orders error: {e}")

    # Fallback to SQLite
    conn = get_sqlite_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id as order_id, customer_name, customer_phone, address,
               items_list, subtotal, delivery_fee, total, slip, status,
               coalesce(order_type, 'delivery') as order_type,
               coalesce(special_notes, '') as special_notes,
               datetime(created_at, '+5 hours') as timestamp
        FROM orders
        ORDER BY created_at DESC
        LIMIT ?;
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ─────────────────────────────────────────────
# 🛒 Cart DB Operations
# ─────────────────────────────────────────────
def db_get_cart(phone: str) -> Optional[dict]:
    if is_postgres():
        try:
            pg_conn = get_pg_connection()
            pg_cur = pg_conn.cursor()
            pg_cur.execute("SELECT cart_json FROM carts WHERE phone = %s;", (phone,))
            row = pg_cur.fetchone()
            pg_cur.close()
            pg_conn.close()
            if row and row.get("cart_json"):
                return json.loads(row["cart_json"])
        except Exception:
            pass

    conn = get_sqlite_connection()
    cur = conn.cursor()
    cur.execute("SELECT cart_json FROM carts WHERE phone = ?;", (phone,))
    row = cur.fetchone()
    conn.close()
    if row and row["cart_json"]:
        try:
            return json.loads(row["cart_json"])
        except Exception:
            pass
    return None

def db_save_cart(phone: str, cart_dict: dict):
    cart_json = json.dumps(cart_dict)
    conn = get_sqlite_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO carts (phone, cart_json, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(phone) DO UPDATE SET
            cart_json=excluded.cart_json,
            updated_at=CURRENT_TIMESTAMP;
    """, (phone, cart_json))
    conn.commit()
    conn.close()

    if is_postgres():
        try:
            pg_conn = get_pg_connection()
            pg_cur = pg_conn.cursor()
            pg_cur.execute("""
                INSERT INTO carts (phone, cart_json, updated_at)
                VALUES (%s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT(phone) DO UPDATE SET
                    cart_json=EXCLUDED.cart_json,
                    updated_at=CURRENT_TIMESTAMP;
            """, (phone, cart_json))
            pg_conn.commit()
            pg_cur.close()
            pg_conn.close()
        except Exception:
            pass
