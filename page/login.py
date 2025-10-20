import customtkinter as ctk
from tkinter import messagebox, BooleanVar
from PIL import Image, ImageDraw, ImageTk
import tkinter as tk
import subprocess, sys, os, sqlite3

# ---------- DB ----------
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "Userdata.db"))

# ---------- Theme ----------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
PURPLE_PRIMARY = "#7B66E3"
PURPLE_ACCENT  = "#B388FF"
BG_SOFT        = "#F7F5FF"
TEXT_DARK      = "#2F2A44"

# ---- Perf tuning ----
RESIZE_DELAY = 60        # ms (60-120 กำลังดี)
PANEL_SUPERSAMPLE = 2      # เดิม 4 -> 2 เร็วขึ้นมาก
SIZE_STEP = 2              # ปัดขนาดให้เป็น step ช่วย cache ติดง่ายขึ้น

_pending_job = None
_last_bg_size = (0, 0)
_last_panel_size = (0, 0)

_bg_cache = {}             # {(w,h): PhotoImage}
_panel_cache = {}          # {(w,h): PhotoImage}

# ---------- Window ----------
Login = ctk.CTk()
Login.title("Purple Album — เข้าสู่ระบบ")
Login.geometry("900x600")
Login.minsize(800, 520)
Login.configure(fg_color=BG_SOFT)

# ---------- Canvas + BG ----------
canvas = tk.Canvas(Login, highlightthickness=0, bd=0)
canvas.pack(fill="both", expand=True)

BG_PATH = r"C:\Python\project\\bgstore.png"
bg_raw = Image.open(BG_PATH)
bg_img = ImageTk.PhotoImage(bg_raw.resize((900, 600)))
bg_id  = canvas.create_image(0, 0, image=bg_img, anchor="nw")

def _rounded_size(w, h):
    # ปัดขนาดให้เข้า step เพื่อลดจำนวนคีย์ใน cache
    return (max(1, (w // SIZE_STEP) * SIZE_STEP),
            max(1, (h // SIZE_STEP) * SIZE_STEP))

def resize_bg(w, h, final=False):
    global _last_bg_size
    w, h = _rounded_size(w, h)
    if (w, h) == _last_bg_size and not final:
        return

    key = (w, h, 'final' if final else 'fast')
    if key in _bg_cache:
        canvas.itemconfigure(bg_id, image=_bg_cache[key])
        canvas.bg_img = _bg_cache[key]
    else:
        # เร็ว: BILINEAR ขณะลาก  |  ชัด: LANCZOS เมื่อปล่อยเมาส์
        resample = Image.LANCZOS if final else Image.BILINEAR
        resized = bg_raw.resize((w, h), resample=resample)
        img = ImageTk.PhotoImage(resized)
        _bg_cache[key] = img
        canvas.itemconfigure(bg_id, image=img)
        canvas.bg_img = img

    _last_bg_size = (w, h)

# ---------- Rounded panel image (transparent) ----------
def make_panel_img(w, h, radius=28, border=12, outer="#BFAEF7", inner=BG_SOFT):
    s = PANEL_SUPERSAMPLE
    W, H = w * s, h * s
    R, B = radius * s, border * s

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, W, H], radius=R, fill=outer)
    d.rounded_rectangle([B, B, W - B, H - B], radius=R, fill=inner)

    return img.resize((w, h), Image.LANCZOS)

panel_img  = ImageTk.PhotoImage(make_panel_img(820, 520))
panel_id   = canvas.create_image(0, 0, image=panel_img, anchor="center")

# ---------- Container on panel ----------
container = ctk.CTkFrame(Login, fg_color="transparent", corner_radius=0)
container_win = canvas.create_window(0, 0, window=container, anchor="center")

# ---------- UI inside container ----------
logoimg = r"C:\Python\project\LOGOproject.png"
logo_ctk = ctk.CTkImage(
    light_image=Image.open(logoimg),
    dark_image=Image.open(logoimg),
    size=(100, 100)
)
ctk.CTkLabel(container, image=logo_ctk, text="").pack(pady=(18, 6))

ctk.CTkLabel(container, text="เข้าสู่ระบบ",
             font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
             text_color=PURPLE_PRIMARY).pack(pady=(0, 8))

form = ctk.CTkFrame(container, fg_color="transparent")
form.pack(padx=28, pady=10, fill="x")
form.grid_columnconfigure(0, weight=1)
form.grid_columnconfigure(1, weight=0)

ctk.CTkLabel(form, text="Username", anchor="w",
             font=ctk.CTkFont(size=16), text_color=TEXT_DARK) \
    .grid(row=0, column=0, columnspan=2, sticky="w", padx=(0, 6), pady=(4, 4))

user_row = ctk.CTkFrame(form, fg_color="transparent")
user_row.grid(row=1, column=0, columnspan=2, sticky="we", pady=(0, 12))
user_row.grid_columnconfigure(1, weight=1)
ctk.CTkLabel(user_row, text="👤", width=26).grid(row=0, column=0, padx=(0, 8))
user_entry = ctk.CTkEntry(user_row, placeholder_text="กรอกชื่อผู้ใช้", height=40)
user_entry.grid(row=0, column=1, sticky="we")

ctk.CTkLabel(form, text="Password", anchor="w",
             font=ctk.CTkFont(size=16), text_color=TEXT_DARK) \
    .grid(row=2, column=0, columnspan=2, sticky="w", padx=(0, 6), pady=(6, 4))

pwd_row = ctk.CTkFrame(form, fg_color="transparent")
pwd_row.grid(row=3, column=0, columnspan=2, sticky="we", pady=(0, 8))
pwd_row.grid_columnconfigure(1, weight=1)
ctk.CTkLabel(pwd_row, text="🔒", width=26).grid(row=0, column=0, padx=(0, 8))
pwd_entry = ctk.CTkEntry(pwd_row, placeholder_text="กรอกรหัสผ่าน", height=40)
pwd_entry.grid(row=0, column=1, sticky="we", padx=(0, 8))

masked = BooleanVar(value=True)
def _apply_mask(*_):
    pwd_entry.configure(show="*" if masked.get() and pwd_entry.get() else "")
def _toggle():
    masked.set(not masked.get())
    toggle_btn.configure(text="ซ่อน" if not masked.get() else "แสดง")
    _apply_mask()
pwd_entry.bind("<KeyRelease>", _apply_mask)
pwd_entry.bind("<FocusOut>", _apply_mask)

toggle_btn = ctk.CTkButton(pwd_row, text="แสดง", width=64, height=34,
                           fg_color=PURPLE_ACCENT, hover_color=PURPLE_PRIMARY,
                           command=_toggle)
toggle_btn.grid(row=0, column=2)

links = ctk.CTkFrame(container, fg_color="transparent")
links.pack(fill="x", padx=28, pady=(8, 0))

def _go_register():
    args = [sys.executable, r"C:\Python\project\page\register.py"]
    if not _fullscreen_state["value"]:
        args.append("--windowed")
    Login.destroy()
    subprocess.Popen(args)
def _go_forgot():
    Login.destroy()
    subprocess.Popen([sys.executable, r"C:\Python\project\page\forgot.py"])

ctk.CTkButton(links, text="ลงทะเบียน", corner_radius=18,
              fg_color="white", hover_color=BG_SOFT, text_color=PURPLE_PRIMARY,
              border_width=2, border_color=PURPLE_PRIMARY, width=140,
              command=_go_register).pack(side="left", padx=(0, 10), pady=6)

ctk.CTkButton(links, text="ลืมรหัสผ่าน", corner_radius=18,
              fg_color="white", hover_color=BG_SOFT, text_color=PURPLE_PRIMARY,
              border_width=2, border_color=PURPLE_PRIMARY, width=140,
              command=_go_forgot).pack(side="left", pady=6)

def on_login():
    u = user_entry.get().strip()
    p = pwd_entry.get().strip()
    if not u or not p:
        messagebox.showwarning("กรอกให้ครบ", "กรุณากรอกทั้ง Username และ Password")
        return
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=? AND password=?", (u, p))
    row = c.fetchone(); conn.close()
    if row:
        messagebox.showinfo("เข้าสู่ระบบ", f"ยินดีต้อนรับ, {u}")
        Login.destroy()
        subprocess.Popen([sys.executable, r"C:\Python\project\page\main.py"])
    else:
        messagebox.showwarning("ผิดพลาด", "ไม่มี Username/Password หรือรหัสผ่านไม่ถูกต้อง")

ctk.CTkButton(container, text="เข้าสู่ระบบ", text_color="white",
              height=46, corner_radius=22,
              fg_color="#B388FF", hover_color="#8D50F7",
              command=on_login).pack(pady=18, ipadx=16)

# ---------- Layout (ให้ทุกอย่าง "อยู่ในกรอบ") ----------
MARGIN_W = 40   # เว้นข้างซ้าย-ขวาของแผง
MARGIN_H = 80   # เว้นด้านบน-ล่างของแผง (เผื่อโลโก้/หัวข้อ/ปุ่ม)

def layout_panel(final=False):
    global _last_panel_size

    w = max(Login.winfo_width(),  400)
    h = max(Login.winfo_height(), 300)

    # BG: เร็ว/ชัดตามโหมด
    resize_bg(w, h, final=final)

    container.update_idletasks()
    need_w = container.winfo_reqwidth()
    need_h = container.winfo_reqheight()

    panel_w = max(min(int(w * 0.86), w - 40), need_w + MARGIN_W)
    panel_h = max(min(int(h * 0.78), h - 40), need_h + MARGIN_H)

    # ปัดขนาดช่วย cache
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
    # re-run panel layout after switching fullscreen state
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

# ---------- Resize Optimization (Debounce + Cache) ----------

def _on_configure(_event):
    # แสดงพรีวิวเร็วขณะลาก/ย่อหน้าต่าง
    layout_panel(final=False)

    # ถ้าผู้ใช้หยุดลากสักพัก ค่อยเรนเดอร์คมชัดและ cache ไว้
    global _pending_job
    if _pending_job is not None:
        Login.after_cancel(_pending_job)
    _pending_job = Login.after(RESIZE_DELAY, lambda: layout_panel(final=True))

# ผูกอีเวนต์เมื่อขนาดหน้าต่างเปลี่ยน
Login.bind("<Configure>", _on_configure)

# เรียกครั้งแรกตอนเปิดหน้าต่าง
Login.update_idletasks()
layout_panel(final=True)

Login.mainloop()