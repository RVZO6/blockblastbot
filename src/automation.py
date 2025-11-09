"""
Module for calculating and executing swipe automation.
"""

import time
from typing import cast

import src.util as util
from src.solver import Placement, Solution
import config


def _get_block_dims(block_shape: list[list[int]]) -> tuple[int, int]:
    """Get the width and height of a block in cells."""
    if not block_shape or not block_shape[0]:
        return 0, 0
    height = len(block_shape)
    width = len(block_shape[0])
    return width, height


def _get_start_anchor(
    block_id: int, block_shape: list[list[int]]
) -> tuple[float, float]:
    """
    Calculates the top-left anchor of a block in its "picked-up" state.

    Args:
        block_id: The block's original slot (1, 2, or 3).
        block_shape: The 2D list representing the block's shape.

    Returns:
        A tuple of (column, row) for the top-left anchor in grid units.
    """
    width, height = _get_block_dims(block_shape)

    # Calculate vertical position based on height
    # block is centered vertically on the bottom edge of the grid (row 8)
    start_row = 8.0 - (height / 2.0)

    # Calculate horizontal position based on width and block_id
    if block_id == 1:  # Left
        anchor_col_center = 1.5
    elif block_id == 2:  # Center
        anchor_col_center = 4.0
    else:  # Right
        anchor_col_center = 6.5

    start_col = anchor_col_center - (width / 2.0)

    return start_col, start_row


def _get_target_anchor(placement: Placement) -> tuple[int, int]:
    """
    Calculates the top-left anchor of the block's destination.

    Args:
        placement: The Placement object from the solver.

    Returns:
        A tuple of (column, row) for the target anchor in grid units.
    """
    return placement.col, placement.row


def _calculate_swipe_ratios(
    swipe_start_rel: tuple[float, float],
    block_travel_rel: tuple[float, float],
    block_start_y_rel: float,
) -> tuple[tuple[float, float], tuple[float, float]]:
    """
    Applies swipe physics to calculate the finger's swipe path.

    Args:
        swipe_start_rel: Relative (x, y) of the finger's start position.
        block_travel_rel: Relative (x, y) vector of the block's conceptual travel.
        block_start_y_rel: Relative y-position of the block's "picked-up" state.

    Returns:
        A tuple containing two (x, y) tuples for the swipe start and end
        in relative screen coordinates.
    """
    start_x_rel, start_y_rel = swipe_start_rel
    block_delta_x, block_delta_y = block_travel_rel

    # Calculate position-dependent gain for Y axis based on block's start pos
    y_sensitivity_factor = (
        config.NORMALIZED_Y_SLOPE * block_start_y_rel
    ) + config.BASE_Y_INTERCEPT_NORMALIZED
    if y_sensitivity_factor == 0:  # Avoid division by zero
        y_gain = 1.0
    else:
        y_gain = config.GRID_CELL_SIZE_REL / y_sensitivity_factor

    # X gain is constant
    x_gain = config.BASE_X_GAIN
    if x_gain == 0:
        x_gain = 1.0

    finger_delta_x = block_delta_x / x_gain
    finger_delta_y = block_delta_y / y_gain

    swipe_end_rel = (start_x_rel + finger_delta_x, start_y_rel + finger_delta_y)

    return swipe_start_rel, swipe_end_rel


def execute_solution(
    solution: Solution, available_blocks: dict[int, list[list[int]]]
) -> None:
    """
    Executes a series of swipes to place blocks according to the solution.

    Args:
        solution: The solution object from the solver.
        available_blocks: Dictionary mapping block_id to its shape.
    """
    print("Executing solution...")
    try:
        img = util.screenshot()
        screen_width, screen_height = img.width, img.height
    except Exception as e:
        print(f"Error getting screen dimensions: {e}")
        print("Cannot execute solution. Is `adb` connected and a device attached?")
        return

    for placement in solution.placements:
        block_id = placement.block_id
        block_shape = available_blocks.get(block_id)

        if not block_shape:
            print(f"Warning: Could not find shape for block_id {block_id}. Skipping.")
            continue

        # 1. Determine Swipe Start Point (finger's physical start)
        # This is the center of the block in its resting position.
        swipe_start_rel = config.BLOCK_CENTERS_REL[block_id - 1]

        # 2. Calculate the Block's Conceptual Travel Vector
        # 2a. Get block's conceptual start anchor ("picked-up" state) in grid units
        start_anchor_col, start_anchor_row = _get_start_anchor(block_id, block_shape)
        # 2b. Get block's target anchor in grid units
        target_anchor_col, target_anchor_row = _get_target_anchor(placement)
        # 2c. Convert grid units to relative screen coordinates
        block_start_x_rel = config.GRID_LEFT_REL + start_anchor_col * config.GRID_CELL_SIZE_REL
        block_start_y_rel = config.GRID_TOP_REL + start_anchor_row * config.GRID_CELL_SIZE_REL
        block_target_x_rel = config.GRID_LEFT_REL + target_anchor_col * config.GRID_CELL_SIZE_REL
        block_target_y_rel = config.GRID_TOP_REL + target_anchor_row * config.GRID_CELL_SIZE_REL
        # 2d. Calculate the block's conceptual travel vector
        block_travel_x_rel = block_target_x_rel - block_start_x_rel
        block_travel_y_rel = block_target_y_rel - block_start_y_rel

        # 3. Calculate the finger swipe path in relative coordinates
        swipe_start_rel, swipe_end_rel = _calculate_swipe_ratios(
            swipe_start_rel,
            (block_travel_x_rel, block_travel_y_rel),
            block_start_y_rel,
        )

        # 4. Convert to absolute pixel coordinates for swiping
        x1 = int(swipe_start_rel[0] * screen_width)
        y1 = int(swipe_start_rel[1] * screen_height)
        x2 = int(swipe_end_rel[0] * screen_width)
        y2 = int(swipe_end_rel[1] * screen_height)

        # 5. Execute swipe
        width, height = _get_block_dims(block_shape)
        print(
            f"  Swiping Block {block_id} ({width}x{height}) to ({placement.row}, {placement.col})..."
        )
        util.swipe(x1, y1, x2, y2)
        time.sleep(0.05)  # Pause briefly between swipes

