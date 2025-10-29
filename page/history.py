import os,sys,subprocess
from typing import Dict, List
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageOps

# --- ตั้งค่าพื้นฐาน ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database import sell_db

SELL_DB_PATH = os.path.join(PROJECT_ROOT, "database", "Sell_item.db")
ALBUM_DB_PATH = os.path.join(PROJECT_ROOT, "database", "album_data.db")

sell_db.init(sell_db_path=SELL_DB_PATH, album_db_path=ALBUM_DB_PATH)

LOGIN_USERNAME = sys.argv[1] if len(sys.argv) > 1 else "achira"

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# --- เครื่องมือเกี่ยวกับรูปภาพ ---
def resolve_cover_path(path: str) -> str:
    if not path:
        return ""

    candidates = [
        os.path.normpath(path),
        os.path.normpath(os.path.join(PROJECT_ROOT, path)),
        os.path.normpath(os.path.join(os.path.dirname(SELL_DB_PATH), path)),
    ]

    more = []
    part = os.path.join("database", "assets")
    for cand in candidates:
        if part in cand:
            more.append(cand.replace(part, "assets"))
        elif os.path.join("assets") in cand and part not in cand:
            more.append(cand.replace("assets", part, 1))
    candidates.extend(more)

    cleaned = []
    for cand in candidates:
        cand = cand.replace(" _", "_")
        while "  " in cand:
            cand = cand.replace("  ", " ")
        cleaned.append(cand)
    candidates = cleaned

    for cand in candidates:
        if os.path.isfile(cand):
            return cand

    exts = [".jpg", ".jpeg", ".png", ".webp", ".JPG", ".JPEG", ".PNG", ".WEBP"]
    for cand in candidates:
        root, ext = os.path.splitext(cand)
        if not ext:
            for e in exts:
                alt = root + e
                if os.path.isfile(alt):
                    return alt
    return ""

def load_image(path: str, size=(60, 60)) -> ctk.CTkImage | None:
    real = resolve_cover_path(path)
    if not real:
        return None

    cache = load_image._cache
    key = (real, size)
    if key in cache:
        return cache[key]

    try:
        pic = Image.open(real).convert("RGBA")
    except Exception:
        cache[key] = None
        return None
    pic = ImageOps.contain(pic, size, Image.LANCZOS)
    canvas = Image.new("RGBA", size, (255, 255, 255, 0))
    canvas.paste(pic, ((size[0] - pic.width) // 2, (size[1] - pic.height) // 2), pic)
    img = ctk.CTkImage(light_image=canvas, dark_image=canvas, size=size)
    cache[key] = img
    return img


load_image._cache = {}


def load_placeholder(size=(60, 60)) -> ctk.CTkImage:
    cache = load_placeholder._cache
    key = (size[0], size[1])
    if key in cache:
        return cache[key]
    pic = Image.new("RGBA", size, (226, 214, 255, 255))
    img = ctk.CTkImage(light_image=pic, dark_image=pic, size=size)
    cache[key] = img
    return img

load_placeholder._cache = {}

# --- จัดการข้อมูล ---
def refresh_history() -> List[Dict]:
    orders = sell_db.order_history(LOGIN_USERNAME)
    render_history(orders)
    return orders

# --- สร้าง UI สำหรับรายการ ---
def render_history(orders: List[Dict]) -> None:
    header_count.configure(text=f"รวม {len(orders)} รายการ")

    for child in history_body.winfo_children():
        child.destroy()

    if not orders:
        ctk.CTkLabel(
            history_body,
            text="ยังไม่มีประวัติการสั่งซื้อ",
            font=("Mitr", 16),
            text_color="#6D6A86",
        ).pack(pady=40)
        return

    for order in orders:
        card = ctk.CTkFrame(history_body, fg_color="#F0ECFF", corner_radius=12)
        card.pack(fill="x", padx=10, pady=8)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=12, pady=(10, 4))
        ctk.CTkLabel(top, text=f"คำสั่งซื้อ #{order['order_id']}", font=("Mitr", 18)).pack(side="left")
        ctk.CTkLabel(top, text=order["created_at"], font=("Mitr", 13), text_color="#6D6A86").pack(side="right")

        for item in order["items"]:
            line = ctk.CTkFrame(card, fg_color="transparent")
            line.pack(fill="x", padx=12, pady=4)

            cover_path = item.get("cover_path", "")
            img = load_image(cover_path, size=(56, 56))
            if img is None:
                img = load_placeholder((56, 56))

            img_label = ctk.CTkLabel(line, image=img, text="")
            img_label.image = img
            img_label.pack(side="left", padx=6, pady=6)

            info = ctk.CTkFrame(line, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, padx=8)
            ctk.CTkLabel(info, text=item["title"], font=("Mitr", 15)).pack(anchor="w")

            detail = f"{item['quantity']} ชิ้น x {item['price']:,.0f} บาท"
            group = item.get("group")
            if group:
                detail = f"{group} • {detail}"
            ctk.CTkLabel(info, text=detail, font=("Mitr", 13), text_color="#6D6A86").pack(anchor="w")

        ctk.CTkLabel(
            card,
            text=f"ยอดรวม {order['total']:,.0f} บาท",
            font=("Mitr", 16, "bold"),
            text_color="#2F2A44",
        ).pack(anchor="e", padx=12, pady=(0, 10))

# --- สร้างหน้าจอหลัก ---
history_win = ctk.CTk()
history_win.title("ประวัติการสั่งซื้อ")
history_win.geometry("720x560+900+260")
history_win.configure(fg_color="#dac5ff")

header = ctk.CTkFrame(history_win, fg_color="transparent")
header.pack(fill="x", padx=18, pady=(18, 8))

row = ctk.CTkFrame(header, fg_color="transparent")
row.pack(fill="x")

def back_main():
    arg = [sys.executable,r"C:\Python\project\page\main.py"]
    p = subprocess.Popen(arg)
    history_win.after(800, history_win.destroy)

ctk.CTkLabel(row, text="ประวัติการสั่งซื้อ", font=("Mitr", 24, "bold")).pack(side="left")
ctk.CTkButton(
    row,
    text="ย้อนกลับ",width=110,fg_color="#D5D2EE",text_color="#2F2A44",hover_color="#C2BDE0",  
    font=("Mitr", 16),command=back_main).pack(side="right")

header_count = ctk.CTkLabel(header, text="รวม 0 รายการ", font=("Mitr", 14), text_color="#6D6A86")
header_count.pack(anchor="w")

history_body = ctk.CTkScrollableFrame(history_win, fg_color="white", corner_radius=16)
history_body.pack(fill="both", expand=True, padx=18, pady=(0, 18))

# จัดวาง panel
def layout_panel(final=False):
    global _last_panel_size
    w = max(history_win.winfo_width(),  400)
    h = max(history_win.winfo_height(), 300)
    header.update_idletasks()
    need_w = header.winfo_reqwidth()
    need_h = header.winfo_reqheight()
    panel_w = max(min(int(w * 0.86), w - 40), need_w)
    panel_h = max(min(int(h * 0.78), h - 40), need_h)

    PADDING_X = 80
    PADDING_Y = 120

    inner_w = max(panel_w - PADDING_X, need_w)
    inner_h = max(panel_h - PADDING_Y, need_h)

# ---------- Fullscreen toggle (F11 / ESC) ----------
_fullscreen_state = {"value": False, "geometry": None}

# เลื่อนการจัดวาง layout ไปทำทีหลัง
def _apply_layout_later():
    history_win.after(20, lambda: layout_panel(final=True))
    
def _enter_fullscreen():
    if _fullscreen_state["value"]:
        return
    _fullscreen_state["value"] = True
    _fullscreen_state["geometry"] = history_win.winfo_geometry()
    try:
        history_win.state("zoomed")
    except tk.TclError:
        pass
    history_win.attributes("-fullscreen", True)
    history_win.geometry(f"{history_win.winfo_screenwidth()}x{history_win.winfo_screenheight()}+0+0")
    _apply_layout_later()

def _leave_fullscreen():
    if not _fullscreen_state["value"]:
        return
    _fullscreen_state["value"] = False
    history_win.attributes("-fullscreen", False)
    try:
        history_win.state("normal")
    except tk.TclError:
        pass
    if _fullscreen_state["geometry"]:
        history_win.geometry("1000x600")
    _apply_layout_later()

def _toggle_fullscreen(event=None):
    if _fullscreen_state["value"]:
        _leave_fullscreen()
    else:
        _enter_fullscreen()
    return "break"

def _exit_fullscreen(event=None):
    _leave_fullscreen()
    return "break"

def _on_escape_quit(event=None):
    # ปิดแอปทั้งโปรแกรม
    try:
        history_win.destroy()
    except Exception:
        history_win.quit()
    return "break"
history_win.bind("<F11>", _toggle_fullscreen)
history_win.bind("<Escape>", _on_escape_quit),_exit_fullscreen()

# เริ่มในโหมด fullscreen 
_force_full = "--start-fullscreen" in sys.argv
_want_windowed = "--windowed" in sys.argv
if _force_full or not _want_windowed:
    history_win.after(0, _enter_fullscreen)  

refresh_history()
history_win.mainloop()


