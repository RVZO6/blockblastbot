import math
from typing import cast
from PIL import Image
import src.device as device
from config import (
    BLOCK_BACKGROUND_COLORS,
    BLOCK_CELL_SIZE_NORMALIZED,
    BLOCK_CENTERS_NORMALIZED,
    BLOCK_COLOR_TOLERANCE,
    BLOCK_INDICES,
    BLOCK_ROI_RADIUS_NORMALIZED,
    GRID_CELL_SIZE_NORMALIZED,
    GRID_EMPTY_COLOR,
    GRID_COLOR_TOLERANCE,
    GRID_LEFT_NORMALIZED,
    GRID_SIZE,
    GRID_TOP_NORMALIZED,
)


def color_distance(color1: tuple[int, int, int], color2: tuple[int, int, int]) -> float:
    return math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(color1, color2)))


def grid() -> list[list[int]]:
    grid_state: list[list[int]] = []
    screenshot_image = device.screenshot()

    grid_left_px = int(screenshot_image.width * GRID_LEFT_NORMALIZED)
    grid_top_px = int(screenshot_image.height * GRID_TOP_NORMALIZED)
    grid_width_px = int(screenshot_image.width * GRID_CELL_SIZE_NORMALIZED * GRID_SIZE)
    grid_height_px = grid_width_px

    grid_image = screenshot_image.crop(
        (
            grid_left_px,
            grid_top_px,
            grid_left_px + grid_width_px,
            grid_top_px + grid_height_px,
        )
    )
    cell_size_px = grid_image.width / GRID_SIZE

    for i in range(GRID_SIZE):
        row_state: list[int] = []
        for j in range(GRID_SIZE):
            center_x_px = int((j + 0.5) * cell_size_px)
            center_y_px = int((i + 0.5) * cell_size_px)

            pixel_rgba = cast(
                tuple[int, int, int, int],
                grid_image.getpixel((center_x_px, center_y_px)),
            )
            pixel_rgb = (pixel_rgba[0], pixel_rgba[1], pixel_rgba[2])

            if color_distance(pixel_rgb, GRID_EMPTY_COLOR) < GRID_COLOR_TOLERANCE:
                row_state.append(0)
            else:
                row_state.append(1)
        grid_state.append(row_state)

    return grid_state


def blocks(indices: list[int] | int) -> dict[int, list[list[int]]]:
    if isinstance(indices, int):
        indices = [indices]

    if not all(index in BLOCK_INDICES for index in indices):
        raise ValueError(f"Block index must be in {BLOCK_INDICES}, got {indices}")

    screenshot_image = device.screenshot()
    detected_blocks: dict[int, list[list[int]]] = {}
    for index in indices:
        block_data = _extract_block_from_image(screenshot_image, index)
        if block_data:
            detected_blocks[index] = block_data

    return detected_blocks


def _extract_block_from_image(
    screenshot: Image.Image, index: int
) -> list[list[int]] | None:
    center_normalized = BLOCK_CENTERS_NORMALIZED[index - 1]
    center_x_px = int(screenshot.width * center_normalized[0])
    center_y_px = int(screenshot.height * center_normalized[1])

    roi_radius_px = int(screenshot.width * BLOCK_ROI_RADIUS_NORMALIZED)
    roi_left = max(0, center_x_px - roi_radius_px)
    roi_top = max(0, center_y_px - roi_radius_px)
    roi_right = min(screenshot.width, center_x_px + roi_radius_px)
    roi_bottom = min(screenshot.height, center_y_px + roi_radius_px)

    roi_image = screenshot.crop((roi_left, roi_top, roi_right, roi_bottom))

    min_x, min_y = roi_image.width, roi_image.height
    max_x, max_y = 0, 0
    has_block_pixels = False

    for y in range(roi_image.height):
        for x in range(roi_image.width):
            pixel_rgba = cast(tuple[int, int, int, int], roi_image.getpixel((x, y)))
            pixel_rgb = (pixel_rgba[0], pixel_rgba[1], pixel_rgba[2])

            is_background = any(
                color_distance(pixel_rgb, bg_color) < BLOCK_COLOR_TOLERANCE
                for bg_color in BLOCK_BACKGROUND_COLORS
            )

            if not is_background:
                has_block_pixels = True
                min_x, min_y = min(min_x, x), min(min_y, y)
                max_x, max_y = max(max_x, x), max(max_y, y)

    if not has_block_pixels:
        return None

    block_image = roi_image.crop((min_x, min_y, max_x + 1, max_y + 1))
    cell_size_px = screenshot.width * BLOCK_CELL_SIZE_NORMALIZED
    cols = round(block_image.width / cell_size_px)
    rows = round(block_image.height / cell_size_px)

    if cols <= 0 or rows <= 0:
        return None

    block_shape: list[list[int]] = []
    cell_width_px = block_image.width / cols
    cell_height_px = block_image.height / rows

    for i in range(rows):
        row_shape: list[int] = []
        for j in range(cols):
            center_x_cell = int((j + 0.5) * cell_width_px)
            center_y_cell = int((i + 0.5) * cell_height_px)

            pixel_rgba = cast(
                tuple[int, int, int, int],
                block_image.getpixel((center_x_cell, center_y_cell)),
            )
            pixel_rgb = (pixel_rgba[0], pixel_rgba[1], pixel_rgba[2])

            is_background = any(
                color_distance(pixel_rgb, bg_color) < BLOCK_COLOR_TOLERANCE
                for bg_color in BLOCK_BACKGROUND_COLORS
            )
            row_shape.append(0 if is_background else 1)
        block_shape.append(row_shape)

    return block_shape
