# page/profile_user.py
import customtkinter as ctk
from tkinter import messagebox, filedialog
import tkinter as tk
from PIL import Image, ImageDraw
import os, sqlite3
from io import BytesIO
import sys ,subprocess

# ---------------- Config / Path ----------------
#รับ username จาก login.py
if len( sys.argv ) > 1: 
    username = sys.argv[1] 
else: 
    username = None
#LOGIN_USERNAME = "achira"
BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH   = os.path.join(BASE_DIR, "database", "Userdata.db")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
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

def get_user(username: str):
    con = db_conn(); cur = con.cursor()
    cur.execute("""
        SELECT username, first_name, last_name, gender, birth_date,
               email, phone, profile_image
        FROM users WHERE username=?
    """, (username,))
    row = cur.fetchone()
    if not row:
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
        "username":      row[0] or "",
        "first_name":    row[1] or "",
        "last_name":     row[2] or "",
        "gender":        row[3] or "",
        "birth_date":    row[4] or "",
        "email":         row[5] or "",
        "phone":         row[6] or "",
        "profile_image": row[7],
    }

#อัพเดต username
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
    con = db_conn(); cur = con.cursor()
    if avatar_blob is None:
        cur.execute("""
            UPDATE users
            SET first_name=?, last_name=?, gender=?, birth_date=?,
                email=?, phone=?
            WHERE username=?
        """, (data["first_name"], data["last_name"], data["gender"], data["birth_date"],
              data["email"], data["phone"], username))
    else:
        cur.execute("""
            UPDATE users
            SET first_name=?, last_name=?, gender=?, birth_date=?,
                email=?, phone=?, profile_image=?
            WHERE username=?
        """, (data["first_name"], data["last_name"], data["gender"], data["birth_date"],
              data["email"], data["phone"], avatar_blob, username))
    con.commit(); con.close()

# ---------------- Image Helpers ----------------
def pil_round_avatar(pil_img, size: int = 180):
    pil_img = pil_img.convert("RGBA")
    pil_img.thumbnail((size, size))
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
    pil.thumbnail((target_size, target_size))
    pil = pil_round_avatar(pil, size=min(target_size, 512))
    buf = BytesIO(); pil.save(buf, format="PNG")
    return buf.getvalue()

# ---------------- UI ----------------
profile_edit_user = ctk.CTk()
profile_edit_user.title("Purple Album — แก้ไขโปรไฟล์ผู้ใช้")
profile_edit_user.geometry("900x560")
profile_edit_user.configure(fg_color=PURPLE_PRIMARY)

shell = ctk.CTkFrame(profile_edit_user, fg_color=BG_SOFT, corner_radius=20)
shell.pack(fill="both", padx=30, pady=30, expand=True)

header = ctk.CTkFrame(shell, fg_color="transparent")
header.pack(fill="x", padx=20, pady=(18, 8))
ctk.CTkLabel(header, text="แก้ไขโปรไฟล์ผู้ใช้", text_color=TEXT_DARK,
             font=ctk.CTkFont(family="Mitr", size=26, weight="bold")).pack(side="left")

body = ctk.CTkFrame(shell, fg_color="white", corner_radius=16)
body.pack(fill="both", padx=20, pady=(0,18), expand=True)

left  = ctk.CTkFrame(body, fg_color="white"); left.pack(side="left", fill="y", padx=(16, 8), pady=16)
right = ctk.CTkFrame(body, fg_color="white"); right.pack(side="left", fill="both", expand=True, padx=(8, 16), pady=16)

# ------- Load user -------
user = get_user(username)

# Avatar
avatar_img = blob_to_ctkimage(user["profile_image"], size=170)
avatar_label = ctk.CTkLabel(left, image=avatar_img, text="")
avatar_label.pack(pady=(8,10))

form_state = {"pending_avatar_blob": None}

def on_change_avatar():
    path = filedialog.askopenfilename(
        title="เลือกรูปโปรไฟล์",
        filetypes=[("Images","*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.gif")]
    )
    if not path: return
    try:
        blob = image_file_to_blob(path, target_size=512)
        img  = blob_to_ctkimage(blob, size=170)
        avatar_label.configure(image=img); avatar_label.image = img
        form_state["pending_avatar_blob"] = blob
    except Exception as e:
        messagebox.showerror("รูปโปรไฟล์", f"ไม่สามารถโหลดรูปได้\n{e}")

def on_clear_avatar():
    form_state["pending_avatar_blob"] = b""
    img = blob_to_ctkimage(None, size=170)
    avatar_label.configure(image=img); avatar_label.image = img

ctk.CTkButton(left, text="เปลี่ยนรูปโปรไฟล์",font=ctk.CTkFont(family="Mitr"), fg_color=PURPLE_PRIMARY, command=on_change_avatar).pack(pady=(0,8), fill="x")
ctk.CTkButton(left, text="ลบรูปโปรไฟล์",font=ctk.CTkFont(family="Mitr"), fg_color="#E86", hover_color="#D55", command=on_clear_avatar).pack(pady=(0,8), fill="x")

# ------- Form (Basic) -------
right.grid_columnconfigure(0, weight=1)

def field(label, row, placeholder=""):
    ctk.CTkLabel(right, text=label, text_color=TEXT_DARK, font=("Mitr", 15)).grid(row=row, column=0, sticky="w", padx=(6,8), pady=(2,0))
    ent = ctk.CTkEntry(right, height=38, fg_color="#F4F3FE", border_color="#E0DDFC", text_color=TEXT_DARK, font=("Mitr", 15), placeholder_text=placeholder)
    ent.grid(row=row+1, column=0, sticky="ew", padx=(6,8), pady=(0,6))
    return ent

entry_username = field("Username", 0); entry_username.insert(0, user["username"])
entry_first    = field("ชื่อ",        2); entry_first.insert(0, user["first_name"])
entry_last     = field("นามสกุล",     4); entry_last.insert(0, user["last_name"])
entry_gender   = field("เพศ ", 6); entry_gender.insert(0, user["gender"])
entry_birth    = field("วันเกิด", 8); entry_birth.insert(0, user["birth_date"])
entry_email    = field("อีเมล", 10); entry_email.insert(0, user["email"])
entry_phone    = field("เบอร์โทร", 12); entry_phone.insert(0, user["phone"])

# ------- Buttons -------
btns = ctk.CTkFrame(right, fg_color="white")
btns.grid(row=14, column=0, sticky="e", padx=(6,8), pady=(6,0))

def reload_form(username: str):
    u = get_user(username)
    entry_username.delete(0, "end"); entry_username.insert(0, u["username"])
    entry_first.delete(0, "end"); entry_first.insert(0, u["first_name"])
    entry_last.delete(0, "end"); entry_last.insert(0, u["last_name"])
    entry_gender.delete(0, "end"); entry_gender.insert(0, u["gender"])
    entry_birth.delete(0, "end"); entry_birth.insert(0, u["birth_date"])
    entry_email.delete(0, "end"); entry_email.insert(0, u["email"])
    entry_phone.delete(0, "end"); entry_phone.insert(0, u["phone"])
    img = blob_to_ctkimage(u["profile_image"], size=170)
    avatar_label.configure(image=img); avatar_label.image = img
    form_state["pending_avatar_blob"] = None

def on_reset():
    reload_form(username)

def on_save():
    global username
    new_username = entry_username.get().strip()
    data = {
        "first_name": entry_first.get().strip(),
        "last_name":  entry_last.get().strip(),
        "gender":     entry_gender.get().strip(),     
        "birth_date": entry_birth.get().strip(),       
        "email":      entry_email.get().strip(),
        "phone":      entry_phone.get().strip(),
    }

    # เช็คเบื้องต้นแบบเบสิค
    if data["email"] and ("@" not in data["email"] or "." not in data["email"].split("@")[-1]):
        messagebox.showwarning("ตรวจสอบข้อมูล", "อีเมลไม่ถูกต้อง")
        return

    # เปลี่ยน username ถ้าแก้
    old_username = username
    username = upsert_user_username(old_username, new_username)

    # จัดการรูป
    avatar_blob = form_state["pending_avatar_blob"]
    if avatar_blob == b"":  # ลบรูป
        con = db_conn(); cur = con.cursor()
        cur.execute("UPDATE users SET profile_image=NULL WHERE username=?", (username,))
        con.commit(); con.close()
        avatar_blob = None

    update_user(username, data, avatar_blob)
    form_state["pending_avatar_blob"] = None
    messagebox.showinfo("บันทึกแล้ว", "อัปเดตโปรไฟล์เรียบร้อย")

def goback_page():
    if not username:
        messagebox.showerror("โปรไฟล์", "ไม่พบผู้ใช้งานสำหรับกลับไปดูโปรไฟล์")
        return
    args = [sys.executable, os.path.join(BASE_DIR, "page", "profile_show_user.py"), username]
    subprocess.Popen(args)
    profile_edit_user.after(800, profile_edit_user.destroy)


ctk.CTkButton(btns, text="บันทึก", fg_color=PURPLE_PRIMARY ,font=ctk.CTkFont(family="Mitr"), command=on_save).pack(side="left", padx=6)
ctk.CTkButton(btns, text="ย้อนกลับ", fg_color="#888",font=ctk.CTkFont(family="Mitr"), command=goback_page).pack(side="left", padx=6)

# ตัวแปรเก็บขนาด panel
MARGIN_W = 40
MARGIN_H = 80

# จัดวาง panel
def layout_panel(final=False):
    global _last_panel_size
    w = max(profile_edit_user.winfo_width(),  400)
    h = max(profile_edit_user.winfo_height(), 300)
    header.update_idletasks()
    need_w = header.winfo_reqwidth()
    need_h = header.winfo_reqheight()
    panel_w = max(min(int(w * 0.86), w - 40), need_w + MARGIN_W)
    panel_h = max(min(int(h * 0.78), h - 40), need_h + MARGIN_H)

    PADDING_X = 80
    PADDING_Y = 120

    inner_w = max(panel_w - PADDING_X, need_w)
    inner_h = max(panel_h - PADDING_Y, need_h)
    
# ---------- Fullscreen toggle (F11 / ESC) ----------
_fullscreen_state = {"value": False, "geometry": None}

# เลื่อนการจัดวาง layout ไปทำทีหลัง
def _apply_layout_later():
    profile_edit_user.after(20, lambda: layout_panel(final=True))
    
def _enter_fullscreen():
    if _fullscreen_state["value"]:
        return
    _fullscreen_state["value"] = True
    _fullscreen_state["geometry"] = profile_edit_user.winfo_geometry()
    try:
        profile_edit_user.state("zoomed")
    except tk.TclError:
        pass
    profile_edit_user.attributes("-fullscreen", True)
    profile_edit_user.geometry(f"{profile_edit_user.winfo_screenwidth()}x{profile_edit_user.winfo_screenheight()}+0+0")
    _apply_layout_later()

def _leave_fullscreen():
    if not _fullscreen_state["value"]:
        return
    _fullscreen_state["value"] = False
    profile_edit_user.attributes("-fullscreen", False)
    try:
        profile_edit_user.state("normal")
    except tk.TclError:
        pass
    if _fullscreen_state["geometry"]:
        profile_edit_user.geometry("1000x600")
    _apply_layout_later()

def _toggle_fullscreen(event=None):
    if _fullscreen_state["value"]:
        _leave_fullscreen()
    else:
        _enter_fullscreen()
    return "break"

def _on_escape_quit(event=None):
    # ปิดแอปทั้งโปรแกรม
    try:
        profile_edit_user.destroy()
    except Exception:
        profile_edit_user.quit()
    return "break"
profile_edit_user.bind("<F11>", _toggle_fullscreen)
profile_edit_user.bind("<Escape>", _on_escape_quit)

# เริ่มในโหมด fullscreen 
_force_full = "--start-fullscreen" in sys.argv
_want_windowed = "--windowed" in sys.argv
if _force_full or not _want_windowed:
    profile_edit_user.after(0, _enter_fullscreen) 
    
profile_edit_user.mainloop()
