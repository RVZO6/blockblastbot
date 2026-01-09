import subprocess
from PIL import Image
from io import BytesIO
import math
from config import SWIPE_BASE_DURATION_MS, SWIPE_DURATION_PER_PIXEL


def adb(*args: str) -> bytes:
    result = subprocess.run(["adb", *args], capture_output=True, check=True)
    return result.stdout


def swipe(x1: int, y1: int, x2: int, y2: int) -> None:
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    duration_ms = SWIPE_BASE_DURATION_MS + int(distance * SWIPE_DURATION_PER_PIXEL)
    adb(
        "shell",
        "input",
        "swipe",
        str(x1),
        str(y1),
        str(x2),
        str(y2),
        str(duration_ms),
    )


def screenshot() -> Image.Image:
    data = adb("shell", "screencap", "-p")
    return Image.open(BytesIO(data))
