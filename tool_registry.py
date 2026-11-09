# tool_registry.py

from tools import (
    open_application, close_application,
    open_folder, open_named_folder, close_folder, create_folder, create_file,
    rename_folder, rename_file, move_folder, move_file, delete_file, delete_folder,
    type_text, press_key, hotkey,
    list_windows, focus_window, minimize_window, maximize_window, restore_window,
    close_window, switch_window,
    find_file, find_folder, find_application, find_large_files, find_recent_files,
    run_terminal_command,
    open_website, browser_search, read_webpage,
    gpu_temperature, system_status, running_processes, find_process, close_process,
    battery_status,
    media_control, volume_control,
    get_current_time, set_timer, list_timers, cancel_timer,
    notify_user, schedule_reminder, list_reminders, cancel_reminder,
    remember, recall_memory, forget_memory, clear_memory,
    auto_scroll, scroll_to_top, scroll_to_end,
)
from clipboard import copy_to_clipboard, read_clipboard, clear_clipboard


TOOL_FUNCTIONS = {
    "open_application": open_application, "close_application": close_application,
    "open_folder": open_folder, "open_named_folder": open_named_folder, "close_folder": close_folder,
    "create_folder": create_folder, "create_file": create_file, "rename_folder": rename_folder,
    "rename_file": rename_file, "move_folder": move_folder, "move_file": move_file,
    "delete_file": delete_file, "delete_folder": delete_folder,
    "type_text": type_text, "press_key": press_key, "hotkey": hotkey,
    "copy_to_clipboard": copy_to_clipboard, "read_clipboard": read_clipboard, "clear_clipboard": clear_clipboard,
    "list_windows": list_windows, "focus_window": focus_window, "minimize_window": minimize_window,
    "maximize_window": maximize_window, "restore_window": restore_window, "close_window": close_window,
    "switch_window": switch_window,
    "find_file": find_file, "find_folder": find_folder, "find_application": find_application,
    "find_large_files": find_large_files, "find_recent_files": find_recent_files,
    "run_terminal_command": run_terminal_command,
    "open_website": open_website, "browser_search": browser_search, "read_webpage": read_webpage,
    "gpu_temperature": gpu_temperature, "system_status": system_status, "running_processes": running_processes,
    "find_process": find_process, "close_process": close_process, "battery_status": battery_status,
    "media_control": media_control, "volume_control": volume_control,
    "get_current_time": get_current_time, "set_timer": set_timer, "list_timers": list_timers,
    "cancel_timer": cancel_timer, "notify_user": notify_user,
    "schedule_reminder": schedule_reminder, "list_reminders": list_reminders, "cancel_reminder": cancel_reminder,
    "remember": remember, "recall_memory": recall_memory, "forget_memory": forget_memory, "clear_memory": clear_memory,
    "auto_scroll": auto_scroll, "scroll_to_top": scroll_to_top, "scroll_to_end": scroll_to_end,
}


def obj(properties=None, required=None):
    result={"type":"object","properties":properties or {}}
    if required: result["required"]=required
    return result

def string(name, description): return {"type":"string","description":description}
def integer(name, description): return {"type":"integer","description":description}
def number(name, description): return {"type":"number","description":description}

def required_string(name, description): return obj({name:string(name,description)},[name])


TOOL_DECLARATIONS = [
    {"name":"open_application","description":"Open an installed Windows application.","parameters":required_string("application_name","Application name.")},
    {"name":"close_application","description":"Close a running application. Use only when explicitly requested.","parameters":required_string("application_name","Application name or executable name.")},
    {"name":"open_folder","description":"Open a folder by complete Windows path.","parameters":required_string("folder_path","Complete folder path.")},
    {"name":"open_named_folder","description":"Find and open a folder by name.","parameters":required_string("folder_name","Folder name.")},
    {"name":"close_folder","description":"Close File Explorer windows.","parameters":obj()},
    {"name":"create_folder","description":"Create a folder.","parameters":required_string("folder_path","Path of folder to create.")},
    {"name":"create_file","description":"Create an empty file.","parameters":required_string("file_path","Path of file to create.")},
    {"name":"rename_folder","description":"Rename a folder.","parameters":obj({"folder_path":string("folder_path","Current folder path."),"new_name":string("new_name","New folder name.")},["folder_path","new_name"])},
    {"name":"rename_file","description":"Rename a file.","parameters":obj({"file_path":string("file_path","Current file path."),"new_name":string("new_name","New file name.")},["file_path","new_name"])},
    {"name":"move_folder","description":"Move a folder to another folder.","parameters":obj({"folder_path":string("folder_path","Folder to move."),"destination_folder":string("destination_folder","Destination folder.")},["folder_path","destination_folder"])},
    {"name":"move_file","description":"Move a file to another folder.","parameters":obj({"file_path":string("file_path","File to move."),"destination_folder":string("destination_folder","Destination folder.")},["file_path","destination_folder"])},
    {"name":"delete_file","description":"Move a file to the Recycle Bin. Use only when explicitly requested.","parameters":required_string("file_path","File path.")},
    {"name":"delete_folder","description":"Move a folder to the Recycle Bin. Use only when explicitly requested.","parameters":required_string("folder_path","Folder path.")},
    {"name":"type_text","description":"Type text into the currently focused application using the keyboard.","parameters":required_string("text","Exact text to type.")},
    {"name":"press_key","description":"Press one keyboard key.","parameters":required_string("key","Key name.")},
    {"name":"hotkey","description":"Press a keyboard shortcut.","parameters":obj({"keys":{"type":"array","items":{"type":"string"},"description":"Keys, e.g. Ctrl+C."}},["keys"])},
    {"name":"copy_to_clipboard","description":"Copy exact text to the clipboard. Use when explicitly requested.","parameters":required_string("text","Text to copy.")},
    {"name":"read_clipboard","description":"Read current clipboard text when requested.","parameters":obj()},
    {"name":"clear_clipboard","description":"Clear clipboard when explicitly requested.","parameters":obj()},
    {"name":"list_windows","description":"List visible open windows.","parameters":obj()},
    {"name":"focus_window","description":"Bring a matching window to the foreground.","parameters":required_string("window_title","Full or partial window title.")},
    {"name":"minimize_window","description":"Minimize a matching window.","parameters":required_string("window_title","Window title.")},
    {"name":"maximize_window","description":"Maximize a matching window.","parameters":required_string("window_title","Window title.")},
    {"name":"restore_window","description":"Restore a matching window.","parameters":required_string("window_title","Window title.")},
    {"name":"close_window","description":"Close a matching window. Use only when requested.","parameters":required_string("window_title","Window title.")},
    {"name":"switch_window","description":"Switch to the next window using Alt+Tab.","parameters":obj()},
    {"name":"find_file","description":"Search for files by name, optionally by location and extension.","parameters":obj({"file_name":string("file_name","File name or part of name."),"location":string("location","Optional root folder."),"max_results":integer("max_results","Maximum results."),"extension":string("extension","Optional extension such as .py.")},["file_name"])},
    {"name":"find_folder","description":"Search for folders by name.","parameters":obj({"folder_name":string("folder_name","Folder name."),"location":string("location","Optional root folder."),"max_results":integer("max_results","Maximum results.")},["folder_name"])},
    {"name":"find_application","description":"Find installed Start Menu applications.","parameters":required_string("application_name","Application name.")},
    {"name":"find_large_files","description":"Find files larger than a size threshold.","parameters":obj({"location":string("location","Optional root folder."),"minimum_mb":number("minimum_mb","Minimum size in MB."),"max_results":integer("max_results","Maximum results.")})},
    {"name":"find_recent_files","description":"Find files modified within the specified number of hours.","parameters":obj({"location":string("location","Optional root folder."),"hours":number("hours","Lookback period in hours."),"max_results":integer("max_results","Maximum results.")})},
    {"name":"run_terminal_command","description":"Run a terminal command. Use only for a requested command or computer task.","parameters":required_string("command","Command to run.")},
    {"name":"open_website","description":"Open a website in the default browser.","parameters":required_string("url","Website URL.")},
    {"name":"browser_search","description":"Open a web search in the default browser.","parameters":required_string("query","Search query.")},
    {"name":"read_webpage","description":"Fetch and extract readable text from a webpage URL.","parameters":obj({"url":string("url","Webpage URL."),"max_characters":integer("max_characters","Maximum text to return.")},["url"])},
    {"name":"see_screen","description":"Capture and inspect the current screen.","parameters":obj()},
    {"name":"gpu_temperature","description":"Report NVIDIA GPU temperature when available.","parameters":obj()},
    {"name":"system_status","description":"Report CPU, RAM, disk, network, battery, uptime, and GPU telemetry. CPU temperature is intentionally not included.","parameters":obj()},
    {"name":"running_processes","description":"List running processes ranked by resource usage.","parameters":obj({"limit":integer("limit","Maximum processes to return.")})},
    {"name":"find_process","description":"Find a running process by name.","parameters":required_string("process_name","Process name or part of name.")},
    {"name":"close_process","description":"Terminate a running process. Use only when explicitly requested.","parameters":required_string("process_name_or_pid","Process name or PID.")},
    {"name":"battery_status","description":"Report battery percentage and charging state.","parameters":obj()},
    {"name":"media_control","description":"Control media playback with play, pause, next, previous, or mute.","parameters":required_string("action","Media action.")},
    {"name":"volume_control","description":"Change volume with up, down, or mute.","parameters":required_string("action","Volume action.")},
    {"name":"get_current_time","description":"Return current local date and time.","parameters":obj()},
    {"name":"set_timer","description":"Set a short-lived timer while JARVIS is running.","parameters":obj({"seconds":number("seconds","Timer duration in seconds."),"message":string("message","Notification message.")},["seconds"])},
    {"name":"list_timers","description":"List active timers.","parameters":obj()},
    {"name":"cancel_timer","description":"Cancel an active timer.","parameters":{"type":"object","properties":{"timer_id":integer("timer_id","Timer ID.")},"required":["timer_id"]}},
    {"name":"notify_user","description":"Display a desktop notification.","parameters":required_string("message","Notification message.")},
    {"name":"schedule_reminder","description":"Schedule a persistent one-time, daily, or weekly reminder. Time format YYYY-MM-DD HH:MM or YYYY-MM-DD HH:MM:SS.","parameters":obj({"reminder_time":string("reminder_time","Local date/time."),"message":string("message","Reminder message."),"repeat":string("repeat","none, daily, or weekly.")},["reminder_time","message"])},
    {"name":"list_reminders","description":"List persistent reminders.","parameters":obj()},
    {"name":"cancel_reminder","description":"Cancel a scheduled reminder.","parameters":{"type":"object","properties":{"reminder_id":integer("reminder_id","Reminder ID.")},"required":["reminder_id"]}},
    {"name":"remember","description":"Save a user-approved fact permanently. Do not invent memories.","parameters":obj({"key":string("key","Short memory name."),"value":string("value","Fact to remember.")},["key","value"])},
    {"name":"recall_memory","description":"Recall saved permanent memory. If no key is supplied, list saved memories.","parameters":obj({"key":string("key","Optional memory name.")})},
    {"name":"forget_memory","description":"Forget a specific saved memory when requested.","parameters":required_string("key","Memory name.")},
    {"name":"clear_memory","description":"Clear all permanent JARVIS memory. Use only when explicitly requested.","parameters":obj()},
    {"name":"auto_scroll","description":"Scroll the focused page or document using keyboard PageUp/PageDown. No mouse control is used.","parameters":obj({"direction":string("direction","up or down"),"pages":integer("pages","Number of pages, 1 to 50."),"interval":number("interval","Seconds between page movements.")},["direction"])},
    {"name":"scroll_to_top","description":"Scroll the focused page or document to the top using the Home key.","parameters":obj()},
    {"name":"scroll_to_end","description":"Scroll the focused page or document to the end using the End key.","parameters":obj()},
]


def get_tool_declarations():
    return TOOL_DECLARATIONS


def get_tool_function(tool_name):
    return TOOL_FUNCTIONS.get(tool_name)
