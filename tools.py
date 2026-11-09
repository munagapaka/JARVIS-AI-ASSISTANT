# tools.py

import ctypes
import datetime as dt
import html
import json
import os
import re
import subprocess
import threading
import time
import urllib.parse
import urllib.request
import webbrowser
from html.parser import HTMLParser

import psutil
import pyautogui


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _expand_path(path):
    return os.path.abspath(os.path.expandvars(os.path.expanduser(str(path))))


def _run_powershell(command, timeout=15):
    return subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        capture_output=True, text=True, timeout=timeout,
    )


def _safe_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# ============================================================
# APPLICATION TOOLS
# ============================================================

def _start_menu_shortcuts():
    locations = [
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
        os.path.expandvars(r"%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs"),
    ]
    for location in locations:
        if not os.path.isdir(location):
            continue
        for root, _, files in os.walk(location):
            for file in files:
                if file.lower().endswith((".lnk", ".url")):
                    yield os.path.join(root, file)


def open_application(application_name):
    """Find and open a Windows application through Start Menu shortcuts."""
    try:
        name = str(application_name).strip()
        if not name:
            return "Application name is required."
        search = name.lower()
        candidates = []
        for path in _start_menu_shortcuts():
            base = os.path.splitext(os.path.basename(path))[0].strip().lower()
            if search in base:
                candidates.append(path)
        exact = [p for p in candidates if os.path.splitext(os.path.basename(p))[0].strip().lower() == search]
        selected = exact[0] if exact else (candidates[0] if candidates else None)
        if selected:
            os.startfile(selected)
            return f"Opened application: {name}"
        try:
            escaped = name.replace("'", "''")
            result = _run_powershell(f"$ErrorActionPreference='Stop'; Start-Process -FilePath '{escaped}'", 10)
            if result.returncode == 0:
                return f"Opened application: {name}"
        except Exception:
            pass
        return f"Couldn't find '{name}' in the Windows Start Menu."
    except Exception as e:
        return f"Couldn't open application '{application_name}': {e}"


def close_application(application_name):
    """Close an application by executable image name."""
    try:
        name = str(application_name).strip()
        if not name:
            return "Application name is required."
        image = name if name.lower().endswith('.exe') else name + '.exe'
        result = subprocess.run(["taskkill", "/IM", image, "/F"], capture_output=True, text=True)
        if result.returncode == 0:
            return f"Closed application: {name}"
        return f"Couldn't close application: {name}"
    except Exception as e:
        return f"Couldn't close application '{application_name}': {e}"


# ============================================================
# FILE / FOLDER TOOLS
# ============================================================

def open_folder(folder_path):
    try:
        path = _expand_path(folder_path)
        if not os.path.isdir(path):
            return f"Folder not found: {path}"
        os.startfile(path)
        return f"Opened folder: {path}"
    except Exception as e:
        return f"Couldn't open folder: {e}"


def open_named_folder(folder_name):
    try:
        name = str(folder_name).strip()
        if not name:
            return "Folder name is required."
        home = os.path.expanduser("~")
        for root, dirs, _ in os.walk(home):
            for directory in dirs:
                if directory.lower() == name.lower():
                    path = os.path.join(root, directory)
                    os.startfile(path)
                    return f"Opened folder: {path}"
        return f"Couldn't find folder: {name}"
    except Exception as e:
        return f"Couldn't find folder: {e}"


def close_folder():
    try:
        _run_powershell("Get-Process explorer -ErrorAction SilentlyContinue | ForEach-Object { $_.CloseMainWindow() | Out-Null }", 10)
        return "Closed File Explorer windows."
    except Exception as e:
        return f"Couldn't close File Explorer: {e}"


def create_folder(folder_path):
    try:
        path = _expand_path(folder_path)
        os.makedirs(path, exist_ok=True)
        return f"Created folder: {path}"
    except Exception as e:
        return f"Couldn't create folder: {e}"


def create_file(file_path):
    try:
        path = _expand_path(file_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8"):
            pass
        return f"Created file: {path}"
    except Exception as e:
        return f"Couldn't create file: {e}"


def rename_folder(folder_path, new_name):
    try:
        old = _expand_path(folder_path)
        new = os.path.join(os.path.dirname(old), str(new_name).strip())
        os.rename(old, new)
        return f"Renamed folder to: {new}"
    except Exception as e:
        return f"Couldn't rename folder: {e}"


def rename_file(file_path, new_name):
    try:
        old = _expand_path(file_path)
        new = os.path.join(os.path.dirname(old), str(new_name).strip())
        os.rename(old, new)
        return f"Renamed file to: {new}"
    except Exception as e:
        return f"Couldn't rename file: {e}"


def move_folder(folder_path, destination_folder):
    try:
        old = _expand_path(folder_path)
        dest_dir = _expand_path(destination_folder)
        os.makedirs(dest_dir, exist_ok=True)
        destination = os.path.join(dest_dir, os.path.basename(os.path.normpath(old)))
        os.rename(old, destination)
        return f"Moved folder to: {destination}"
    except Exception as e:
        return f"Couldn't move folder: {e}"


def move_file(file_path, destination_folder):
    try:
        old = _expand_path(file_path)
        dest_dir = _expand_path(destination_folder)
        os.makedirs(dest_dir, exist_ok=True)
        destination = os.path.join(dest_dir, os.path.basename(old))
        os.rename(old, destination)
        return f"Moved file to: {destination}"
    except Exception as e:
        return f"Couldn't move file: {e}"


def delete_file(file_path):
    try:
        import send2trash
        path = _expand_path(file_path)
        if not os.path.isfile(path):
            return f"File not found: {path}"
        send2trash.send2trash(path)
        return f"Moved file to Recycle Bin: {path}"
    except Exception as e:
        return f"Couldn't delete file: {e}"


def delete_folder(folder_path):
    try:
        import send2trash
        path = _expand_path(folder_path)
        if not os.path.isdir(path):
            return f"Folder not found: {path}"
        send2trash.send2trash(path)
        return f"Moved folder to Recycle Bin: {path}"
    except Exception as e:
        return f"Couldn't delete folder: {e}"


# ============================================================
# KEYBOARD TOOLS — NO MOUSE TOOLS
# ============================================================

def type_text(text):
    try:
        if text is None:
            return "Text is required."
        text = str(text)
        pyautogui.write(text, interval=0.01)
        return f"Typed text: {text}"
    except Exception as e:
        return f"Couldn't type text: {e}"


def press_key(key):
    try:
        if key is None:
            return "Key is required."
        key = str(key).lower().strip()
        pyautogui.press(key)
        return f"Pressed key: {key}"
    except Exception as e:
        return f"Couldn't press key: {e}"


def hotkey(keys):
    try:
        if not keys:
            return "Keys are required."
        if isinstance(keys, str):
            keys = [k.strip() for k in keys.split('+')]
        keys = [str(k).lower().strip() for k in keys]
        pyautogui.hotkey(*keys)
        return f"Pressed hotkey: {'+'.join(keys)}"
    except Exception as e:
        return f"Couldn't press hotkey: {e}"


# ============================================================
# WINDOW TOOLS
# ============================================================

def _find_window_handle(title):
    if os.name != "nt":
        return None
    title = str(title).strip().lower()
    if not title:
        return None
    user32 = ctypes.windll.user32
    matches = []
    Proc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def callback(hwnd, _):
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return True
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        if title in buffer.value.strip().lower():
            matches.append(hwnd)
            return False
        return True
    user32.EnumWindows(Proc(callback), 0)
    return matches[0] if matches else None


def list_windows():
    try:
        user32 = ctypes.windll.user32
        windows = []
        Proc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        def callback(hwnd, _):
            if not user32.IsWindowVisible(hwnd):
                return True
            length = user32.GetWindowTextLengthW(hwnd)
            if length <= 0:
                return True
            buffer = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buffer, length + 1)
            title = buffer.value.strip()
            if title:
                windows.append(title)
            return True
        user32.EnumWindows(Proc(callback), 0)
        return "Open windows:\n" + "\n".join(windows[:50]) if windows else "No visible windows found."
    except Exception as e:
        return f"Couldn't list windows: {e}"


def _window_action(window_title, command, description):
    try:
        hwnd = _find_window_handle(window_title)
        if not hwnd:
            return f"Couldn't find window: {window_title}"
        ctypes.windll.user32.ShowWindow(hwnd, command)
        if command == 9:
            ctypes.windll.user32.SetForegroundWindow(hwnd)
        return f"{description}: {window_title}"
    except Exception as e:
        return f"Window operation failed: {e}"


def focus_window(window_title): return _window_action(window_title, 9, "Focused window")
def minimize_window(window_title): return _window_action(window_title, 6, "Minimized window")
def maximize_window(window_title): return _window_action(window_title, 3, "Maximized window")
def restore_window(window_title): return _window_action(window_title, 9, "Restored window")


def close_window(window_title):
    try:
        hwnd = _find_window_handle(window_title)
        if not hwnd:
            return f"Couldn't find window: {window_title}"
        ctypes.windll.user32.PostMessageW(hwnd, 0x0010, 0, 0)
        return f"Closed window: {window_title}"
    except Exception as e:
        return f"Couldn't close window: {e}"


def switch_window():
    try:
        pyautogui.hotkey("alt", "tab")
        return "Switched to the next window."
    except Exception as e:
        return f"Couldn't switch window: {e}"


# ============================================================
# PC SEARCH
# ============================================================

def _search_root(location):
    return _expand_path(location) if location else os.path.expanduser("~")


def find_file(file_name, location=None, max_results=20, extension=None):
    try:
        needle = str(file_name).strip().lower()
        root = _search_root(location)
        limit = max(1, min(_safe_int(max_results, 20), 100))
        ext = str(extension).strip().lower() if extension else None
        if ext and not ext.startswith('.'):
            ext = '.' + ext
        matches = []
        for current, dirs, files in os.walk(root):
            for filename in files:
                if needle in filename.lower() and (not ext or filename.lower().endswith(ext)):
                    matches.append(os.path.join(current, filename))
                    if len(matches) >= limit:
                        break
            if len(matches) >= limit:
                break
        return "Found files:\n" + "\n".join(matches) if matches else f"No files matching '{needle}' were found."
    except Exception as e:
        return f"File search failed: {e}"


def find_folder(folder_name, location=None, max_results=20):
    try:
        needle = str(folder_name).strip().lower()
        root = _search_root(location)
        limit = max(1, min(_safe_int(max_results, 20), 100))
        matches = []
        for current, dirs, _ in os.walk(root):
            for dirname in dirs:
                if needle in dirname.lower():
                    matches.append(os.path.join(current, dirname))
                    if len(matches) >= limit:
                        break
            if len(matches) >= limit:
                break
        return "Found folders:\n" + "\n".join(matches) if matches else f"No folders matching '{needle}' were found."
    except Exception as e:
        return f"Folder search failed: {e}"


def find_application(application_name):
    try:
        needle = str(application_name).strip().lower()
        matches = []
        for path in _start_menu_shortcuts():
            name = os.path.splitext(os.path.basename(path))[0]
            if needle in name.lower():
                matches.append(f"{name} -> {path}")
        return "Applications found:\n" + "\n".join(matches[:30]) if matches else f"No application matching '{application_name}' was found."
    except Exception as e:
        return f"Application search failed: {e}"


def find_large_files(location=None, minimum_mb=100, max_results=20):
    try:
        root = _search_root(location)
        minimum_bytes = float(minimum_mb) * 1024 * 1024
        limit = max(1, min(_safe_int(max_results, 20), 100))
        found = []
        for current, _, files in os.walk(root):
            for filename in files:
                path = os.path.join(current, filename)
                try:
                    size = os.path.getsize(path)
                    if size >= minimum_bytes:
                        found.append((size, path))
                except OSError:
                    continue
        found.sort(reverse=True)
        lines = [f"{size / (1024*1024):.1f} MB - {path}" for size, path in found[:limit]]
        return "Largest matching files:\n" + "\n".join(lines) if lines else "No files matched the size limit."
    except Exception as e:
        return f"Large-file search failed: {e}"


def find_recent_files(location=None, hours=24, max_results=20):
    try:
        root = _search_root(location)
        cutoff = time.time() - float(hours) * 3600
        limit = max(1, min(_safe_int(max_results, 20), 100))
        found = []
        for current, _, files in os.walk(root):
            for filename in files:
                path = os.path.join(current, filename)
                try:
                    modified = os.path.getmtime(path)
                    if modified >= cutoff:
                        found.append((modified, path))
                except OSError:
                    continue
        found.sort(reverse=True)
        return "Recently modified files:\n" + "\n".join(dt.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M') + " - " + p for t,p in found[:limit]) if found else "No recently modified files found."
    except Exception as e:
        return f"Recent-file search failed: {e}"


# ============================================================
# TERMINAL
# ============================================================

def run_terminal_command(command):
    """Run a terminal command requested by the user."""
    try:
        command = str(command).strip()
        if not command:
            return "Command is required."
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
        output = (result.stdout or "") + (result.stderr or "")
        output = output.strip()
        if len(output) > 12000:
            output = output[-12000:]
        return f"Exit code: {result.returncode}\n{output or '(no output)'}"
    except subprocess.TimeoutExpired:
        return "Terminal command timed out after 60 seconds."
    except Exception as e:
        return f"Terminal command failed: {e}"


# ============================================================
# BROWSER / WEB
# ============================================================

class _TextExtractor(HTMLParser):
    BLOCK = {"p","div","br","li","h1","h2","h3","h4","h5","h6","article","section"}
    SKIP = {"script","style","noscript","svg"}
    def __init__(self):
        super().__init__()
        self.parts=[]
        self.skip=0
    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP: self.skip += 1
        if tag in self.BLOCK and self.parts and not self.parts[-1].endswith("\n"): self.parts.append("\n")
    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip: self.skip -= 1
        if tag in self.BLOCK: self.parts.append("\n")
    def handle_data(self, data):
        if not self.skip:
            text=re.sub(r"\s+", " ", html.unescape(data)).strip()
            if text: self.parts.append(text + " ")


def open_website(url):
    try:
        url = str(url).strip()
        if not url:
            return "Website URL is required."
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
            url = "https://" + url
        webbrowser.open(url)
        return f"Opened website: {url}"
    except Exception as e:
        return f"Couldn't open website: {e}"


def browser_search(query):
    try:
        query = str(query).strip()
        if not query:
            return "Search query is required."
        url = "https://www.google.com/search?" + urllib.parse.urlencode({"q": query})
        webbrowser.open(url)
        return f"Opened browser search for: {query}"
    except Exception as e:
        return f"Couldn't perform browser search: {e}"


def read_webpage(url, max_characters=8000):
    try:
        url = str(url).strip()
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
            url = "https://" + url
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 JARVIS"})
        with urllib.request.urlopen(request, timeout=15) as response:
            content_type = response.headers.get("Content-Type", "")
            raw = response.read(2_000_000)
            charset = response.headers.get_content_charset() or "utf-8"
        if "html" not in content_type.lower():
            return raw.decode(charset, errors="replace")[:int(max_characters)]
        parser = _TextExtractor()
        parser.feed(raw.decode(charset, errors="replace"))
        text = re.sub(r"\n{3,}", "\n\n", "".join(parser.parts)).strip()
        return text[:int(max_characters)] if text else "The webpage contained no readable text."
    except Exception as e:
        return f"Couldn't read webpage: {e}"


# ============================================================
# SYSTEM INFORMATION
# ============================================================

def _nvidia_info():
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,temperature.gpu,utilization.gpu,memory.used,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=8,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return []
        rows=[]
        for line in result.stdout.strip().splitlines():
            parts=[p.strip() for p in line.split(',')]
            if len(parts)>=5:
                rows.append({"name":parts[0],"temperature":parts[1],"utilization":parts[2],"memory_used":parts[3],"memory_total":parts[4]})
        return rows
    except Exception:
        return []


def gpu_temperature():
    try:
        gpus = _nvidia_info()
        if not gpus:
            return "GPU temperature is unavailable. NVIDIA nvidia-smi was not available or no NVIDIA GPU was detected."
        return "GPU temperature: " + ", ".join(f"{g['name']} = {g['temperature']} °C" for g in gpus)
    except Exception as e:
        return f"Couldn't read GPU temperature: {e}"


def system_status():
    try:
        cpu = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage(os.path.abspath(os.sep))
        boot = dt.datetime.fromtimestamp(psutil.boot_time())
        uptime = dt.datetime.now() - boot
        net = psutil.net_io_counters()
        lines = [
            f"CPU usage: {cpu:.1f}%",
            f"RAM: {memory.percent:.1f}% used ({memory.used/(1024**3):.1f} GB / {memory.total/(1024**3):.1f} GB)",
            f"System drive: {disk.percent:.1f}% used ({disk.free/(1024**3):.1f} GB free)",
            f"Network totals: {net.bytes_sent/(1024**2):.1f} MB sent, {net.bytes_recv/(1024**2):.1f} MB received",
            f"Uptime: {str(uptime).split('.')[0]}",
        ]
        battery = psutil.sensors_battery()
        if battery:
            lines.append(f"Battery: {battery.percent:.0f}% ({'charging' if battery.power_plugged else 'on battery'})")
        gpus = _nvidia_info()
        if gpus:
            for g in gpus:
                lines.append(f"GPU {g['name']}: {g['utilization']}% usage, {g['memory_used']} / {g['memory_total']} MB VRAM, {g['temperature']} °C")
        else:
            lines.append("GPU: NVIDIA telemetry unavailable.")
        lines.append("CPU temperature: intentionally not monitored in this build.")
        return "\n".join(lines)
    except Exception as e:
        return f"Couldn't read system status: {e}"


def running_processes(limit=25):
    try:
        limit=max(1,min(_safe_int(limit,25),100))
        rows=[]
        for p in psutil.process_iter(["pid","name","cpu_percent","memory_percent"]):
            try:
                info=p.info
                rows.append((float(info.get("cpu_percent") or 0), float(info.get("memory_percent") or 0), info.get("pid"), info.get("name") or "Unknown"))
            except (psutil.NoSuchProcess, psutil.AccessDenied): pass
        rows.sort(key=lambda x:(x[0],x[1]), reverse=True)
        return "Top running processes:\n" + "\n".join(f"{name} (PID {pid}) - CPU {cpu:.1f}% - RAM {mem:.1f}%" for cpu,mem,pid,name in rows[:limit])
    except Exception as e:
        return f"Couldn't read running processes: {e}"


def find_process(process_name):
    try:
        needle=str(process_name).strip().lower()
        matches=[]
        for p in psutil.process_iter(["pid","name"]):
            try:
                name=p.info.get("name") or ""
                if needle in name.lower(): matches.append(f"{name} (PID {p.info['pid']})")
            except (psutil.NoSuchProcess,psutil.AccessDenied): pass
        return "Matching processes:\n"+"\n".join(matches[:50]) if matches else f"No process matching '{process_name}' was found."
    except Exception as e:
        return f"Process search failed: {e}"


def close_process(process_name_or_pid):
    """Terminate a named process or PID. Use only when explicitly requested."""
    try:
        value=str(process_name_or_pid).strip()
        if not value: return "Process name or PID is required."
        targets=[]
        if value.isdigit():
            try: targets=[psutil.Process(int(value))]
            except psutil.NoSuchProcess: return f"No process with PID {value} was found."
        else:
            needle=value.lower()
            for p in psutil.process_iter(["name"]):
                try:
                    if needle in (p.info.get("name") or "").lower(): targets.append(p)
                except (psutil.NoSuchProcess,psutil.AccessDenied): pass
        if not targets: return f"No matching process was found: {value}"
        closed=0
        for p in targets:
            try:
                p.terminate(); closed += 1
            except (psutil.NoSuchProcess,psutil.AccessDenied): pass
        return f"Requested termination of {closed} matching process(es): {value}"
    except Exception as e:
        return f"Couldn't close process: {e}"


def battery_status():
    try:
        battery=psutil.sensors_battery()
        if not battery: return "Battery information is unavailable."
        return f"Battery: {battery.percent:.0f}% — {'charging' if battery.power_plugged else 'running on battery'}"
    except Exception as e:
        return f"Couldn't read battery status: {e}"


# ============================================================
# MEDIA / VOLUME
# ============================================================

def media_control(action):
    try:
        action=str(action).lower().strip()
        mapping={"play":"playpause","pause":"playpause","playpause":"playpause","next":"nexttrack","next_track":"nexttrack","previous":"prevtrack","previous_track":"prevtrack","prev":"prevtrack","mute":"volumemute"}
        key=mapping.get(action)
        if not key: return "Unknown media action. Use play, pause, next, previous, or mute."
        pyautogui.press(key)
        return f"Media action performed: {action}"
    except Exception as e: return f"Couldn't control media: {e}"


def volume_control(action):
    try:
        action=str(action).lower().strip()
        mapping={"up":"volumeup","increase":"volumeup","down":"volumedown","decrease":"volumedown","mute":"volumemute"}
        key=mapping.get(action)
        if not key: return "Unknown volume action. Use up, down, or mute."
        pyautogui.press(key)
        return f"Volume action performed: {action}"
    except Exception as e: return f"Couldn't control volume: {e}"


# ============================================================
# TIME / NOTIFICATIONS / REMINDERS
# ============================================================

_timer_lock=threading.Lock()
_timers={}
_next_timer_id=1

_REMINDER_FILE=os.path.join(os.path.expanduser("~"), ".jarvis_reminders.json")
_reminder_lock=threading.Lock()
_reminders={}
_next_reminder_id=1
_reminder_started=False


def get_current_time():
    now=dt.datetime.now()
    return f"The current local time is {now.strftime('%I:%M:%S %p')} on {now.strftime('%A, %d %B %Y')}."


def _show_windows_notification(message,title="J.A.R.V.I.S."):
    try:
        # Optional non-blocking desktop notification when plyer is installed.
        try:
            from plyer import notification
            notification.notify(title=str(title), message=str(message), app_name="J.A.R.V.I.S.", timeout=5)
            return
        except Exception:
            pass
        if os.name == "nt":
            escaped_title=str(title).replace("'","''")
            escaped_message=str(message).replace("'","''")
            ps=("Add-Type -AssemblyName PresentationFramework; "
                f"[System.Windows.MessageBox]::Show('{escaped_message}','{escaped_title}') | Out-Null")
            _run_powershell(ps,10)
        else:
            print(f"{title}: {message}")
    except Exception:
        print(f"{title}: {message}")


def set_timer(seconds, message="Timer finished."):
    global _next_timer_id
    try:
        seconds=float(seconds)
        if seconds<=0: return "Timer duration must be greater than zero."
        if seconds>7*24*60*60: return "Timer duration cannot exceed 7 days."
        with _timer_lock:
            timer_id=_next_timer_id; _next_timer_id+=1
        def finish():
            try: _show_windows_notification(message,"J.A.R.V.I.S. Timer")
            finally:
                with _timer_lock: _timers.pop(timer_id,None)
        timer=threading.Timer(seconds,finish); timer.daemon=True
        with _timer_lock: _timers[timer_id]={"timer":timer,"seconds":seconds,"message":str(message),"created":time.time()}
        timer.start()
        return f"Timer {timer_id} set for {seconds:g} seconds. Message: {message}"
    except Exception as e: return f"Couldn't set timer: {e}"


def list_timers():
    with _timer_lock:
        if not _timers: return "No active timers."
        now=time.time()
        return "\n".join(f"Timer {i}: {max(0,v['seconds']-(now-v['created'])):.0f} seconds remaining - {v['message']}" for i,v in _timers.items())


def cancel_timer(timer_id):
    try:
        timer_id=int(timer_id)
        with _timer_lock:
            info=_timers.pop(timer_id,None)
            if not info: return f"Timer {timer_id} was not found."
            info["timer"].cancel()
        return f"Cancelled timer {timer_id}."
    except Exception as e: return f"Couldn't cancel timer: {e}"


def notify_user(message):
    try:
        if not message: return "Notification message is required."
        _show_windows_notification(message,"J.A.R.V.I.S.")
        return "Notification displayed."
    except Exception as e: return f"Couldn't display notification: {e}"


def _load_reminders():
    try:
        if not os.path.exists(_REMINDER_FILE): return {}
        with open(_REMINDER_FILE,"r",encoding="utf-8") as f: data=json.load(f)
        return data if isinstance(data,dict) else {}
    except Exception: return {}


def _save_reminders(data):
    try:
        with open(_REMINDER_FILE,"w",encoding="utf-8") as f: json.dump(data,f,indent=2,ensure_ascii=False)
        return True
    except Exception: return False


def _schedule_reminder_thread(reminder_id, when_ts, message, repeat):
    def worker():
        delay=max(0, when_ts-time.time())
        time.sleep(delay)
        while True:
            with _reminder_lock:
                item=_reminders.get(str(reminder_id))
                if not item: return
            _show_windows_notification(message,"J.A.R.V.I.S. Reminder")
            if repeat not in ("daily","weekly"):
                with _reminder_lock:
                    _reminders.pop(str(reminder_id),None); _save_reminders(_reminders)
                return
            seconds=86400 if repeat=="daily" else 604800
            when_ts=time.time()+seconds
            with _reminder_lock:
                if str(reminder_id) in _reminders:
                    _reminders[str(reminder_id)]["when"] = when_ts
                    _save_reminders(_reminders)
            time.sleep(seconds)
    t=threading.Thread(target=worker,daemon=True)
    t.start()


def _start_saved_reminders():
    global _reminders,_next_reminder_id,_reminder_started
    if _reminder_started: return
    _reminder_started=True
    _reminders=_load_reminders()
    now=time.time()
    for key,item in list(_reminders.items()):
        try:
            rid=int(key); _next_reminder_id=max(_next_reminder_id,rid+1)
            when=float(item["when"]); message=str(item["message"]); repeat=item.get("repeat")
            if when < now and repeat not in ("daily","weekly"):
                del _reminders[key]; continue
            _schedule_reminder_thread(rid,when,message,repeat)
        except Exception:
            _reminders.pop(key,None)
    _save_reminders(_reminders)


def schedule_reminder(reminder_time, message, repeat="none"):
    """Schedule a one-time, daily, or weekly reminder. Use ISO datetime, e.g. 2026-08-20 18:30."""
    global _next_reminder_id
    try:
        _start_saved_reminders()
        when_text=str(reminder_time).strip()
        repeat=str(repeat or "none").lower().strip()
        if repeat not in ("none","daily","weekly"): return "Repeat must be none, daily, or weekly."
        try: when=dt.datetime.fromisoformat(when_text)
        except ValueError: return "Use reminder time format YYYY-MM-DD HH:MM or YYYY-MM-DD HH:MM:SS."
        when_ts=when.timestamp()
        if when_ts<=time.time(): return "Reminder time must be in the future."
        with _reminder_lock:
            rid=_next_reminder_id; _next_reminder_id+=1
            _reminders[str(rid)]={"when":when_ts,"message":str(message),"repeat":repeat}
            if not _save_reminders(_reminders): return "Couldn't save reminder."
        _schedule_reminder_thread(rid,when_ts,str(message),repeat)
        return f"Reminder {rid} scheduled for {when.strftime('%Y-%m-%d %H:%M:%S')} ({repeat})."
    except Exception as e: return f"Couldn't schedule reminder: {e}"


def list_reminders():
    _start_saved_reminders()
    with _reminder_lock:
        if not _reminders: return "No scheduled reminders."
        lines=[]
        for rid,item in _reminders.items():
            when=dt.datetime.fromtimestamp(float(item["when"])).strftime('%Y-%m-%d %H:%M:%S')
            lines.append(f"Reminder {rid}: {when} - {item['message']} ({item.get('repeat','none')})")
        return "\n".join(lines)


def cancel_reminder(reminder_id):
    try:
        rid=str(int(reminder_id))
        with _reminder_lock:
            if rid not in _reminders: return f"Reminder {rid} was not found."
            del _reminders[rid]
            _save_reminders(_reminders)
        return f"Cancelled reminder {rid}."
    except Exception as e: return f"Couldn't cancel reminder: {e}"




# ============================================================
# AUTO SCROLL / PAGE NAVIGATION
# ============================================================

def auto_scroll(direction="down", pages=1, interval=0.35):
    """Scroll using keyboard PageUp/PageDown so no mouse control is required."""
    try:
        direction = str(direction).lower().strip()
        pages = max(1, min(int(pages), 50))
        interval = max(0.05, min(float(interval), 2.0))
        key = "pagedown" if direction in ("down", "next", "forward") else "pageup" if direction in ("up", "previous", "back") else None
        if key is None:
            return "Direction must be up or down."
        for _ in range(pages):
            pyautogui.press(key)
            time.sleep(interval)
        return f"Scrolled {direction} {pages} page(s)."
    except Exception as e:
        return f"Couldn't auto-scroll: {e}"


def scroll_to_end():
    try:
        pyautogui.press("end")
        return "Scrolled to the end of the current page or document."
    except Exception as e:
        return f"Couldn't scroll to end: {e}"


def scroll_to_top():
    try:
        pyautogui.press("home")
        return "Scrolled to the top of the current page or document."
    except Exception as e:
        return f"Couldn't scroll to top: {e}"

# ============================================================
# PERMANENT MEMORY
# ============================================================

_MEMORY_FILE=os.path.join(os.path.expanduser("~"), ".jarvis_memory.json")
_memory_lock=threading.Lock()


def _load_memory():
    try:
        if not os.path.exists(_MEMORY_FILE): return {}
        with open(_MEMORY_FILE,"r",encoding="utf-8") as f: data=json.load(f)
        return data if isinstance(data,dict) else {}
    except Exception: return {}


def _save_memory(memory):
    try:
        with open(_MEMORY_FILE,"w",encoding="utf-8") as f: json.dump(memory,f,indent=2,ensure_ascii=False)
        return True
    except Exception: return False


def remember(key,value):
    try:
        key=str(key).strip()
        if not key: return "Memory key is required."
        with _memory_lock:
            memory=_load_memory(); memory[key]=str(value)
            if not _save_memory(memory): return "Couldn't save memory."
        return f"Remembered: {key} = {value}"
    except Exception as e: return f"Couldn't save memory: {e}"


def recall_memory(key=None):
    try:
        with _memory_lock: memory=_load_memory()
        if not memory: return "J.A.R.V.I.S. has no saved memories."
        if key:
            key=str(key).strip()
            return f"Memory: {key} = {memory[key]}" if key in memory else f"I don't have a saved memory for '{key}'."
        return "Saved memories:\n"+"\n".join(f"{k} = {v}" for k,v in memory.items())
    except Exception as e: return f"Couldn't read memory: {e}"


def forget_memory(key):
    try:
        key=str(key).strip()
        with _memory_lock:
            memory=_load_memory()
            if key not in memory: return f"No saved memory named '{key}'."
            del memory[key]
            if not _save_memory(memory): return "Couldn't update memory."
        return f"Forgot memory: {key}"
    except Exception as e: return f"Couldn't forget memory: {e}"


def clear_memory():
    try:
        with _memory_lock:
            if os.path.exists(_MEMORY_FILE): os.remove(_MEMORY_FILE)
        return "All saved J.A.R.V.I.S. memory was cleared."
    except Exception as e: return f"Couldn't clear memory: {e}"


# Start persisted reminder workers when the tool module is loaded.
_start_saved_reminders()
