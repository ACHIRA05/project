import os
import sqlite3
import sys
import subprocess
from typing import Dict, List

import customtkinter as ctk
from PIL import Image, ImageOps
from tkinter import messagebox

# --- ตั้งค่าพื้นฐาน ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SELL_DB_PATH = os.path.join(BASE_DIR, "database", "Sell_item.db")
ALBUM_DB_PATH = os.path.join(BASE_DIR, "database", "album_data.db")
QR_IMAGE_PATH = os.path.join(BASE_DIR, "qrcode.jpg")
LOGIN_USERNAME = sys.argv[1] if len(sys.argv) > 1 else "achira"

# --- ธีมสำหรับ CustomTkinter ---
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
PURPLE = "#7B66E3"
BG = "#F7F5FF"
TEXT_DARK = "#2F2A44"

# --- ตัวแปรสถานะของหน้า ---
items_cache: Dict[int, ctk.CTkImage] = {}
placeholder_cache: Dict[tuple[int, int], ctk.CTkImage] = {}
cart_items: List[Dict] = []
cart_calc: Dict[str, float] = {}

# ตัวแปรที่จะถูกกำหนดตอนสร้าง UI
payment: ctk.CTk
items_frame: ctk.CTkScrollableFrame
qr_label: ctk.CTkLabel
subtotal_var: ctk.StringVar
discount_var: ctk.StringVar
total_var: ctk.StringVar
confirm_btn: ctk.CTkButton


def _load_album_info(album_ids: List[int]) -> Dict[int, sqlite3.Row]:
    """ดึงข้อมูลอัลบั้มจากฐานข้อมูลตาม id ที่ให้มา"""
    if not album_ids:
        return {}
    placeholders = ",".join(["?"] * len(album_ids))
    con = sqlite3.connect(ALBUM_DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        cur = con.cursor()
        cur.execute(
            f"""
            SELECT id, album_name, group_name, version, price, cover_path
            FROM albums
            WHERE id IN ({placeholders})
            """,
            album_ids,
        )
        return {row["id"]: row for row in cur.fetchall()}
    finally:
        con.close()


def fetch_cart_items(username: str) -> List[Dict]:
    """อ่านข้อมูลสินค้าในตะกร้า และเติมรายละเอียดอัลบั้ม"""
    con = sqlite3.connect(SELL_DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        cur = con.cursor()
        cur.execute("SELECT album_id, quantity FROM cart WHERE username=?", (username,))
        rows = cur.fetchall()
    finally:
        con.close()

    if not rows:
        return []

    album_ids = [row["album_id"] for row in rows]
    album_map = _load_album_info(album_ids)

    items: List[Dict] = []
    for row in rows:
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
                "group": album["group_name"] or "",
                "cover_path": album["cover_path"],
            }
        )
    return items


def compute_pricing(items: List[Dict]) -> Dict[str, float]:
    """คำนวณยอดรวม ส่วนลด และยอดสุทธิ"""
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
    """บันทึกคำสั่งซื้อและรายการย่อย แล้วล้างตะกร้า"""
    if not items:
        raise ValueError("ไม่พบสินค้าที่ต้องชำระเงิน")
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


def resolve_cover_path(path: str) -> str:
    """พยายามหาที่อยู่รูปภาพจากค่า cover_path ที่อาจเป็น relative"""
    if not path:
        return ""

    candidates = []
    # ค่าเดิม
    candidates.append(os.path.normpath(path))
    # อ้างจากโฟลเดอร์โปรเจกต์
    candidates.append(os.path.normpath(os.path.join(BASE_DIR, path)))
    # อ้างจากโฟลเดอร์ database
    db_dir = os.path.dirname(SELL_DB_PATH)
    candidates.append(os.path.normpath(os.path.join(db_dir, path)))

    # ลองสลับ database/assets กับ assets
    more = []
    for cand in candidates:
        part = os.path.join("database", "assets")
        if part in cand:
            more.append(cand.replace(part, "assets"))
        elif os.path.join("assets") in cand and part not in cand:
            more.append(cand.replace("assets", part, 1))
    candidates.extend(more)

    # ลบ space แปลกๆ
    cleaned = []
    for cand in candidates:
        cand = cand.replace(" _", "_")
        while "  " in cand:
            cand = cand.replace("  ", " ")
        cleaned.append(cand)
    candidates = cleaned

    # ตรวจสอบมีไฟล์จริงหรือไม่
    for cand in candidates:
        if os.path.isfile(cand):
            return cand

    # ลองเปลี่ยนนามสกุล
    exts = [".jpg", ".jpeg", ".png", ".webp", ".JPG", ".JPEG", ".PNG", ".WEBP"]
    for cand in candidates:
        root, ext = os.path.splitext(cand)
        if not ext:
            for e in exts:
                alt = root + e
                if os.path.isfile(alt):
                    return alt
    return ""


def load_image(path: str, size=(80, 80)):
    """โหลดรูปภาพและคืนค่าเป็น CTkImage"""
    real = resolve_cover_path(path)
    if not real:
        return None
    try:
        pic = Image.open(real).convert("RGBA")
    except Exception:
        return None
    pic = ImageOps.contain(pic, size, Image.LANCZOS)
    canvas = Image.new("RGBA", size, (255, 255, 255, 0))
    canvas.paste(pic, ((size[0] - pic.width) // 2, (size[1] - pic.height) // 2), pic)
    return ctk.CTkImage(light_image=canvas, dark_image=canvas, size=size)


def load_placeholder(size=(68, 68)) -> ctk.CTkImage:
    """สร้างรูป placeholder สีม่วงอ่อนเพื่อใช้แทนหากไม่มีรูป"""
    key = (size[0], size[1])
    if key in placeholder_cache:
        return placeholder_cache[key]
    pic = Image.new("RGBA", size, (226, 214, 255, 255))
    placeholder = ctk.CTkImage(light_image=pic, dark_image=pic, size=size)
    placeholder_cache[key] = placeholder
    return placeholder


# --- ฟังก์ชันจัดการ UI ---
def add_summary_row(parent: ctk.CTkFrame, title: str, variable: ctk.StringVar, bold: bool = False) -> None:
    """เพิ่มแถวสรุปตัวเลขด้านขวา"""
    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", padx=14, pady=6)
    font = ("Mitr", 16, "bold") if bold else ("Mitr", 16)
    ctk.CTkLabel(row, text=title, font=font, text_color=TEXT_DARK).pack(side="left")
    ctk.CTkLabel(row, textvariable=variable, font=font, text_color=TEXT_DARK).pack(side="right")


def render_items() -> None:
    """สร้างรายการสินค้าในตะกร้าใหม่ทั้งหมด"""
    for widget in items_frame.winfo_children():
        widget.destroy()

    if not cart_items:
        ctk.CTkLabel(
            items_frame,
            text="ไม่มีสินค้าในตะกร้า",
            text_color="#7F7C98",
            font=("Mitr", 18),
        ).pack(pady=40)
        return

    for item in cart_items:
        row = ctk.CTkFrame(items_frame, fg_color="white")
        row.pack(fill="x", padx=12, pady=8)

        img = items_cache.get(item["album_id"])
        if not img:
            img = load_image(item["cover_path"], size=(68, 68))
            if img:
                items_cache[item["album_id"]] = img
        if not img:
            img = load_placeholder((68, 68))

        img_label = ctk.CTkLabel(row, image=img, text="")
        img_label.image = img
        img_label.pack(side="left", padx=10, pady=10)

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


def update_totals() -> None:
    """อัปเดตข้อความสรุปยอดรวม"""
    subtotal_var.set(f"{cart_calc.get('subtotal', 0):,.0f} บาท")
    discount = cart_calc.get("discount", 0)
    discount_var.set(f"-{discount:,.0f} บาท" if discount else "0 บาท")
    total_var.set(f"{cart_calc.get('total', 0):,.0f} บาท")


def load_qr_image() -> None:
    """แสดง QR code สำหรับชำระเงิน"""
    qr = load_image(QR_IMAGE_PATH, size=(180, 180))
    if qr:
        qr_label.configure(image=qr, text="")
        qr_label.image = qr
    else:
        qr_label.configure(image=None, text="ไม่พบไฟล์ QR Code", font=("Mitr", 14), text_color="#999")
        qr_label.image = None


def refresh_data() -> None:
    """โหลดข้อมูลใหม่และรีเฟรชหน้าจอ"""
    global cart_items, cart_calc
    cart_items = fetch_cart_items(LOGIN_USERNAME)
    cart_calc = compute_pricing(cart_items) if cart_items else {
        "subtotal": 0,
        "total_qty": 0,
        "discount_rate": 0,
        "discount": 0,
        "total": 0,
    }
    render_items()
    update_totals()
    load_qr_image()
    confirm_btn.configure(state="normal" if cart_items else "disabled")


def open_history_app() -> None:
    """เปิดหน้าประวัติการสั่งซื้อ"""
    script_path = os.path.join(BASE_DIR, "page", "history.py")
    args = [sys.executable, script_path, LOGIN_USERNAME]
    subprocess.Popen(args)


def on_confirm() -> None:
    """เมื่อผู้ใช้กดยืนยันการชำระเงิน"""
    if not cart_items:
        return
    confirm_btn.configure(state="disabled")
    try:
        order_id = record_order(LOGIN_USERNAME, cart_items, cart_calc["total"])
    except Exception as exc:
        confirm_btn.configure(state="normal")
        messagebox.showerror(title="เกิดข้อผิดพลาด", message=str(exc))
        return
    refresh_data()
    open_success_dialog(order_id)


def open_success_dialog(order_id: int) -> None:
    """แสดงหน้าต่างสำเร็จหลังบันทึกคำสั่งซื้อ"""
    win = ctk.CTkToplevel(payment)
    win.title("ชำระเงินสำเร็จ")
    win.geometry("420x360+960+360")
    win.transient(payment)
    win.grab_set()
    win.configure(fg_color=BG)

    ctk.CTkLabel(win, text="ชำระเงินสำเร็จ!", font=("Mitr", 28, "bold"), text_color=TEXT_DARK).pack(pady=(36, 12))
    ctk.CTkLabel(
        win,
        text=f"รหัสคำสั่งซื้อ #{order_id}\nสามารถตรวจสอบประวัติได้ตลอดเวลา",
        font=("Mitr", 16),
        text_color="#5C5875",
        justify="center",
    ).pack(pady=(0, 24))

    btn_area = ctk.CTkFrame(win, fg_color="transparent")
    btn_area.pack(fill="x", expand=True, padx=30)

    def _view_history():
        try:
            win.grab_release()
        except Exception:
            pass
        win.destroy()
        open_history_app()

    ctk.CTkButton(
        btn_area,
        text="ดูประวัติการสั่งซื้อ",
        font=("Mitr", 16, "bold"),
        fg_color=PURPLE,
        height=42,
        command=_view_history,
    ).pack(fill="x", pady=(0, 12))

    ctk.CTkButton(
        btn_area,
        text="กลับหน้าหลัก",
        font=("Mitr", 16),
        fg_color="#D5D2EE",
        text_color=TEXT_DARK,
        height=40,
        command=lambda: (win.destroy(), payment.destroy()),
    ).pack(fill="x")


# --- สร้างหน้าจอหลัก ---
def build_layout() -> None:
    """ประกอบ UI หลักของหน้า"""
    global payment, items_frame, qr_label, subtotal_var, discount_var, total_var, confirm_btn

    payment = ctk.CTk()
    payment.title("ชำระเงิน")
    payment.geometry("900x620")
    payment.configure(fg_color=PURPLE)

    shell = ctk.CTkFrame(payment, fg_color=BG, corner_radius=20)
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

    items_frame = ctk.CTkScrollableFrame(content, fg_color="white", corner_radius=16, width=520, height=420)
    items_frame.pack(side="left", fill="both", expand=True, padx=(0, 12), pady=6)

    summary = ctk.CTkFrame(content, fg_color="white", corner_radius=16, width=260)
    summary.pack(side="right", fill="y", padx=(12, 0), pady=6)

    ctk.CTkLabel(summary, text="ชำระเงิน", font=("Mitr", 24, "bold"), text_color=TEXT_DARK).pack(pady=(18, 4))
    ctk.CTkLabel(summary, text="สแกนเพื่อชำระ", font=("Mitr", 16), text_color="#555").pack()

    qr_label = ctk.CTkLabel(summary, text="")
    qr_label.pack(pady=12)

    subtotal_var = ctk.StringVar(value="0 บาท")
    discount_var = ctk.StringVar(value="0 บาท")
    total_var = ctk.StringVar(value="0 บาท")

    summary_box = ctk.CTkFrame(summary, fg_color=BG, corner_radius=14)
    summary_box.pack(fill="x", padx=18, pady=(10, 18))
    add_summary_row(summary_box, "ยอดรวมสินค้า", subtotal_var)
    add_summary_row(summary_box, "ส่วนลด", discount_var)
    add_summary_row(summary_box, "ยอดที่ต้องชำระ", total_var, bold=True)

    confirm_btn = ctk.CTkButton(
        summary,
        text="ยืนยันการชำระเงิน",
        font=("Mitr", 18, "bold"),
        fg_color=PURPLE,
        height=48,
        command=on_confirm,
    )
    confirm_btn.pack(fill="x", padx=18, pady=(0, 12))

    ctk.CTkButton(
        summary,
        text="กลับไปหน้าหลัก",
        font=("Mitr", 16),
        fg_color="#D5D2EE",
        text_color=TEXT_DARK,
        height=40,
        command=payment.destroy,
    ).pack(fill="x", padx=18, pady=(0, 18))


# --- จุดเริ่มต้นของโปรแกรม ---
def main() -> None:
    build_layout()
    refresh_data()
    payment.mainloop()


if __name__ == "__main__":
    main()
