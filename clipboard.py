# clipboard.py

import pyperclip


def copy_to_clipboard(text):
    """Copy text to the Windows clipboard."""
    try:
        if text is None:
            return "Text is required."
        pyperclip.copy(str(text))
        return "Text copied to clipboard."
    except Exception as e:
        return f"Couldn't copy to clipboard: {e}"


def read_clipboard():
    """Read text currently stored in the Windows clipboard."""
    try:
        text = pyperclip.paste()
        if not text:
            return "Clipboard is empty."
        return f"Clipboard contents: {text}"
    except Exception as e:
        return f"Couldn't read clipboard: {e}"


def clear_clipboard():
    """Clear the Windows clipboard."""
    try:
        pyperclip.copy("")
        return "Clipboard cleared."
    except Exception as e:
        return f"Couldn't clear clipboard: {e}"
