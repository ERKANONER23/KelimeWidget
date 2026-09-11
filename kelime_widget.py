import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import csv
import os
import sys
import random
import time
import threading
import math

# Kütüphane kontrolü
try:
    import pystray
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Lütfen 'pystray' ve 'Pillow' kütüphanelerini kurun: pip install pystray Pillow")
    sys.exit()

try:
    import winreg
    IS_WINDOWS = True
except ImportError:
    IS_WINDOWS = False

# ==============================================================================
# 1. YAPILANDIRMA VE TEMALAR
# ==============================================================================
APP_DIR = os.path.join(os.getenv('APPDATA'), 'KelimeWidget') if IS_WINDOWS else os.path.expanduser('~/.KelimeWidget')
os.makedirs(APP_DIR, exist_ok=True)
SETTINGS_FILE = os.path.join(APP_DIR, 'settings.json')
WORDS_FILE = os.path.join(APP_DIR, 'words.csv')

THEMES = {
    "Modern": {"bg": "#1E1E1E", "fg": "#FFFFFF", "accent": "#007ACC", "trans": "#010101"},
    "Neon": {"bg": "#000000", "fg": "#39FF14", "accent": "#FF00FF", "trans": "#020202"},
    "Klasik": {"bg": "#2C3E50", "fg": "#ECF0F1", "accent": "#E74C3C", "trans": "#030303"},
    "Matrix": {"bg": "#000000", "fg": "#00FF00", "accent": "#008F00", "trans": "#040404"},
    "Sıcak": {"bg": "#3E2723", "fg": "#FFCC80", "accent": "#FF8A65", "trans": "#050505"},
    "Mor Gece": {"bg": "#1A0033", "fg": "#E0B0FF", "accent": "#9D00FF", "trans": "#060606"}
}

DEFAULT_SETTINGS = {
    "theme": "Modern",
    "animation": "Daktilo",
    "interval": 60,
    "position": "Orta",
    "x": 0, "y": 0,
    "width": 400, "height": 200,
    "startup": False,
    "always_on_top": True
}

ANIMATIONS = ["Daktilo", "Tırmanma", "Süzülme", "Birleştirme", "Blok", 
              "Patlama", "Sıçrama", "İnme", "Kaykay", "Yayılım", "Netleştirme"]

# ==============================================================================
# 2. KELİME YÖNETİMİ
# ==============================================================================
class WordManager:
    def __init__(self):
        self.words = []
        self.load()

    def load(self):
        if not os.path.exists(WORDS_FILE):
            self.words = [("apple", "elma"), ("book", "kitap"), ("computer", "bilgisayar")]
            self.save()
            return
        
        self.words = []
        try:
            with open(WORDS_FILE, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2:
                        self.words.append((row[0].strip(), row[1].strip()))
        except Exception as e:
            print(f"Kelime yükleme hatası: {e}")

    def save(self):
        with open(WORDS_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(self.words)

    def add(self, en, tr):
        en, tr = en.strip().lower(), tr.strip().lower()
        if not en or not tr: return False, "Kelimeler boş olamaz."
        if any(w[0].lower() == en for w in self.words): return False, "Bu kelime zaten var."
        self.words.append((en, tr))
        self.save()
        return True, "Eklendi."

    def edit(self, index, en, tr):
        en, tr = en.strip().lower(), tr.strip().lower()
        if any(i != index and w[0].lower() == en for i, w in enumerate(self.words)): 
            return False, "Bu kelime zaten var."
        self.words[index] = (en, tr)
        self.save()
        return True, "Güncellendi."

    def delete(self, index):
        self.words.pop(index)
        self.save()

    def get_random(self):
        return random.choice(self.words) if self.words else ("No Word", "Kelime Bulunamadı")

    def import_csv(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                added = 0
                for row in reader:
                    if len(row) >= 2:
                        en, tr = row[0].strip().lower(), row[1].strip().lower()
                        if en and tr and not any(w[0] == en for w in self.words):
                            self.words.append((en, tr))
                            added += 1
                self.save()
                return True, f"{added} kelime içe aktarıldı."
        except Exception as e:
            return False, str(e)

    def export_csv(self, filepath):
        try:
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(self.words)
            return True, "Dışa aktarıldı."
        except Exception as e:
            return False, str(e)

# ==============================================================================
# 3. ANİMASYON MOTORU
# ==============================================================================
class AnimationEngine:
    def __init__(self, canvas):
        self.canvas = canvas
        self.active_animations = []

    def stop_all(self):
        for anim in self.active_animations:
            anim['running'] = False
        self.active_animations = []

    def _animate(self, item_id, duration, update_func, easing='linear', on_complete=None):
        anim = {'running': True, 'start': time.time()}
        self.active_animations.append(anim)
        
        def step():
            if not anim['running']: return
            elapsed = time.time() - anim['start']
            t = min(elapsed / duration, 1.0)
            
            # Easing calculations
            if easing == 'ease_out': 
                t = 1 - (1 - t) ** 3
            elif easing == 'bounce':
                # Fixed: Separated the subtraction from the math expression
                if t < 1/2.75:
                    t = 7.5625 * t * t
                elif t < 2/2.75:
                    t2 = t - 1.5/2.75
                    t = 7.5625 * t2 * t2 + 0.75
                elif t < 2.5/2.75:
                    t2 = t - 2.25/2.75
                    t = 7.5625 * t2 * t2 + 0.9375
                else:
                    t2 = t - 2.625/2.75
                    t = 7.5625 * t2 * t2 + 0.984375
            elif easing == 'elastic':
                if t != 0 and t != 1:
                    t = (2**(-10*t) * math.sin((t*10 - 0.75) * (2*math.pi)/3) + 1)

            update_func(t)
            if elapsed < duration:
                self.canvas.after(16, step)
            else:
                update_func(1.0)
                if on_complete: 
                    on_complete()

        step()

    # 11 Animasyon Tipi
    def typewriter(self, item_id, text, duration, on_complete):
        self._animate(item_id, duration, lambda t: self.canvas.itemconfig(item_id, text=text[:int(len(text)*t)]), on_complete=on_complete)

    def climb(self, item_id, start_y, end_y, duration, on_complete):
        self._animate(item_id, duration, lambda t: self.canvas.coords(item_id, self.canvas.coords(item_id)[0], start_y + (end_y - start_y)*t), easing='ease_out', on_complete=on_complete)

    def glide(self, item_id, start_x, end_x, duration, on_complete):
        self._animate(item_id, duration, lambda t: self.canvas.coords(item_id, start_x + (end_x - start_x)*t, self.canvas.coords(item_id)[1]), easing='ease_out', on_complete=on_complete)

    def merge(self, item_ids, text, center_x, y, duration, on_complete):
        half = len(text) // 2
        t1, t2 = text[:half], text[half:]
        id1, id2 = item_ids
        self.canvas.itemconfig(id1, text=t1)
        self.canvas.itemconfig(id2, text=t2)
        
        def update(t):
            self.canvas.coords(id1, center_x - 50*(1-t), y)
            self.canvas.coords(id2, center_x + 50*(1-t), y)
            if t == 1.0:
                self.canvas.delete(id2)
                self.canvas.itemconfig(id1, text=text)
        self._animate(id1, duration, update, easing='ease_out', on_complete=on_complete)

    def block(self, item_id, text, duration, on_complete):
        words = text.split()
        self._animate(item_id, duration, lambda t: self.canvas.itemconfig(item_id, text=" ".join(words[:max(1, int(len(words)*t))])), on_complete=on_complete)

    def explode(self, item_id, duration, on_complete):
        self._animate(item_id, duration, lambda t: self.canvas.itemconfig(item_id, font=("Arial", int(10 + 40*t), "bold")), easing='ease_out', on_complete=on_complete)

    def bounce(self, item_id, start_y, end_y, duration, on_complete):
        self._animate(item_id, duration, lambda t: self.canvas.coords(item_id, self.canvas.coords(item_id)[0], start_y + (end_y - start_y)*t), easing='bounce', on_complete=on_complete)

    def drop(self, item_id, start_y, end_y, duration, on_complete):
        self._animate(item_id, duration, lambda t: self.canvas.coords(item_id, self.canvas.coords(item_id)[0], start_y + (end_y - start_y)*t), easing='ease_out', on_complete=on_complete)

    def skateboard(self, item_id, start_x, end_x, duration, on_complete):
        self._animate(item_id, duration, lambda t: self.canvas.coords(item_id, start_x + (end_x - start_x)*t, self.canvas.coords(item_id)[1]), easing='elastic', on_complete=on_complete)

    def spread(self, item_id, text, center_x, y, duration, on_complete):
        self._animate(item_id, duration, lambda t: self.canvas.itemconfig(item_id, text=text), on_complete=on_complete) # Basitleştirilmiş yayılım

    def clarify(self, item_id, bg_color, fg_color, duration, on_complete):
        # Renk geçişi (Hex parse)
        r1, g1, b1 = int(bg_color[1:3], 16), int(bg_color[3:5], 16), int(bg_color[5:7], 16)
        r2, g2, b2 = int(fg_color[1:3], 16), int(fg_color[3:5], 16), int(fg_color[5:7], 16)
        
        def update(t):
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            self.canvas.itemconfig(item_id, fill=f"#{r:02x}{g:02x}{b:02x}")
            
        self._animate(item_id, duration, update, on_complete=on_complete)

# ==============================================================================
# 4. WIDGET PENCERESİ
# ==============================================================================
# ==============================================================================
# 4. WIDGET PENCERESİ (GÜNCELLENMİŞ - TRANSPARAN ARKA PLAN)
# ==============================================================================
class WordWidget(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        self.settings = app.settings
        self.theme = THEMES[self.settings["theme"]]

        self.overrideredirect(True)
        self.attributes('-topmost', self.settings.get("always_on_top", True))

        # --- TRANSPARAN ARKA PLAN ---
        # transparentcolor KALDIRILDI.
        # Bunun yerine arka plan tema rengi + pencere alpha kullanılıyor.
        self.bg_color = self.theme["bg"]
        self.configure(bg=self.bg_color)
        self.attributes('-alpha', 0.85)  # %85 opaklık (0.0 = tam şeffaf, 1.0 = tam opak)
        # --------------------------------

        self.canvas = tk.Canvas(self, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.anim_engine = AnimationEngine(self.canvas)
        self.en_id = None
        self.tr_id = None
        self.bg_rect_id = None
        self.is_visible = False
        self.timer_id = None

        self._setup_drag()
        self._apply_position()
        self.withdraw()

    # --- YARDIMCI: Yuvarlatılmış Köşeli Dikdörtgen ---
    def _round_rectangle(self, x1, y1, x2, y2, radius=20, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def _setup_drag(self):
        self.canvas.bind("<Button-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._do_drag)
        self.canvas.bind("<ButtonRelease-1>", self._end_drag)
        self.canvas.bind("<Button-3>", self._show_context_menu)
        self.drag_data = {"x": 0, "y": 0}

    def _start_drag(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def _do_drag(self, event):
        x = self.winfo_x() + event.x - self.drag_data["x"]
        y = self.winfo_y() + event.y - self.drag_data["y"]
        self.geometry(f"+{x}+{y}")

    def _end_drag(self, event):
        self.settings["x"] = self.winfo_x()
        self.settings["y"] = self.winfo_y()
        self.settings["position"] = "Manuel"
        self.app.save_settings()

    def _show_context_menu(self, event):
        menu = tk.Menu(self, tearoff=0, bg=self.theme["bg"], fg=self.theme["fg"],
                       activebackground=self.theme["accent"], activeforeground="white")
        menu.add_command(label="⚙ Ayarlar", command=self.app.show_settings)
        menu.add_command(label="⏭ Sonraki Kelime", command=self.force_next)
        menu.add_separator()
        menu.add_command(label="✕ Kapat", command=self.app.exit_app)
        menu.tk_popup(event.x_root, event.y_root)

    def _apply_position(self):
        w, h = self.settings["width"], self.settings["height"]
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        pos = self.settings["position"]
        if pos == "Orta":
            x, y = (screen_w - w) // 2, (screen_h - h) // 2
        elif pos == "Sol Üst":
            x, y = 20, 20
        elif pos == "Sağ Üst":
            x, y = screen_w - w - 20, 20
        elif pos == "Sol Alt":
            x, y = 20, screen_h - h - 60  # Görev çubuğu payı
        elif pos == "Sağ Alt":
            x, y = screen_w - w - 20, screen_h - h - 60
        else:
            x, y = self.settings.get("x", 100), self.settings.get("y", 100)

        self.geometry(f"{w}x{h}+{x}+{y}")

    def _hex_darken(self, hex_color, factor=0.6):
        """Rengi koyulaştırır (gölge için)"""
        r = int(int(hex_color[1:3], 16) * factor)
        g = int(int(hex_color[3:5], 16) * factor)
        b = int(int(hex_color[5:7], 16) * factor)
        return f"#{r:02x}{g:02x}{b:02x}"

    def show_word(self):
        if not self.app.word_manager.words:
            return

        self.anim_engine.stop_all()
        self.canvas.delete("all")
        self._apply_position()
        self.deiconify()
        self.is_visible = True

        en, tr = self.app.word_manager.get_random()
        w, h = self.settings["width"], self.settings["height"]

        # --- ARKA PLAN DİKDÖRTGENİ ---
        self.bg_rect_id = self._round_rectangle(
            4, 4, w - 4, h - 4,
            radius=18,
            fill=self.bg_color,
            outline=self.theme["accent"],
            width=2
        )
        # -------------------------------

        # Dinamik Font Boyutu
        en_size = max(20, min(60, int(w / max(len(en) * 0.55, 1))))
        tr_size = max(16, min(45, int(w / max(len(tr) * 0.55, 1))))

        # --- GÖLGE + ANA YAZI (okunabilirlik için) ---
        # Gölge (hafif offset, koyu renk)
        shadow_color = self._hex_darken(self.bg_color, 0.3)

        self.en_shadow_id = self.canvas.create_text(
            w / 2 + 2, h * 0.35 + 2, text="",
            fill=shadow_color, font=("Segoe UI", en_size, "bold"), anchor="center"
        )
        self.en_id = self.canvas.create_text(
            w / 2, h * 0.35, text="",
            fill=self.theme["fg"], font=("Segoe UI", en_size, "bold"), anchor="center"
        )

        self.tr_shadow_id = self.canvas.create_text(
            w / 2 + 2, h * 0.70 + 2, text="",
            fill=shadow_color, font=("Segoe UI", tr_size, "bold"), anchor="center"
        )
        self.tr_id = self.canvas.create_text(
            w / 2, h * 0.70, text="",
            fill=self.theme["accent"], font=("Segoe UI", tr_size, "bold"), anchor="center"
        )
        # -----------------------------------------------

        # Ayırıcı çizgi (kelime ile anlam arasında)
        self.canvas.create_line(
            w * 0.2, h * 0.52, w * 0.8, h * 0.52,
            fill=self.theme["accent"], width=1, dash=(4, 4)
        )

        self._run_animation_sequence(en, tr)

    def _run_animation_sequence(self, en, tr):
        anim_type = self.settings["animation"]

        # 1. saniye: İngilizce
        self.after(1000, lambda: self._animate_text(self.en_id, en, anim_type, is_english=True))
        self.after(1000, lambda: self.canvas.itemconfig(self.en_shadow_id, text=en))

        # 6. saniye (1 + 5): Türkçe
        self.after(6000, lambda: self._animate_text(self.tr_id, tr, anim_type, is_english=False))
        self.after(6000, lambda: self.canvas.itemconfig(self.tr_shadow_id, text=tr))

        # 12. saniye (1 + 11): Gizle
        self.after(12000, self.hide_word)

    def _animate_text(self, item_id, text, anim_type, is_english):
        w, h = self.settings["width"], self.settings["height"]
        duration = 1.0

        # Gölge item id'sini bul
        shadow_id = self.en_shadow_id if is_english else self.tr_shadow_id
        coords = self.canvas.coords(item_id)

        if anim_type == "Daktilo":
            self.anim_engine.typewriter(item_id, text, duration, None)
            # Gölge de aynı anda yazılsın
            self.anim_engine.typewriter(shadow_id, text, duration, None)
        elif anim_type == "Tırmanma":
            self.canvas.itemconfig(item_id, text=text)
            self.canvas.itemconfig(shadow_id, text=text)
            end_y = coords[1]
            self.anim_engine.climb(item_id, h, end_y, duration, None)
            self.anim_engine.climb(shadow_id, h + 2, end_y + 2, duration, None)
        elif anim_type == "Süzülme":
            self.canvas.itemconfig(item_id, text=text)
            self.canvas.itemconfig(shadow_id, text=text)
            self.anim_engine.glide(item_id, -100, w / 2, duration, None)
            self.anim_engine.glide(shadow_id, -98, w / 2 + 2, duration, None)
        elif anim_type == "Birleştirme":
            if is_english:
                id2 = self.canvas.create_text(
                    w / 2, coords[1], text="",
                    font=self.canvas.itemcget(item_id, "font"), fill=self.theme["fg"]
                )
                self.anim_engine.merge([item_id, id2], text, w / 2, coords[1], duration, None)
                self.canvas.itemconfig(shadow_id, text=text)
            else:
                self.canvas.itemconfig(item_id, text=text)
                self.canvas.itemconfig(shadow_id, text=text)
        elif anim_type == "Blok":
            self.anim_engine.block(item_id, text, duration, None)
            self.anim_engine.block(shadow_id, text, duration, None)
        elif anim_type == "Patlama":
            self.canvas.itemconfig(item_id, text=text, font=("Segoe UI", 10, "bold"))
            self.canvas.itemconfig(shadow_id, text=text, font=("Segoe UI", 10, "bold"))
            self.anim_engine.explode(item_id, duration, None)
        elif anim_type == "Sıçrama":
            self.canvas.itemconfig(item_id, text=text)
            self.canvas.itemconfig(shadow_id, text=text)
            self.anim_engine.bounce(item_id, -50, coords[1], duration, None)
        elif anim_type == "İnme":
            self.canvas.itemconfig(item_id, text=text)
            self.canvas.itemconfig(shadow_id, text=text)
            self.anim_engine.drop(item_id, -50, coords[1], duration, None)
        elif anim_type == "Kaykay":
            self.canvas.itemconfig(item_id, text=text)
            self.canvas.itemconfig(shadow_id, text=text)
            self.anim_engine.skateboard(item_id, w + 100, w / 2, duration, None)
        elif anim_type == "Yayılım":
            self.canvas.itemconfig(item_id, text=text)
            self.canvas.itemconfig(shadow_id, text=text)
        elif anim_type == "Netleştirme":
            self.canvas.itemconfig(item_id, text=text, fill=self.bg_color)
            self.canvas.itemconfig(shadow_id, text=text)
            target_color = self.theme["fg"] if is_english else self.theme["accent"]
            self.anim_engine.clarify(item_id, self.bg_color, target_color, duration, None)
        else:
            self.canvas.itemconfig(item_id, text=text)
            self.canvas.itemconfig(shadow_id, text=text)

    def hide_word(self):
        self.withdraw()
        self.is_visible = False

    def force_next(self):
        if self.timer_id:
            self.after_cancel(self.timer_id)
        self.hide_word()
        self.app.schedule_next_word(0)
# ==============================================================================
# 5. AYARLAR PENCERESİ
# ==============================================================================
class SettingsWindow(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        self.title("Kelime Widget Ayarları")
        self.geometry("500x600")
        self.configure(bg="#2D2D2D")
        self.resizable(False, False)
        
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure("TNotebook", background="#2D2D2D", borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#3D3D3D", foreground="white", padding=[10, 5])
        self.style.map("TNotebook.Tab", background=[("selected", "#007ACC")])
        
        self.style.configure("TFrame", background="#2D2D2D")
        self.style.configure("TLabel", background="#2D2D2D", foreground="white")
        self.style.configure("TButton", background="#3D3D3D", foreground="white", borderwidth=0)
        self.style.map("TButton", background=[("active", "#007ACC")])
        self.style.configure("TEntry", fieldbackground="#3D3D3D", foreground="white", borderwidth=1)
        self.style.configure("TCombobox", fieldbackground="#3D3D3D", foreground="white", borderwidth=1)

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._create_general_tab(notebook)
        self._create_words_tab(notebook)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.grab_set()

    def _create_general_tab(self, parent):
        tab = ttk.Frame(parent)
        parent.add(tab, text="Genel & Görünüm")

        # Tema
        ttk.Label(tab, text="Tema:").grid(row=0, column=0, sticky="w", pady=5)
        self.theme_var = tk.StringVar(value=self.app.settings["theme"])
        ttk.Combobox(tab, textvariable=self.theme_var, values=list(THEMES.keys()), state="readonly").grid(row=0, column=1, sticky="ew", pady=5)

        # Animasyon
        ttk.Label(tab, text="Animasyon:").grid(row=1, column=0, sticky="w", pady=5)
        self.anim_var = tk.StringVar(value=self.app.settings["animation"])
        ttk.Combobox(tab, textvariable=self.anim_var, values=ANIMATIONS, state="readonly").grid(row=1, column=1, sticky="ew", pady=5)

        # Konum
        ttk.Label(tab, text="Konum:").grid(row=2, column=0, sticky="w", pady=5)
        self.pos_var = tk.StringVar(value=self.app.settings["position"])
        ttk.Combobox(tab, textvariable=self.pos_var, values=["Orta", "Sol Üst", "Sağ Üst", "Sol Alt", "Sağ Alt", "Manuel"], state="readonly").grid(row=2, column=1, sticky="ew", pady=5)

        # Süre
        ttk.Label(tab, text="Bekleme Süresi (sn):").grid(row=3, column=0, sticky="w", pady=5)
        self.interval_var = tk.StringVar(value=self.app.settings["interval"])
        ttk.Entry(tab, textvariable=self.interval_var).grid(row=3, column=1, sticky="ew", pady=5)

        # Boyut
        ttk.Label(tab, text="Genişlik / Yükseklik:").grid(row=4, column=0, sticky="w", pady=5)
        size_frame = ttk.Frame(tab)
        size_frame.grid(row=4, column=1, sticky="ew")
        self.w_var = tk.StringVar(value=self.app.settings["width"])
        self.h_var = tk.StringVar(value=self.app.settings["height"])
        ttk.Entry(size_frame, textvariable=self.w_var, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Entry(size_frame, textvariable=self.h_var, width=8).pack(side=tk.LEFT, padx=2)

        # Başlangıç
        self.startup_var = tk.BooleanVar(value=self.app.settings["startup"])
        ttk.Checkbutton(tab, text="Windows başlangıcında çalıştır", variable=self.startup_var).grid(row=5, column=0, columnspan=2, sticky="w", pady=10)

        # Kaydet Butonu
        ttk.Button(tab, text="Kaydet ve Uygula", command=self.save_settings).grid(row=6, column=0, columnspan=2, pady=20)

    def _create_words_tab(self, parent):
        tab = ttk.Frame(parent)
        parent.add(tab, text="Kelimeler")

        # Arama ve Ekleme
        search_frame = ttk.Frame(tab)
        search_frame.pack(fill=tk.X, pady=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_words)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(search_frame, text="Ekle", command=self.add_word).pack(side=tk.RIGHT, padx=5)

        # Liste
        cols = ("en", "tr")
        self.tree = ttk.Treeview(tab, columns=cols, show="headings", height=15)
        self.tree.heading("en", text="İngilizce")
        self.tree.heading("tr", text="Türkçe")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tree.bind("<Double-1>", self.edit_word)

        # Butonlar
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="Sil", command=self.delete_word).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="CSV İçe Aktar", command=self.import_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="CSV Dışa Aktar", command=self.export_csv).pack(side=tk.LEFT, padx=5)

        self.refresh_word_list()

    def refresh_word_list(self, filter_text=""):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for i, (en, tr) in enumerate(self.app.word_manager.words):
            if filter_text.lower() in en.lower() or filter_text.lower() in tr.lower():
                self.tree.insert("", "end", iid=i, values=(en, tr))

    def filter_words(self, *args):
        self.refresh_word_list(self.search_var.get())

    def add_word(self):
        win = tk.Toplevel(self)
        win.title("Yeni Kelime")
        win.geometry("300x150")
        win.configure(bg="#2D2D2D")
        win.grab_set()

        ttk.Label(win, text="İngilizce:").pack(pady=5)
        en_entry = ttk.Entry(win)
        en_entry.pack()
        ttk.Label(win, text="Türkçe:").pack(pady=5)
        tr_entry = ttk.Entry(win)
        tr_entry.pack()

        def save():
            success, msg = self.app.word_manager.add(en_entry.get(), tr_entry.get())
            messagebox.showinfo("Bilgi", msg, parent=win)
            if success:
                self.refresh_word_list()
                win.destroy()

        ttk.Button(win, text="Kaydet", command=save).pack(pady=10)

    def edit_word(self, event):
        item = self.tree.selection()[0]
        index = int(item)
        en, tr = self.app.word_manager.words[index]

        win = tk.Toplevel(self)
        win.title("Kelime Düzenle")
        win.geometry("300x150")
        win.configure(bg="#2D2D2D")
        win.grab_set()

        ttk.Label(win, text="İngilizce:").pack(pady=5)
        en_entry = ttk.Entry(win)
        en_entry.insert(0, en)
        en_entry.pack()
        ttk.Label(win, text="Türkçe:").pack(pady=5)
        tr_entry = ttk.Entry(win)
        tr_entry.insert(0, tr)
        tr_entry.pack()

        def save():
            success, msg = self.app.word_manager.edit(index, en_entry.get(), tr_entry.get())
            messagebox.showinfo("Bilgi", msg, parent=win)
            if success:
                self.refresh_word_list()
                win.destroy()

        ttk.Button(win, text="Güncelle", command=save).pack(pady=10)

    def delete_word(self):
        item = self.tree.selection()
        if not item: return
        index = int(item[0])
        if messagebox.askyesno("Onay", "Silmek istediğinize emin misiniz?"):
            self.app.word_manager.delete(index)
            self.refresh_word_list()

    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if path:
            success, msg = self.app.word_manager.import_csv(path)
            messagebox.showinfo("İçe Aktarma", msg)
            self.refresh_word_list()

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if path:
            success, msg = self.app.word_manager.export_csv(path)
            messagebox.showinfo("Dışa Aktarma", msg)

    def save_settings(self):
        self.app.settings["theme"] = self.theme_var.get()
        self.app.settings["animation"] = self.anim_var.get()
        self.app.settings["position"] = self.pos_var.get()
        self.app.settings["startup"] = self.startup_var.get()
        
        try:
            self.app.settings["interval"] = int(self.interval_var.get())
            self.app.settings["width"] = int(self.w_var.get())
            self.app.settings["height"] = int(self.h_var.get())
        except ValueError:
            messagebox.showerror("Hata", "Lütfen sayısal değerler girin.")
            return

        self.app.save_settings()
        self.app.widget.theme = THEMES[self.app.settings["theme"]]
        self.app.widget.trans_color = self.app.widget.theme["trans"]
        if IS_WINDOWS:
            self.app.widget.attributes('-transparentcolor', self.app.widget.trans_color)
        self.app.widget.canvas.config(bg=self.app.widget.trans_color)
        
        self.app.schedule_next_word(0)
        self.destroy()

    def on_close(self):
        self.destroy()

# ==============================================================================
# 6. SİSTEM TEPSİSİ (TRAY)
# ==============================================================================
class SystemTray:
    def __init__(self, app):
        self.app = app
        self.icon = None
        self._create_icon()

    def _create_icon(self):
        # Basit bir 'W' harfi veya kare ikon oluştur
        img = Image.new('RGB', (64, 64), color=(30, 30, 30))
        d = ImageDraw.Draw(img)
        d.text((20, 15), "W", fill=(0, 122, 204))
        self.image = img

    def setup(self):
        menu = pystray.Menu(
            pystray.MenuItem("Ayarlar", lambda: self.app.root.after(0, self.app.show_settings)),
            pystray.MenuItem("Sonraki Kelime", lambda: self.app.root.after(0, self.app.widget.force_next)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Çıkış", lambda: self.app.root.after(0, self.app.exit_app))
        )
        self.icon = pystray.Icon("KelimeWidget", self.image, "Kelime Widget", menu)
        # pystray run blocking olduğu için thread'de çalıştır
        threading.Thread(target=self.icon.run, daemon=True).start()

    def stop(self):
        if self.icon:
            self.icon.stop()

# ==============================================================================
# 7. ANA UYGULAMA KONTROLÜSÜ
# ==============================================================================
class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw() # Ana pencereyi gizle
        
        self.settings = self._load_settings()
        self.word_manager = WordManager()
        
        self.widget = WordWidget(self)
        self.tray = SystemTray(self)
        self.tray.setup()

        self._setup_startup()
        
        # İlk açılışta ayarları göster
        self.root.after(500, self.show_settings)
        self.root.after(1000, self.schedule_next_word)
        
        self.root.mainloop()

    def _load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Eksik anahtarları varsayılanlarla doldur
                    for k, v in DEFAULT_SETTINGS.items():
                        if k not in loaded:
                            loaded[k] = v
                    return loaded
            except:
                pass
        return DEFAULT_SETTINGS.copy()

    def save_settings(self):
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=4, ensure_ascii=False)

    def _setup_startup(self):
        if not IS_WINDOWS: return
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "KelimeWidget"
        app_path = f'"{sys.executable}" "{os.path.abspath(__file__)}"'
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            if self.settings["startup"]:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
            else:
                try: winreg.DeleteValue(key, app_name)
                except FileNotFoundError: pass
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Registry hatası: {e}")

    def show_settings(self):
        if not hasattr(self, 'settings_window') or not self.settings_window.winfo_exists():
            self.settings_window = SettingsWindow(self)

    def schedule_next_word(self, delay=None):
        if delay is None:
            delay = self.settings["interval"] * 1000
        
        if hasattr(self, 'timer_id') and self.timer_id:
            self.root.after_cancel(self.timer_id)
            
        self.timer_id = self.root.after(delay, self._show_and_schedule)

    def _show_and_schedule(self):
        self.widget.show_word()
        # Widget 12 saniye ekranda kalacak, sonra tekrar schedule edilecek
        # Toplam döngü: 12sn gösterim + (interval * 1000) bekleme
        wait_time = 12000 + (self.settings["interval"] * 1000)
        self.timer_id = self.root.after(wait_time, self._show_and_schedule)

    def exit_app(self):
        self.save_settings()
        self.tray.stop()
        self.root.quit()
        sys.exit()

if __name__ == "__main__":
    App()