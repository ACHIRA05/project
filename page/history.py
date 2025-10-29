import os
import sys
from typing import Dict, List

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

# --- ตัวแปรสถานะของหน้า ---
orders_data: List[Dict] = []
cover_cache: Dict[str, ctk.CTkImage] = {}
placeholder_cache: Dict[tuple[int, int], ctk.CTkImage] = {}

def layout_panel(final=False):
    global _last_panel_size
    w = max(Login.winfo_width(),  400)
    h = max(Login.winfo_height(), 300)
    resize_bg(w, h, final=final)
    container.update_idletasks()
    need_w = container.winfo_reqwidth()
    need_h = container.winfo_reqheight()
    panel_w = max(min(int(w * 0.86), w - 40), need_w)
    panel_h = max(min(int(h * 0.78), h - 40), need_h)
    panel_w, panel_h = _rounded_size(panel_w, panel_h)
    if (panel_w, panel_h) != _last_panel_size:
        key = (panel_w, panel_h)
        if key in _panel_cache:
            img = _panel_cache[key]
        else:
            img = ImageTk.PhotoImage(make_panel_img(panel_w, panel_h,
                                                    radius=28, border=12,
                                                    outer="#BFAEF7", inner=BG_SOFT))
            _panel_cache[key] = img
        canvas.itemconfigure(panel_id, image=img)
        canvas.panel_img = img
        _last_panel_size = (panel_w, panel_h)
    cx, cy = w // 2, h // 2
    canvas.coords(panel_id, cx, cy)

    PADDING_X = 80
    PADDING_Y = 120

    inner_w = max(panel_w - PADDING_X, need_w)
    inner_h = max(panel_h - PADDING_Y, need_h)
    canvas.coords(container_win, cx, cy)
    canvas.itemconfigure(container_win, width=inner_w, height=inner_h)

# ---------- Fullscreen toggle (F11 / ESC) ----------
_fullscreen_state = {"value": False, "geometry": None}
def _apply_layout_later():
    Login.after(20, lambda: layout_panel(final=True))
    
def _enter_fullscreen():
    if _fullscreen_state["value"]:
        return
    _fullscreen_state["value"] = True
    _fullscreen_state["geometry"] = Login.winfo_geometry()
    try:
        Login.state("zoomed")
    except tk.TclError:
        pass
    Login.attributes("-fullscreen", True)
    Login.geometry(f"{Login.winfo_screenwidth()}x{Login.winfo_screenheight()}+0+0")
    _apply_layout_later()

def _leave_fullscreen():
    if not _fullscreen_state["value"]:
        return
    _fullscreen_state["value"] = False
    Login.attributes("-fullscreen", False)
    try:
        Login.state("normal")
    except tk.TclError:
        pass
    if _fullscreen_state["geometry"]:
        Login.geometry(_fullscreen_state["geometry"])
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
Login.bind("<F11>", _toggle_fullscreen)
Login.bind("<Escape>", _exit_fullscreen)
_force_full = "--start-fullscreen" in sys.argv
_want_windowed = "--windowed" in sys.argv
if _force_full or not _want_windowed:
    Login.after(0, _enter_fullscreen)

history_win: ctk.CTk
history_body: ctk.CTkScrollableFrame
header_count: ctk.CTkLabel


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
    try:
        pic = Image.open(real).convert("RGBA")
    except Exception:
        return None
    pic = ImageOps.contain(pic, size, Image.LANCZOS)
    canvas = Image.new("RGBA", size, (255, 255, 255, 0))
    canvas.paste(pic, ((size[0] - pic.width) // 2, (size[1] - pic.height) // 2), pic)
    return ctk.CTkImage(light_image=canvas, dark_image=canvas, size=size)


def load_placeholder(size=(60, 60)) -> ctk.CTkImage:
    key = (size[0], size[1])
    if key in placeholder_cache:
        return placeholder_cache[key]
    pic = Image.new("RGBA", size, (226, 214, 255, 255))
    img = ctk.CTkImage(light_image=pic, dark_image=pic, size=size)
    placeholder_cache[key] = img
    return img


# --- จัดการข้อมูล ---
def refresh_history() -> None:
    global orders_data
    orders_data = sell_db.order_history(LOGIN_USERNAME)
    render_history()


# --- สร้าง UI สำหรับรายการ ---
def render_history() -> None:
    header_count.configure(text=f"รวม {len(orders_data)} รายการ")

    for child in history_body.winfo_children():
        child.destroy()

    if not orders_data:
        ctk.CTkLabel(
            history_body,
            text="ยังไม่มีประวัติการสั่งซื้อ",
            font=("Mitr", 16),
            text_color="#6D6A86",
        ).pack(pady=40)
        return

    for order in orders_data:
        card = ctk.CTkFrame(history_body, fg_color="#F0ECFF", corner_radius=12)
        card.pack(fill="x", padx=10, pady=8)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=12, pady=(10, 4))
        ctk.CTkLabel(top, text=f"คำสั่งซื้อ #{order['order_id']}", font=("Mitr", 18, "bold")).pack(side="left")
        ctk.CTkLabel(top, text=order["created_at"], font=("Mitr", 13), text_color="#6D6A86").pack(side="right")

        for item in order["items"]:
            line = ctk.CTkFrame(card, fg_color="transparent")
            line.pack(fill="x", padx=12, pady=4)

            cache_key = item.get("cover_path") or f"placeholder"
            img = cover_cache.get(cache_key)
            if not img:
                img = load_image(item.get("cover_path", ""), size=(56, 56))
                if img:
                    cover_cache[cache_key] = img
            if not img:
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
def build_layout() -> None:
    global history_win, history_body, header_count

    history_win = ctk.CTk()
    history_win.title("ประวัติการสั่งซื้อ")
    history_win.geometry("720x560+900+260")
    history_win.configure(fg_color="#F7F5FF")

    header = ctk.CTkFrame(history_win, fg_color="transparent")
    header.pack(fill="x", padx=18, pady=(18, 8))

    row = ctk.CTkFrame(header, fg_color="transparent")
    row.pack(fill="x")

    ctk.CTkLabel(row, text="ประวัติการสั่งซื้อ", font=("Mitr", 24, "bold")).pack(side="left")
    ctk.CTkButton(
        row,
        text="ย้อนกลับ",
        width=110,
        fg_color="#D5D2EE",
        text_color="#2F2A44",
        hover_color="#C2BDE0",
        font=("Mitr", 16),
        command=history_win.destroy,
    ).pack(side="right")

    header_count = ctk.CTkLabel(header, text="รวม 0 รายการ", font=("Mitr", 14), text_color="#6D6A86")
    header_count.pack(anchor="w")

    history_body = ctk.CTkScrollableFrame(history_win, fg_color="white", corner_radius=16)
    history_body.pack(fill="both", expand=True, padx=18, pady=(0, 18))


# --- จุดเริ่มต้นของโปรแกรม ---
def main() -> None:
    build_layout()
    refresh_history()
    history_win.mainloop()


if __name__ == "__main__":
    main()

