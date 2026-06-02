import customtkinter as ctk
import json
import os
import subprocess
import re

# === ДИЗАЙН-СИСТЕМА DATracer (Вайб сайта) ===
BG_COLOR = "#0B0B10"        # Глубокий темный фон приложения
CARD_COLOR = "#16161E"      # Цвет карточек (чуть светлее фона)
ACCENT_COLOR = "#6B4EE6"    # Фиолетовый акцент (как на сайте)
ACCENT_HOVER = "#5A3FD1"    # Фиолетовый при наведении
DANGER_COLOR = "#E64E4E"    # Красный для удаления
TEXT_SUB = "#8A8A9E"        # Серый цвет для подзаголовков

ctk.set_appearance_mode("dark")

CONFIG_FILE = "config.json"

# === СЛОВАРЬ ПЕРЕВОДОВ (С возвращенной базой 😎) ===
TRANSLATIONS = {
    "ru": {
        "dash_title": "DATracer Панель",
        "dash_sub": "Твой статус в Discord под контролем",
        "dash_toggle": "Синхронизация с Discord",
        "priv_title": "Скрытые сайты",
        "priv_sub": "Введите сайт, где хранятся ваши тайны 🤫\n(Мы сами отрежем лишнее вроде https://)",
        "priv_placeholder": "Например: pornhub.com",
        "priv_btn": "Спрятать",
        "priv_warn": "⚠️ Неверный формат! Нужен домен (например, сайт.com)",
        "set_title": "Настройки",
        "set_lang": "Язык интерфейса:"
    },
    "en": {
        "dash_title": "DATracer Control Panel",
        "dash_sub": "Your Discord status under control",
        "dash_toggle": "Discord Synchronization",
        "priv_title": "Hidden Sites",
        "priv_sub": "Enter a site where your secrets are kept 🤫\n(We'll auto-strip https://)",
        "priv_placeholder": "Example: pornhub.com",
        "priv_btn": "Hide",
        "priv_warn": "⚠️ Invalid format! Need a domain (site.com)",
        "set_title": "Settings",
        "set_lang": "Interface Language:"
    }
}

class DATracerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("DATracer")
        self.geometry("540x460")
        self.resizable(False, False)
        
        # Красим главное окно в глубокий темный цвет
        self.configure(fg_color=BG_COLOR)
        
        self.tracker_process = None 
        self.config_data = self.load_config()
        
        self.current_lang = self.config_data.get("language", "ru")
        if self.current_lang not in TRANSLATIONS:
            self.current_lang = "ru"

        # Кастомный дизайн вкладок
        self.tabview = ctk.CTkTabview(
            self, width=500, height=420,
            fg_color=BG_COLOR, # Фон под карточками
            segmented_button_fg_color=CARD_COLOR, # Фон кнопок вкладок
            segmented_button_selected_color=ACCENT_COLOR, # Активная вкладка
            segmented_button_selected_hover_color=ACCENT_HOVER,
            segmented_button_unselected_color=CARD_COLOR,
            segmented_button_unselected_hover_color="#21212E",
            corner_radius=12
        )
        self.tabview.pack(padx=20, pady=10)

        self.tab_dash_name = "💻 Dashboard"
        self.tab_priv_name = "🤫 Privacy"
        self.tab_set_name = "⚙️ Settings"
        
        self.tabview.add(self.tab_dash_name)
        self.tabview.add(self.tab_priv_name)
        self.tabview.add(self.tab_set_name)

        # Убираем фон у самих вкладок, чтобы было видно карточки
        self.tabview.tab(self.tab_dash_name).configure(fg_color=BG_COLOR)
        self.tabview.tab(self.tab_priv_name).configure(fg_color=BG_COLOR)
        self.tabview.tab(self.tab_set_name).configure(fg_color=BG_COLOR)

        self.setup_dashboard_tab()
        self.setup_privacy_tab()
        self.setup_settings_tab()
        
        self.apply_translations()
        
        if self.config_data.get("is_tracking_active"):
            self.start_tracker()

    def load_config(self):
        default_cfg = {"is_tracking_active": False, "language": "ru", "blacklisted_domains": []}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "language" not in data:
                        data["language"] = "ru"
                    return data
            except json.JSONDecodeError:
                pass
        return default_cfg

    def save_config(self):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config_data, f, indent=4, ensure_ascii=False)

    def t(self, key):
        return TRANSLATIONS[self.current_lang].get(key, key)

    def apply_translations(self):
        self.lbl_dash_title.configure(text=self.t("dash_title"))
        self.lbl_dash_sub.configure(text=self.t("dash_sub"))
        self.toggle_switch.configure(text=self.t("dash_toggle"))
        
        self.lbl_priv_title.configure(text=self.t("priv_title"))
        self.lbl_priv_sub.configure(text=self.t("priv_sub"))
        self.site_entry.configure(placeholder_text=self.t("priv_placeholder"))
        self.add_btn.configure(text=self.t("priv_btn"))
        
        if self.lbl_priv_warn.cget("text"): 
            self.lbl_priv_warn.configure(text=self.t("priv_warn"))
            
        self.lbl_set_title.configure(text=self.t("set_title"))
        self.lbl_lang.configure(text=self.t("set_lang"))

    # ==========================
    # ВКЛАДКА 1: DASHBOARD
    # ==========================
    def setup_dashboard_tab(self):
        tab = self.tabview.tab(self.tab_dash_name)
        
        # Карточка для главного меню
        card = ctk.CTkFrame(tab, fg_color=CARD_COLOR, corner_radius=15)
        card.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.lbl_dash_title = ctk.CTkLabel(card, text="", font=("Helvetica", 24, "bold"))
        self.lbl_dash_title.pack(pady=(40, 10))

        self.lbl_dash_sub = ctk.CTkLabel(card, text="", text_color=TEXT_SUB, font=("Helvetica", 14))
        self.lbl_dash_sub.pack(pady=(0, 40))

        start_val = "on" if self.config_data.get("is_tracking_active") else "off"
        self.tracking_var = ctk.StringVar(value=start_val)
        
        self.toggle_switch = ctk.CTkSwitch(
            card, text="", font=("Helvetica", 18, "bold"),
            variable=self.tracking_var, onvalue="on", offvalue="off",
            command=self.on_toggle_tracking,
            progress_color=ACCENT_COLOR, # Фиолетовый ползунок
            button_color="#FFFFFF",
            button_hover_color="#E0E0E0"
        )
        self.toggle_switch.pack(pady=20)

    # ==========================
    # ВКЛАДКА 2: PRIVACY
    # ==========================
    def setup_privacy_tab(self):
        tab = self.tabview.tab(self.tab_priv_name)

        # Верхняя карточка с инпутом
        top_card = ctk.CTkFrame(tab, fg_color=CARD_COLOR, corner_radius=15)
        top_card.pack(fill="x", padx=10, pady=(10, 5))

        self.lbl_priv_title = ctk.CTkLabel(top_card, text="", font=("Helvetica", 20, "bold"))
        self.lbl_priv_title.pack(pady=(15, 5))

        self.lbl_priv_sub = ctk.CTkLabel(top_card, text="", text_color=TEXT_SUB)
        self.lbl_priv_sub.pack(pady=(0, 10))

        self.lbl_priv_warn = ctk.CTkLabel(top_card, text="", text_color=DANGER_COLOR, font=("Helvetica", 12))
        self.lbl_priv_warn.pack(pady=(0, 5))

        input_frame = ctk.CTkFrame(top_card, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.site_entry = ctk.CTkEntry(
            input_frame, placeholder_text="", width=250, height=35,
            fg_color=BG_COLOR, border_color=ACCENT_COLOR, border_width=1
        )
        self.site_entry.pack(side="left", padx=(0, 10))

        self.add_btn = ctk.CTkButton(
            input_frame, text="", width=90, height=35,
            fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, corner_radius=8,
            command=self.add_to_blacklist
        )
        self.add_btn.pack(side="left")

        # Нижняя карточка со списком
        bot_card = ctk.CTkFrame(tab, fg_color=CARD_COLOR, corner_radius=15)
        bot_card.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        self.blacklist_frame = ctk.CTkScrollableFrame(bot_card, fg_color="transparent")
        self.blacklist_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.refresh_blacklist_ui()

    def add_to_blacklist(self):
        raw_input = self.site_entry.get().strip().lower()
        if not raw_input:
            return

        clean_site = raw_input.replace("http://", "").replace("https://", "").split("/")[0]

        domain_pattern = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
        if not re.match(domain_pattern, clean_site):
            self.lbl_priv_warn.configure(text=self.t("priv_warn"))
            return
            
        self.lbl_priv_warn.configure(text="")
        if clean_site not in self.config_data["blacklisted_domains"]:
            self.config_data["blacklisted_domains"].append(clean_site)
            self.save_config()
            self.site_entry.delete(0, 'end')
            self.refresh_blacklist_ui()

    def remove_from_blacklist(self, site):
        if site in self.config_data["blacklisted_domains"]:
            self.config_data["blacklisted_domains"].remove(site)
            self.save_config()
            self.refresh_blacklist_ui()

    def refresh_blacklist_ui(self):
        for widget in self.blacklist_frame.winfo_children():
            widget.destroy()

        for site in self.config_data["blacklisted_domains"]:
            # Стилизуем каждую строку как мини-карточку
            row = ctk.CTkFrame(self.blacklist_frame, fg_color=BG_COLOR, corner_radius=8)
            row.pack(fill="x", pady=4, ipady=2)
            
            lbl = ctk.CTkLabel(row, text=site, font=("Helvetica", 14, "bold"), text_color="#E0E0E0")
            lbl.pack(side="left", padx=15)
            
            del_btn = ctk.CTkButton(
                row, text="✖", width=28, height=28, 
                fg_color="transparent", hover_color=DANGER_COLOR, text_color=DANGER_COLOR,
                font=("Helvetica", 16, "bold"),
                command=lambda s=site: self.remove_from_blacklist(s)
            )
            del_btn.pack(side="right", padx=10)

    # ==========================
    # ВКЛАДКА 3: SETTINGS
    # ==========================
    def setup_settings_tab(self):
        tab = self.tabview.tab(self.tab_set_name)
        
        card = ctk.CTkFrame(tab, fg_color=CARD_COLOR, corner_radius=15)
        card.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.lbl_set_title = ctk.CTkLabel(card, text="", font=("Helvetica", 20, "bold"))
        self.lbl_set_title.pack(pady=(30, 20))

        lang_frame = ctk.CTkFrame(card, fg_color="transparent")
        lang_frame.pack()

        self.lbl_lang = ctk.CTkLabel(lang_frame, text="", font=("Helvetica", 16))
        self.lbl_lang.pack(side="left", padx=10)

        start_lang = "Русский" if self.current_lang == "ru" else "English"
        self.lang_menu = ctk.CTkOptionMenu(
            lang_frame, 
            values=["Русский", "English"],
            fg_color=ACCENT_COLOR,
            button_color=ACCENT_HOVER,
            button_hover_color=ACCENT_COLOR,
            dropdown_hover_color=ACCENT_HOVER,
            command=self.on_language_change
        )
        self.lang_menu.set(start_lang)
        self.lang_menu.pack(side="left")

    def on_language_change(self, choice):
        self.current_lang = "ru" if choice == "Русский" else "en"
        self.config_data["language"] = self.current_lang
        self.save_config()
        self.apply_translations()

    # ==========================
    # УПРАВЛЕНИЕ ТРЕКЕРОМ (ФОН)
    # ==========================
    def on_toggle_tracking(self):
        is_active = self.tracking_var.get() == "on"
        self.config_data["is_tracking_active"] = is_active
        self.save_config()
        
        if is_active:
            self.start_tracker()
        else:
            self.stop_tracker()

    def start_tracker(self):
        if self.tracker_process is None:
            self.tracker_process = subprocess.Popen(["python", "-m", "src.core.tracker"])

    def stop_tracker(self):
        if self.tracker_process is not None:
            self.tracker_process.terminate()
            self.tracker_process = None

    def destroy(self):
        self.stop_tracker()
        super().destroy()

if __name__ == "__main__":
    app = DATracerApp()
    app.mainloop()