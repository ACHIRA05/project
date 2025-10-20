import customtkinter as ctk
from tkinter import messagebox, filedialog
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import subprocess, sys, os, sqlite3
from io import BytesIO

# ---------- PATH DB ----------
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "Userdata.db"))
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# ---------- สร้างตารางให้พร้อม ----------
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT UNIQUE NOT NULL,
    profile_image BLOB
)
""")
conn.commit()
conn.close()

# ---------- THEME ----------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
PURPLE_PRIMARY = "#7B66E3"
BG_SOFT        = "#F7F5FF"
TEXT_DARK      = "#2F2A44"
PROFILE_IMG_SIZE = 140  # square preview dimension for the profile image
RESIZE_DELAY = 60
PANEL_SUPERSAMPLE = 2
SIZE_STEP = 2

_pending_job = None
_last_bg_size = (0, 0)
_last_panel_size = (0, 0)

_bg_cache = {}
_panel_cache = {}

# ---------- WINDOW ----------
register = ctk.CTk()
register.title("Purple Album — ลงทะเบียน")
register.geometry("1000x620+300+60")
register.minsize(900, 560)
register.configure(fg_color=BG_SOFT)

# ---------- Canvas + BG ----------
canvas = tk.Canvas(register, highlightthickness=0, bd=0)
canvas.pack(fill="both", expand=True)

BG_PATH = r"C:\Python\project\\bgstore.png"
bg_raw = Image.open(BG_PATH)
bg_img = ImageTk.PhotoImage(bg_raw.resize((1000, 620)))
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

panel_img = ImageTk.PhotoImage(make_panel_img(880, 560))
panel_id = canvas.create_image(0, 0, image=panel_img, anchor="center")

container = ctk.CTkFrame(register, fg_color="transparent", corner_radius=0)
container_win = canvas.create_window(0, 0, window=container, anchor="center")

# ---------- LOGO ----------
logo_path = r"C:\Python\project\LOGOproject.png"  # ปรับพาธตามเครื่อง
if os.path.exists(logo_path):
    logo_img = ctk.CTkImage(light_image=Image.open(logo_path),
                            dark_image=Image.open(logo_path), size=(100,100))
    ctk.CTkLabel(container, image=logo_img, text="").pack(pady=(8,6))
else:
    ctk.CTkLabel(container, text="PURPLE\nALBUM", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(16,6))

ctk.CTkLabel(container, text="ลงทะเบียน",
             font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
             text_color=PURPLE_PRIMARY).pack(pady=4)

# ---------- FORM 2 COLUMNS ----------
form = ctk.CTkFrame(container, fg_color="transparent")
form.pack(padx=28, pady=5, fill="x")
form.grid_columnconfigure((0,1), weight=1, uniform="col")

left_col = ctk.CTkFrame(form, fg_color="transparent")
left_col.grid(row=0, column=0, sticky="nsew", padx=(16,8), pady=16)
left_col.grid_columnconfigure(0, weight=1)

right_col = ctk.CTkFrame(form, fg_color="transparent")
right_col.grid(row=0, column=1, sticky="nsew", padx=(8,16), pady=16)
right_col.grid_columnconfigure(0, weight=1)

def make_input(parent, label, placeholder, emoji="", show=None, first=False):
    pad_top = 0 if first else 12
    block = ctk.CTkFrame(parent, fg_color="transparent")
    block.pack(fill="x", pady=(pad_top, 0))

    ctk.CTkLabel(block, text=label, anchor="w",
                 font=ctk.CTkFont(size=16), text_color=TEXT_DARK)\
        .pack(anchor="w", pady=(0,4))

    rowbox = ctk.CTkFrame(block, fg_color="transparent")
    rowbox.pack(fill="x")
    rowbox.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(rowbox, text=emoji, width=26).grid(row=0, column=0, padx=(0,8))
    entry = ctk.CTkEntry(rowbox, placeholder_text=placeholder, height=40, show=show)
    entry.grid(row=0, column=1, sticky="we")
    return entry

# ซ้าย: Username, Password, Confirm Password, Email, Phone
userentry  = make_input(left_col, "Username", "กรอกชื่อผู้ใช้", "👤", first=True)
pass_entry = make_input(left_col, "Password", "กรอกรหัสผ่าน", "🔒", show="•")
pass2_entry = make_input(left_col, "Confirm Password", "ยืนยันรหัสผ่าน", "🔒", show="•")
email_entry = make_input(left_col, "Email", "example@email.com", "✉️")
phone_entry = make_input(left_col, "Phone", "เช่น 0812345678", "📱")

# ---------- UPLOAD BOX (ขวาด้านบน) ----------
img_box = ctk.CTkFrame(right_col, fg_color="#F1E9FF", corner_radius=12)
img_box.pack(fill="x", pady=(0,18))

ctk.CTkLabel(img_box, text="🖼️ รูปโปรไฟล์", anchor="w",
             font=ctk.CTkFont(size=16), text_color=TEXT_DARK)\
    .pack(anchor="w", padx=12, pady=(12,6))

preview_label = ctk.CTkLabel(img_box, text="(ยังไม่มีรูป)", width=PROFILE_IMG_SIZE, height=PROFILE_IMG_SIZE,
                             fg_color="white", corner_radius=10)
preview_label.pack(padx=12, pady=6)

image_bytes_cache = {"data": None}
_preview_obj = {"img": None}  # กัน GC

def choose_image():
    path = filedialog.askopenfilename(
        title="เลือกไฟล์รูป",
        filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.webp;*.bmp")]
    )
    if not path:
        return
    im = Image.open(path).convert("RGBA")
    im.thumbnail((PROFILE_IMG_SIZE, PROFILE_IMG_SIZE))
    _preview_obj["img"] = ctk.CTkImage(light_image=im, dark_image=im, size=im.size)
    preview_label.configure(image=_preview_obj["img"], text="")
    buf = BytesIO()
    im.save(buf, format="PNG")
    image_bytes_cache["data"] = buf.getvalue()

ctk.CTkButton(img_box, text="เลือกไฟล์รูป", command=choose_image, height=36,
              fg_color="#B388FF", hover_color="#8D50F7")\
    .pack(padx=12, pady=(6,12), fill="x")

# ---------- BUTTONS ----------
links_frame = ctk.CTkFrame(container, fg_color="transparent")
links_frame.pack(fill="x", padx=28, pady=(20))
links_frame.grid_columnconfigure((0,1), weight=1)

def check():
    u  = userentry.get().strip()
    p1 = pass_entry.get().strip()
    p2 = pass2_entry.get().strip()
    em = email_entry.get().strip()
    ph = phone_entry.get().strip()

    if not (u and p1 and p2 and em and ph):
        messagebox.showwarning("กรอกให้ครบ", "กรุณากรอกข้อมูลให้ครบทุกช่อง")
        return
    if p1 != p2:
        messagebox.showwarning("รหัสไม่ตรง", "รหัสผ่านและยืนยันรหัสผ่านต้องตรงกัน")
        return

    img_bytes = image_bytes_cache["data"]  # ไม่บังคับมีรูป

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            INSERT INTO users (username, password, email, phone, profile_image)
            VALUES (?, ?, ?, ?, ?)
        """, (u, p1, em, ph, img_bytes))
        conn.commit()
        messagebox.showinfo("สำเร็จ", "สมัครสมาชิกเรียบร้อย\nกำลังไปหน้าเข้าสู่ระบบ")
        register.destroy()
        subprocess.Popen([sys.executable, r"C:\Python\project\page\login.py"])  # ปรับพาธตามโปรเจกต์
    except sqlite3.IntegrityError as e:
        msg = "ข้อมูลซ้ำ กรุณาเปลี่ยน "
        s = str(e)
        if "username" in s: msg += "Username"
        elif "email" in s: msg += "Email"
        elif "phone" in s: msg += "เบอร์โทร"
        else: msg = "ข้อมูลซ้ำ กรุณาตรวจสอบอีกครั้ง"
        messagebox.showwarning("ผิดพลาด", msg)
    except Exception as e:
        messagebox.showerror("ผิดพลาด", f"เกิดข้อผิดพลาด: {e}")
    finally:
        try: conn.close()
        except: pass

def backtolog():
    reopen_full = _fullscreen_state["value"]
    register.destroy()
    args = [sys.executable, r"C:\Python\project\page\login.py"]
    if not reopen_full:
        args.append("--windowed")
    subprocess.Popen(args)

ctk.CTkButton(links_frame, text="ย้อนกลับ", text_color="white",
              height=46, corner_radius=22, fg_color="#B388FF",
              hover_color="#8D50F7", command=backtolog)\
    .grid(row=0, column=0, padx=4, sticky="e", ipadx=12)

ctk.CTkButton(links_frame, text="สมัครสมาชิก", text_color="white",
              height=46, corner_radius=22, fg_color="#B388FF",
              hover_color="#8D50F7", command=check)\
    .grid(row=0, column=1, padx=4, sticky="w", ipadx=12)

# ---------- Layout handling ----------
MARGIN_W = 60
MARGIN_H = 120

def layout_panel(final=False):
    global _last_panel_size

    w = max(register.winfo_width(), 400)
    h = max(register.winfo_height(), 300)

    resize_bg(w, h, final=final)

    container.update_idletasks()
    need_w = container.winfo_reqwidth()
    need_h = container.winfo_reqheight()

    panel_w = max(min(int(w * 0.9), w - 40), need_w + MARGIN_W)
    panel_h = max(min(int(h * 0.84), h - 40), need_h + MARGIN_H)

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

    PADDING_X = 90
    PADDING_Y = 160
    inner_w = max(panel_w - PADDING_X, need_w)
    inner_h = max(panel_h - PADDING_Y, need_h)
    canvas.coords(container_win, cx, cy)
    canvas.itemconfigure(container_win, width=inner_w, height=inner_h)


def _on_configure(_event):
    layout_panel(final=False)

    global _pending_job
    if _pending_job is not None:
        register.after_cancel(_pending_job)
    _pending_job = register.after(RESIZE_DELAY, lambda: layout_panel(final=True))

register.bind("<Configure>", _on_configure)
register.update_idletasks()
layout_panel(final=True)

# ---------- Fullscreen toggle (F11 / ESC) ----------
_fullscreen_state = {"value": False, "geometry": None}
 
def _enter_fullscreen():
    if _fullscreen_state["value"]:
        return
    _fullscreen_state["value"] = True
    _fullscreen_state["geometry"] = register.winfo_geometry()
    try:
        register.state("zoomed")
    except tk.TclError:
        pass
    register.attributes("-fullscreen", True)
    register.geometry(f"{register.winfo_screenwidth()}x{register.winfo_screenheight()}+0+0")

def _leave_fullscreen():
    if not _fullscreen_state["value"]:
        return
    _fullscreen_state["value"] = False
    register.attributes("-fullscreen", False)
    try:
        register.state("normal")
    except tk.TclError:
        pass
    if _fullscreen_state["geometry"]:
        register.geometry(_fullscreen_state["geometry"])

def _toggle_fullscreen(event=None):
    if _fullscreen_state["value"]:
        _leave_fullscreen()
    else:
        _enter_fullscreen()
    return "break"

def _exit_fullscreen(event=None):
    _leave_fullscreen()
    return "break"

register.bind("<F11>", _toggle_fullscreen)
register.bind("<Escape>", _exit_fullscreen)

_force_full = "--start-fullscreen" in sys.argv
_want_windowed = "--windowed" in sys.argv
if _force_full or not _want_windowed:
    register.after(0, _enter_fullscreen)

register.mainloop()