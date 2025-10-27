# setup_orders_min.py  (รันครั้งเดียวพอ)
import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "Sell_item.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

# หัวออเดอร์: ใครซื้อ, เมื่อไหร่, ยอดรวม
cur.execute("""
CREATE TABLE IF NOT EXISTS orders (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  username   TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
  total      REAL NOT NULL DEFAULT 0
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS order_items (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id  INTEGER NOT NULL,
  album_id  INTEGER NOT NULL,
  price     REAL    NOT NULL,
  quantity  INTEGER NOT NULL
)
""")

con.commit()
con.close()
print("✅ สร้างตาราง orders / order_items เรียบร้อย")
