import os
import sqlite3
from typing import Any, Dict, List, Optional, Sequence, Tuple

_sell_db_path: Optional[str] = None
_album_db_path: Optional[str] = None


def init(*, sell_db_path: str, album_db_path: str) -> None:
    """Configure database locations and ensure required tables exist."""
    global _sell_db_path, _album_db_path

    _sell_db_path = os.path.abspath(sell_db_path)
    _album_db_path = os.path.abspath(album_db_path)

    if not _sell_db_path:
        raise ValueError("sell_db_path must not be empty")
    if not _album_db_path:
        raise ValueError("album_db_path must not be empty")

    os.makedirs(os.path.dirname(_sell_db_path), exist_ok=True)

    with _connect_sell() as con:
        cur = con.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS cart (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                album_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                UNIQUE(username, album_id)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
                total REAL NOT NULL DEFAULT 0
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                album_id INTEGER NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL
            )
            """
        )
        con.commit()


def add(username: str, album_id: int, quantity: int = 1) -> None:
    """Add an album to the cart or increase quantity."""
    if quantity <= 0:
        return
    _ensure_ready()
    with _connect_sell() as con:
        cur = con.cursor()
        cur.execute(
            """
            INSERT INTO cart (username, album_id, quantity)
            VALUES (?, ?, ?)
            ON CONFLICT(username, album_id)
            DO UPDATE SET quantity = quantity + excluded.quantity
            """,
            (username, int(album_id), int(quantity)),
        )
        con.commit()


def set_qty(username: str, album_id: int, quantity: int) -> None:
    """Override quantity for a cart line."""
    _ensure_ready()
    if quantity <= 0:
        remove(username, album_id)
        return
    with _connect_sell() as con:
        cur = con.cursor()
        cur.execute(
            "UPDATE cart SET quantity = ? WHERE username = ? AND album_id = ?",
            (int(quantity), username, int(album_id)),
        )
        con.commit()


def remove(username: str, album_id: int) -> None:
    """Remove one album from the cart."""
    _ensure_ready()
    with _connect_sell() as con:
        cur = con.cursor()
        cur.execute(
            "DELETE FROM cart WHERE username = ? AND album_id = ?",
            (username, int(album_id)),
        )
        con.commit()


def clear(username: str) -> None:
    """Remove all cart lines for the user."""
    _ensure_ready()
    with _connect_sell() as con:
        cur = con.cursor()
        cur.execute("DELETE FROM cart WHERE username = ?", (username,))
        con.commit()


def count(username: str) -> int:
    """Return total quantity across all cart lines."""
    _ensure_ready()
    with _connect_sell() as con:
        cur = con.cursor()
        row = cur.execute(
            "SELECT COALESCE(SUM(quantity), 0) FROM cart WHERE username = ?",
            (username,),
        ).fetchone()
        return int(row[0] or 0)


def total(username: str) -> float:
    """Return total price after discounts."""
    return pricing(username)["total"]


def items(username: str) -> List[Tuple[int, str, float, int, str]]:
    """
    Return enriched cart items for UI rendering.
    Each tuple is (album_id, title, price, quantity, cover_path).
    """
    _ensure_ready()
    cart_rows = _cart_rows(username)
    if not cart_rows:
        return []

    album_map = _load_albums({row["album_id"] for row in cart_rows})

    enriched: List[Tuple[int, str, float, int, str]] = []
    for row in cart_rows:
        album = album_map.get(row["album_id"])
        if not album:
            continue
        title = album["album_name"]
        if album["version"]:
            title = f"{title} ({album['version']})"
        price = float(album["price"] or 0)
        enriched.append(
            (
                row["album_id"],
                title,
                price,
                row["quantity"],
                album.get("cover_path", "") or "",
            )
        )
    enriched.sort(key=lambda entry: (entry[1].lower(), entry[0]))
    return enriched


def pricing(username: str) -> Dict[str, float]:
    """Compute cart totals, subtotal, discount, and item count."""
    _ensure_ready()
    cart_items = items(username)
    if not cart_items:
        return {
            "item_count": 0,
            "subtotal": 0.0,
            "discount_rate": 0.0,
            "discount": 0.0,
            "total": 0.0,
        }

    subtotal = sum(price * qty for _, _, price, qty, _ in cart_items)
    item_count = sum(qty for _, _, _, qty, _ in cart_items)
    discount_rate = 0.2 if item_count >= 3 else 0.0
    discount = subtotal * discount_rate
    total_value = subtotal - discount

    return {
        "item_count": int(item_count),
        "subtotal": float(subtotal),
        "discount_rate": float(discount_rate),
        "discount": float(discount),
        "total": float(total_value),
    }


def _cart_rows(username: str) -> List[Dict[str, int]]:
    with _connect_sell() as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        rows = cur.execute(
            "SELECT album_id, quantity FROM cart WHERE username = ? ORDER BY id",
            (username,),
        ).fetchall()
        return [dict(row) for row in rows]


def _load_albums(album_ids: Sequence[int]) -> Dict[int, Dict[str, object]]:
    if not album_ids:
        return {}
    if _album_db_path is None:
        raise RuntimeError("Album database path is not configured")
    if not os.path.exists(_album_db_path):
        return {}
    placeholders = ",".join("?" for _ in album_ids)
    con = sqlite3.connect(_album_db_path)
    con.row_factory = sqlite3.Row
    try:
        cur = con.cursor()
        rows = cur.execute(
            f"""
            SELECT id, group_name, album_name, version, price, cover_path
            FROM albums
            WHERE id IN ({placeholders})
            """,
            tuple(album_ids),
        ).fetchall()
        return {row["id"]: dict(row) for row in rows}
    finally:
        con.close()


def order_history(username: str) -> List[Dict[str, Any]]:
    """Return past orders including nested line items."""
    _ensure_ready()
    with _connect_sell() as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        orders = cur.execute(
            """
            SELECT id, created_at, total
            FROM orders
            WHERE username = ?
            ORDER BY datetime(created_at) DESC, id DESC
            """,
            (username,),
        ).fetchall()

        if not orders:
            return []

        order_ids = [row["id"] for row in orders]
        placeholders = ",".join("?" for _ in order_ids)
        order_items_rows = cur.execute(
            f"""
            SELECT order_id, album_id, price, quantity
            FROM order_items
            WHERE order_id IN ({placeholders})
            ORDER BY order_id, id
            """,
            tuple(order_ids),
        ).fetchall()

    album_ids = sorted({row["album_id"] for row in order_items_rows})
    album_map = _load_albums(album_ids)

    items_by_order: Dict[int, List[Dict[str, Any]]] = {row["id"]: [] for row in orders}
    for row in order_items_rows:
        album = album_map.get(row["album_id"])
        if album:
            title = album["album_name"]
            if album.get("version"):
                title = f"{title} ({album['version']})"
            cover_path = album.get("cover_path", "") or ""
            group_name = album.get("group_name", "")
        else:
            title = f"Album #{row['album_id']}"
            cover_path = ""
            group_name = ""

        items_by_order.setdefault(row["order_id"], []).append(
            {
                "album_id": row["album_id"],
                "title": title,
                "group": group_name,
                "price": float(row["price"] or 0),
                "quantity": int(row["quantity"] or 0),
                "cover_path": cover_path,
            }
        )

    history: List[Dict[str, Any]] = []
    for row in orders:
        history.append(
            {
                "order_id": int(row["id"]),
                "created_at": row["created_at"],
                "total": float(row["total"] or 0),
                "items": items_by_order.get(row["id"], []),
            }
        )

    return history


def _ensure_ready() -> None:
    if _sell_db_path is None or _album_db_path is None:
        raise RuntimeError("sell_db.init must be called before using the module")


def _connect_sell() -> sqlite3.Connection:
    if _sell_db_path is None:
        raise RuntimeError("sell_db.init must be called before using the module")
    return sqlite3.connect(_sell_db_path)
