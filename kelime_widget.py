#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
İngilizce-Türkçe Masaüstü Kelime Widget Uygulaması
kelime_widget.py - Tek dosya, tam çalışır uygulama
font.measure() ile KESİN piksel ölçümü
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tkinter.font as tkfont
import json
import csv
import os
import sys
import random
import time
import threading

try:
    import pystray
    from PIL import Image, ImageDraw, ImageFont
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False

try:
    import winreg
    WINREG_AVAILABLE = True
except ImportError:
    WINREG_AVAILABLE = False

# ─── Taşınabilir EXE Desteği ──────────────────────────────────────────────────

def get_app_dir():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    data_dir = os.path.join(base_path, "data")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

APP_NAME = "Kelime Widget"
APP_DIR = get_app_dir()
SETTINGS_FILE = os.path.join(APP_DIR, "settings.json")
WORDS_FILE = os.path.join(APP_DIR, "words.json")
CUSTOM_LISTS_FILE = os.path.join(APP_DIR, "custom_lists.json")

# ─── Sabitler ─────────────────────────────────────────────────────────────────

MONO_FONT = "Montserrat Bold"

THEMES = {
    "Modern Koyu": {"bg": "#1E1E2E", "fg": "#CDD6F4", "accent": "#89B4FA", "panel": "#313244"},
    "Neon": {"bg": "#0A0A0F", "fg": "#00FF9F", "accent": "#FF00FF", "panel": "#1A1A2E"},
    "Klasik Koyu": {"bg": "#2D2D2D", "fg": "#E8E8E8", "accent": "#FFB347", "panel": "#3A3A3A"},
    "Matrix": {"bg": "#000000", "fg": "#00FF41", "accent": "#008F11", "panel": "#0D0D0D"},
    "Modern Açık": {"bg": "#FFFFFF", "fg": "#2C3E50", "accent": "#3498DB", "panel": "#F8F9FA"},
    "Klasik Açık": {"bg": "#F5F5F5", "fg": "#212121", "accent": "#FF6B35", "panel": "#FFFFFF"},
    "Gece Mavisi": {"bg": "#1a1a2e", "fg": "#eaeaea", "accent": "#4ecca3", "panel": "#16213e"},
    "Gün Batımı": {"bg": "#2d1b4e", "fg": "#ffd6e0", "accent": "#ff85a2", "panel": "#3d2b5e"},
    "Okyanus": {"bg": "#001f3f", "fg": "#E0FFFF", "accent": "#0074D9", "panel": "#003366"},
    "Orman": {"bg": "#1e3f20", "fg": "#e8f5e9", "accent": "#4CAF50", "panel": "#2e5f30"},
    "Kahve": {"bg": "#3e2723", "fg": "#efebe9", "accent": "#d7ccc8", "panel": "#4e342e"},
    "Lavanta": {"bg": "#3d2b5e", "fg": "#f3e5f5", "accent": "#ab47bc", "panel": "#4a3b6e"},
    "Turuncu": {"bg": "#e65100", "fg": "#fff3e0", "accent": "#ffcc80", "panel": "#ff6d00"},
    "Deniz": {"bg": "#006064", "fg": "#e0f7fa", "accent": "#4dd0e1", "panel": "#00838f"},
}

ANIMATIONS = ["Daktilo", "Tırmanma", "Süzülme", "Birleştirme", "Blok",
              "Patlama", "Sıçrama", "İnme", "Kaykay", "Yayılım", "Netleştirme"]

DEFAULT_WORD_LISTS = ["Kullanıcı Listesi", "A1 Seviye", "A2 Seviye", "B1 Seviye", "B2 Seviye", "TOEFL", "IELTS"]

BORDER_OPTIONS = {
    "Yok": {"width": 0, "color": None},
    "İnce": {"width": 1, "color": "#555555"},
    "Orta": {"width": 2, "color": "#007ACC"},
    "Kalın": {"width": 3, "color": "#89B4FA"},
    "Yuvarlak": {"width": 2, "color": "#4ecca3"},
}

ASPECT_RATIO = 2.5

DEFAULT_SETTINGS = {
    "theme": "Modern Koyu",
    "animation": "Daktilo",
    "interval": 30,
    "display_duration": 11,
    "opacity": 95,
    "width": 500,
    "height": 200,
    "position_x": 100,
    "position_y": 100,
    "start_with_windows": False,
    "font_size": 28,
    "sentence_font_size": 13,
    "selected_lists": ["Kullanıcı Listesi"],
    "border": "Orta",
}

A1_WORDS = [
    {"en": "apple", "tr": "elma", "sentence": "I eat an apple every day.", "sentence_tr": "Her gün bir elma yerim.", "list": "A1 Seviye"},
    {"en": "book", "tr": "kitap", "sentence": "She reads a book before bed.", "sentence_tr": "Yatmadan önce kitap okur.", "list": "A1 Seviye"},
    {"en": "cat", "tr": "kedi", "sentence": "The cat is sleeping on the sofa.", "sentence_tr": "Kedi kanepede uyuyor.", "list": "A1 Seviye"},
    {"en": "dog", "tr": "köpek", "sentence": "My dog likes to play in the park.", "sentence_tr": "Köpeğim parkta oynamayı sever.", "list": "A1 Seviye"},
    {"en": "house", "tr": "ev", "sentence": "They live in a big house.", "sentence_tr": "Büyük bir evde yaşıyorlar.", "list": "A1 Seviye"},
    {"en": "water", "tr": "su", "sentence": "Please give me some water.", "sentence_tr": "Lütfen bana biraz su ver.", "list": "A1 Seviye"},
    {"en": "friend", "tr": "arkadaş", "sentence": "She is my best friend.", "sentence_tr": "O benim en iyi arkadaşım.", "list": "A1 Seviye"},
    {"en": "school", "tr": "okul", "sentence": "The children go to school every day.", "sentence_tr": "Çocuklar her gün okula gider.", "list": "A1 Seviye"},
    {"en": "teacher", "tr": "öğretmen", "sentence": "Our teacher is very kind.", "sentence_tr": "Öğretmenimiz çok nazik.", "list": "A1 Seviye"},
    {"en": "family", "tr": "aile", "sentence": "I love my family very much.", "sentence_tr": "Ailemi çok seviyorum.", "list": "A1 Seviye"},
]

A2_WORDS = [
    {"en": "adventure", "tr": "macera", "sentence": "Life is an adventure.", "sentence_tr": "Hayat bir maceradır.", "list": "A2 Seviye"},
    {"en": "believe", "tr": "inanmak", "sentence": "I believe in you.", "sentence_tr": "Sana inanıyorum.", "list": "A2 Seviye"},
    {"en": "celebrate", "tr": "kutlamak", "sentence": "We celebrate birthdays.", "sentence_tr": "Doğum günlerini kutlarız.", "list": "A2 Seviye"},
    {"en": "decide", "tr": "karar vermek", "sentence": "You must decide quickly.", "sentence_tr": "Hızlıca karar vermelisin.", "list": "A2 Seviye"},
    {"en": "environment", "tr": "çevre", "sentence": "Protect the environment.", "sentence_tr": "Çevreyi koru.", "list": "A2 Seviye"},
    {"en": "experience", "tr": "deneyim", "sentence": "Travel gives experience.", "sentence_tr": "Seyahat deneyim kazandırır.", "list": "A2 Seviye"},
    {"en": "imagine", "tr": "hayal etmek", "sentence": "Imagine a better world.", "sentence_tr": "Daha iyi bir dünya hayal et.", "list": "A2 Seviye"},
    {"en": "journey", "tr": "yolculuk", "sentence": "The journey was long.", "sentence_tr": "Yolculuk uzundu.", "list": "A2 Seviye"},
    {"en": "knowledge", "tr": "bilgi", "sentence": "Knowledge is power.", "sentence_tr": "Bilgi güçtür.", "list": "A2 Seviye"},
    {"en": "language", "tr": "dil", "sentence": "Learning a language is fun.", "sentence_tr": "Dil öğrenmek eğlencelidir.", "list": "A2 Seviye"},
]

TOEFL_WORDS = [
    {"en": "abundant", "tr": "bol / bereketli", "sentence": "The region has abundant resources.", "sentence_tr": "Bölge bol kaynaklara sahiptir.", "list": "TOEFL"},
    {"en": "accommodate", "tr": "yerleştirmek", "sentence": "The hotel can accommodate 500 guests.", "sentence_tr": "Otel 500 konuğu ağırlayabilir.", "list": "TOEFL"},
    {"en": "accumulate", "tr": "biriktirmek", "sentence": "Dust accumulates quickly.", "sentence_tr": "Toz hızlıca birikir.", "list": "TOEFL"},
    {"en": "advocate", "tr": "savunmak", "sentence": "She advocates for rights.", "sentence_tr": "Hakları savunuyor.", "list": "TOEFL"},
    {"en": "ambiguous", "tr": "belirsiz", "sentence": "The instructions were ambiguous.", "sentence_tr": "Talimatlar belirsizdi.", "list": "TOEFL"},
    {"en": "analyze", "tr": "analiz etmek", "sentence": "Scientists analyze data.", "sentence_tr": "Bilim insanları veri analiz eder.", "list": "TOEFL"},
    {"en": "anticipate", "tr": "beklemek / öngörmek", "sentence": "We anticipate growth.", "sentence_tr": "Büyüme bekliyoruz.", "list": "TOEFL"},
    {"en": "comprehensive", "tr": "kapsamlı", "sentence": "We need a comprehensive plan.", "sentence_tr": "Kapsamlı bir plana ihtiyacımız var.", "list": "TOEFL"},
    {"en": "controversial", "tr": "tartışmalı", "sentence": "The decision was controversial.", "sentence_tr": "Karar tartışmalıydı.", "list": "TOEFL"},
    {"en": "demonstrate", "tr": "göstermek", "sentence": "The experiment demonstrates the theory.", "sentence_tr": "Deney teoriyi gösteriyor.", "list": "TOEFL"},
]

IELTS_WORDS = [
    {"en": "acquisition", "tr": "edinme", "sentence": "Language acquisition takes time.", "sentence_tr": "Dil edinimi zaman alır.", "list": "IELTS"},
    {"en": "adequate", "tr": "yeterli", "sentence": "The supply was adequate.", "sentence_tr": "Kaynak yeterliydi.", "list": "IELTS"},
    {"en": "allocate", "tr": "tahsis etmek", "sentence": "Allocate more resources.", "sentence_tr": "Daha fazla kaynak tahsis et.", "list": "IELTS"},
    {"en": "alternative", "tr": "alternatif", "sentence": "Find an alternative solution.", "sentence_tr": "Alternatif bir çözüm bul.", "list": "IELTS"},
    {"en": "approach", "tr": "yaklaşım", "sentence": "We need a new approach.", "sentence_tr": "Yeni bir yaklaşım lazım.", "list": "IELTS"},
    {"en": "assess", "tr": "değerlendirmek", "sentence": "Assess the situation.", "sentence_tr": "Durumu değerlendir.", "list": "IELTS"},
    {"en": "attribute", "tr": "atfetmek", "sentence": "She attributes success to hard work.", "sentence_tr": "Başarıyı sıkı çalışmaya atfediyor.", "list": "IELTS"},
    {"en": "coherent", "tr": "tutarlı", "sentence": "The argument was coherent.", "sentence_tr": "Argüman tutarlıydı.", "list": "IELTS"},
    {"en": "collaborate", "tr": "işbirliği yapmak", "sentence": "Teams must collaborate.", "sentence_tr": "Ekipler işbirliği yapmalı.", "list": "IELTS"},
    {"en": "compensate", "tr": "tazmin etmek", "sentence": "Nothing can compensate for loss.", "sentence_tr": "Hiçbir şey kaybı telafi edemez.", "list": "IELTS"},
]

# ─── Yardımcı Fonksiyonlar ────────────────────────────────────────────────────

def ensure_app_dir():
    os.makedirs(APP_DIR, exist_ok=True)

def load_settings():
    ensure_app_dir()
    settings = DEFAULT_SETTINGS.copy()
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            if saved.get("theme") == "Modern":
                saved["theme"] = "Modern Koyu"
            if saved.get("theme") not in THEMES:
                saved["theme"] = "Modern Koyu"
            if saved.get("animation") not in ANIMATIONS:
                saved["animation"] = "Daktilo"
            if not isinstance(saved.get("position_x"), int):
                saved["position_x"] = 100
            if not isinstance(saved.get("position_y"), int):
                saved["position_y"] = 100
            if "selected_lists" not in saved or not saved["selected_lists"]:
                saved["selected_lists"] = ["Kullanıcı Listesi"]
            if "border" not in saved:
                saved["border"] = "Orta"
            if "opacity" not in saved or saved["opacity"] < 30:
                saved["opacity"] = 95
            if "start_with_windows" not in saved:
                saved["start_with_windows"] = False
            if "width" in saved and "height" not in saved:
                saved["height"] = int(saved["width"] / ASPECT_RATIO)
            elif "height" in saved and "width" not in saved:
                saved["width"] = int(saved["height"] * ASPECT_RATIO)
            settings.update(saved)
        except Exception:
            pass
    return settings

def save_settings(settings):
    ensure_app_dir()
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

def load_custom_lists():
    ensure_app_dir()
    if os.path.exists(CUSTOM_LISTS_FILE):
        try:
            with open(CUSTOM_LISTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_custom_lists(lists):
    ensure_app_dir()
    with open(CUSTOM_LISTS_FILE, "w", encoding="utf-8") as f:
        json.dump(lists, f, ensure_ascii=False, indent=2)

def get_all_word_lists():
    custom = load_custom_lists()
    return DEFAULT_WORD_LISTS + custom

def load_words():
    ensure_app_dir()
    all_words = []
    all_words.extend(A1_WORDS)
    all_words.extend(A2_WORDS)
    all_words.extend(TOEFL_WORDS)
    all_words.extend(IELTS_WORDS)
    
    if os.path.exists(WORDS_FILE):
        try:
            with open(WORDS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                for w in data:
                    if "list" not in w:
                        w["list"] = "Kullanıcı Listesi"
                    if "sentence_tr" not in w:
                        w["sentence_tr"] = ""
                    exists = any(ew["en"].lower() == w["en"].lower() and ew.get("list") == w.get("list") for ew in all_words)
                    if not exists:
                        all_words.append(w)
        except Exception:
            pass
    return all_words

def save_all_words(words):
    ensure_app_dir()
    default_ens = set()
    for w in A1_WORDS + A2_WORDS + TOEFL_WORDS + IELTS_WORDS:
        default_ens.add(w["en"].lower())
    words_to_save = [w for w in words if w["en"].lower() not in default_ens]
    with open(WORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(words_to_save, f, ensure_ascii=False, indent=2)

def capitalize_first(text):
    if not text:
        return text
    return text[0].upper() + text[1:]

def get_list_counts(words, all_lists):
    counts = {}
    for lst in all_lists:
        counts[lst] = len([w for w in words if w.get("list") == lst])
    return counts

def set_startup(enable):
    if not WINREG_AVAILABLE:
        return
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        if enable:
            exe_path = f'"{sys.executable}" "{os.path.abspath(__file__)}"'
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe_path)
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except Exception:
        pass


# ─── KESİN METİN ÖLÇÜM FONKSİYONLARI ─────────────────────────────────────────

def measure_text_width(text, font_name, font_size, bold=False):
    """
    Tkinter font.measure() ile metnin GERÇEK piksel genişliğini ölç.
    """
    weight = "bold" if bold else "normal"
    font = tkfont.Font(family=font_name, size=font_size, weight=weight)
    return font.measure(text)

def get_line_height(font_name, font_size):
    """Satır yüksekliğini piksel olarak al"""
    font = tkfont.Font(family=font_name, size=font_size)
    return font.metrics("linespace")

def smart_fit_text(text, max_width_px, max_height_px, font_name, max_font=80, min_font=7):
    """
    Metni widget alanına KESİN olarak sığdır.
    
    Algoritma:
    1. Tek satırda en büyük fontu bul (binary search)
    2. Metni boşluktan ikiye böl, 2 satır için en büyük fontu bul
    3. Hangisi DAHA BÜYÜK font veriyorsa onu seç
    
    Tek kelimelik metinler → sadece tek satır denenir.
    ASLA widget boyutunu geçmez.
    """
    if not text:
        return 10, "", 1
    
    # ── AŞAMA 1: Tek satırda en büyük fontu bul ──
    low = min_font
    high = max_font
    best_single_font = min_font
    
    while low <= high:
        mid_font = (low + high) // 2
        width = measure_text_width(text, font_name, mid_font, bold=False)
        line_h = get_line_height(font_name, mid_font)
        
        # TEK SATIR için: line_h <= max_height_px (line_h * 2 DEĞİL!)
        if width <= max_width_px and line_h <= max_height_px:
            best_single_font = mid_font
            low = mid_font + 1
        else:
            high = mid_font - 1
    
    single_result = (best_single_font, text, 1)
    
    # ── AŞAMA 2: 2 satıra böl (boşluklardan) ──
    words = text.split(' ')
    
    if len(words) <= 1:
        # Tek kelimelik metin → bölünemez, sadece tek satır sonucunu döndür
        return single_result
    
    # Kelimeleri ortadan ikiye böl
    mid_idx = len(words) // 2
    line1 = ' '.join(words[:mid_idx])
    line2 = ' '.join(words[mid_idx:])
    
    # 2 satır için en büyük fontu bul (binary search)
    low = min_font
    high = max_font
    best_double_font = min_font
    
    while low <= high:
        mid_font = (low + high) // 2
        w1 = measure_text_width(line1, font_name, mid_font, bold=False)
        w2 = measure_text_width(line2, font_name, mid_font, bold=False)
        line_h = get_line_height(font_name, mid_font)
        
        # 2 SATIR için: line_h * 2 <= max_height_px
        if w1 <= max_width_px and w2 <= max_width_px and line_h * 2 <= max_height_px:
            best_double_font = mid_font
            low = mid_font + 1
        else:
            high = mid_font - 1
    
    double_result = (best_double_font, f"{line1}\n{line2}", 2)
    
    # ── AŞAMA 3: Hangisi DAHA BÜYÜK font veriyorsa onu seç ──
    if double_result[0] > single_result[0]:
        return double_result
    else:
        return single_result
    """
    Metni widget alanına KESİN olarak sığdır.
    
    Algoritma:
    1. Tek satırda en büyük fontu bul (binary search)
    2. Metni boşluktan ikiye böl, 2 satır için en büyük fontu bul
    3. Hangisi DAHA BÜYÜK font veriyorsa onu seç
    
    ASLA widget boyutunu geçmez.
    """
    if not text:
        return 10, "", 1
    
    # ── AŞAMA 1: Tek satırda en büyük fontu bul ──
    low = min_font
    high = max_font
    best_single_font = min_font
    
    while low <= high:
        mid_font = (low + high) // 2
        width = measure_text_width(text, font_name, mid_font, bold=False)
        
        if width <= max_width_px:
            best_single_font = mid_font
            low = mid_font + 1
        else:
            high = mid_font - 1
    
    # Tek satır yükseklik kontrolü
    single_line_h = get_line_height(font_name, best_single_font)
    if single_line_h <= max_height_px:
        single_result = (best_single_font, text, 1)
    else:
        single_result = (min_font, text, 1)
    
    # ── AŞAMA 2: 2 satıra böl (boşluklardan) ──
    words = text.split(' ')
    
    if len(words) <= 1:
        # Tek kelimelik metin, bölünemez
        return single_result
    
    # Kelimeleri ikiye böl (ortadan)
    mid_idx = len(words) // 2
    line1_words = words[:mid_idx]
    line2_words = words[mid_idx:]
    line1 = ' '.join(line1_words)
    line2 = ' '.join(line2_words)
    
    # 2 satır için en büyük fontu bul (binary search)
    low = min_font
    high = max_font
    best_double_font = min_font
    
    while low <= high:
        mid_font = (low + high) // 2
        w1 = measure_text_width(line1, font_name, mid_font, bold=False)
        w2 = measure_text_width(line2, font_name, mid_font, bold=False)
        line_h = get_line_height(font_name, mid_font)
        total_h = line_h * 2
        
        if w1 <= max_width_px and w2 <= max_width_px and total_h <= max_height_px:
            best_double_font = mid_font
            low = mid_font + 1
        else:
            high = mid_font - 1
    
    double_line_h = get_line_height(font_name, best_double_font)
    if double_line_h * 2 <= max_height_px:
        double_result = (best_double_font, f"{line1}\n{line2}", 2)
    else:
        double_result = (min_font, f"{line1}\n{line2}", 2)
    
    # ── AŞAMA 3: Hangisi daha büyük font veriyorsa onu seç ──
    if double_result[0] > single_result[0]:
        return double_result
    else:
        return single_result

# ─── Ana Widget Sınıfı ────────────────────────────────────────────────────────

class KelimeWidget:
    def __init__(self):
        self.settings = load_settings()
        self.words = load_words()
        self.recent_words = []
        self.running = True
        self.paused = False
        self.current_word = None
        self.animating = False
        self.anim_after_ids = []

        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        
        opacity_value = self.settings.get("opacity", 95) / 100.0
        self.root.attributes("-alpha", opacity_value)

        theme = THEMES[self.settings["theme"]]

        w = self.settings["width"]
        h = self.settings["height"]
        x = self.settings["position_x"]
        y = self.settings["position_y"]
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        border_cfg = BORDER_OPTIONS.get(self.settings.get("border", "Orta"), BORDER_OPTIONS["Orta"])
        border_width = border_cfg["width"]
        border_color = border_cfg.get("color", "#555555")

        self.panel = tk.Frame(
            self.root, bg=theme["panel"], bd=0,
            highlightthickness=border_width,
            highlightbackground=border_color if border_width > 0 else theme["panel"],
            highlightcolor=border_color if border_width > 0 else theme["panel"]
        )
        self.panel.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        self.word_label = tk.Label(
            self.panel, text="", bg=theme["panel"], fg=theme["fg"],
            font=(MONO_FONT, 28, "bold"),
            anchor="center", justify="center"
        )
        self.word_label.pack(pady=(0, 0), fill=tk.BOTH, expand=True, padx=4)

        self.meaning_label = tk.Label(
            self.panel, text="", bg=theme["panel"], fg=theme["accent"],
            font=(MONO_FONT, 20),
            anchor="center", justify="center"
        )
        self.meaning_label.pack(pady=(0, 0), fill=tk.BOTH, expand=True, padx=4)

        self.panel.bind("<ButtonPress-1>", self.start_drag)
        self.panel.bind("<B1-Motion>", self.on_drag)
        self.panel.bind("<ButtonRelease-1>", self.end_drag)
        self.word_label.bind("<ButtonPress-1>", self.start_drag)
        self.word_label.bind("<B1-Motion>", self.on_drag)
        self.meaning_label.bind("<ButtonPress-1>", self.start_drag)
        self.meaning_label.bind("<B1-Motion>", self.on_drag)

        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="⚙️ Ayarlar", command=self.open_settings)
        self.context_menu.add_command(label="📝 Quiz Modu", command=self.open_quiz)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="⏸️ Duraklat / ▶️ Devam", command=self.toggle_pause)
        self.context_menu.add_command(label="⏭️ Sonraki Kelime", command=self.next_word)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="❌ Çıkış", command=self.quit_app)

        self.root.bind("<Button-3>", self.show_context_menu)
        self.panel.bind("<Button-3>", self.show_context_menu)
        self.word_label.bind("<Button-3>", self.show_context_menu)
        self.meaning_label.bind("<Button-3>", self.show_context_menu)

        self.drag_data = {"x": 0, "y": 0}
        self.settings_window = None
        self.quiz_window = None

        self.root.withdraw()

        self.root.after(100, self.main_loop)

        if TRAY_AVAILABLE:
            self.setup_tray()

        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

    def start_drag(self, event):
        self.drag_data["x"] = event.x_root - self.root.winfo_x()
        self.drag_data["y"] = event.y_root - self.root.winfo_y()

    def on_drag(self, event):
        x = event.x_root - self.drag_data["x"]
        y = event.y_root - self.drag_data["y"]
        self.root.geometry(f"+{x}+{y}")

    def end_drag(self, event):
        self.settings["position_x"] = self.root.winfo_x()
        self.settings["position_y"] = self.root.winfo_y()
        save_settings(self.settings)

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def toggle_pause(self):
        self.paused = not self.paused

    def next_word(self):
        if not self.animating:
            self.show_word_cycle()

    def get_filtered_words(self):
        selected = self.settings.get("selected_lists", ["Kullanıcı Listesi"])
        filtered = [w for w in self.words if w.get("list") in selected]
        return filtered

    def get_random_word(self):
        filtered = self.get_filtered_words()
        if not filtered:
            return None
        if len(self.recent_words) >= 20:
            self.recent_words.clear()
        available = [w for w in filtered if w["en"].lower() not in [r.lower() for r in self.recent_words]]
        if not available:
            self.recent_words.clear()
            available = filtered
        if not available:
            return None
        word = random.choice(available)
        self.recent_words.append(word["en"].lower())
        return word

    def main_loop(self):
        if not self.running:
            return
        if not self.paused and not self.animating:
            self.show_word_cycle()
        interval_ms = int(self.settings["interval"] * 1000)
        self.root.after(interval_ms, self.main_loop)

    def cancel_animations(self):
        for aid in self.anim_after_ids:
            try:
                self.root.after_cancel(aid)
            except:
                pass
        self.anim_after_ids.clear()

    def calculate_font_sizes(self, en_text, tr_text):
        """
        KESİN hesaplama: font.measure() ile gerçek piksel ölçümü.
        Her gösterimde yeniden hesaplanır.
        """
        w = self.settings["width"]
        h = self.settings["height"]
        
        available_width = w - 10  # Padding
        
        # Her bölüm %50 yükseklik
        word_section_height = h * 0.50
        meaning_section_height = h * 0.50
        
        # KESİN ölçüm ile font ve metin bul
        word_font, word_display, word_lines = smart_fit_text(
            en_text, available_width, word_section_height, MONO_FONT, max_font=80, min_font=8
        )
        meaning_font, meaning_display, meaning_lines = smart_fit_text(
            tr_text, available_width, meaning_section_height, MONO_FONT, max_font=70, min_font=7
        )
        
        return word_font, word_display, meaning_font, meaning_display

    def show_word_cycle(self):
        filtered = self.get_filtered_words()
        if len(filtered) == 0:
            return
        self.animating = True
        word_data = self.get_random_word()
        if not word_data:
            self.animating = False
            return
        self.current_word = word_data

        en_text = capitalize_first(word_data["en"])
        tr_text = word_data["tr"]

        self.root.deiconify()
        
        # KESİN hesaplama (her seferinde yeniden)
        word_font, word_display, meaning_font, meaning_display = self.calculate_font_sizes(en_text, tr_text)
        
        theme = THEMES[self.settings["theme"]]
        
        self.cancel_animations()
        
        # wraplength=9999 → Tkinter bölmesin, bizim \n'lerimizle bölünsün
        self.word_label.config(
            font=(MONO_FONT, word_font, "bold"),
            wraplength=9999,
            bg=theme["panel"], fg=theme["fg"],
            text=""
        )
        self.meaning_label.config(
            font=(MONO_FONT, meaning_font),
            wraplength=9999,
            bg=theme["panel"], fg=theme["accent"],
            text=""
        )

        animation = self.settings["animation"]
        display_duration = self.settings["display_duration"]

        self.animate_text(self.word_label, word_display, animation, duration=1.2)

        meaning_delay = int(display_duration * 0.4 * 1000)
        aid = self.root.after(meaning_delay, lambda: self.animate_text(self.meaning_label, meaning_display, animation, duration=1.2))
        self.anim_after_ids.append(aid)

        hide_delay = int(display_duration * 1000)
        aid = self.root.after(hide_delay, self.hide_widget)
        self.anim_after_ids.append(aid)

    def hide_widget(self):
        self.word_label.config(text="")
        self.meaning_label.config(text="")
        self.root.withdraw()
        self.animating = False

    def animate_text(self, label, text, animation, duration=1.5):
        label.config(text="")
        steps = max(5, int(duration * 20))
        step_time = max(20, int((duration * 1000) / steps))

        if animation == "Daktilo":
            self.anim_typewriter(label, text, steps, step_time, 0)
        elif animation == "Tırmanma":
            self.anim_climb(label, text, steps, step_time, 0)
        elif animation == "Süzülme":
            self.anim_glide(label, text, steps, step_time, 0)
        elif animation == "Birleştirme":
            self.anim_merge(label, text, steps, step_time, 0)
        elif animation == "Blok":
            self.anim_block(label, text, steps, step_time, 0)
        elif animation == "Patlama":
            self.anim_explode(label, text, steps, step_time, 0)
        elif animation == "Sıçrama":
            self.anim_bounce(label, text, steps, step_time, 0)
        elif animation == "İnme":
            self.anim_descend(label, text, steps, step_time, 0)
        elif animation == "Kaykay":
            self.anim_skateboard(label, text, steps, step_time, 0)
        elif animation == "Yayılım":
            self.anim_spread(label, text, steps, step_time, 0)
        elif animation == "Netleştirme":
            self.anim_focus(label, text, steps, step_time, 0)
        else:
            label.config(text=text)

    def anim_typewriter(self, label, text, steps, step_time, current):
        if current >= len(text):
            label.config(text=text)
            return
        label.config(text=text[:current + 1])
        aid = self.root.after(step_time, lambda: self.anim_typewriter(label, text, steps, step_time, current + 1))
        self.anim_after_ids.append(aid)

    def anim_climb(self, label, text, steps, step_time, current):
        if current > steps:
            label.config(text=text)
            return
        progress = current / steps
        visible_chars = int(len(text) * progress)
        label.config(text=text[:visible_chars])
        aid = self.root.after(step_time, lambda: self.anim_climb(label, text, steps, step_time, current + 1))
        self.anim_after_ids.append(aid)

    def anim_glide(self, label, text, steps, step_time, current):
        if current > steps:
            label.config(text=text)
            return
        progress = current / steps
        visible_chars = int(len(text) * progress)
        label.config(text=text[:visible_chars])
        aid = self.root.after(step_time, lambda: self.anim_glide(label, text, steps, step_time, current + 1))
        self.anim_after_ids.append(aid)

    def anim_merge(self, label, text, steps, step_time, current):
        if current > steps:
            label.config(text=text)
            return
        progress = current / steps
        if progress < 0.5:
            garbled = ""
            for i, ch in enumerate(text):
                if i % 2 == 0 and progress < 0.3:
                    garbled += random.choice("░█")
                else:
                    garbled += ch
            label.config(text=garbled)
        else:
            visible = int(len(text) * (progress - 0.5) * 2)
            label.config(text=text[:visible])
        aid = self.root.after(step_time, lambda: self.anim_merge(label, text, steps, step_time, current + 1))
        self.anim_after_ids.append(aid)

    def anim_block(self, label, text, steps, step_time, current):
        if current > steps:
            label.config(text=text)
            return
        progress = current / steps
        blocks = "█" * int(len(text) * progress)
        if progress > 0.7:
            reveal = int(len(text) * (progress - 0.7) / 0.3)
            label.config(text=text[:reveal])
        else:
            label.config(text=blocks)
        aid = self.root.after(step_time, lambda: self.anim_block(label, text, steps, step_time, current + 1))
        self.anim_after_ids.append(aid)

    def anim_explode(self, label, text, steps, step_time, current):
        if current > steps:
            label.config(text=text)
            return
        progress = current / steps
        if progress < 0.4:
            label.config(text="")
        elif progress < 0.6:
            scattered = ""
            for ch in text:
                if random.random() < progress:
                    scattered += ch
                else:
                    scattered += random.choice("·•○")
            label.config(text=scattered)
        else:
            visible = int(len(text) * (progress - 0.6) / 0.4)
            label.config(text=text[:visible])
        aid = self.root.after(step_time, lambda: self.anim_explode(label, text, steps, step_time, current + 1))
        self.anim_after_ids.append(aid)

    def anim_bounce(self, label, text, steps, step_time, current):
        if current > steps:
            label.config(text=text)
            return
        progress = current / steps
        visible_chars = int(len(text) * min(1.0, progress * 1.5))
        display = text[:visible_chars]
        if visible_chars < len(text) and current % 2 == 0:
            display += "_"
        label.config(text=display)
        aid = self.root.after(step_time, lambda: self.anim_bounce(label, text, steps, step_time, current + 1))
        self.anim_after_ids.append(aid)

    def anim_descend(self, label, text, steps, step_time, current):
        if current > steps:
            label.config(text=text)
            return
        progress = current / steps
        visible_chars = int(len(text) * progress)
        label.config(text=text[:visible_chars])
        aid = self.root.after(step_time, lambda: self.anim_descend(label, text, steps, step_time, current + 1))
        self.anim_after_ids.append(aid)

    def anim_skateboard(self, label, text, steps, step_time, current):
        if current > steps:
            label.config(text=text)
            return
        progress = current / steps
        visible_chars = int(len(text) * progress)
        start_idx = len(text) - visible_chars
        label.config(text=text[start_idx:])
        aid = self.root.after(step_time, lambda: self.anim_skateboard(label, text, steps, step_time, current + 1))
        self.anim_after_ids.append(aid)

    def anim_spread(self, label, text, steps, step_time, current):
        if current > steps:
            label.config(text=text)
            return
        progress = current / steps
        mid = len(text) // 2
        half_width = int((len(text) / 2) * progress)
        start = max(0, mid - half_width)
        end = min(len(text), mid + half_width)
        label.config(text=text[start:end])
        aid = self.root.after(step_time, lambda: self.anim_spread(label, text, steps, step_time, current + 1))
        self.anim_after_ids.append(aid)

    def anim_focus(self, label, text, steps, step_time, current):
        if current > steps:
            label.config(text=text)
            return
        progress = current / steps
        if progress < 0.5:
            dots = "•" * int(len(text) * progress * 2)
            label.config(text=dots)
        else:
            reveal = int(len(text) * (progress - 0.5) * 2)
            label.config(text=text[:reveal])
        aid = self.root.after(step_time, lambda: self.anim_focus(label, text, steps, step_time, current + 1))
        self.anim_after_ids.append(aid)

    def open_settings(self):
        if self.settings_window and self.settings_window.win.winfo_exists():
            self.settings_window.win.focus()
            return
        self.settings_window = SettingsWindow(self)

    def open_quiz(self):
        if self.quiz_window and self.quiz_window.win.winfo_exists():
            self.quiz_window.win.focus()
            return
        self.quiz_window = QuizWindow(self)

    def apply_settings(self):
        theme = THEMES[self.settings["theme"]]
        opacity_value = self.settings.get("opacity", 95) / 100.0
        self.root.attributes("-alpha", opacity_value)
        
        self.root.configure(bg=theme["bg"])
        border_cfg = BORDER_OPTIONS.get(self.settings.get("border", "Orta"), BORDER_OPTIONS["Orta"])
        border_width = border_cfg["width"]
        border_color = border_cfg.get("color", "#555555")
        
        self.panel.config(
            bg=theme["panel"],
            highlightthickness=border_width,
            highlightbackground=border_color,
            highlightcolor=border_color
        )
        
        self.word_label.config(bg=theme["panel"], fg=theme["fg"])
        self.meaning_label.config(bg=theme["panel"], fg=theme["accent"])
        
        w = self.settings["width"]
        h = self.settings["height"]
        x = self.settings["position_x"]
        y = self.settings["position_y"]
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        
        # Widget açıksa mevcut kelimeyi yeniden göster
        if self.root.winfo_ismapped() and self.current_word:
            self.cancel_animations()
            self.animating = False
            self.show_word_cycle()

    def setup_tray(self):
        self._last_click_time = 0

        def create_image():
            img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.rectangle([8, 8, 56, 56], fill="#89B4FA", outline="#FFFFFF", width=2)
            try:
                font = ImageFont.truetype("arial.ttf", 28)
            except:
                font = ImageFont.load_default()
            draw.text((18, 14), "W", fill="#FFFFFF", font=font)
            return img

        def on_tray_click(icon, item):
            current_time = time.time()
            if current_time - self._last_click_time < 0.5:
                self.root.after(0, self.open_settings)
            else:
                self.root.after(0, self.root.deiconify)
            self._last_click_time = current_time

        def on_quit(icon, item):
            self.running = False
            self.root.after(0, self.root.destroy)

        def on_settings(icon, item):
            self.root.after(0, self.open_settings)

        menu = pystray.Menu(
            pystray.MenuItem("Göster", on_tray_click, default=True),
            pystray.MenuItem("Ayarlar", on_settings),
            pystray.MenuItem("Çıkış", on_quit),
        )
        self.tray_icon = pystray.Icon(APP_NAME, create_image(), APP_NAME, menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def quit_app(self):
        self.running = False
        save_settings(self.settings)
        if TRAY_AVAILABLE and hasattr(self, "tray_icon"):
            try:
                self.tray_icon.stop()
            except:
                pass
        self.root.destroy()


# ─── Scroll Edilebilir Sekme ──────────────────────────────────────────────────

class ScrollableTab:
    def __init__(self, parent, bg_color="#1a1a2e"):
        self.container = ttk.Frame(parent)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.container, bg=bg_color, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self._bind_mousewheel(self.canvas)
        self._bind_mousewheel(self.scrollable_frame)
        self._bind_mousewheel(self.container)
        self._bind_mousewheel(self.scrollbar)
    
    def _bind_mousewheel(self, widget):
        widget.bind("<MouseWheel>", self._on_mousewheel, add="+")
        widget.bind("<Button-4>", self._on_mousewheel, add="+")
        widget.bind("<Button-5>", self._on_mousewheel, add="+")
        widget.bind_class("TFrame", "<MouseWheel>", self._on_mousewheel, add="+")
        widget.bind_class("TFrame", "<Button-4>", self._on_mousewheel, add="+")
        widget.bind_class("TFrame", "<Button-5>", self._on_mousewheel, add="+")
        widget.bind_class("TLabel", "<MouseWheel>", self._on_mousewheel, add="+")
        widget.bind_class("TLabel", "<Button-4>", self._on_mousewheel, add="+")
        widget.bind_class("TLabel", "<Button-5>", self._on_mousewheel, add="+")
        widget.bind_class("TButton", "<MouseWheel>", self._on_mousewheel, add="+")
        widget.bind_class("TButton", "<Button-4>", self._on_mousewheel, add="+")
        widget.bind_class("TButton", "<Button-5>", self._on_mousewheel, add="+")
        widget.bind_class("TCheckbutton", "<MouseWheel>", self._on_mousewheel, add="+")
        widget.bind_class("TCheckbutton", "<Button-4>", self._on_mousewheel, add="+")
        widget.bind_class("TCheckbutton", "<Button-5>", self._on_mousewheel, add="+")
        widget.bind_class("TEntry", "<MouseWheel>", self._on_mousewheel, add="+")
        widget.bind_class("TEntry", "<Button-4>", self._on_mousewheel, add="+")
        widget.bind_class("TEntry", "<Button-5>", self._on_mousewheel, add="+")
        widget.bind_class("TCombobox", "<MouseWheel>", self._on_mousewheel, add="+")
        widget.bind_class("TCombobox", "<Button-4>", self._on_mousewheel, add="+")
        widget.bind_class("TCombobox", "<Button-5>", self._on_mousewheel, add="+")
        widget.bind_class("TScale", "<MouseWheel>", self._on_mousewheel, add="+")
        widget.bind_class("TScale", "<Button-4>", self._on_mousewheel, add="+")
        widget.bind_class("TScale", "<Button-5>", self._on_mousewheel, add="+")
        widget.bind_class("TNotebook", "<MouseWheel>", self._on_mousewheel, add="+")
        widget.bind_class("TNotebook", "<Button-4>", self._on_mousewheel, add="+")
        widget.bind_class("TNotebook", "<Button-5>", self._on_mousewheel, add="+")
        widget.bind_class("TSpinbox", "<MouseWheel>", self._on_mousewheel, add="+")
        widget.bind_class("TSpinbox", "<Button-4>", self._on_mousewheel, add="+")
        widget.bind_class("TSpinbox", "<Button-5>", self._on_mousewheel, add="+")
    
    def _on_mousewheel(self, event):
        if event.num == 5 or event.delta == -120:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta == 120:
            self.canvas.yview_scroll(-1, "units")
    
    def get_frame(self):
        return self.scrollable_frame


# ─── Ayarlar Penceresi ────────────────────────────────────────────────────────

class SettingsWindow:
    def __init__(self, widget):
        self.widget = widget
        self.settings = dict(widget.settings)
        self.words = list(widget.words)
        self.all_lists = get_all_word_lists()
        self.total_label = None

        self.win = tk.Toplevel()
        self.win.title("Ayarlar")
        self.win.geometry("620x750")
        self.win.configure(bg="#1a1a2e")
        self.win.resizable(True, True)

        self.apply_style()
        self.build_ui()

        self.win.protocol("WM_DELETE_WINDOW", self.on_close)

    def apply_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(".", background="#1a1a2e", foreground="#e0e0e0",
                         fieldbackground="#16213e", borderwidth=0)
        style.configure("TFrame", background="#1a1a2e")
        style.configure("TLabel", background="#1a1a2e", foreground="#e0e0e0",
                         font=("Segoe UI", 10))
        style.configure("Title.TLabel", background="#1a1a2e", foreground="#ffffff",
                         font=("Segoe UI", 20, "bold"))
        style.configure("Card.TFrame", background="#16213e")
        style.configure("CardTitle.TLabel", background="#16213e", foreground="#4ecca3",
                         font=("Segoe UI", 12, "bold"))
        style.configure("TButton", background="#0f3460", foreground="#e0e0e0",
                         font=("Segoe UI", 10), padding=8, borderwidth=0)
        style.map("TButton", background=[("active", "#4ecca3"), ("pressed", "#3db892")],
                   foreground=[("active", "#1a1a2e"), ("pressed", "#1a1a2e")])
        style.configure("Accent.TButton", background="#4ecca3", foreground="#1a1a2e",
                         font=("Segoe UI", 10, "bold"), padding=10)
        style.map("Accent.TButton", background=[("active", "#45b393"), ("pressed", "#3a9a7e")])
        style.configure("Success.TButton", background="#4ecca3", foreground="#1a1a2e",
                         font=("Segoe UI", 10, "bold"), padding=10)
        style.map("Success.TButton", background=[("active", "#45b393"), ("pressed", "#3a9a7e")])
        style.configure("Danger.TButton", background="#e94560", foreground="#ffffff",
                         font=("Segoe UI", 10, "bold"), padding=10)
        style.map("Danger.TButton", background=[("active", "#c73e54"), ("pressed", "#a83245")])
        style.configure("TCombobox", fieldbackground="#16213e", background="#16213e",
                         foreground="#e0e0e0", arrowcolor="#4ecca3")
        style.configure("TEntry", fieldbackground="#16213e", foreground="#e0e0e0",
                         insertcolor="#e0e0e0")
        style.configure("TNotebook", background="#1a1a2e", borderwidth=0)
        style.configure("TNotebook.Tab", background="#16213e", foreground="#e0e0e0",
                         padding=[15, 8], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab",
                   background=[("selected", "#4ecca3")],
                   foreground=[("selected", "#1a1a2e")])
        style.configure("Treeview", background="#16213e", foreground="#e0e0e0",
                         fieldbackground="#16213e", rowheight=30, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", background="#0f3460", foreground="#4ecca3",
                         font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", "#4ecca3")],
                   foreground=[("selected", "#1a1a2e")])

    def build_ui(self):
        title_frame = ttk.Frame(self.win)
        title_frame.pack(fill=tk.X, padx=20, pady=(15, 10))
        ttk.Label(title_frame, text="Ayarlar", style="Title.TLabel").pack(side=tk.LEFT)

        notebook = ttk.Notebook(self.win)
        notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        tab1_container = ttk.Frame(notebook)
        notebook.add(tab1_container, text="  Genel & Görünüm  ")
        
        scroll1 = ScrollableTab(tab1_container, bg_color="#1a1a2e")
        tab1 = scroll1.get_frame()

        card1 = self.create_card(tab1, "Bildirim Aralığı", f"({self.settings['interval']} sn)")
        card1.pack(fill=tk.X, padx=10, pady=5)

        btn_frame1 = ttk.Frame(card1)
        btn_frame1.pack(fill=tk.X, padx=10, pady=8)
        interval_presets = [("5 dk", 300), ("15 dk", 900), ("30 dk", 1800), ("1 sa", 3600)]
        for text, val in interval_presets:
            btn = ttk.Button(btn_frame1, text=text, command=lambda v=val: self.set_interval(v))
            btn.pack(side=tk.LEFT, padx=3)

        custom_frame1 = ttk.Frame(card1)
        custom_frame1.pack(fill=tk.X, padx=10, pady=(0, 8))
        ttk.Label(custom_frame1, text="Özel Süre (saniye):").pack(side=tk.LEFT)
        self.interval_var = tk.IntVar(value=self.settings["interval"])
        ttk.Entry(custom_frame1, textvariable=self.interval_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(custom_frame1, text="✓ Uygula", style="Success.TButton",
                    command=self.apply_interval).pack(side=tk.LEFT, padx=5)

        card2 = self.create_card(tab1, "Bildirim Ekranda Kalma Süresi", f"({self.settings['display_duration']} sn)")
        card2.pack(fill=tk.X, padx=10, pady=5)

        btn_frame2 = ttk.Frame(card2)
        btn_frame2.pack(fill=tk.X, padx=10, pady=8)
        duration_presets = [("10 sn", 10), ("15 sn", 15), ("20 sn", 20), ("25 sn", 25), ("30 sn", 30)]
        for text, val in duration_presets:
            btn = ttk.Button(btn_frame2, text=text, command=lambda v=val: self.set_duration(v))
            btn.pack(side=tk.LEFT, padx=3)

        custom_frame2 = ttk.Frame(card2)
        custom_frame2.pack(fill=tk.X, padx=10, pady=(0, 8))
        ttk.Label(custom_frame2, text="Özel Süre (saniye):").pack(side=tk.LEFT)
        self.duration_var = tk.IntVar(value=self.settings["display_duration"])
        ttk.Entry(custom_frame2, textvariable=self.duration_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(custom_frame2, text="✓ Uygula", style="Success.TButton",
                    command=self.apply_duration).pack(side=tk.LEFT, padx=5)

        card3 = self.create_card(tab1, "Yazı Efekti")
        card3.pack(fill=tk.X, padx=10, pady=5)

        btn_frame3 = ttk.Frame(card3)
        btn_frame3.pack(fill=tk.X, padx=10, pady=8)
        effect_presets = ["Daktilo", "Tırmanma", "Süzülme", "Birleştirme", "Blok",
                          "Patlama", "Sıçrama", "İnme", "Kaykay", "Yayılım", "Netleştirme"]
        for effect in effect_presets[:5]:
            btn = ttk.Button(btn_frame3, text=effect, command=lambda e=effect: self.set_animation(e))
            btn.pack(side=tk.LEFT, padx=3)
        
        btn_frame3b = ttk.Frame(card3)
        btn_frame3b.pack(fill=tk.X, padx=10, pady=(0, 8))
        for effect in effect_presets[5:]:
            btn = ttk.Button(btn_frame3b, text=effect, command=lambda e=effect: self.set_animation(e))
            btn.pack(side=tk.LEFT, padx=3)

        card4 = self.create_card(tab1, "Bildirim Teması")
        card4.pack(fill=tk.X, padx=10, pady=5)

        theme_frame = ttk.Frame(card4)
        theme_frame.pack(fill=tk.X, padx=10, pady=8)
        ttk.Label(theme_frame, text="Tema Seçin:").pack(side=tk.LEFT)
        self.theme_var = tk.StringVar(value=self.settings.get("theme", "Modern Koyu"))
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var,
                                    values=list(THEMES.keys()), state="readonly", width=20)
        theme_combo.pack(side=tk.LEFT, padx=10)
        theme_combo.bind("<<ComboboxSelected>>", lambda e: self.set_theme(self.theme_var.get()))

        card5 = self.create_card(tab1, "Şeffaflık", f"({self.settings['opacity']}%)")
        card5.pack(fill=tk.X, padx=10, pady=5)

        opacity_frame = ttk.Frame(card5)
        opacity_frame.pack(fill=tk.X, padx=10, pady=8)
        self.opacity_var = tk.IntVar(value=self.settings["opacity"])
        opacity_scale = ttk.Scale(opacity_frame, from_=30, to=100, variable=self.opacity_var,
                                   orient=tk.HORIZONTAL, length=300)
        opacity_scale.pack(side=tk.LEFT, padx=5)
        self.opacity_label = ttk.Label(opacity_frame, text=f"{self.settings['opacity']}%")
        self.opacity_label.pack(side=tk.LEFT)
        opacity_scale.bind("<Motion>", self.update_opacity_label)
        opacity_scale.bind("<ButtonRelease-1>", self.update_opacity_label)

        card6 = self.create_card(tab1, "Boyut (Sabit Oran 2.5:1)", f"({self.settings['width']}x{self.settings['height']})")
        card6.pack(fill=tk.X, padx=10, pady=5)

        size_frame = ttk.Frame(card6)
        size_frame.pack(fill=tk.X, padx=10, pady=8)
        ttk.Label(size_frame, text="Genişlik:").pack(side=tk.LEFT)
        self.width_var = tk.IntVar(value=self.settings["width"])
        width_spin = ttk.Spinbox(size_frame, from_=400, to=900, textvariable=self.width_var, width=8)
        width_spin.pack(side=tk.LEFT, padx=5)
        self.height_var = tk.IntVar(value=self.settings["height"])
        ttk.Label(size_frame, text=f"→ Yükseklik: {self.settings['height']}px (otomatik)", 
                 foreground="#4ecca3").pack(side=tk.LEFT, padx=10)
        ttk.Button(size_frame, text="🔄 Varsayılan (500x200)", command=self.reset_size).pack(side=tk.LEFT, padx=10)
        
        self.width_var.trace_add("write", self.update_size_label)
        self.size_label = ttk.Label(size_frame, text=f"({self.settings['width']}x{self.settings['height']})", foreground="#4ecca3")
        self.size_label.pack(side=tk.LEFT, padx=10)

        card_border = self.create_card(tab1, "Çerçeve Kenarlığı")
        card_border.pack(fill=tk.X, padx=10, pady=5)
        
        border_frame = ttk.Frame(card_border)
        border_frame.pack(fill=tk.X, padx=10, pady=8)
        self.border_var = tk.StringVar(value=self.settings.get("border", "Orta"))
        border_combo = ttk.Combobox(border_frame, textvariable=self.border_var, 
                                     values=list(BORDER_OPTIONS.keys()), state="readonly", width=15)
        border_combo.pack(side=tk.LEFT, padx=5)
        ttk.Button(border_frame, text="✓ Uygula", style="Success.TButton",
                    command=self.apply_border).pack(side=tk.LEFT, padx=5)

        card_startup = self.create_card(tab1, "Başlangıç")
        card_startup.pack(fill=tk.X, padx=10, pady=5)
        
        startup_frame = ttk.Frame(card_startup)
        startup_frame.pack(fill=tk.X, padx=10, pady=8)
        self.startup_var = tk.BooleanVar(value=self.settings.get("start_with_windows", False))
        ttk.Checkbutton(startup_frame, text="Windows ile başlat", variable=self.startup_var).pack(side=tk.LEFT)
        ttk.Button(startup_frame, text="✓ Uygula", style="Success.TButton",
                    command=self.apply_startup).pack(side=tk.LEFT, padx=10)

        card7 = self.create_card(tab1, "Yazı Düzeni (Kesin Ölçüm)")
        card7.pack(fill=tk.X, padx=10, pady=5)
        
        info_frame = ttk.Frame(card7)
        info_frame.pack(fill=tk.X, padx=10, pady=8)
        info_lines = [
            f"Font: {MONO_FONT} (Monospace)",
            "",
            "font.measure() ile GERÇEK piksel ölçümü yapılır.",
            "Taşma İMKANSIZ.",
            "",
            "Widget yüksekliği 100 birim:",
            "• İngilizce kelime: %50 (max 2 satır)",
            "• Türkçe anlam: %50 (max 2 satır)",
            "",
            "Uzun metinler boşluktan bölünür:",
            "  müsait mevcut kullanılabilir",
            "  → müsait mevcut",
            "  → kullanılabilir",
            "",
            "En-boy oranı sabit: 2.5:1 (500x200)"
        ]
        for line in info_lines:
            ttk.Label(info_frame, text=line, foreground="#888888", 
                     font=("Segoe UI", 9, "italic" if line.startswith("•") or line.startswith("→") else "normal")).pack(anchor=tk.W)

        btn_frame_bottom = ttk.Frame(tab1)
        btn_frame_bottom.pack(fill=tk.X, padx=10, pady=15)
        ttk.Button(btn_frame_bottom, text="💾 Tüm Ayarları Kaydet", style="Accent.TButton",
                    command=self.save_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame_bottom, text="Kapat", command=self.on_close).pack(side=tk.RIGHT, padx=5)

        tab2_container = ttk.Frame(notebook)
        notebook.add(tab2_container, text="  Kelime Listeleri  ")
        
        scroll2 = ScrollableTab(tab2_container, bg_color="#1a1a2e")
        tab2 = scroll2.get_frame()

        new_list_card = self.create_card(tab2, "Yeni Liste Ekle")
        new_list_card.pack(fill=tk.X, padx=10, pady=5)
        
        new_list_frame = ttk.Frame(new_list_card)
        new_list_frame.pack(fill=tk.X, padx=10, pady=8)
        ttk.Label(new_list_frame, text="Liste Adı:").pack(side=tk.LEFT)
        self.new_list_var = tk.StringVar()
        ttk.Entry(new_list_frame, textvariable=self.new_list_var, width=25).pack(side=tk.LEFT, padx=10)
        ttk.Button(new_list_frame, text="➕ Ekle", style="Success.TButton",
                    command=self.add_new_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(new_list_frame, text="🗑️ Sil", style="Danger.TButton",
                    command=self.delete_list).pack(side=tk.LEFT, padx=5)

        list_card = self.create_card(tab2, "Aktif Kelime Listeleri")
        list_card.pack(fill=tk.X, padx=10, pady=5)

        self.list_frame_container = ttk.Frame(list_card)
        self.list_frame_container.pack(fill=tk.X, padx=10, pady=8)

        self.list_vars = {}
        
        total_frame = ttk.Frame(list_card)
        total_frame.pack(fill=tk.X, padx=10, pady=(5, 8))
        self.total_label = ttk.Label(total_frame, text="",
                                      foreground="#4ecca3", font=("Segoe UI", 11, "bold"))
        self.total_label.pack(side=tk.LEFT)
        
        self._build_list_checkboxes()

        tab3_container = ttk.Frame(notebook)
        notebook.add(tab3_container, text="  Kelimeler  ")

        search_frame = ttk.Frame(tab3_container)
        search_frame.pack(fill=tk.X, pady=5, padx=10)
        ttk.Label(search_frame, text=" Ara:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_search)
        ttk.Entry(search_frame, textvariable=self.search_var, width=25).pack(side=tk.LEFT, padx=10)
        
        ttk.Label(search_frame, text="Liste:").pack(side=tk.LEFT, padx=(15, 0))
        self.filter_list_var = tk.StringVar(value="Tümü")
        filter_combo = ttk.Combobox(search_frame, textvariable=self.filter_list_var,
                                     values=["Tümü"] + self.all_lists, state="readonly", width=15)
        filter_combo.pack(side=tk.LEFT, padx=10)
        filter_combo.bind("<<ComboboxSelected>>", lambda e: self.populate_tree())

        tree_frame = ttk.Frame(tab3_container)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("en", "tr", "list", "sentence", "sentence_tr")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12, selectmode="extended")
        self.tree.heading("en", text="İngilizce")
        self.tree.heading("tr", text="Türkçe")
        self.tree.heading("list", text="Liste")
        self.tree.heading("sentence", text="Örnek Cümle")
        self.tree.heading("sentence_tr", text="Örnek Cümle (TR)")
        self.tree.column("en", width=110)
        self.tree.column("tr", width=110)
        self.tree.column("list", width=90)
        self.tree.column("sentence", width=180)
        self.tree.column("sentence_tr", width=180)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", self.edit_word)
        self.populate_tree()

        info_label = ttk.Label(tab3_container, text="💡 Çoklu seçim: Ctrl+Click veya Shift+Click",
                               foreground="#888888", font=("Segoe UI", 9, "italic"))
        info_label.pack(pady=(0, 5))

        btn_frame3 = ttk.Frame(tab3_container)
        btn_frame3.pack(fill=tk.X, pady=10, padx=10)
        ttk.Button(btn_frame3, text="➕ Ekle", command=self.add_word).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame3, text="✏️ Düzenle", command=self.edit_word_btn).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame3, text="🗑️ Tek Sil", command=self.delete_word).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame3, text="🗑️ Seçilenleri Sil", style="Danger.TButton",
                    command=self.delete_selected_words).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame3, text="📥 CSV İçe", command=self.import_csv).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame3, text="📤 CSV Dışa", command=self.export_csv).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame3, text=" Kaydet", style="Accent.TButton",
                    command=self.save_words).pack(side=tk.RIGHT, padx=3)

    def create_card(self, parent, title, subtitle=""):
        card = ttk.Frame(parent, style="Card.TFrame")
        card_inner = ttk.Frame(card, style="Card.TFrame")
        card_inner.pack(fill=tk.X, padx=12, pady=8)
        title_text = f"{title} {subtitle}" if subtitle else title
        ttk.Label(card_inner, text=title_text, style="CardTitle.TLabel").pack(anchor=tk.W)
        return card

    def _build_list_checkboxes(self):
        for widget in self.list_frame_container.winfo_children():
            widget.destroy()
        
        self.list_vars = {}
        counts = get_list_counts(self.words, self.all_lists)
        
        for lst in self.all_lists:
            count = counts.get(lst, 0)
            current_selected = self.widget.settings.get("selected_lists", ["Kullanıcı Listesi"])
            var = tk.BooleanVar(value=lst in current_selected)
            self.list_vars[lst] = var
            cb_frame = ttk.Frame(self.list_frame_container)
            cb_frame.pack(fill=tk.X, pady=3)
            ttk.Checkbutton(cb_frame, text=f"{lst}", variable=var,
                           command=self._on_list_checkbox_change).pack(side=tk.LEFT)
            ttk.Label(cb_frame, text=f"({count} kelime)", foreground="#888888").pack(side=tk.LEFT, padx=10)
        
        self._update_total_label()

    def _on_list_checkbox_change(self):
        selected = [lst for lst, var in self.list_vars.items() if var.get()]
        if not selected:
            selected = ["Kullanıcı Listesi"]
        
        self.widget.settings["selected_lists"] = list(selected)
        self.settings["selected_lists"] = list(selected)
        
        self._update_total_label()

    def _update_total_label(self):
        if self.total_label is None:
            return
        selected = self.widget.settings.get("selected_lists", ["Kullanıcı Listesi"])
        counts = get_list_counts(self.words, self.all_lists)
        total = sum(counts.get(lst, 0) for lst in selected)
        self.total_label.config(text=f"Toplam Aktif Kelime: {total}")

    def add_new_list(self):
        list_name = self.new_list_var.get().strip()
        if not list_name:
            messagebox.showwarning("Uyarı", "Liste adı boş bırakılamaz!")
            return
        if list_name in self.all_lists:
            messagebox.showwarning("Uyarı", f"'{list_name}' adında bir liste zaten var!")
            return
        
        self.all_lists.append(list_name)
        save_custom_lists([l for l in self.all_lists if l not in DEFAULT_WORD_LISTS])
        
        self._build_list_checkboxes()
        
        for widget in self.win.winfo_children():
            if isinstance(widget, ttk.Notebook):
                for tab_id in widget.tabs():
                    tab_widget = widget.nametowidget(tab_id)
                    for child in tab_widget.winfo_children():
                        if isinstance(child, ScrollableTab):
                            frame = child.get_frame()
                            for w in frame.winfo_children():
                                if isinstance(w, ttk.Frame):
                                    for c in w.winfo_children():
                                        if isinstance(c, ttk.Combobox):
                                            c['values'] = ["Tümü"] + self.all_lists
        
        self.new_list_var.set("")
        messagebox.showinfo("Başarılı", f"'{list_name}' listesi eklendi!")

    def delete_list(self):
        list_name = self.new_list_var.get().strip()
        if not list_name:
            messagebox.showwarning("Uyarı", "Silinecek liste adını girin!")
            return
        if list_name in DEFAULT_WORD_LISTS:
            messagebox.showwarning("Uyarı", "Varsayılan listeler silinemez!")
            return
        if list_name not in self.all_lists:
            messagebox.showwarning("Uyarı", f"'{list_name}' adında bir liste bulunamadı!")
            return
        
        words_to_remove = [w for w in self.words if w.get("list") == list_name]
        if words_to_remove:
            if not messagebox.askyesno("Onay", f"'{list_name}' listesinde {len(words_to_remove)} kelime var. Hepsini silmek istediğinize emin misiniz?"):
                return
            for w in words_to_remove:
                self.words.remove(w)
        
        self.all_lists.remove(list_name)
        save_custom_lists([l for l in self.all_lists if l not in DEFAULT_WORD_LISTS])
        
        if list_name in self.widget.settings.get("selected_lists", []):
            self.widget.settings["selected_lists"].remove(list_name)
        
        self._build_list_checkboxes()
        self.populate_tree()
        messagebox.showinfo("Başarılı", f"'{list_name}' listesi silindi!")

    def set_interval(self, val):
        self.interval_var.set(val)
        self.settings["interval"] = val

    def apply_interval(self):
        self.settings["interval"] = self.interval_var.get()

    def set_duration(self, val):
        self.duration_var.set(val)
        self.settings["display_duration"] = val

    def apply_duration(self):
        self.settings["display_duration"] = self.duration_var.get()

    def set_animation(self, anim):
        self.settings["animation"] = anim

    def set_theme(self, theme):
        self.settings["theme"] = theme

    def update_opacity_label(self, event=None):
        val = int(self.opacity_var.get())
        self.opacity_label.config(text=f"{val}%")
        self.settings["opacity"] = val

    def update_size_label(self, *args):
        w = self.width_var.get()
        h = int(w / ASPECT_RATIO)
        self.height_var.set(h)
        self.size_label.config(text=f"({w}x{h})")
        for widget in self.win.winfo_children():
            if isinstance(widget, ttk.Notebook):
                for tab_id in widget.tabs():
                    tab_widget = widget.nametowidget(tab_id)
                    for child in tab_widget.winfo_children():
                        if isinstance(child, ScrollableTab):
                            frame = child.get_frame()
                            for w_widget in frame.winfo_children():
                                if isinstance(w_widget, ttk.Frame):
                                    for c in w_widget.winfo_children():
                                        if isinstance(c, ttk.Label) and "Yükseklik" in c.cget("text"):
                                            c.config(text=f"→ Yükseklik: {h}px (otomatik)")

    def reset_size(self):
        self.width_var.set(500)

    def apply_border(self):
        self.settings["border"] = self.border_var.get()

    def apply_startup(self):
        self.settings["start_with_windows"] = self.startup_var.get()
        set_startup(self.startup_var.get())
        status = "açıldı" if self.startup_var.get() else "kapatıldı"
        messagebox.showinfo("Başarılı", f"Windows ile başlatma {status}.")

    def update_list_selection(self):
        selected = [lst for lst, var in self.list_vars.items() if var.get()]
        self.settings["selected_lists"] = selected if selected else ["Kullanıcı Listesi"]
        self._update_total_label()

    def populate_tree(self, filter_text=""):
        for item in self.tree.get_children():
            self.tree.delete(item)
        filter_list = self.filter_list_var.get()
        for w in self.words:
            if filter_text:
                ft = filter_text.lower()
                if ft not in w["en"].lower() and ft not in w["tr"].lower():
                    continue
            if filter_list != "Tümü" and w.get("list") != filter_list:
                continue
            self.tree.insert("", tk.END, values=(
                w["en"], w["tr"], w.get("list", "Kullanıcı Listesi"),
                w.get("sentence", ""), w.get("sentence_tr", "")
            ))

    def on_search(self, *args):
        self.populate_tree(self.search_var.get())

    def add_word(self):
        dialog = WordDialog(self, "Yeni Kelime Ekle", all_lists=self.all_lists)
        self.win.wait_window(dialog.win)
        if dialog.result:
            existing = [w for w in self.words if w["en"].lower() == dialog.result["en"].lower()]
            if existing:
                messagebox.showwarning("Uyarı", f"'{dialog.result['en']}' kelimesi zaten mevcut!")
                return
            self.words.append(dialog.result)
            self.populate_tree(self.search_var.get())
            self._build_list_checkboxes()

    def edit_word_btn(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Bilgi", "Lütfen düzenlemek için bir kelime seçin.")
            return
        if len(selected) > 1:
            messagebox.showinfo("Bilgi", "Lütfen sadece bir kelime seçin.")
            return
        values = self.tree.item(selected[0], "values")
        word = None
        for w in self.words:
            if w["en"] == values[0] and w["tr"] == values[1]:
                word = w
                break
        if not word:
            return
        dialog = WordDialog(self, "Kelime Düzenle", word, all_lists=self.all_lists)
        self.win.wait_window(dialog.win)
        if dialog.result:
            existing = [w for w in self.words if w["en"].lower() == dialog.result["en"].lower() and w is not word]
            if existing:
                messagebox.showwarning("Uyarı", f"'{dialog.result['en']}' kelimesi zaten mevcut!")
                return
            idx = self.words.index(word)
            self.words[idx] = dialog.result
            self.populate_tree(self.search_var.get())

    def edit_word(self, event):
        self.edit_word_btn()

    def delete_word(self):
        selected = self.tree.selection()
        if not selected:
            return
        if len(selected) > 1:
            self.delete_selected_words()
            return
        values = self.tree.item(selected[0], "values")
        word = None
        for w in self.words:
            if w["en"] == values[0] and w["tr"] == values[1]:
                word = w
                break
        if not word:
            return
        if messagebox.askyesno("Sil", f"'{word['en']}' kelimesini silmek istediğinize emin misiniz?"):
            self.words.remove(word)
            self.populate_tree(self.search_var.get())
            self._build_list_checkboxes()

    def delete_selected_words(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Bilgi", "Lütfen silmek için en az bir kelime seçin.\n(Ctrl+Click veya Shift+Click ile çoklu seçim)")
            return
        
        count = len(selected)
        if not messagebox.askyesno("Toplu Silme", f"{count} kelimeyi silmek istediğinize emin misiniz?"):
            return
        
        words_to_delete = []
        for item in selected:
            values = self.tree.item(item, "values")
            for w in self.words:
                if w["en"] == values[0] and w["tr"] == values[1]:
                    words_to_delete.append(w)
                    break
        
        for w in words_to_delete:
            if w in self.words:
                self.words.remove(w)
        
        self.populate_tree(self.search_var.get())
        self._build_list_checkboxes()
        messagebox.showinfo("Başarılı", f"{count} kelime silindi!")

    def import_csv(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV Dosyası", "*.csv")])
        if not filepath:
            return
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                added = 0
                skipped = 0
                for row in reader:
                    en = row.get("en", row.get("english", row.get("İngilizce", ""))).strip()
                    tr = row.get("tr", row.get("turkish", row.get("Türkçe", ""))).strip()
                    sentence = row.get("sentence", row.get("example", row.get("Örnek", ""))).strip()
                    sentence_tr = row.get("sentence_tr", row.get("türkçe_cümle", "")).strip()
                    lst = row.get("list", row.get("liste", "Kullanıcı Listesi")).strip()
                    if en and tr:
                        if any(w["en"].lower() == en.lower() for w in self.words):
                            skipped += 1
                            continue
                        self.words.append({"en": en, "tr": tr, "sentence": sentence, 
                                          "sentence_tr": sentence_tr, "list": lst})
                        added += 1
            self.populate_tree(self.search_var.get())
            self._build_list_checkboxes()
            msg = f"{added} kelime eklendi."
            if skipped > 0:
                msg += f" {skipped} kelime zaten mevcut olduğu için atlandı."
            messagebox.showinfo("Başarılı", msg)
        except Exception as e:
            messagebox.showerror("Hata", f"CSV okunamadı: {e}")

    def export_csv(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV Dosyası", "*.csv")])
        if not filepath:
            return
        try:
            with open(filepath, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["en", "tr", "sentence", "sentence_tr", "list"])
                writer.writeheader()
                for w in self.words:
                    writer.writerow({
                        "en": w["en"], "tr": w["tr"], 
                        "sentence": w.get("sentence", ""),
                        "sentence_tr": w.get("sentence_tr", ""),
                        "list": w.get("list", "Kullanıcı Listesi")
                    })
            messagebox.showinfo("Başarılı", "CSV dosyası başarıyla dışa aktarıldı.")
        except Exception as e:
            messagebox.showerror("Hata", f"CSV yazılamadı: {e}")

    def save_words(self):
        save_all_words(self.words)
        self.widget.words = list(self.words)
        self._build_list_checkboxes()
        messagebox.showinfo("Başarılı", "Kelimeler kaydedildi!")

    def save_all(self):
        self.settings["theme"] = self.theme_var.get()
        self.settings["animation"] = self.settings.get("animation", "Daktilo")
        self.settings["interval"] = self.interval_var.get()
        self.settings["display_duration"] = self.duration_var.get()
        self.settings["opacity"] = self.opacity_var.get()
        self.settings["width"] = self.width_var.get()
        self.settings["height"] = self.height_var.get()
        self.settings["border"] = self.border_var.get()
        self.settings["start_with_windows"] = self.startup_var.get()

        save_settings(self.settings)
        save_all_words(self.words)
        set_startup(self.startup_var.get())
        
        self.widget.settings = dict(self.settings)
        self.widget.words = list(self.words)
        self.widget.apply_settings()
        messagebox.showinfo("Başarılı", "Tüm ayarlar kaydedildi!")

    def on_close(self):
        self.win.destroy()


class WordDialog:
    def __init__(self, parent, title, values=None, all_lists=None):
        self.result = None
        self.win = tk.Toplevel(parent.win if hasattr(parent, 'win') else parent)
        self.win.title(title)
        self.win.geometry("520x400")
        self.win.configure(bg="#1a1a2e")

        style = ttk.Style()
        style.configure("TFrame", background="#1a1a2e")
        style.configure("TLabel", background="#1a1a2e", foreground="#e0e0e0", font=("Segoe UI", 10))
        style.configure("TEntry", fieldbackground="#16213e", foreground="#e0e0e0")
        style.configure("TCombobox", fieldbackground="#16213e", foreground="#e0e0e0")
        style.configure("Accent.TButton", background="#4ecca3", foreground="#1a1a2e",
                         font=("Segoe UI", 10, "bold"), padding=8)

        frame = ttk.Frame(self.win)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(frame, text="İngilizce:").grid(row=0, column=0, sticky=tk.W, pady=8)
        self.en_var = tk.StringVar(value=values["en"] if values and isinstance(values, dict) else (values[0] if values else ""))
        ttk.Entry(frame, textvariable=self.en_var, width=45).grid(row=0, column=1, pady=8, padx=10)

        ttk.Label(frame, text="Türkçe:").grid(row=1, column=0, sticky=tk.W, pady=8)
        self.tr_var = tk.StringVar(value=values["tr"] if values and isinstance(values, dict) else (values[1] if values else ""))
        ttk.Entry(frame, textvariable=self.tr_var, width=45).grid(row=1, column=1, pady=8, padx=10)

        ttk.Label(frame, text="Örnek Cümle (İngilizce):").grid(row=2, column=0, sticky=tk.W, pady=8)
        self.sent_var = tk.StringVar(value=values.get("sentence", "") if values and isinstance(values, dict) else (values[2] if values and len(values) > 2 else ""))
        ttk.Entry(frame, textvariable=self.sent_var, width=45).grid(row=2, column=1, pady=8, padx=10)

        ttk.Label(frame, text="Örnek Cümle (Türkçe):").grid(row=3, column=0, sticky=tk.W, pady=8)
        self.sent_tr_var = tk.StringVar(value=values.get("sentence_tr", "") if values and isinstance(values, dict) else (values[3] if values and len(values) > 3 else ""))
        ttk.Entry(frame, textvariable=self.sent_tr_var, width=45).grid(row=3, column=1, pady=8, padx=10)

        ttk.Label(frame, text="Liste:").grid(row=4, column=0, sticky=tk.W, pady=8)
        lists = all_lists if all_lists else get_all_word_lists()
        default_list = "Kullanıcı Listesi"
        if values and isinstance(values, dict) and values.get("list"):
            default_list = values["list"]
        self.list_var = tk.StringVar(value=default_list)
        list_combo = ttk.Combobox(frame, textvariable=self.list_var, values=lists, state="readonly", width=42)
        list_combo.grid(row=4, column=1, pady=8, padx=10)
        if default_list not in lists:
            list_combo['values'] = lists + [default_list]
            self.list_var.set(default_list)

        info_label = ttk.Label(frame, text="💡 Örnek cümle alanları opsiyoneldir.",
                               foreground="#888888", font=("Segoe UI", 9, "italic"))
        info_label.grid(row=5, column=0, columnspan=2, pady=10)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="💾 Kaydet", style="Accent.TButton",
                    command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="İptal", command=self.win.destroy).pack(side=tk.LEFT, padx=5)

    def save(self):
        en = self.en_var.get().strip()
        tr = self.tr_var.get().strip()
        sent = self.sent_var.get().strip()
        sent_tr = self.sent_tr_var.get().strip()
        lst = self.list_var.get().strip()
        if not lst:
            lst = "Kullanıcı Listesi"
        if not en or not tr:
            messagebox.showwarning("Uyarı", "İngilizce ve Türkçe alanları boş bırakılamaz!")
            return
        self.result = {"en": en, "tr": tr, "sentence": sent, "sentence_tr": sent_tr, "list": lst}
        self.win.destroy()


class QuizWindow:
    def __init__(self, widget):
        self.widget = widget
        self.words = widget.get_filtered_words()
        self.score = 0
        self.total = 0
        self.current_answer = ""

        self.win = tk.Toplevel(widget.root)
        self.win.title("📝 Quiz Modu")
        self.win.geometry("500x400")
        self.win.configure(bg="#1E1E2E")

        self.build_ui()
        self.next_question()

    def build_ui(self):
        theme = THEMES[self.widget.settings["theme"]]

        self.score_label = tk.Label(self.win, text="Skor: 0/0", bg="#1E1E2E", fg="#CDD6F4",
                                     font=("Segoe UI", 14, "bold"))
        self.score_label.pack(pady=10)

        self.question_label = tk.Label(self.win, text="", bg="#1E1E2E", fg=theme["accent"],
                                        font=("Segoe UI", 22, "bold"), wraplength=450)
        self.question_label.pack(pady=15)

        self.buttons_frame = tk.Frame(self.win, bg="#1E1E2E")
        self.buttons_frame.pack(fill=tk.X, padx=30, pady=10)

        self.option_buttons = []
        for i in range(4):
            btn = tk.Button(self.buttons_frame, text="", bg="#313244", fg="#CDD6F4",
                            font=("Segoe UI", 12), relief=tk.FLAT, padx=15, pady=10,
                            activebackground="#89B4FA", activeforeground="#1E1E2E",
                            command=lambda idx=i: self.check_answer(idx))
            btn.pack(fill=tk.X, pady=5)
            self.option_buttons.append(btn)

        self.result_label = tk.Label(self.win, text="", bg="#1E1E2E", fg="#CDD6F4",
                                      font=("Segoe UI", 14))
        self.result_label.pack(pady=10)

        self.next_btn = tk.Button(self.win, text="Sonraki Soru ➡️", bg="#89B4FA", fg="#1E1E2E",
                                   font=("Segoe UI", 12), relief=tk.FLAT, padx=20, pady=8,
                                   command=self.next_question)
        self.next_btn.pack(pady=10)
        self.next_btn.config(state=tk.DISABLED)

    def next_question(self):
        if len(self.words) < 4:
            self.question_label.config(text="Yetersiz kelime sayısı! (En az 4 gerekli)")
            return

        for btn in self.option_buttons:
            btn.config(bg="#313244", fg="#CDD6F4", state=tk.NORMAL)
        self.result_label.config(text="")
        self.next_btn.config(state=tk.DISABLED)

        correct_word = random.choice(self.words)
        self.current_answer = correct_word["tr"]
        self.question_label.config(text=f"\"{capitalize_first(correct_word['en'])}\" ne demek?")

        options = [correct_word["tr"]]
        others = [w["tr"] for w in self.words if w["tr"] != correct_word["tr"]]
        random.shuffle(others)
        for o in others[:3]:
            options.append(o)
        random.shuffle(options)

        for i, btn in enumerate(self.option_buttons):
            btn.config(text=options[i])

    def check_answer(self, idx):
        selected = self.option_buttons[idx]["text"]
        self.total += 1

        if selected == self.current_answer:
            self.score += 1
            self.option_buttons[idx].config(bg="#4ecca3", fg="#1a1a2e")
            self.result_label.config(text="✅ Doğru!", fg="#4ecca3")
        else:
            self.option_buttons[idx].config(bg="#e94560", fg="#ffffff")
            for btn in self.option_buttons:
                if btn["text"] == self.current_answer:
                    btn.config(bg="#4ecca3", fg="#1a1a2e")
            self.result_label.config(text=f"❌ Yanlış! Doğru cevap: {self.current_answer}", fg="#e94560")

        self.score_label.config(text=f"Skor: {self.score}/{self.total}")
        self.next_btn.config(state=tk.NORMAL)

        for btn in self.option_buttons:
            btn.config(state=tk.DISABLED)


def main():
    ensure_app_dir()
    app = KelimeWidget()
    app.root.mainloop()

if __name__ == "__main__":
    main()