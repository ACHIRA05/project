# project/database/sell_db.py
import os, sqlite3

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# ค่า default (เปลี่ยนได้ตอน init)
SELL_DB  = os.path.join(PROJECT_ROOT, "database", "Sell_item.db")
ALBUM_DB = os.path.join(PROJECT_ROOT, "database", "album_data.db")

def init(sell_db_path: str = SELL_DB, album_db_path: str = ALBUM_DB):
    """ตั้ง path และสร้างตารางให้ครบถ้ายังไม่มี"""
    global SELL_DB, ALBUM_DB
    SELL_DB, ALBUM_DB = sell_db_path, album_db_path
    os.makedirs(os.path.dirname(SELL_DB), exist_ok=True)
    _create_tables()

def _conn():
    return sqlite3.connect(SELL_DB)

def _create_tables():
    con = _conn(); cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cart (
      id        INTEGER PRIMARY KEY AUTOINCREMENT,
      username  TEXT    NOT NULL,
      album_id  INTEGER NOT NULL,
      quantity  INTEGER NOT NULL DEFAULT 1,
      UNIQUE(username, album_id)
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
      id         INTEGER PRIMARY KEY AUTOINCREMENT,
      username   TEXT NOT NULL,
      created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
      total      REAL NOT NULL DEFAULT 0
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
      id        INTEGER PRIMARY KEY AUTOINCREMENT,
      order_id  INTEGER NOT NULL,
      album_id  INTEGER NOT NULL,
      price     REAL    NOT NULL,
      quantity  INTEGER NOT NULL
    )""")
    con.commit(); con.close()

# ---------- CART ----------
def add(username: str, album_id: int, qty: int = 1):
    con = _conn(); cur = con.cursor()
    cur.execute("""
        INSERT INTO cart(username, album_id, quantity)
        VALUES(?,?,?)
        ON CONFLICT(username, album_id)
        DO UPDATE SET quantity = quantity + excluded.quantity
    """, (username, album_id, qty))
    con.commit(); con.close()

def set_qty(username: str, album_id: int, qty: int):
    con = _conn(); cur = con.cursor()
    if qty <= 0:
        cur.execute("DELETE FROM cart WHERE username=? AND album_id=?", (username, album_id))
    else:
        cur.execute("UPDATE cart SET quantity=? WHERE username=? AND album_id=?", (qty, username, album_id))
    con.commit(); con.close()

def remove(username: str, album_id: int):
    con = _conn(); cur = con.cursor()
    cur.execute("DELETE FROM cart WHERE username=? AND album_id=?", (username, album_id))
    con.commit(); con.close()

def clear(username: str):
    con = _conn(); cur = con.cursor()
    cur.execute("DELETE FROM cart WHERE username=?", (username,))
    con.commit(); con.close()

def count(username: str) -> int:
    con = _conn(); cur = con.cursor()
    cur.execute("SELECT IFNULL(SUM(quantity),0) FROM cart WHERE username=?", (username,))
    n = cur.fetchone()[0] or 0
    con.close()
    return int(n)

def items(username: str):
    """คืน [(album_id, title, price, qty, cover_path)]"""
    con = _conn(); cur = con.cursor()
    cur.execute("ATTACH DATABASE ? AS albumdb", (ALBUM_DB,))
    cur.execute("""
        SELECT a.id,
               a.album_name || CASE WHEN IFNULL(a.version,'')<>'' THEN ' ('||a.version||')' ELSE '' END AS title,
               IFNULL(a.price,0), c.quantity, IFNULL(a.cover_path,'')
        FROM cart c
        JOIN albumdb.albums a ON a.id = c.album_id
        WHERE c.username=?
        ORDER BY c.id DESC
    """, (username,))
    rows = cur.fetchall()
    cur.execute("DETACH DATABASE albumdb")
    con.close()
    return rows

def total(username: str) -> float:
    con = _conn(); cur = con.cursor()
    cur.execute("ATTACH DATABASE ? AS albumdb", (ALBUM_DB,))
    cur.execute("""
        SELECT IFNULL(SUM(a.price * c.quantity),0.0)
        FROM cart c JOIN albumdb.albums a ON a.id=c.album_id
        WHERE c.username=?
    """, (username,))
    t = cur.fetchone()[0] or 0.0
    cur.execute("DETACH DATABASE albumdb")
    con.close()
    return float(t)

# ---------- CHECKOUT (จำลอง) ----------
def checkout(username: str) -> int | None:
    items_in_cart = items(username)
    if not items_in_cart:
        return None
    tot = sum(price * qty for _, _, price, qty, _ in items_in_cart)

    con = _conn(); cur = con.cursor()
    cur.execute("INSERT INTO orders(username, total) VALUES(?,?)", (username, tot))
    order_id = cur.lastrowid
    for album_id, _, price, qty, _ in items_in_cart:
        cur.execute("""
            INSERT INTO order_items(order_id, album_id, price, quantity)
            VALUES(?,?,?,?)
        """, (order_id, album_id, price, qty))
    cur.execute("DELETE FROM cart WHERE username=?", (username,))
    con.commit(); con.close()
    return order_id

# --- วางต่อจากฟังก์ชัน total() เดิม หรือแทนที่ใช้งานแทน total ไปเลย ---

def pricing(username: str) -> dict:
    """
    คำนวณราคาตะกร้าแบบละเอียด
    return {
        "items": [(album_id, title, price, qty, cover_path)],
        "item_count": จำนวนชิ้นรวม,
        "subtotal": ราคารวมก่อนหักส่วนลด,
        "discount_rate": อัตราส่วนลด (0..1),
        "discount": ยอดส่วนลดเป็นเงิน,
        "total": ยอดสุทธิหลังหักส่วนลด
    }
    กติกา: ซื้อครบ 3 อัลบั้มขึ้นไป ลด 20%
    """
    rows = items(username)  # [(album_id, title, price, qty, cover)]
    item_count = sum(q for _, _, _, q, _ in rows)
    subtotal = float(sum(p*q for _, _, p, q, _ in rows))

    # กติกาส่วนลด
    discount_rate = 0.20 if item_count >= 3 else 0.0
    discount = subtotal * discount_rate
    total = subtotal - discount

    # ให้เป็นตัวเลขสวย ๆ (บาทปกติไม่ต้อง .xx ก็ได้)
    return {
        "items": rows,
        "item_count": int(item_count),
        "subtotal": float(subtotal),
        "discount_rate": float(discount_rate),
        "discount": float(discount),
        "total": float(total),
    }

# หากยังอยากคง total() ไว้ให้ GUI เก่าเรียกได้เหมือนเดิม:
def total(username: str) -> float:
    return pricing(username)["total"]

# ---------- CHECKOUT (จำลอง) ----------
def checkout(username: str) -> int | None:
    """
    ใช้ยอดสุทธิหลังส่วนลดในการสร้างออเดอร์
    """
    calc = pricing(username)
    if not calc["items"]:
        return None

    con = _conn(); cur = con.cursor()
    cur.execute("INSERT INTO orders(username, total) VALUES(?,?)", (username, calc["total"]))
    order_id = cur.lastrowid

    for album_id, _, price, qty, _ in calc["items"]:
        cur.execute("""
            INSERT INTO order_items(order_id, album_id, price, quantity)
            VALUES(?,?,?,?)
        """, (order_id, album_id, price, qty))

    cur.execute("DELETE FROM cart WHERE username=?", (username,))
    con.commit(); con.close()
    return order_id
