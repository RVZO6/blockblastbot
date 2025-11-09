import subprocess
from PIL import Image
from io import BytesIO


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
    """Swipe from (x1, y1) to (x2, y2) with 150ms duration"""
    return (
        adb("shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), "250")
        .decode("utf-8")
        .strip()
    )


def screenshot() -> Image.Image:
    """Take a screenshot and return as PIL Image"""
    data = adb("shell", "screencap", "-p")
    return Image.open(BytesIO(data))
