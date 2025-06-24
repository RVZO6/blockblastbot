# capture.py
import subprocess
import sys
import tempfile
from PIL import Image
from Quartz import (
    CGWindowListCopyWindowInfo,
    kCGWindowListOptionOnScreenOnly,
    kCGNullWindowID,
)
from . import config


def _find_window_id(window_title):
    """Internal helper to find the window ID for a given title using Quartz."""
    window_list = CGWindowListCopyWindowInfo(
        kCGWindowListOptionOnScreenOnly, kCGNullWindowID
    )
    for window in window_list:
        if "kCGWindowName" in window and window["kCGWindowName"] == window_title:
            return window["kCGWindowNumber"]
    return None


def capture_window_as_pil():
    """
    Captures the specified window and returns it as a Pillow (PIL) Image object.

    Returns:
        PIL.Image.Image or None: An Image object in RGB format, or None if capture fails.
    """
    target_window_id = _find_window_id(config.WINDOW_TITLE)
    if not target_window_id:
        print(
            f"Error: Could not find window with title '{config.WINDOW_TITLE}'.",
            file=sys.stderr,
        )
        return None

    with tempfile.NamedTemporaryFile(suffix=".png") as temp_file:
        command = ["screencapture", "-l", str(target_window_id), temp_file.name]
        try:
            subprocess.run(command, check=True, capture_output=True)
            image = Image.open(temp_file.name)
            return image.convert(
                "RGB"
            )  # Convert to standard RGB to handle transparency
        except Exception as e:
            print(f"Error during screenshot: {e}", file=sys.stderr)
            return None
