# vision.py

import math
import sys
from . import config


def _hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def _color_distance(rgb1, rgb2):
    return math.sqrt(sum([(a - b) ** 2 for a, b in zip(rgb1, rgb2)]))


def _analyze_cropped_block_image(cropped_image, bg_colors_rgb):
    cropped_width, cropped_height = cropped_image.size
    num_cols = round(cropped_width / config.BLOCK_CELL_SIZE)
    num_rows = round(cropped_height / config.BLOCK_CELL_SIZE)

    if num_rows == 0 or num_cols == 0:
        return None

    block_grid = [[" " for _ in range(num_cols)] for _ in range(num_rows)]
    for r in range(num_rows):
        for c in range(num_cols):
            sample_x = (c * config.BLOCK_CELL_SIZE) + (config.BLOCK_CELL_SIZE // 2)
            sample_y = (r * config.BLOCK_CELL_SIZE) + (config.BLOCK_CELL_SIZE // 2)
            try:
                pixel_color = cropped_image.getpixel((sample_x, sample_y))
                is_background = any(
                    _color_distance(pixel_color, bg) < config.BLOCK_COLOR_TOLERANCE
                    for bg in bg_colors_rgb
                )
                if not is_background:
                    block_grid[r][c] = "X"
            except IndexError:
                continue
    return block_grid


def analyze_grid_from_image(game_image):
    grid = [[" " for _ in range(8)] for _ in range(8)]
    offset_x, offset_y = config.GRID_TOP_LEFT
    empty_color_rgb = _hex_to_rgb(config.GRID_EMPTY_COLOR_HEX)

    for row in range(8):
        for col in range(8):
            x = offset_x + (col * config.GRID_CELL_SIZE) + (config.GRID_CELL_SIZE // 2)
            y = offset_y + (row * config.GRID_CELL_SIZE) + (config.GRID_CELL_SIZE // 2)
            try:
                pixel_color = game_image.getpixel((x, y))
                if (
                    _color_distance(pixel_color, empty_color_rgb)
                    > config.GRID_COLOR_TOLERANCE
                ):
                    grid[row][col] = "X"
            except IndexError:
                print(
                    f"Error: Grid analysis coordinates ({x}, {y}) out of bounds in screenshot.",
                    file=sys.stderr,
                )
                return None
    return grid


def analyze_available_blocks(game_image):
    detected_blocks = []
    bg_colors_rgb = [_hex_to_rgb(c) for c in config.BLOCK_BG_COLORS_HEX]

    for i, center_coord in enumerate(config.BLOCK_CENTERS):
        roi_half = config.BLOCK_ROI_SIZE // 2
        roi_x_start, roi_y_start = (
            center_coord[0] - roi_half,
            center_coord[1] - roi_half,
        )

        min_x, min_y = float("inf"), float("inf")
        max_x, max_y = float("-inf"), float("-inf")

        for x_offset in range(config.BLOCK_ROI_SIZE):
            for y_offset in range(config.BLOCK_ROI_SIZE):
                if x_offset in (0, config.BLOCK_ROI_SIZE - 1) or y_offset in (
                    0,
                    config.BLOCK_ROI_SIZE - 1,
                ):
                    continue
                abs_x, abs_y = roi_x_start + x_offset, roi_y_start + y_offset
                try:
                    pixel_color = game_image.getpixel((abs_x, abs_y))
                    is_background = any(
                        _color_distance(pixel_color, bg) < config.BLOCK_COLOR_TOLERANCE
                        for bg in bg_colors_rgb
                    )
                    if not is_background:
                        min_x, min_y = min(min_x, abs_x), min(min_y, abs_y)
                        max_x, max_y = max(max_x, abs_x), max(max_y, abs_y)
                except IndexError:
                    continue

        if min_x == float("inf"):
            detected_blocks.append(None)
            continue

        cropped_image = game_image.crop((min_x, min_y, max_x + 1, max_y + 1))
        block_grid = _analyze_cropped_block_image(cropped_image, bg_colors_rgb)
        detected_blocks.append(block_grid)
    return detected_blocks
