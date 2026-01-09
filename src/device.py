import subprocess
from PIL import Image
from io import BytesIO
import math

from config import SWIPE_BASE_DURATION_MS, SWIPE_DURATION_PER_PIXEL


def adb(*args: str) -> bytes:
    """
    Execute an ADB command and return raw output as bytes.

    Args:
        *args: ADB command arguments (e.g., 'devices', 'shell', 'ls')

    Returns:
        Command output as bytes

    Raises:
        subprocess.CalledProcessError: If command fails
    """
    result = subprocess.run(["adb", *args], capture_output=True, check=True)
    return result.stdout


def swipe(x1: int, y1: int, x2: int, y2: int) -> str:
    """
    Simulates a swipe gesture on the device screen.

    The duration of the swipe is calculated based on the distance between
    the start and end points.

    Args:
        x1: The starting X-coordinate in pixels.
        y1: The starting Y-coordinate in pixels.
        x2: The ending X-coordinate in pixels.
        y2: The ending Y-coordinate in pixels.

    Returns:
        The raw output from the ADB command as a string.
    """
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    duration_ms = SWIPE_BASE_DURATION_MS + int(distance * SWIPE_DURATION_PER_PIXEL)
    return (
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
        .decode("utf-8")
        .strip()
    )


def screenshot() -> Image.Image:
    """Take a screenshot and return as PIL Image.

    Returns:
        A PIL Image object representing the current screen content.
    """
    data = adb("shell", "screencap", "-p")
    return Image.open(BytesIO(data))
