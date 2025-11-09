"""Vision module for grid and block detection."""

import math
from typing import cast

from PIL import Image

import src.util as util
from config import (
    BLOCK_BG_COLORS,
    BLOCK_CELL_SIZE_REL,
    BLOCK_CENTERS_REL,
    BLOCK_COLOR_TOLERANCE,
    BLOCK_INDICES,
    BLOCK_ROI_REL_RADIUS,
    GRID_CELL_SIZE_REL,
    GRID_EMPTY_COLOR,
    GRID_COLOR_TOLERANCE,
    GRID_LEFT_REL,
    GRID_SIZE,
    GRID_TOP_REL,
)


def color_distance(c1: tuple[int, int, int], c2: tuple[int, int, int]) -> float:
    """Calculate Euclidean distance between two RGB colors."""
    return math.sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2)


def grid() -> list[list[int]]:
    """
    Get the current grid state from screenshot.

    Returns:
        8x8 2D list representing occupied (1) and empty (0) cells
    """
    data: list[list[int]] = []
    img = util.screenshot()
    grid_img = img.crop(
        (
            int(img.width * GRID_LEFT_REL),
            int(img.height * GRID_TOP_REL),
            int(img.width * (GRID_LEFT_REL + GRID_CELL_SIZE_REL * GRID_SIZE)),
            int(img.height * GRID_TOP_REL + img.width * GRID_CELL_SIZE_REL * GRID_SIZE),
        )
    )
    cell_size = grid_img.width / GRID_SIZE

    for i in range(GRID_SIZE):
        row: list[int] = []
        for j in range(GRID_SIZE):
            # Calculate center point of cell
            center_x = int((j + 0.5) * cell_size)
            center_y = int((i + 0.5) * cell_size)

            # Get pixel color at center (RGBA format)
            pixel = cast(
                tuple[int, int, int, int], grid_img.getpixel((center_x, center_y))
            )
            rgb: tuple[int, int, int] = (pixel[0], pixel[1], pixel[2])

            # Check if it's close to background color
            if color_distance(rgb, GRID_EMPTY_COLOR) < GRID_COLOR_TOLERANCE:
                row.append(0)
            else:
                row.append(1)
        data.append(row)

    return data


def blocks(indices: list[int] | int) -> dict[int, list[list[int]]]:
    """
    Get the grid data for one or more selection blocks.

    Args:
        indices: Single block index (1, 2, or 3) or list of indices

    Returns:
        Dictionary mapping block index to its 2D grid data.
        Only includes blocks that were successfully detected.

    Raises:
        ValueError: If any index is not 1, 2, or 3
    """
    # Normalize input to list
    if isinstance(indices, int):
        indices = [indices]

    # Validate all indices
    for index in indices:
        if index not in BLOCK_INDICES:
            raise ValueError(f"Block index must be in {BLOCK_INDICES}, got {index}")

    # Take single screenshot for all blocks
    img = util.screenshot()

    result: dict[int, list[list[int]]] = {}

    for index in indices:
        block_data = _extract_block_from_image(img, index)
        if block_data is not None:
            result[index] = block_data

    return result


def _extract_block_from_image(img: Image.Image, index: int) -> list[list[int]] | None:
    """
    Extract block grid data from a screenshot image.

    Args:
        img: PIL Image of the screenshot
        index: Block index (1, 2, or 3)

    Returns:
        2D list representing the block's occupied cells (1) and empty cells (0),
        or None if no block is found at this position
    """

    # Get block center based on index
    center_rel = BLOCK_CENTERS_REL[index - 1]
    center_x = int(img.width * center_rel[0])
    center_y = int(img.height * center_rel[1])

    # Calculate ROI around block center
    roi_radius = int(img.width * BLOCK_ROI_REL_RADIUS)
    roi_left = max(0, center_x - roi_radius)
    roi_top = max(0, center_y - roi_radius)
    roi_right = min(img.width, center_x + roi_radius)
    roi_bottom = min(img.height, center_y + roi_radius)

    # Crop to ROI
    roi_img = img.crop((roi_left, roi_top, roi_right, roi_bottom))

    # Find bounding box of non-background pixels
    min_x, min_y = roi_img.width, roi_img.height
    max_x, max_y = 0, 0

    for y in range(roi_img.height):
        for x in range(roi_img.width):
            pixel = cast(tuple[int, int, int, int], roi_img.getpixel((x, y)))
            rgb: tuple[int, int, int] = (pixel[0], pixel[1], pixel[2])

            # Check if pixel is NOT background
            is_background = any(
                color_distance(rgb, bg_color) < BLOCK_COLOR_TOLERANCE
                for bg_color in BLOCK_BG_COLORS
            )

            if not is_background:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

    # Check if any non-background pixels were found
    if max_x == 0 and max_y == 0:
        # No block found at this position
        return None

    # Crop to bounding box
    block_img = roi_img.crop((min_x, min_y, max_x + 1, max_y + 1))

    # Determine block dimensions based on cell size
    cell_size = img.width * BLOCK_CELL_SIZE_REL
    cols = round(block_img.width / cell_size)
    rows = round(block_img.height / cell_size)

    # Sanity check - if dimensions are invalid, return None
    if cols <= 0 or rows <= 0:
        return None

    # Extract grid data
    data: list[list[int]] = []
    actual_cell_width = block_img.width / cols
    actual_cell_height = block_img.height / rows

    for i in range(rows):
        row: list[int] = []
        for j in range(cols):
            # Calculate center point of cell
            center_x_cell = int((j + 0.5) * actual_cell_width)
            center_y_cell = int((i + 0.5) * actual_cell_height)

            # Get pixel color at center
            pixel = cast(
                tuple[int, int, int, int],
                block_img.getpixel((center_x_cell, center_y_cell)),
            )
            rgb = (pixel[0], pixel[1], pixel[2])

            # Check if it's close to any background color
            is_background = any(
                color_distance(rgb, bg_color) < BLOCK_COLOR_TOLERANCE
                for bg_color in BLOCK_BG_COLORS
            )

            if is_background:
                row.append(0)
            else:
                row.append(1)
        data.append(row)

    return data
