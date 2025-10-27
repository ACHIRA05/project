# page/profile_user.py
import customtkinter as ctk
from tkinter import messagebox, filedialog
import tkinter as tk
from PIL import Image, ImageDraw
import sys, os, sqlite3, datetime
from io import BytesIO

# ---------------- Config / Path ----------------
LOGIN_USERNAME = "achira"  # เปลี่ยนเป็นค่าจากระบบล็อกอินจริงได้
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "Userdata.db"))
ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
DEFAULT_PROFILE_IMAGE = os.path.join(ASSETS_DIR, "default_user.png")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# ---------------- Theme ----------------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
PURPLE_PRIMARY = "#7B66E3"
BG_SOFT        = "#F7F5FF"
TEXT_DARK      = "#2F2A44"

# ---------------- DB Utils ----------------
def db_conn():
    return sqlite3.connect(DB_PATH)

def ensure_schema():
    con = db_conn()
    cur = con.cursor()
    # ถ้ายังไม่มีตาราง users ให้สร้างแบบบางส่วนก่อน
    cur.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY)")
    # เช็คคอลัมน์ที่มีอยู่
    cur.execute("PRAGMA table_info(users)")
    existing = {r[1] for r in cur.fetchall()}

    required = {
        "password":      "TEXT",     # เผื่ออนาคต (ไม่ใช้ในหน้านี้)
        "first_name":    "TEXT",
        "last_name":     "TEXT",
        "gender":        "TEXT",
        "birth_date":    "TEXT",     # จัดเก็บรูปแบบ YYYY-MM-DD
        "email":         "TEXT",
        "phone":         "TEXT",
        "profile_image": "BLOB",
    }
    for col, typ in required.items():
        if col not in existing:
            cur.execute(f"ALTER TABLE users ADD COLUMN {col} {typ}")
    con.commit()
    con.close()

def get_user(username: str):
    ensure_schema()
    con = db_conn(); cur = con.cursor()
    cur.execute("""
        SELECT username, first_name, last_name, gender, birth_date,
               email, phone, profile_image
        FROM users WHERE username=?
    """, (username,))
    row = cur.fetchone()
    if not row:
        # seed user หากไม่มี
        cur.execute("""
            INSERT OR IGNORE INTO users(username, first_name, last_name, gender, birth_date, email, phone, profile_image)
            VALUES(?,?,?,?,?,?,?,?)
        """, (username, "", "", "", "", "", "", None))
        con.commit()
        cur.execute("""
            SELECT username, first_name, last_name, gender, birth_date,
                   email, phone, profile_image
            FROM users WHERE username=?
        """, (username,))
        row = cur.fetchone()
    con.close()
    return {
        "username":      row[0],
        "first_name":    row[1] or "",
        "last_name":     row[2] or "",
        "gender":        row[3] or "",
        "birth_date":    row[4] or "",  # YYYY-MM-DD
        "email":         row[5] or "",
        "phone":         row[6] or "",
        "profile_image": row[7],
    }

def upsert_user_username(old_username: str, new_username: str):
    """อัปเดต username (PK) หากเปลี่ยน"""
    if not new_username or new_username == old_username:
        return old_username
    con = db_conn(); cur = con.cursor()
    try:
        cur.execute("UPDATE users SET username=? WHERE username=?", (new_username, old_username))
        con.commit()
        return new_username
    except sqlite3.IntegrityError:
        messagebox.showerror("บันทึกไม่สำเร็จ", "username นี้มีผู้ใช้งานแล้ว")
        return old_username
    finally:
        con.close()

def update_user(username: str, data: dict, avatar_blob: bytes | None):
    ensure_schema()
    con = db_conn(); cur = con.cursor()
    if avatar_blob is None:
        cur.execute("""
            UPDATE users
            SET first_name=?, last_name=?, gender=?, birth_date=?,
                email=?, phone=?
            WHERE username=?
        """, (
            data["first_name"], data["last_name"], data["gender"], data["birth_date"],
            data["email"], data["phone"], username
        ))
    else:
        cur.execute("""
            UPDATE users
            SET first_name=?, last_name=?, gender=?, birth_date=?,
                email=?, phone=?, profile_image=?
            WHERE username=?
        """, (
            data["first_name"], data["last_name"], data["gender"], data["birth_date"],
            data["email"], data["phone"], avatar_blob, username
        ))
    con.commit(); con.close()

# ---------------- Image Helpers ----------------
def pil_round_avatar(pil_img: Image.Image, size: int = 180) -> Image.Image:
    pil_img = pil_img.convert("RGBA")
    pil_img.thumbnail((size, size), Image.LANCZOS)
    mask = Image.new("L", pil_img.size, 0)
    draw = ImageDraw.Draw(mask); draw.ellipse((0, 0, *pil_img.size), fill=255)
    out = Image.new("RGBA", pil_img.size, (0,0,0,0))
    out.paste(pil_img, (0,0), mask=mask)
    return out

def blob_to_ctkimage(blob: bytes | None, size: int = 180) -> ctk.CTkImage:
    from PIL import Image as PILImage
    if blob:
        try:
            pil = PILImage.open(BytesIO(blob))
        except Exception:
            pil = PILImage.open(DEFAULT_PROFILE_IMAGE) if os.path.exists(DEFAULT_PROFILE_IMAGE) else PILImage.new("RGBA",(size,size),(230,220,255,255))
    else:
        pil = PILImage.open(DEFAULT_PROFILE_IMAGE) if os.path.exists(DEFAULT_PROFILE_IMAGE) else PILImage.new("RGBA",(size,size),(230,220,255,255))
    rounded = pil_round_avatar(pil, size)
    return ctk.CTkImage(light_image=rounded, dark_image=rounded, size=rounded.size)

def image_file_to_blob(path: str, target_size: int = 512) -> bytes:
    from PIL import Image as PILImage
    pil = PILImage.open(path).convert("RGBA")
    pil.thumbnail((target_size, target_size), PILImage.LANCZOS)
    pil = pil_round_avatar(pil, size=min(target_size, 512))
    buf = BytesIO(); pil.save(buf, format="PNG")
    return buf.getvalue()

# ---------------- Date / Age ----------------
def ymd_from_controls() -> str:
    y = year_var.get(); m = month_var.get(); d = day_var.get()
    if not (y and m and d): return ""
    return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"

def calc_age(yyyy_mm_dd: str) -> int | None:
    try:
        y, m, d = map(int, yyyy_mm_dd.split("-"))
        b = datetime.date(y, m, d)
        today = datetime.date.today()
        age = today.year - b.year - ((today.month, today.day) < (b.month, b.day))
        return max(age, 0)
    except Exception:
        return None

def on_birth_change(*_):
    bd = ymd_from_controls()
    a = calc_age(bd) if bd else None
    age_var.set(str(a) if a is not None else "-")

# ---------------- UI ----------------
profile_user = ctk.CTk()
profile_user.title("Purple Album — โปรไฟล์ผู้ใช้")
profile_user.geometry("1000x640")
profile_user.minsize(900, 560)
profile_user.configure(fg_color=PURPLE_PRIMARY)

# Fullscreen / ESC
_fullscreen_state = {"value": False, "geometry": None}
def _enter_fullscreen():
    if _fullscreen_state["value"]: return
    _fullscreen_state["value"] = True
    _fullscreen_state["geometry"] = profile_user.winfo_geometry()
    try: profile_user.state("zoomed")
    except tk.TclError: pass
    profile_user.attributes("-fullscreen", True)
def _leave_fullscreen():
    if not _fullscreen_state["value"]: return
    _fullscreen_state["value"] = False
    profile_user.attributes("-fullscreen", False)
    try: profile_user.state("normal")
    except tk.TclError: pass
    if _fullscreen_state["geometry"]:
        profile_user.geometry("1000x640")
def _toggle_fullscreen(_=None):
    _leave_fullscreen() if _fullscreen_state["value"] else _enter_fullscreen(); return "break"
def _on_escape_quit(_=None):
    try: profile_user.destroy()
    except Exception: profile_user.quit()
    return "break"
profile_user.bind("<F11>", _toggle_fullscreen)
profile_user.bind("<Escape>", _on_escape_quit)

# เริ่มในโหมด fullscreen 
_force_full = "--start-fullscreen" in sys.argv
_want_windowed = "--windowed" in sys.argv
if _force_full or not _want_windowed:
    profile_user.after(0, _enter_fullscreen)  
      
# Shell
shell = ctk.CTkFrame(profile_user, fg_color=BG_SOFT, corner_radius=20)
shell.pack(fill="both", padx=40, pady=40, expand=True)

# Header
header = ctk.CTkFrame(shell, fg_color="transparent")
header.pack(fill="x", padx=20, pady=(20, 10))
title_lbl = ctk.CTkLabel(header, text="โปรไฟล์ผู้ใช้", text_color=TEXT_DARK,
                         font=ctk.CTkFont(family="Mitr", size=28, weight="bold"))
title_lbl.pack(side="left")

# Body
body = ctk.CTkFrame(shell, fg_color="white", corner_radius=16)
body.pack(fill="both", padx=20, pady=(0,20), expand=True)

left = ctk.CTkFrame(body, fg_color="white"); left.pack(side="left", fill="y", padx=(18, 8), pady=18)
right = ctk.CTkFrame(body, fg_color="white"); right.pack(side="left", fill="both", expand=True, padx=(8, 18), pady=18)

# ------- Load user -------
user = get_user(LOGIN_USERNAME)

# Avatar
avatar_img = blob_to_ctkimage(user["profile_image"], size=180)
avatar_label = ctk.CTkLabel(left, image=avatar_img, text="")
avatar_label.pack(pady=(10,10))

form_state = {"pending_avatar_blob": None}

def on_change_avatar():
    path = filedialog.askopenfilename(
        title="เลือกรูปโปรไฟล์",
        filetypes=[("Images","*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.gif")]
    )
    if not path: return
    try:
        blob = image_file_to_blob(path, target_size=512)
        avatar_label.configure(image=blob_to_ctkimage(blob, size=180))
        avatar_label.image = blob_to_ctkimage(blob, size=180)
        form_state["pending_avatar_blob"] = blob
    except Exception as e:
        messagebox.showerror("รูปโปรไฟล์", f"ไม่สามารถโหลดรูปได้\n{e}")

def on_clear_avatar():
    form_state["pending_avatar_blob"] = b""
    avatar_label.configure(image=blob_to_ctkimage(None, size=180))
    avatar_label.image = blob_to_ctkimage(None, size=180)

ctk.CTkButton(left, text="เปลี่ยนรูปโปรไฟล์", fg_color=PURPLE_PRIMARY, command=on_change_avatar).pack(pady=(0,8), fill="x")
ctk.CTkButton(left, text="ลบรูปโปรไฟล์", fg_color="#E86", hover_color="#D55", command=on_clear_avatar).pack(pady=(0,8), fill="x")

# ------- Form -------
right.grid_columnconfigure(0, weight=1)

def e(label, row, placeholder=""):
    ctk.CTkLabel(right, text=label, text_color=TEXT_DARK, font=("Mitr", 16)).grid(row=row, column=0, sticky="w", padx=(8,10), pady=(4,0))
    ent = ctk.CTkEntry(right, height=40, fg_color="#F4F3FE", border_color="#E0DDFC", text_color=TEXT_DARK, font=("Mitr", 16), placeholder_text=placeholder)
    ent.grid(row=row+1, column=0, sticky="ew", padx=(8,10), pady=(0,8))
    return ent

entry_username = e("Username", 0); entry_username.insert(0, user["username"])
entry_first    = e("ชื่อ",        2); entry_first.insert(0, user["first_name"])
entry_last     = e("นามสกุล",     4); entry_last.insert(0, user["last_name"])

# Gender
ctk.CTkLabel(right, text="เพศ", text_color=TEXT_DARK, font=("Mitr", 16)).grid(row=6, column=0, sticky="w", padx=(8,10), pady=(4,0))
gender_var = tk.StringVar(value=user["gender"] or "")
gender_menu = ctk.CTkOptionMenu(right, variable=gender_var, values=["", "ชาย", "หญิง", "อื่น ๆ"])
gender_menu.grid(row=7, column=0, sticky="ew", padx=(8,10), pady=(0,8))

# Birthdate (day / month / year)
ctk.CTkLabel(right, text="วัน-เดือน-ปีเกิด", text_color=TEXT_DARK, font=("Mitr", 16)).grid(row=8, column=0, sticky="w", padx=(8,10), pady=(4,0))
row_birth = ctk.CTkFrame(right, fg_color="white"); row_birth.grid(row=9, column=0, sticky="ew", padx=(8,10), pady=(0,8))
row_birth.grid_columnconfigure((0,1,2), weight=1)

day_var   = tk.StringVar()
month_var = tk.StringVar()
year_var  = tk.StringVar()
age_var   = tk.StringVar(value="-")

# set initial
if user["birth_date"]:
    try:
        y,m,d = user["birth_date"].split("-")
        year_var.set(y); month_var.set(str(int(m))); day_var.set(str(int(d)))
        a = calc_age(user["birth_date"]); age_var.set(str(a) if a is not None else "-")
    except:
        pass

days   = [str(i) for i in range(1,32)]
months = [str(i) for i in range(1,13)]
this_year = datetime.date.today().year
years  = [str(y) for y in range(this_year, this_year-100, -1)]

ctk.CTkOptionMenu(row_birth, variable=day_var,   values=days,   width=110, command=lambda *_: on_birth_change()).grid(column=0, row=0, padx=2)
ctk.CTkOptionMenu(row_birth, variable=month_var, values=months, width=110, command=lambda *_: on_birth_change()).grid(column=1, row=0, padx=2)
ctk.CTkOptionMenu(row_birth, variable=year_var,  values=years,  width=120, command=lambda *_: on_birth_change()).grid(column=2, row=0, padx=2)

# Age (read-only label)
age_row = ctk.CTkFrame(right, fg_color="white"); age_row.grid(row=10, column=0, sticky="w", padx=(8,10), pady=(0,8))
ctk.CTkLabel(age_row, text="อายุ: ", text_color=TEXT_DARK, font=("Mitr", 16)).pack(side="left")
ctk.CTkLabel(age_row, textvariable=age_var, text_color="#6b6b86", font=("Mitr", 16)).pack(side="left")

entry_email = e("อีเมล", 12); entry_email.insert(0, user["email"])
entry_phone = e("เบอร์โทร", 14); entry_phone.insert(0, user["phone"])

# ------- Buttons -------
btns = ctk.CTkFrame(right, fg_color="white")
btns.grid(row=16, column=0, sticky="e", padx=(8,10), pady=(8,0))

def reload_form():
    u = get_user(entry_username.get().strip() or LOGIN_USERNAME)
    entry_username.delete(0, "end"); entry_username.insert(0, u["username"])
    entry_first.delete(0, "end"); entry_first.insert(0, u["first_name"])
    entry_last.delete(0, "end"); entry_last.insert(0, u["last_name"])
    gender_var.set(u["gender"] or "")
    if u["birth_date"]:
        try:
            y,m,d = u["birth_date"].split("-")
            year_var.set(y); month_var.set(str(int(m))); day_var.set(str(int(d)))
            a = calc_age(u["birth_date"]); age_var.set(str(a) if a is not None else "-")
        except:
            year_var.set(""); month_var.set(""); day_var.set(""); age_var.set("-")
    else:
        year_var.set(""); month_var.set(""); day_var.set(""); age_var.set("-")
    entry_email.delete(0, "end"); entry_email.insert(0, u["email"])
    entry_phone.delete(0, "end"); entry_phone.insert(0, u["phone"])
    ai = blob_to_ctkimage(u["profile_image"], size=180)
    avatar_label.configure(image=ai); avatar_label.image = ai
    form_state["pending_avatar_blob"] = None

def on_reset():
    reload_form()

def on_save():
    global LOGIN_USERNAME
    new_username = entry_username.get().strip()
    data = {
        "first_name": entry_first.get().strip(),
        "last_name":  entry_last.get().strip(),
        "gender":     gender_var.get().strip(),
        "birth_date": ymd_from_controls(),  # "" หากไม่เลือกครบ
        "email":      entry_email.get().strip(),
        "phone":      entry_phone.get().strip(),
    }
    # validate
    if data["email"] and ("@" not in data["email"] or "." not in data["email"].split("@")[-1]):
        messagebox.showwarning("ตรวจสอบข้อมูล", "อีเมลไม่ถูกต้อง")
        return
    if data["phone"] and not data["phone"].replace("-", "").isdigit():
        messagebox.showwarning("ตรวจสอบข้อมูล", "เบอร์โทรควรเป็นตัวเลข")
        return

    # เปลี่ยน username ถ้ามีการแก้
    old_username = LOGIN_USERNAME
    LOGIN_USERNAME = upsert_user_username(old_username, new_username)

    # จัดการรูป
    avatar_blob = form_state["pending_avatar_blob"]
    if avatar_blob == b"":  # ลบรูป
        con = db_conn(); cur = con.cursor()
        cur.execute("UPDATE users SET profile_image=NULL WHERE username=?", (LOGIN_USERNAME,))
        con.commit(); con.close()
        avatar_blob = None

    update_user(LOGIN_USERNAME, data, avatar_blob)
    form_state["pending_avatar_blob"] = None
    messagebox.showinfo("บันทึกแล้ว", "อัปเดตโปรไฟล์เรียบร้อย")

def on_close():
    profile_user.destroy()

ctk.CTkButton(btns, text="รีเซ็ต", fg_color="#CCC", text_color="black", command=on_reset).pack(side="left", padx=6)
ctk.CTkButton(btns, text="บันทึก", fg_color=PURPLE_PRIMARY, command=on_save).pack(side="left", padx=6)
ctk.CTkButton(btns, text="ปิด", fg_color="#888", command=on_close).pack(side="left", padx=6)

profile_user.mainloop()