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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

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

    # SQLite
    conn = get_sqlite_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO orders (id, customer_name, customer_phone, address, items_list, subtotal, delivery_fee, total, slip, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', CURRENT_TIMESTAMP)
        ON CONFLICT(id) DO UPDATE SET
            address=excluded.address,
            total=excluded.total,
            slip=excluded.slip;
    """, (oid, cname, cphone, addr, items_list, subtotal, delivery_fee, total, slip))

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
                INSERT INTO orders (id, customer_name, customer_phone, address, items_list, subtotal, delivery_fee, total, slip, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending', CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    address=EXCLUDED.address,
                    total=EXCLUDED.total,
                    slip=EXCLUDED.slip;
            """, (oid, cname, cphone, addr, items_list, subtotal, delivery_fee, total, slip))

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

def db_get_recent_orders(limit: int = 50) -> List[Dict[str, Any]]:
    """Fetches recent orders for the live kitchen dashboard."""
    if is_postgres():
        try:
            pg_conn = get_pg_connection()
            pg_cur = pg_conn.cursor()
            pg_cur.execute("""
                SELECT id as order_id, customer_name, customer_phone, address,
                       items_list, subtotal, delivery_fee, total, slip, status,
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
               created_at as timestamp
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
