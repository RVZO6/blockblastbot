"""Vision module for grid and block detection."""

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


def color_distance(
    color1: tuple[int, int, int], color2: tuple[int, int, int]
) -> float:
    """Calculate Euclidean distance between two RGB colors."""
    return math.sqrt(
        (color1[0] - color2[0]) ** 2
        + (color1[1] - color2[1]) ** 2
        + (color1[2] - color2[2]) ** 2
    )


def grid() -> list[list[int]]:
    """
    Captures a screenshot and analyzes it to determine the current state
    of the game grid.

    Each cell in the 8x8 grid is identified as either empty (0) or occupied (1)
    based on its color.

    Returns:
        A 2D list (8x8) representing the grid, where 0 is an empty cell
        and 1 is an occupied cell.
    """
    grid_state: list[list[int]] = []
    screenshot_image = device.screenshot()

    # Define the grid's pixel boundaries
    grid_left_px = int(screenshot_image.width * GRID_LEFT_NORMALIZED)
    grid_top_px = int(screenshot_image.height * GRID_TOP_NORMALIZED)
    grid_width_px = int(screenshot_image.width * GRID_CELL_SIZE_NORMALIZED * GRID_SIZE)
    grid_height_px = int(
        screenshot_image.width * GRID_CELL_SIZE_NORMALIZED * GRID_SIZE
    )  # Note: width-based for square cells
    grid_right_px = grid_left_px + grid_width_px
    grid_bottom_px = grid_top_px + grid_height_px

    grid_image = screenshot_image.crop(
        (grid_left_px, grid_top_px, grid_right_px, grid_bottom_px)
    )
    cell_size_px = grid_image.width / GRID_SIZE

    for i in range(GRID_SIZE):
        row_state: list[int] = []
        for j in range(GRID_SIZE):
            # Calculate the center point of the cell to sample its color
            center_x_px = int((j + 0.5) * cell_size_px)
            center_y_px = int((i + 0.5) * cell_size_px)

            pixel_rgba = cast(
                tuple[int, int, int, int], grid_image.getpixel((center_x_px, center_y_px))
            )
            pixel_rgb = (pixel_rgba[0], pixel_rgba[1], pixel_rgba[2])

            # Check if the cell's color is close to the empty color
            if color_distance(pixel_rgb, GRID_EMPTY_COLOR) < GRID_COLOR_TOLERANCE:
                row_state.append(0)  # Empty
            else:
                row_state.append(1)  # Occupied
        grid_state.append(row_state)

    return grid_state


def blocks(indices: list[int] | int) -> dict[int, list[list[int]]]:
    """
    Detects and extracts the shapes of one or more blocks from the
    block selection area of the screen.

    Args:
        indices: A single block index (1, 2, or 3) or a list of indices
                 for the blocks to detect.

    Returns:
        A dictionary where keys are block indices (int) and values are
        their corresponding 2D shapes (list of lists of int). Only blocks
        that are successfully detected will be included.

    Raises:
        ValueError: If any provided index is not 1, 2, or 3.
    """
    if isinstance(indices, int):
        indices = [indices]

    if not all(index in BLOCK_INDICES for index in indices):
        raise ValueError(f"Block index must be in {BLOCK_INDICES}, got {indices}")

    # A single screenshot is used to detect all requested blocks for efficiency.
    screenshot_image = util.screenshot()

    detected_blocks: dict[int, list[list[int]]] = {}
    for index in indices:
        block_data = _extract_block_from_image(screenshot_image, index)
        if block_data:
            detected_blocks[index] = block_data

    return detected_blocks


def _extract_block_from_image(
    screenshot: Image.Image, index: int
) -> list[list[int]] | None:
    """
    Extracts a single block's shape data from a full screenshot.

    This function crops a Region of Interest (ROI) around the expected
    position of a block, then identifies the block's pixels within that
    ROI, and finally converts the pixel data into a 2D grid representing
    the block's shape.

    Args:
        screenshot: The PIL Image object of the entire screen.
        index: The slot index of the block (1, 2, or 3) to extract.

    Returns:
        A 2D list of integers (1s for block pixels, 0s for empty) representing
        the block's shape, or None if no block is detected at the specified
        position.
    """
    center_normalized = BLOCK_CENTERS_NORMALIZED[index - 1]
    center_x_px = int(screenshot.width * center_normalized[0])
    center_y_px = int(screenshot.height * center_normalized[1])

    # Define a Region of Interest (ROI) around the block's expected center
    roi_radius_px = int(screenshot.width * BLOCK_ROI_RADIUS_NORMALIZED)
    roi_left = max(0, center_x_px - roi_radius_px)
    roi_top = max(0, center_y_px - roi_radius_px)
    roi_right = min(screenshot.width, center_x_px + roi_radius_px)
    roi_bottom = min(screenshot.height, center_y_px + roi_radius_px)

    roi_image = screenshot.crop((roi_left, roi_top, roi_right, roi_bottom))

    # Find the bounding box of non-background pixels to isolate the block
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
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

    if not has_block_pixels:
        return None  # No block found at this position

    # Crop the ROI to the actual block shape
    block_image = roi_image.crop((min_x, min_y, max_x + 1, max_y + 1))

    # Determine block dimensions in cells
    cell_size_px = screenshot.width * BLOCK_CELL_SIZE_NORMALIZED
    cols = round(block_image.width / cell_size_px)
    rows = round(block_image.height / cell_size_px)

    if cols <= 0 or rows <= 0:
        return None  # Invalid dimensions

    # Sample the center of each cell to determine if it's part of the block
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
