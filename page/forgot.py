import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import subprocess, sys, os, sqlite3

# ---------- PATH DB ----------
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "Userdata.db"))
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# ---------- THEME ----------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
PURPLE_PRIMARY = "#7B66E3"
PURPLE_ACCENT  = "#B388FF"
BG_SOFT        = "#F7F5FF"
TEXT_DARK      = "#2F2A44"
RESIZE_DELAY = 60
PANEL_SUPERSAMPLE = 2
SIZE_STEP = 2

_pending_job = None
_last_bg_size = (0, 0)
_last_panel_size = (0, 0)

_bg_cache = {}
_panel_cache = {}

# ---------- WINDOW ----------
forgot = ctk.CTk()
forgot.title("Purple Album — ลืมรหัสผ่าน")
forgot.geometry("900x600+300+60")
forgot.minsize(800, 520)
forgot.configure(fg_color=BG_SOFT)

# ---------- Canvas + BG ----------
canvas = tk.Canvas(forgot, highlightthickness=0, bd=0)
canvas.pack(fill="both", expand=True)

BG_PATH = r"C:\Python\project\\bgstore.png"
bg_raw = Image.open(BG_PATH)
bg_img = ImageTk.PhotoImage(bg_raw.resize((900, 600)))
bg_id = canvas.create_image(0, 0, image=bg_img, anchor="nw")

def _rounded_size(w, h):
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
        resample = Image.LANCZOS if final else Image.BILINEAR
        resized = bg_raw.resize((w, h), resample=resample)
        img = ImageTk.PhotoImage(resized)
        _bg_cache[key] = img
        canvas.itemconfigure(bg_id, image=img)
        canvas.bg_img = img

    _last_bg_size = (w, h)

def make_panel_img(w, h, radius=28, border=12, outer="#BFAEF7", inner=BG_SOFT):
    s = PANEL_SUPERSAMPLE
    W, H = w * s, h * s
    R, B = radius * s, border * s

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, W, H], radius=R, fill=outer)
    d.rounded_rectangle([B, B, W - B, H - B], radius=R, fill=inner)

    return img.resize((w, h), Image.LANCZOS)

panel_img = ImageTk.PhotoImage(make_panel_img(820, 540))
panel_id = canvas.create_image(0, 0, image=panel_img, anchor="center")

container = ctk.CTkFrame(forgot, fg_color="transparent", corner_radius=0)
container_win = canvas.create_window(0, 0, window=container, anchor="center")

# ---------- LOGO ----------
logo_path = r"C:\Python\project\LOGOproject.png"
if os.path.exists(logo_path):
    logo_img = ctk.CTkImage(light_image=Image.open(logo_path),
                            dark_image=Image.open(logo_path), size=(100, 100))
    ctk.CTkLabel(container, image=logo_img, text="").pack(pady=(18, 6))
else:
    ctk.CTkLabel(container, text="PURPLE\nALBUM",
                 font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(18, 6))

ctk.CTkLabel(container, text="ลืมรหัสผ่าน",
             font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
             text_color=PURPLE_PRIMARY).pack(pady=(0, 8))

# ---------- FORM ----------
form = ctk.CTkFrame(container, fg_color="transparent")
form.pack(padx=28, pady=10, fill="x")

def make_input(label, placeholder, emoji="", show=None, first=False):
    pad = (0, 0) if first else (12, 0)
    block = ctk.CTkFrame(form, fg_color="transparent")
    block.pack(fill="x", pady=pad)

    ctk.CTkLabel(block, text=label, anchor="w",
                 font=ctk.CTkFont(size=16), text_color=TEXT_DARK)\
        .pack(anchor="w", pady=(0, 4))

    row = ctk.CTkFrame(block, fg_color="transparent")
    row.pack(fill="x")
    row.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(row, text=emoji, width=26).grid(row=0, column=0, padx=(0, 8))
    entry = ctk.CTkEntry(row, placeholder_text=placeholder, height=40, show=show)
    entry.grid(row=0, column=1, sticky="we")
    return entry

user_entry   = make_input("Username", "กรอกชื่อผู้ใช้", "👤", first=True)
email_entry  = make_input("Email", "example@email.com", "✉️")
new_entry    = make_input("New Password", "กรอกรหัสผ่านใหม่", "🔒", show="•")
confirm_entry = make_input("Confirm Password", "ยืนยันรหัสผ่านใหม่", "🔒", show="•")

ctk.CTkLabel(container,
             text="กรุณากรอกข้อมูลให้ตรงกับที่ลงทะเบียนไว้ ระบบจะตั้งรหัสใหม่ให้คุณโดยใช้รหัสที่กรอกด้านบน",
             text_color=TEXT_DARK, wraplength=520,
             font=ctk.CTkFont(size=14)).pack(padx=28, pady=(4, 12))

# ---------- BUTTONS ----------
buttons = ctk.CTkFrame(container, fg_color="transparent")
buttons.pack(fill="x", padx=28, pady=(8, 0))
buttons.grid_columnconfigure((0, 1), weight=1)

def back_to_login():
    reopen_full = _fullscreen_state["value"]
    forgot.destroy()
    args = [sys.executable, r"C:\Python\project\page\login.py"]
    if not reopen_full:
        args.append("--windowed")
    subprocess.Popen(args)

def reset_password():
    u = user_entry.get().strip()
    em = email_entry.get().strip()
    p1 = new_entry.get().strip()
    p2 = confirm_entry.get().strip()

    if not (u and em and p1 and p2):
        messagebox.showwarning("กรอกให้ครบ", "กรุณากรอกข้อมูลให้ครบทุกช่อง")
        return
    if p1 != p2:
        messagebox.showwarning("รหัสไม่ตรง", "รหัสผ่านใหม่และยืนยันรหัสผ่านต้องตรงกัน")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username=? AND email=?", (u, em))
        row = c.fetchone()
        if not row:
            messagebox.showwarning("ไม่พบข้อมูล", "ไม่พบผู้ใช้หรืออีเมลไม่ตรงกับระบบ")
            return

        c.execute("UPDATE users SET password=? WHERE id=?", (p1, row[0]))
        conn.commit()
        messagebox.showinfo("สำเร็จ", "รีเซ็ตรหัสผ่านเรียบร้อยแล้ว\nกรุณาเข้าสู่ระบบด้วยรหัสใหม่ของคุณ")
        back_to_login()
    except Exception as exc:
        messagebox.showerror("ผิดพลาด", f"เกิดข้อผิดพลาด: {exc}")
    finally:
        try:
            conn.close()
        except:
            pass

ctk.CTkButton(buttons, text="ย้อนกลับ", text_color="white",
              height=46, corner_radius=22,
              fg_color="#B388FF", hover_color="#8D50F7",
              command=back_to_login)\
    .grid(row=0, column=0, padx=4, sticky="e", ipadx=12)

ctk.CTkButton(buttons, text="รีเซ็ตรหัสผ่าน", text_color="white",
              height=46, corner_radius=22,
              fg_color="#B388FF", hover_color="#8D50F7",
              command=reset_password)\
    .grid(row=0, column=1, padx=4, sticky="w", ipadx=12)

# ---------- Layout handling ----------
MARGIN_W = 40
MARGIN_H = 120

def layout_panel(final=False):
    global _last_panel_size

    w = max(forgot.winfo_width(), 400)
    h = max(forgot.winfo_height(), 300)

    resize_bg(w, h, final=final)

    container.update_idletasks()
    need_w = container.winfo_reqwidth()
    need_h = container.winfo_reqheight()

    panel_w = max(min(int(w * 0.88), w - 40), need_w + MARGIN_W)
    panel_h = max(min(int(h * 0.82), h - 40), need_h + MARGIN_H)

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
    PADDING_Y = 150
    inner_w = max(panel_w - PADDING_X, need_w)
    inner_h = max(panel_h - PADDING_Y, need_h)
    canvas.coords(container_win, cx, cy)
    canvas.itemconfigure(container_win, width=inner_w, height=inner_h)

def _on_configure(_event):
    layout_panel(final=False)

    global _pending_job
    if _pending_job is not None:
        forgot.after_cancel(_pending_job)
    _pending_job = forgot.after(RESIZE_DELAY, lambda: layout_panel(final=True))

forgot.bind("<Configure>", _on_configure)
forgot.update_idletasks()
layout_panel(final=True)

# ---------- Fullscreen toggle (F11 / ESC) ----------
_fullscreen_state = {"value": False, "geometry": None}

def _enter_fullscreen():
    if _fullscreen_state["value"]:
        return
    _fullscreen_state["value"] = True
    _fullscreen_state["geometry"] = forgot.winfo_geometry()
    try:
        forgot.state("zoomed")
    except tk.TclError:
        pass
    forgot.attributes("-fullscreen", True)
    forgot.geometry(f"{forgot.winfo_screenwidth()}x{forgot.winfo_screenheight()}+0+0")

def _leave_fullscreen():
    if not _fullscreen_state["value"]:
        return
    _fullscreen_state["value"] = False
    forgot.attributes("-fullscreen", False)
    try:
        forgot.state("normal")
    except tk.TclError:
        pass
    if _fullscreen_state["geometry"]:
        forgot.geometry(_fullscreen_state["geometry"])

def _toggle_fullscreen(event=None):
    if _fullscreen_state["value"]:
        _leave_fullscreen()
    else:
        _enter_fullscreen()
    return "break"

def _exit_fullscreen(event=None):
    _leave_fullscreen()
    return "break"

forgot.bind("<F11>", _toggle_fullscreen)
forgot.bind("<Escape>", _exit_fullscreen)

_force_full = "--start-fullscreen" in sys.argv
_want_windowed = "--windowed" in sys.argv
if _force_full or not _want_windowed:
    forgot.after(0, _enter_fullscreen)

forgot.mainloop()