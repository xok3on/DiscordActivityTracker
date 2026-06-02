import time
import json
import os
from src.monitors.browser_tabs import BrowserMonitor
from src.core.rpc_client import DiscordRPCClient

CLIENT_ID = "1508185923756626030" 
CONFIG_FILE = "config.json"

STATUS_TRANSLATIONS = {
    "ru": {
        "watching": "Слушает/Смотрит",
        "browsing": "Сайт",
        "browser_empty": "В браузере",
        "hidden_details": "Скрытая активность",
        "idling_details": "Отдыхает",
        "idling_state": "Нет активности"
    },
    "en": {
        "watching": "Watching/Listening",
        "browsing": "Website",
        "browser_empty": "In Browser",
        "hidden_details": "Hidden Activity",
        "idling_details": "Idling",
        "idling_state": "No Activity"
    }
}

def load_config():
    """Читает актуальный конфиг, чтобы узнать выбранный язык и черный список"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {"language": "ru", "blacklisted_domains": []}

def main_loop():
    monitor = BrowserMonitor()
    monitor.start_monitoring()
    print("[Tracker] Продвинутый мониторинг браузера запущен...")

    rpc_client = DiscordRPCClient(CLIENT_ID)
    rpc_client.connect()

    print("[Tracker] Главный цикл запущен. Нажми Ctrl+C для выхода.")
    
    try:
        while True:
            config_data = load_config()
            
            # 🔥 ФИКС: Передаем черный список из интерфейса прямо в монитор!
            user_blacklist = config_data.get("blacklisted_domains", [])
            monitor.config["domain_blacklist"] = user_blacklist
            
            # Применяем язык
            lang = config_data.get("language", "ru")
            if lang not in STATUS_TRANSLATIONS:
                lang = "ru"
            t = STATUS_TRANSLATIONS[lang]
            
            tab_data = monitor.get_current_tab()
            
            if tab_data["url"] and tab_data["url"] != "hidden://protected":
                site = tab_data["domain"] if tab_data["domain"] else t["browser_empty"]
                
                if tab_data["has_audio"]:
                    details = f"{t['watching']}: {site}"
                else:
                    details = f"{t['browsing']}: {site}"
                    
                state = tab_data["title"]
                image = tab_data.get("favicon_url") or "https://cdn-icons-png.flaticon.com/512/841/841364.png"
                
            elif tab_data["url"] == "hidden://protected":
                details = t["hidden_details"]
                state = tab_data["title"] 
                image = "https://cdn-icons-png.flaticon.com/512/3064/3064155.png" 
            else:
                details = t["idling_details"]
                state = t["idling_state"]
                image = "gaming"

            rpc_client.update_presence(details=details, state=state, large_image=image)
            
            time.sleep(15)
            
    except KeyboardInterrupt:
        print("\n[Tracker] Работа программы завершена.")
        monitor.stop_monitoring() 

if __name__ == "__main__":
    main_loop()