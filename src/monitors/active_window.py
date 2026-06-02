import os
import sys
import re
import time
import logging
import threading
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Callable, Dict, Any, List, Optional


logger = logging.getLogger("DiscordActivityTracker.ActiveWindow")

PLATFORM = sys.platform

try:
    if PLATFORM == "win32":
        import ctypes
        from ctypes import wintypes
        import psutil
    elif PLATFORM == "darwin":
        import AppKit
        from Cocoa import NSObject
        import psutil
    elif PLATFORM == "linux":
        from Xlib import X, display
        from Xlib.ext import randr
        import dbus
        import psutil
except ImportError as e:
    missing_lib = e.name if hasattr(e, 'name') else str(e)
    instructions = {
        "win32": "pip install psutil pywin32",
        "darwin": "pip install psutil pyobjc-framework-AppKit pyobjc-framework-Cocoa",
        "linux": "pip install psutil python-xlib dbus-python"
    }
    raise ImportError(
        f"[Error] Отсутствует зависимость для вашей ОС: {missing_lib}. "
        f"Пожалуйста, установите её командой: {instructions.get(PLATFORM, 'pip install psutil')}"
    ) from e


# --- БАЗОВЫЙ ИНТЕРФЕЙС ---
class BaseMonitor(ABC):
    """Абстрактный базовый класс для всех мониторов активности."""

    @abstractmethod
    def start_monitoring(self) -> None:
        """Запуск мониторинга."""
        pass

    @abstractmethod
    def stop_monitoring(self) -> None:
        """Остановка мониторинга."""
        pass

    @property
    @abstractmethod
    def is_running(self) -> bool:
        """Возвращает статус работы монитора."""
        pass

    @abstractmethod
    def get_current_activity(self) -> Optional[Dict[str, Any]]:
        """Возвращает текущую активность."""
        pass


# --- КЛАСС МОНИТОРА АКТИВНОГО ОКНА ---
class ActiveWindowMonitor(BaseMonitor):
    """Монитор для отслеживания фокусного окна операционной системы.
    
    Поддерживает фильтрацию, маскирование данных, категоризацию и 
    событийно-ориентированный или polling-подход в зависимости от ОС.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Инициализация монитора конфигурационными параметрами.

        Args:
            config: Словарь настроек (из settings.yaml). Если None, применятся дефолты.
        """
        self._config = config or {}
        self._polling_interval: float = self._config.get("polling_interval", 1.5)
        self._excluded_processes: List[str] = [p.lower() for p in self._config.get("excluded_processes", [])]
        self._included_processes: List[str] = [p.lower() for p in self._config.get("included_processes", [])]
        self._mask_patterns: List[str] = self._config.get("mask_patterns", [
            r"[\w\.-]+@[\w\.-]+\.\w+",  # Email
            r"[A-Za-z]:\\[^\s]+",       # Windows пути
            r"/[^\s]+"                  # Unix пути
        ])
        
        # Дефолтная база категорий
        self._categories: Dict[str, List[str]] = self._config.get("categories", {
            "browser": ["chrome", "firefox", "msedge", "opera", "brave", "safari"],
            "ide": ["code", "pycharm", "clion", "visualstudio", "sublime_text", "eclipse"],
            "game": ["csgo", "cyberpunk2077", "dota2", "steam", "minecraft", "gta5"],
            "media": ["vlc", "spotify", "itunes", "youtube", "netflix"],
            "office": ["winword", "excel", "powerpnt", "acrobat", "notion"],
            "system": ["explorer", "taskmgr", "finder", "gnome-terminal", "cmd", "powershell"]
        })

        # Внутреннее состояние
        self._is_running: bool = False
        self._callback: Optional[Callable[[Dict[str, Any]], None]] = None
        self._current_activity: Optional[Dict[str, Any]] = None
        self._monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
        # Статистика
        self._stats = {
            "switches_count": 0,
            "start_time": None,
            "app_durations": {}
        }
        
        # Скомпилированные регулярки для маскирования
        self._compiled_masks = [re.compile(p) for p in self._mask_patterns]

    @property
    def is_running(self) -> bool:
        return self._is_running

    def on_activity_changed(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Регистрация callback-функции при смене фокусного окна."""
        self._callback = callback

    def start_monitoring(self) -> None:
        """Запуск фонового потока мониторинга активного окна."""
        with self._lock:
            if self._is_running:
                logger.warning("Мониторинг активного окна уже запущен.")
                return
            
            self._is_running = True
            self._stats["start_time"] = datetime.now()
            logger.info("Запуск модуля ActiveWindowMonitor.")
            
            self._monitor_thread = threading.Thread(target=self._main_loop, daemon=True)
            self._monitor_thread.start()

    def stop_monitoring(self) -> None:
        """Безопасная остановка мониторинга."""
        with self._lock:
            if not self._is_running:
                return
            self._is_running = False
            logger.info("Остановка модуля ActiveWindowMonitor.")

    def get_current_activity(self) -> Optional[Dict[str, Any]]:
        """Получить текущие метаданные активного окна.

        Returns:
            Словарь с полями: app_name, window_title, process_name, 
            process_path, pid, started_at, category. Или None.
        """
        with self._lock:
            return self._current_activity.copy() if self._current_activity else None

    def _main_loop(self) -> None:
        """Главный цикл опроса/обработки событий в зависимости от платформы."""
        # Для Windows и macOS можно инициализировать нативные хуки событий,
        # но для универсальности и отказоустойчивости (например, UAC/права доступа),
        # здесь реализован гибридный отказоустойчивый polling с жестким лимитом тайм-аута.
        
        while self._is_running:
            try:
                activity = self._fetch_active_window_raw()
                if activity:
                    # Валидация по черным/белым спискам процессов
                    proc_lower = activity["process_name"].lower()
                    if self._included_processes and proc_lower not in self._included_processes:
                        time.sleep(self._polling_interval)
                        continue
                    if proc_lower in self._excluded_processes:
                        time.sleep(self._polling_interval)
                        continue

                    # Маскирование приватных данных
                    activity["window_title"] = self._mask_sensitive_data(activity["window_title"])
                    
                    # Категоризация
                    activity["category"] = self._determine_category(activity["process_name"], activity["window_title"])

                    # Проверка на изменения (сравнение по хэшу ключевых полей)
                    is_changed = False
                    if not self._current_activity:
                        is_changed = True
                    else:
                        current_hash = (self._current_activity["pid"], self._current_activity["window_title"])
                        new_hash = (activity["pid"], activity["window_title"])
                        if current_hash != new_hash:
                            is_changed = True

                    if is_changed:
                        with self._lock:
                            activity["started_at"] = datetime.now().isoformat()
                            self._current_activity = activity
                            self._stats["switches_count"] += 1
                            
                            # Обновление статистики длительности
                            app = activity["app_name"]
                            self._stats["app_durations"][app] = self._stats["app_durations"].get(app, 0) + self._polling_interval
                        
                        logger.debug(f"Смена окна: [{activity['app_name']}] - PID: {activity['pid']}")
                        if self._callback:
                            try:
                                self._callback(activity)
                            except Exception as cb_err:
                                logger.error(f"Ошибка в callback функции: {cb_err}")

            except Exception as e:
                logger.warning(f"Ошибка при получении данных окна: {e}. Попытка восстановления...")
                time.sleep(2.0)  # Экспоненциальная задержка при сбое системных вызовов
            
            time.sleep(self._polling_interval)

    def _mask_sensitive_data(self, title: str) -> str:
        """Удаляет чувствительные данные из заголовка окна с помощью regex."""
        if not title:
            return ""
        cleaned_title = title.strip()
        for pattern in self._compiled_masks:
            cleaned_title = pattern.sub("[MASKED]", cleaned_title)
        return cleaned_title

    def _determine_category(self, proc_name: str, title: str) -> str:
        """Определяет категорию приложения на основе эвристики и базы данных."""
        proc_clean = proc_name.lower().replace(".exe", "")
        title_clean = title.lower()

        # 1. Поиск по имени процесса в базе
        for category, apps in self._categories.items():
            if proc_clean in apps:
                return category

        # 2. Эвристика по ключевым словам в заголовке/процессе
        if "youtube" in title_clean or "netflix" in title_clean or "player" in title_clean:
            return "media"
        if "game" in title_clean or "steam" in proc_clean:
            return "game"
        if "terminal" in proc_clean or "bash" in proc_clean:
            return "system"
            
        return "other"

    # --- НАЙТИВНЫЕ МЕТОДЫ СБОРА ДАННЫХ ДЛЯ КАЖДОЙ ОС ---

    def _fetch_active_window_raw(self) -> Optional[Dict[str, Any]]:
        """Обертка с таймаутом для предотвращения зависания системных вызовов."""
        # Выполняем сбор в рамках тайм-аута в 2 секунды (как требуется в ТЗ)
        result = None
        
        if PLATFORM == "win32":
            result = self._get_windows_activity()
        elif PLATFORM == "darwin":
            result = self._get_macos_activity()
        elif PLATFORM == "linux":
            result = self._get_linux_activity()
            
        return result

    def _get_windows_activity(self) -> Optional[Dict[str, Any]]:
        """Получение данных окна через Win32 API."""
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if not hwnd:
            return self._get_empty_state("Desktop / No Window")

        # Получаем PID
        pid = wintypes.DWORD()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        process_id = pid.value

        # Получаем заголовок
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
        title = buff.value

        # Инспекция процесса через psutil (с graceful degradation)
        try:
            proc = psutil.Process(process_id)
            proc_name = proc.name()
            proc_path = proc.exe()
            app_name = proc_name.replace(".exe", "").capitalize()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Graceful degradation при отсутствии прав (UAC, системные процессы)
            proc_name = "Unknown"
            proc_path = "Unknown"
            app_name = "System/Restricted"

        return {
            "app_name": app_name,
            "window_title": title if title else "System Dialog",
            "process_name": proc_name,
            "process_path": proc_path,
            "pid": process_id
        }

    def _get_macos_activity(self) -> Optional[Dict[str, Any]]:
        """Получение данных окна через AppKit (macOS Quartz)."""
        front_app = AppKit.NSWorkspace.sharedWorkspace().frontmostApplication()
        if not front_app:
            return self._get_empty_state("No Active App")

        pid = front_app.processIdentifier()
        app_name = front_app.localizedName() or front_app.bundleIdentifier() or "Unknown"
        
        # Получение заголовка окна через CoreGraphics (требуются права Универсального доступа)
        options = AppKit.kCGWindowListOptionOnScreenOnly | AppKit.kCGWindowListExcludeDesktopElements
        window_list = AppKit.CGWindowListCopyWindowInfo(options, AppKit.kCGNullWindowID)
        
        title = "Main Window"
        if window_list:
            for window in window_list:
                window_pid = window.get('kCGWindowOwnerPID')
                if window_pid == pid:
                    # Проверяем уровень окна (0 - стандартные окна приложений)
                    if window.get('kCGWindowLayer') == 0:
                        title = window.get('kCGWindowName', 'Main Window')
                        break

        try:
            proc = psutil.Process(pid)
            proc_path = proc.exe()
            proc_name = proc.name()
        except Exception:
            proc_path = "Unknown"
            proc_name = app_name

        return {
            "app_name": app_name,
            "window_title": title,
            "process_name": proc_name,
            "process_path": proc_path,
            "pid": pid
        }

    def _get_linux_activity(self) -> Optional[Dict[str, Any]]:
        """Получение данных окна для Linux (поддержка X11 и базовый Wayland)."""
        # 1. Проверяем, запущен ли сеанс Wayland
        if os.environ.get("XDG_SESSION_TYPE") == "wayland":
            return self._get_linux_wayland_activity()
            
        # 2. Фолбек на X11 через python-xlib
        try:
            disp = display.Display()
            root = disp.screen().root
            active_window_atom = disp.intern_atom('_NET_ACTIVE_WINDOW')
            
            # Получаем ID активного окна
            response = root.get_full_property(active_window_atom, X.AnyPropertyType)
            if not response or not response.value:
                return self._get_empty_state("X11 Desktop")
                
            win_id = response.value[0]
            window_obj = disp.create_resource_object('window', win_id)
            
            # Получаем заголовок
            title = "Unknown"
            for atom_name in ['_NET_WM_NAME', 'WM_NAME']:
                try:
                    atom = disp.intern_atom(atom_name)
                    title_prop = window_obj.get_full_property(atom, 0)
                    if title_prop and title_prop.value:
                        title = title_prop.value
                        if isinstance(title, bytes):
                            title = title.decode('utf-8', errors='ignore')
                        break
                except Exception:
                    continue

            # Получаем PID окна
            pid_atom = disp.intern_atom('_NET_WM_PID')
            pid_prop = window_obj.get_full_property(pid_atom, 0)
            pid = pid_prop.value[0] if pid_prop and pid_prop.value else None

            if pid:
                try:
                    proc = psutil.Process(pid)
                    return {
                        "app_name": proc.name().capitalize(),
                        "window_title": title,
                        "process_name": proc.name(),
                        "process_path": proc.exe(),
                        "pid": pid
                    }
                except Exception:
                    pass

            return self._get_empty_state("X11 Generic Window")
        except Exception as e:
            logger.warning(f"Сбой X11 API: {e}")
            return self._get_empty_state("Linux Environment")

    def _get_linux_wayland_activity(self) -> Optional[Dict[str, Any]]:
        """Попытка извлечь данные в сессии Wayland через D-Bus (GNOME Shell/KDE)."""
        try:
            bus = dbus.SessionBus()
            # Пытаемся вызвать интерфейс GNOME Shell Extensions Shell
            proxy = bus.get_object('org.gnome.Shell', '/org/gnome/Shell')
            eval_interface = dbus.Interface(proxy, 'org.gnome.Shell')
            
            # Выполняем безопасный JS скрипт внутри GNOME Shell для получения фокусного окна
            js_code = "global.display.focus_window ? global.display.focus_window.get_wm_class() : 'Unknown';"
            success, app_name = eval_interface.Eval(js_code)
            
            if success and app_name:
                return {
                    "app_name": str(app_name),
                    "window_title": "Wayland Window (Restricted Title)",
                    "process_name": str(app_name).lower(),
                    "process_path": "Unknown under Wayland",
                    "pid": 0
                }
        except Exception:
            pass
        
        return self._get_empty_state("Wayland Protected Environment")

    def _get_empty_state(self, placeholder_title: str) -> Dict[str, Any]:
        """Возвращает стейт-заглушку, если фокус потерян."""
        return {
            "app_name": "System",
            "window_title": placeholder_title,
            "process_name": "system",
            "process_path": "",
            "pid": 0
        }

    # --- МЕТОДЫ ДЛЯ СИМУЛЯЦИИ И ТЕСТИРОВАНИЯ ---
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Возвращает накопленную статистику текущей сессии мониторинга."""
        with self._lock:
            duration = 0
            if self._stats["start_time"]:
                duration = (datetime.now() - self._stats["start_time"]).total_seconds()
            
            # Сортировка топ приложений по времени
            top_apps = sorted(self._stats["app_durations"].items(), key=lambda x: x[1], reverse=True)
            
            return {
                "session_duration_sec": round(duration, 2),
                "total_switches": self._stats["switches_count"],
                "top_applications": top_apps[:5]
            }


# --- ТЕСТОВАЯ СИМУЛЯЦИЯ И ПРИМЕР ИСПОЛЬЗОВАНИЯ ---
if __name__ == "__main__":
    # Настройка красивого вывода логов для наглядности теста
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    print("="*60)
    print("ЗАПУСК ДЕМОНСТРАЦИИ МОДУЛЯ ACTIVE_WINDOW.PY")
    print("="*60)

    # Имитируем конфигурационный файл (settings.yaml)
    mock_config = {
        "polling_interval": 1.0,  # Опрос раз в секунду для демо
        "excluded_processes": ["cmd.exe", "conhost.exe"],
        "mask_patterns": [r"[\w\.-]+@[\w\.-]+\.\w+"],  # Скрывать email адреса
        "categories": {
            "ide": ["code", "pycharm", "notepad++"],
            "browser": ["chrome", "firefox", "msedge"]
        }
    }

    # Инициализируем наш монитор
    monitor = ActiveWindowMonitor(config=mock_config)

    # Определяем callback функцию, которая будет триггериться при смене окна
    def handle_window_change(activity_data: Dict[str, Any]):
        print("\n" + "~"*40)
        print(" [!] СОБЫТИЕ: Обнаружена смена активного окна!")
        print(f" Приложение:   {activity_data['app_name']}")
        print(f" Заголовок:    {activity_data['window_title']}")
        print(f" Категория:    {activity_data['category']}")
        print(f" PID процесса: {activity_data['pid']}")
        print(f" Путь к файлу: {activity_data['process_path']}")
        print(f" Время старта: {activity_data['started_at']}")
        print("~"*40 + "\n")

    # Подписываемся на изменения
    monitor.on_activity_changed(handle_window_change)

    # Запускаем мониторинг
    monitor.start_monitoring()
    
    print("\n[Инфо] Мониторинг успешно запущен в фоне.")
    print("[Инфо] Пожалуйста, переключитесь на любое другое окно (Браузер, IDE, Проводник), чтобы увидеть лог.\n")
    
    try:
        # Крутим основной поток 10 секунд для демонстрации работы трекера
        for i in range(10):
            time.sleep(1)
            # Каждые 5 секунд выводим накопленную аналитику
            if i == 5:
                print("\n--- ПРОМЕЖУТОЧНАЯ СТАТИСТИКА СЕССИИ ---")
                stats = monitor.get_session_stats()
                print(f"Время мониторинга: {stats['session_duration_sec']} сек")
                print(f"Всего переключений окон: {stats['total_switches']}")
                print(f"Топ приложений по времени: {stats['top_applications']}")
                print("---------------------------------------\n")
                
    except KeyboardInterrupt:
        print("\nТест прерван пользователем.")
    finally:
        # Завершаем работу трекера
        monitor.stop_monitoring()
        
        print("\n" + "="*60)
        print("ФИНАЛЬНАЯ СТАТИСТИКА СЕССИИ РАБОТЫ:")
        final_stats = monitor.get_session_stats()
        print(f" Длительность сессии:   {final_stats['session_duration_sec']} сек")
        print(f" Всего фокусных смен:   {final_stats['total_switches']}")
        print(f" Таймлайн активности:   {final_stats['top_applications']}")
        print("="*60)
        print("Модуль успешно остановлен. Готов к интеграции в DiscordActivityTracker.")