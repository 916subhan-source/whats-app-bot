"""
Seed Script: Populates SQLite & PostgreSQL with the official Cherry Peri Menu items.
"""
import os
from database import init_db, seed_menu_items, get_sqlite_connection, is_postgres
from menu import MENU

def main():
    print("🚀 Initializing Database...")
    init_db()

    print("🌱 Seeding Menu Items...")
    seed_menu_items(MENU)

    # Verify SQLite counts
    conn = get_sqlite_connection()
    cur = conn.cursor()
    cur.execute("SELECT count(*) as cnt FROM menu_items;")
    count = cur.fetchone()["cnt"]
    print(f"✅ SQLite initialized with {count} menu items in 'menu_items' table!")

    # Show a few sample rows
    cur.execute("SELECT id, name, price, is_deal FROM menu_items LIMIT 5;")
    for row in cur.fetchall():
        print(f"  • {row['id']}: {row['name']} (Rs. {row['price']}) - Deal: {bool(row['is_deal'])}")
    conn.close()

    if is_postgres():
        print("✅ PostgreSQL is configured and synced!")
    else:
        print("ℹ️ PostgreSQL not configured yet. (Set DATABASE_URL or POSTGRES_URL in .env to sync to PostgreSQL automatically).")

if __name__ == "__main__":
    main()
