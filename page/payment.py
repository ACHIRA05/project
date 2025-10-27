import os
import sqlite3
import sys
from typing import Dict, List, Optional

import customtkinter as ctk
from PIL import Image
from tkinter import messagebox

# -------- CONFIG --------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SELL_DB_PATH = os.path.join(BASE_DIR, "database", "Sell_item.db")
ALBUM_DB_PATH = os.path.join(BASE_DIR, "database", "album_data.db")
QR_IMAGE_PATH = os.path.join(BASE_DIR, "qrcode.jpg")

LOGIN_USERNAME = sys.argv[1] if len(sys.argv) > 1 else "achira"

# -------- THEME --------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
PURPLE = "#7B66E3"
BG = "#F7F5FF"
TEXT_DARK = "#2F2A44"


# -------- DATA HELPERS --------
def _query_cart(username: str) -> List[sqlite3.Row]:
    """Return items (album_id, quantity) from the cart."""
    con = sqlite3.connect(SELL_DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS cart (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, album_id INTEGER, quantity INTEGER DEFAULT 1)")
        cur.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')), total REAL NOT NULL DEFAULT 0)")
        cur.execute("CREATE TABLE IF NOT EXISTS order_items (id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER NOT NULL, album_id INTEGER NOT NULL, price REAL NOT NULL, quantity INTEGER NOT NULL)")
        cur.execute("SELECT album_id, quantity FROM cart WHERE username=?", (username,))
        return cur.fetchall()
    finally:
        con.close()


def _load_album_info(album_ids: List[int]) -> Dict[int, sqlite3.Row]:
    """Return album metadata keyed by album id."""
    if not album_ids:
        return {}
    placeholders = ",".join(["?"] * len(album_ids))
    con = sqlite3.connect(ALBUM_DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        cur = con.cursor()
        cur.execute(f"""
            SELECT id, album_name, group_name, version, price, cover_path
            FROM albums
            WHERE id IN ({placeholders})
        """, album_ids)
        return {row["id"]: row for row in cur.fetchall()}
    finally:
        con.close()


def fetch_cart_items(username: str) -> List[Dict]:
    """Return cart records enriched with album information."""
    cart_rows = _query_cart(username)
    if not cart_rows:
        return []

    album_ids = [row["album_id"] for row in cart_rows]
    album_map = _load_album_info(album_ids)

    items: List[Dict] = []
    for row in cart_rows:
        album = album_map.get(row["album_id"])
        if not album:
            continue
        title = album["album_name"]
        if album["version"]:
            title = f"{title} ({album['version']})"
        items.append(
            {
                "album_id": row["album_id"],
                "quantity": row["quantity"],
                "price": album["price"] or 0,
                "title": title,
                "group": album["group_name"],
                "cover_path": album["cover_path"],
            }
        )
    return items


def compute_pricing(items: List[Dict]) -> Dict[str, float]:
    """Calculate subtotal, discount, and total based on promotion rules."""
    subtotal = sum(item["price"] * item["quantity"] for item in items)
    total_qty = sum(item["quantity"] for item in items)
    discount_rate = 0.2 if total_qty >= 3 else 0.0
    discount = subtotal * discount_rate
    total = subtotal - discount
    return {
        "subtotal": subtotal,
        "total_qty": total_qty,
        "discount_rate": discount_rate,
        "discount": discount,
        "total": total,
    }


def record_order(username: str, items: List[Dict], total: float) -> int:
    """Persist an order and its items. Returns the new order id."""
    if not items:
        raise ValueError("Cannot create order without items.")
    con = sqlite3.connect(SELL_DB_PATH)
    try:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO orders(username, total) VALUES (?, ?)",
            (username, round(total, 2)),
        )
        order_id = cur.lastrowid
        for item in items:
            cur.execute(
                """
                INSERT INTO order_items(order_id, album_id, price, quantity)
                VALUES (?,?,?,?)
                """,
                (order_id, item["album_id"], item["price"], item["quantity"]),
            )
        cur.execute("DELETE FROM cart WHERE username=?", (username,))
        con.commit()
        return order_id
    finally:
        con.close()


def fetch_order_history(username: str) -> List[Dict]:
    """Return order history including nested items."""
    con = sqlite3.connect(SELL_DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        cur = con.cursor()
        cur.execute(
            "SELECT id, created_at, total FROM orders WHERE username=? ORDER BY created_at DESC",
            (username,),
        )
        orders = cur.fetchall()
        if not orders:
            return []

        order_ids = [row["id"] for row in orders]
        placeholders = ",".join(["?"] * len(order_ids))
        cur.execute(
            f"""
            SELECT order_id, album_id, price, quantity
            FROM order_items
            WHERE order_id IN ({placeholders})
            """,
            order_ids,
        )
        order_items_rows = cur.fetchall()
    finally:
        con.close()

    album_ids = [row["album_id"] for row in order_items_rows]
    album_map = _load_album_info(album_ids)

    items_by_order: Dict[int, List[Dict]] = {row["id"]: [] for row in orders}
    for row in order_items_rows:
        album = album_map.get(row["album_id"])
        title = f"{album['album_name']} ({album['version']})" if album and album["version"] else (album["album_name"] if album else f"Album #{row['album_id']}")
        items_by_order.setdefault(row["order_id"], []).append(
            {
                "title": title,
                "group": album["group_name"] if album else "",
                "price": row["price"],
                "quantity": row["quantity"],
            }
        )

    history: List[Dict] = []
    for row in orders:
        history.append(
            {
                "order_id": row["id"],
                "created_at": row["created_at"],
                "total": row["total"],
                "items": items_by_order.get(row["id"], []),
            }
        )
    return history


def load_image(path: str, size=(80, 80)):
    """Load an image from disk into a CTkImage."""
    if not path or not os.path.exists(path):
        return None
    try:
        pil = Image.open(path)
    except Exception:
        return None
    pil = pil.resize(size, Image.LANCZOS)
    return ctk.CTkImage(light_image=pil, dark_image=pil, size=size)


# -------- UI --------
class PaymentApp(ctk.CTk):
    def __init__(self, username: str):
        super().__init__()
        self.username = username
        self.title("ชำระเงิน")
        self.geometry("900x620")
        self.configure(fg_color=PURPLE)

        self._images_cache: Dict[int, ctk.CTkImage] = {}
        self.items: List[Dict] = []
        self.calc: Dict[str, float] = {}

        self._build_layout()
        self.refresh()

    # ---- Layout ----
    def _build_layout(self):
        shell = ctk.CTkFrame(self, fg_color=BG, corner_radius=20)
        shell.pack(fill="both", expand=True, padx=30, pady=26)

        header = ctk.CTkFrame(shell, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(header, text="ตรวจสอบคำสั่งซื้อ", font=("Mitr", 32, "bold"), text_color=TEXT_DARK).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="ตรวจสอบสินค้าและสแกน QR เพื่อชำระเงิน",
            font=("Mitr", 16),
            text_color="#5C5875",
        ).pack(anchor="w")

        content = ctk.CTkFrame(shell, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=18, pady=4)

        # cart-style list
        self.items_frame = ctk.CTkScrollableFrame(
            content, fg_color="white", corner_radius=16, width=520, height=420
        )
        self.items_frame.pack(side="left", fill="both", expand=True, padx=(0, 12), pady=6)

        # summary
        self.summary = ctk.CTkFrame(content, fg_color="white", corner_radius=16, width=260)
        self.summary.pack(side="right", fill="y", padx=(12, 0), pady=6)

        ctk.CTkLabel(self.summary, text="ชำระเงิน", font=("Mitr", 24, "bold"), text_color=TEXT_DARK).pack(pady=(18, 4))
        ctk.CTkLabel(self.summary, text="สแกนเพื่อชำระ", font=("Mitr", 16), text_color="#555").pack()

        self.qr_label = ctk.CTkLabel(self.summary, text="")
        self.qr_label.pack(pady=12)

        # totals
        self.subtotal_var = ctk.StringVar(value="0")
        self.discount_var = ctk.StringVar(value="0")
        self.total_var = ctk.StringVar(value="0")

        summary_box = ctk.CTkFrame(self.summary, fg_color=BG, corner_radius=14)
        summary_box.pack(fill="x", padx=18, pady=(10, 18))
        self._add_summary_row(summary_box, "ยอดรวมสินค้า", self.subtotal_var)
        self._add_summary_row(summary_box, "ส่วนลด", self.discount_var)
        self._add_summary_row(summary_box, "ยอดที่ต้องชำระ", self.total_var, bold=True)

        self.confirm_btn = ctk.CTkButton(
            self.summary,
            text="ยืนยันการชำระเงิน",
            font=("Mitr", 18, "bold"),
            fg_color=PURPLE,
            height=48,
            command=self._on_confirm,
        )
        self.confirm_btn.pack(fill="x", padx=18, pady=(0, 12))

        self.back_btn = ctk.CTkButton(
            self.summary,
            text="กลับไปหน้าหลัก",
            font=("Mitr", 16),
            fg_color="#D5D2EE",
            text_color=TEXT_DARK,
            height=40,
            command=self.destroy,
        )
        self.back_btn.pack(fill="x", padx=18, pady=(0, 18))

    def _add_summary_row(self, parent, title: str, variable: ctk.StringVar, bold: bool = False):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=6)
        font = ("Mitr", 16, "bold") if bold else ("Mitr", 16)
        ctk.CTkLabel(row, text=title, font=font, text_color=TEXT_DARK).pack(side="left")
        ctk.CTkLabel(row, textvariable=variable, font=font, text_color=TEXT_DARK).pack(side="right")

    # ---- Data refresh ----
    def refresh(self):
        self.items = fetch_cart_items(self.username)
        self.calc = compute_pricing(self.items) if self.items else {
            "subtotal": 0,
            "total_qty": 0,
            "discount_rate": 0,
            "discount": 0,
            "total": 0,
        }
        self._render_items()
        self._update_totals()
        self._load_qr()
        self.confirm_btn.configure(state="normal" if self.items else "disabled")

    def _render_items(self):
        for child in self.items_frame.winfo_children():
            child.destroy()

        if not self.items:
            ctk.CTkLabel(
                self.items_frame,
                text="ไม่มีสินค้าในตะกร้า",
                text_color="#7F7C98",
                font=("Mitr", 18),
            ).pack(pady=40)
            return

        for item in self.items:
            row = ctk.CTkFrame(self.items_frame, fg_color="white")
            row.pack(fill="x", padx=12, pady=8)

            img = self._images_cache.get(item["album_id"])
            if not img:
                img = load_image(item["cover_path"], size=(68, 68))
                if img:
                    self._images_cache[item["album_id"]] = img
            if img:
                ctk.CTkLabel(row, image=img, text="").pack(side="left", padx=10, pady=10)

            info = ctk.CTkFrame(row, fg_color="white")
            info.pack(side="left", fill="x", expand=True, padx=4, pady=6)
            ctk.CTkLabel(info, text=item["title"], font=("Mitr", 18, "bold"), text_color=TEXT_DARK).pack(anchor="w")
            ctk.CTkLabel(
                info,
                text=f"{item['group']} • จำนวน {item['quantity']} ชิ้น",
                font=("Mitr", 14),
                text_color="#6D6A86",
            ).pack(anchor="w")

            price_area = ctk.CTkFrame(row, fg_color="white")
            price_area.pack(side="right", padx=10, pady=10)
            ctk.CTkLabel(
                price_area,
                text=f"{item['price'] * item['quantity']:,.0f} บาท",
                font=("Mitr", 18, "bold"),
                text_color=TEXT_DARK,
            ).pack()

    def _update_totals(self):
        self.subtotal_var.set(f"{self.calc['subtotal']:,.0f} บาท")
        discount_text = f"-{self.calc['discount']:,.0f} บาท" if self.calc["discount"] else "0 บาท"
        self.discount_var.set(discount_text)
        self.total_var.set(f"{self.calc['total']:,.0f} บาท")

    def _load_qr(self):
        qr = load_image(QR_IMAGE_PATH, size=(180, 180))
        if qr:
            self.qr_label.configure(image=qr, text="")
            self.qr_label.image = qr
        else:
            self.qr_label.configure(image=None, text="????? QR Code", font=("Mitr", 14), text_color="#999")
            self.qr_label.image = None

    # ---- Confirm flow ----
    def _on_confirm(self):
        if not self.items:
            return
        self.confirm_btn.configure(state="disabled")
        try:
            order_id = record_order(self.username, self.items, self.calc["total"])
        except Exception as exc:
            self.confirm_btn.configure(state="normal")
            messagebox.showerror(title="เกิดข้อผิดพลาด", message=str(exc))
            return
        self.refresh()
        self._open_success_dialog(order_id)

    def _open_success_dialog(self, order_id: int):
        dialog = ctk.CTkToplevel(self)
        dialog.title("ชำระเงินสำเร็จ")
        dialog.geometry("420x360+960+360")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color=BG)

        ctk.CTkLabel(dialog, text="ชำระเงินสำเร็จ!", font=("Mitr", 28, "bold"), text_color=TEXT_DARK).pack(pady=(36, 12))
        ctk.CTkLabel(
            dialog,
            text=f"รหัสคำสั่งซื้อ #{order_id}\nสามารถตรวจสอบประวัติได้ตลอดเวลา",
            font=("Mitr", 16),
            text_color="#5C5875",
            justify="center",
        ).pack(pady=(0, 24))

        btn_area = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_area.pack(fill="x", expand=True, padx=30)

        ctk.CTkButton(
            btn_area,
            text="ดูประวัติการสั่งซื้อ",
            font=("Mitr", 16, "bold"),
            fg_color=PURPLE,
            height=42,
            command=lambda: self._open_history(dialog),
        ).pack(fill="x", pady=(0, 12))

        ctk.CTkButton(
            btn_area,
            text="กลับหน้าหลัก",
            font=("Mitr", 16),
            fg_color="#D5D2EE",
            text_color=TEXT_DARK,
            height=40,
            command=lambda: (dialog.destroy(), self.destroy()),
        ).pack(fill="x")

    def _open_history(self, parent: Optional[ctk.CTkToplevel] = None):
        if parent:
            parent.grab_release()
            parent.destroy()

        history_win = ctk.CTkToplevel(self)
        history_win.title("ประวัติการสั่งซื้อ")
        history_win.geometry("640x520+940+320")
        history_win.configure(fg_color=BG)
        history_win.transient(self)
        history_win.grab_set()

        ctk.CTkLabel(
            history_win,
            text="ประสพการณ์การสั่งซื้อ",
            font=("Mitr", 26, "bold"),
            text_color=TEXT_DARK,
        ).pack(pady=(24, 6))
        ctk.CTkLabel(
            history_win,
            text="รวบรวมคำสั่งซื้อทั้งหมดของคุณ",
            font=("Mitr", 14),
            text_color="#6D6A86",
        ).pack()

        body = ctk.CTkScrollableFrame(history_win, fg_color="white", corner_radius=16, width=580)
        body.pack(fill="both", expand=True, padx=20, pady=20)

        history = fetch_order_history(self.username)
        if not history:
            ctk.CTkLabel(body, text="ยังไม่มีประวัติการสั่งซื้อ", font=("Mitr", 16), text_color="#7F7C98").pack(pady=40)
            return

        for order in history:
            card = ctk.CTkFrame(body, fg_color=BG, corner_radius=14)
            card.pack(fill="x", padx=10, pady=8)

            header = ctk.CTkFrame(card, fg_color="transparent")
            header.pack(fill="x", padx=14, pady=(12, 4))
            ctk.CTkLabel(
                header,
                text=f"คำสั่งซื้อ #{order['order_id']}",
                font=("Mitr", 18, "bold"),
                text_color=TEXT_DARK,
            ).pack(side="left")
            ctk.CTkLabel(
                header,
                text=order["created_at"],
                font=("Mitr", 14),
                text_color="#6D6A86",
            ).pack(side="right")

            for item in order["items"]:
                line = ctk.CTkFrame(card, fg_color="transparent")
                line.pack(fill="x", padx=18, pady=4)
                ctk.CTkLabel(line, text=item["title"], font=("Mitr", 14), text_color=TEXT_DARK).pack(anchor="w")
                ctk.CTkLabel(
                    line,
                    text=f"{item['quantity']} ชิ้น • {item['price']:,.0f} บาท/ชิ้น",
                    font=("Mitr", 13),
                    text_color="#6D6A86",
                ).pack(anchor="w")

            ctk.CTkLabel(
                card,
                text=f"ยอดรวม {order['total']:,.0f} บาท",
                font=("Mitr", 16, "bold"),
                text_color=TEXT_DARK,
            ).pack(anchor="e", padx=18, pady=(0, 12))


if __name__ == "__main__":
    app = PaymentApp(LOGIN_USERNAME)
    app.mainloop()
