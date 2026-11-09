# vision.py

import io
from PIL import ImageGrab


def capture_screen():
    """Capture the primary display and return PNG bytes."""
    screenshot = ImageGrab.grab(all_screens=False).convert("RGB")
    image_bytes = io.BytesIO()
    screenshot.save(image_bytes, format="PNG")
    return image_bytes.getvalue()
