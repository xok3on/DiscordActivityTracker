import os
import re
import json
import time
import logging
import urllib.request
import urllib.parse
from datetime import datetime
from typing import List, Dict, Optional, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

# Настройка логирования для аудита безопасности
logger = logging.getLogger("DiscordActivityTracker.BrowserTabs")
logger.setLevel(logging.INFO)

# Глобальный буфер для данных, поступающих из нативного расширения
_extension_state: Dict[str, Any] = {
    "active_tab": {},
    "all_tabs": [],
    "last_updated": 0
}

class ExtensionHTTPServer(BaseHTTPRequestHandler):
    """Легковесный сервер для приема зашифрованных/структурированных JSON от расширения."""
    
    def end_headers(self):
        """УЛЬТИМАТИВНЫЙ ФИКС CORS"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        """Ответ на предварительный (preflight) запрос браузера"""
        self.send_response(200)
        self.end_headers()
        
    def do_POST(self) -> None:
        if self.path == "/api/tab-update":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                payload = json.loads(post_data.decode('utf-8'))
                
                # Валидация версии протокола взаимодействия
                if payload.get("version") != "1.0":
                    self.send_response(400)
                    self.end_headers()
                    return
                
                global _extension_state
                action = payload.get("action")
                
                if action == "active_tab_sync":
                    _extension_state["active_tab"] = payload.get("data", {})
                    _extension_state["last_updated"] = time.time()
                    # === ВЫВОД ДЛЯ ДЕБАГА В КОНСОЛЬ ===
                    print(f"🔥 Прилетело из браузера: {payload['data'].get('title')}")
                elif action == "all_tabs_sync":
                    _extension_state["all_tabs"] = payload.get("data", [])
                    _extension_state["last_updated"] = time.time()
                elif action == "ping":
                    pass # Heartbeat
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "acknowledged"}).encode())
            except Exception as e:
                logger.error(f"[SECURITY] Ошибка обработки данных расширения: {e}")
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        pass


class BrowserMonitor:
    """Монитор для отслеживания активных вкладок браузеров"""

    def __init__(self, config: Optional[dict] = None) -> None:
        self.config = config or {
            "enabled_browsers": ["chrome", "firefox", "edge", "brave", "opera", "vivaldi", "yandex"],
            "remote_debugging_port": 9222,
            "strip_url_params": True,
            "max_title_length": 128,
            "domain_whitelist": [],
            "domain_blacklist": [
                "tinkoff.ru", "sberbank.ru", "sber.ru", "mail.google.com", 
                "e.mail.ru", "passport.yandex.ru", "github.com/settings"
            ],
            "privacy_filter": {
                "sensitive_tokens": [
                    r"(?i)token=[^&]+", r"(?i)auth=[^&]+", r"(?i)session=[^&]+", 
                    r"(?i)sid=[^&]+", r"(?i)api_key=[^&]+", r"(?i)password=[^&]+"
                ],
                "title_mask_patterns": [
                    r"[\w\.-]+@[\w\.-]+\.\w+", # Email
                    r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b" # Карты
                ]
            }
        }
        
        self._is_running: bool = False
        self._cache_ttl = 5  # секунд
        self._cached_result: Optional[dict] = None
        self._cache_timestamp: float = 0.0
        
        self.token_regexes = [re.compile(p) for p in self.config["privacy_filter"]["sensitive_tokens"]]
        self.title_regexes = [re.compile(p) for p in self.config["privacy_filter"]["title_mask_patterns"]]
        
        self.browser_ports = {
            "chrome": 9222, "edge": 9223, "brave": 9224, "vivaldi": 9225, "yandex": 9226
        }
        
        self._server_thread: Optional[Thread] = None
        self._httpd: Optional[HTTPServer] = None

    def start_monitoring(self) -> None:
        self._show_first_launch_warning()
        self._is_running = True
        
        self._httpd = HTTPServer(('127.0.0.1', 53241), ExtensionHTTPServer)
        self._server_thread = Thread(target=self._httpd.serve_forever, daemon=True)
        self._server_thread.start()
        logger.info("Мониторинг браузеров успешно инициализирован.")

    def stop_monitoring(self) -> None:
        self._is_running = False
        if self._httpd:
            self._httpd.shutdown()
            self._httpd.server_close()
        logger.info("Мониторинг браузеров остановлен.")

    def get_current_tab(self) -> dict:
        now = time.time()
        if self._cached_result and (now - self._cache_timestamp) < self._cache_ttl:
            return self._cached_result

        tab_data = self._fetch_raw_tab_data()
        if tab_data:
            processed_data = self._apply_privacy_filters(tab_data)
            self._cached_result = processed_data
            self._cache_timestamp = now
            return processed_data

        return self._get_empty_state()

    def _fetch_raw_tab_data(self) -> Optional[dict]:
        # === ВНИМАНИЕ: ВОТ ТОТ САМЫЙ ФИКС, 120 СЕКУНД ВМЕСТО 6 ===
        if time.time() - _extension_state["last_updated"] < 120:
            ext_tab = _extension_state["active_tab"]
            if ext_tab:
                return {
                    "browser": ext_tab.get("browser", "Extension-Linked Browser"),
                    "url": ext_tab.get("url", ""),
                    "title": ext_tab.get("title", ""),
                    "has_audio": ext_tab.get("has_audio", False)
                }

        for browser, port in self.browser_ports.items():
            if browser in self.config["enabled_browsers"]:
                cdp_data = self._query_cdp_endpoint(browser, port)
                if cdp_data:
                    return cdp_data

        return self._fallback_ocr_detection()

    def _query_cdp_endpoint(self, browser_name: str, port: int) -> Optional[dict]:
        try:
            url = f"http://127.0.0.1:{port}/json/list"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=1.5) as response:
                tabs = json.loads(response.read().decode('utf-8'))
                
                for tab in tabs:
                    if tab.get("type") == "page" and not tab.get("url", "").startswith("chrome://"):
                        return {
                            "browser": browser_name,
                            "url": tab.get("url", ""),
                            "title": tab.get("title", ""),
                            "has_audio": False 
                        }
        except Exception:
            pass
        return None

    def _fallback_ocr_detection(self) -> Optional[dict]:
        return None

    def _apply_privacy_filters(self, raw_data: dict) -> dict:
        url = raw_data.get("url", "")
        title = raw_data.get("title", "")
        
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc.lower()
        
        for black_domain in self.config["domain_blacklist"]:
            if black_domain in domain:
                return self._get_masked_state(raw_data["browser"], "[Protected Asset]")

        if self.config["domain_whitelist"] and not any(wd in domain for wd in self.config["domain_whitelist"]):
            return self._get_masked_state(raw_data["browser"], "[Unlisted Domain]")

        clean_url = url
        if self.config["strip_url_params"]:
            clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        else:
            query = parsed_url.query
            for regex in self.token_regexes:
                query = regex.sub("token=[REDACTED]", query)
            clean_url = urllib.parse.urlunparse(parsed_url._replace(query=query))

        clean_title = title
        for regex in self.title_regexes:
            clean_title = regex.sub("[REDACTED]", clean_title)
            
        if len(clean_title) > self.config["max_title_length"]:
            clean_title = clean_title[:self.config["max_title_length"]] + "..."

        return {
            "browser": raw_data["browser"],
            "url": clean_url,
            "title": " ".join(clean_title.split()), 
            "domain": domain,
            "favicon_url": f"https://www.google.com/s2/favicons?domain={domain}&sz=64",
            "has_audio": raw_data.get("has_audio", False),
            "started_at": datetime.now().isoformat()
        }

    def _show_first_launch_warning(self) -> None:
        print("\n" + "="*70)
        print("[БЕЗОПАСНОСТЬ] Внимание! Модуль 'browser_tabs' запущен.")
        print("="*70 + "\n")

    def _get_empty_state(self) -> dict:
        return {"browser": "None", "url": "", "title": "No Active Tab", "domain": "", "favicon_url": "", "has_audio": False, "started_at": ""}

    def _get_masked_state(self, browser: str, label: str) -> dict:
        return {"browser": browser, "url": "hidden://protected", "title": label, "domain": "protected", "favicon_url": "", "has_audio": False, "started_at": datetime.now().isoformat()}

# --- Демонстрация работы модуля ---
if __name__ == "__main__":
    print("=== Запуск отладки модуля browser_tabs.py ===")
    monitor = BrowserMonitor()
    monitor.start_monitoring()
    
    try:
        for i in range(5):
            time.sleep(2)
            data = monitor.get_current_tab()
            print(f"\n[Апдейт {i+1}/5] Текущая вкладка:")
            print(f"  Браузер: {data['browser']}")
            print(f"  Домен:   {data['domain']}")
            print(f"  Заголовок: {data['title']}")
            
    finally:
        monitor.stop_monitoring()