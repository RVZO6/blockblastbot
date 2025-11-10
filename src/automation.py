"""
Module for calculating and executing swipe automation.
"""

import time

import src.device as device
from src.solver import Placement, Solution
import config


def _get_block_dimensions(block_shape: list[list[int]]) -> tuple[int, int]:
    """Gets the width and height of a block in cells."""
    if not block_shape or not block_shape[0]:
        return 0, 0
    height = len(block_shape)
    width = len(block_shape[0])
    return width, height


def _get_pickup_anchor_in_grid_units(
    block_id: int, block_shape: list[list[int]]
) -> tuple[float, float]:
    """
    Calculates the top-left anchor of a block in its conceptual "picked-up"
    state, measured in grid cell units.

    The "anchor" is the top-left corner of the block's bounding box.
    This position is relative to the game grid, assuming the block is
    hovering above the selection area.

    Args:
        block_id: The block's original slot (1, 2, or 3).
        block_shape: The 2D list representing the block's shape.

    Returns:
        A tuple of (column, row) for the top-left anchor in grid units
        (float values to allow for sub-cell precision).
    """
    width, height = _get_block_dimensions(block_shape)

    # The block is conceptually centered vertically on the bottom edge of the
    # grid (row 8) when picked up.
    pickup_row = 8.0 - (height / 2.0)

    # The horizontal position depends on which slot the block came from.
    # These values represent the center of the block's bounding box.
    if block_id == 1:  # Left slot
        anchor_center_col = 1.5
    elif block_id == 2:  # Center slot
        anchor_center_col = 4.0
    else:  # Right slot
        anchor_center_col = 6.5

    pickup_col = anchor_center_col - (width / 2.0)

    return pickup_col, pickup_row


def _get_target_anchor_in_grid_units(placement: Placement) -> tuple[int, int]:
    """
    Calculates the top-left anchor of the block's destination in grid units.

    This directly uses the row and column from the `Placement` object,
    as these represent the target top-left corner on the grid.

    Args:
        placement: The Placement object from the solver, containing the
                   target row and column.

    Returns:
        A tuple of (column, row) for the target anchor in integer grid units.
    """
    return placement.col, placement.row


def _calculate_swipe_path_normalized(
    finger_start_normalized: tuple[float, float],
    block_travel_vector_normalized: tuple[float, float],
    block_pickup_y_normalized: float,
) -> tuple[tuple[float, float], tuple[float, float]]:
    """
    Applies swipe physics to calculate the finger's actual swipe path
    based on the block's conceptual travel.

    This function takes into account the game's non-linear swipe sensitivity
    (especially for the Y-axis) to determine how far the finger needs to move
    on the screen to achieve the desired block movement.

    Args:
        finger_start_normalized: The normalized (x, y) coordinates of where
                                 the finger starts the swipe (typically the
                                 center of the block in the selection area).
        block_travel_vector_normalized: The (delta_x, delta_y) vector representing
                                        the block's conceptual movement from its
                                        picked-up state to its target position,
                                        in normalized screen coordinates.
        block_pickup_y_normalized: The normalized Y-coordinate of the block's
                                   conceptual "picked-up" position. This is
                                   used to adjust Y-axis swipe sensitivity.

    Returns:
        A tuple containing two (x, y) tuples: the normalized start and end
        coordinates for the finger's swipe on the screen.
    """
    start_x, start_y = finger_start_normalized
    block_delta_x, block_delta_y = block_travel_vector_normalized

    # Calculate Y-axis sensitivity based on the block's vertical start position.
    y_sensitivity_factor = (
        config.SWIPE_Y_SENSITIVITY_SLOPE * block_pickup_y_normalized
    ) + config.SWIPE_Y_SENSITIVITY_INTERCEPT
    if y_sensitivity_factor == 0:  # Avoid division by zero
        y_gain = 1.0
    else:
        y_gain = config.GRID_CELL_SIZE_NORMALIZED / y_sensitivity_factor

    # X-axis sensitivity is constant.
    x_gain = config.SWIPE_SENSITIVITY_X

    # The finger's swipe distance is the block's travel distance divided by sensitivity.
    finger_delta_x = block_delta_x / x_gain if x_gain != 0 else 0
    finger_delta_y = block_delta_y / y_gain if y_gain != 0 else 0

    finger_end_normalized = (start_x + finger_delta_x, start_y + finger_delta_y)

    return finger_start_normalized, finger_end_normalized


def execute_solution(
    solution: Solution, available_blocks: dict[int, list[list[int]]]
) -> None:
    """
    Executes a series of swipe gestures to place blocks on the grid
    according to a provided solution.

    This function iterates through each placement in the `solution`,
    calculates the necessary finger swipe path based on game physics,
    and then performs the swipe using ADB commands.

    Args:
        solution: The `Solution` object containing the optimal sequence
                  of block placements.
        available_blocks: A dictionary mapping block IDs to their 2D shapes,
                          representing the blocks currently available for placement.
    """
    print("Executing solution...")
    try:
        output = device.adb("shell", "wm", "size").decode("utf-8").strip()
        size_str = output.split(":")[1].strip()  # "1080x2340"
        screen_width, screen_height = map(int, size_str.split("x"))
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

        # 1. FINGER START: The finger starts at the center of the block's
        # resting position in the selection area.
        finger_start_normalized = config.BLOCK_CENTERS_NORMALIZED[block_id - 1]

        # 2. BLOCK TRAVEL: Calculate the block's conceptual travel vector from
        # its "picked-up" position to its final target on the grid.

        # 2a. Get the block's conceptual start anchor ("picked-up" state) in grid units.
        pickup_anchor_col, pickup_anchor_row = _get_pickup_anchor_in_grid_units(
            block_id, block_shape
        )
        # 2b. Get the block's target anchor in grid units.
        target_anchor_col, target_anchor_row = _get_target_anchor_in_grid_units(
            placement
        )

        # 2c. Convert grid unit anchors to normalized screen coordinates.
        block_pickup_x_norm = (
            config.GRID_LEFT_NORMALIZED
            + pickup_anchor_col * config.GRID_CELL_SIZE_NORMALIZED
        )
        block_pickup_y_norm = (
            config.GRID_TOP_NORMALIZED
            + pickup_anchor_row * config.GRID_CELL_SIZE_NORMALIZED
        )
        block_target_x_norm = (
            config.GRID_LEFT_NORMALIZED
            + target_anchor_col * config.GRID_CELL_SIZE_NORMALIZED
        )
        block_target_y_norm = (
            config.GRID_TOP_NORMALIZED
            + target_anchor_row * config.GRID_CELL_SIZE_NORMALIZED
        )

        # 2d. Calculate the block's conceptual travel vector in normalized coordinates.
        block_travel_x_norm = block_target_x_norm - block_pickup_x_norm
        block_travel_y_norm = block_target_y_norm - block_pickup_y_norm

        # 3. FINGER PATH: Calculate the finger's actual swipe path using the
        # block's travel vector and the swipe physics model.
        _finger_start, finger_end = _calculate_swipe_path_normalized(
            finger_start_normalized,
            (block_travel_x_norm, block_travel_y_norm),
            block_pickup_y_norm,
        )

        # 4. CONVERT TO PIXELS: Convert the normalized swipe coordinates to
        # absolute pixel coordinates for the swipe command.
        start_x_px = int(finger_start_normalized[0] * screen_width)
        start_y_px = int(finger_start_normalized[1] * screen_height)
        end_x_px = int(finger_end[0] * screen_width)
        end_y_px = int(finger_end[1] * screen_height)

        # 5. EXECUTE SWIPE
        width, height = _get_block_dimensions(block_shape)
        print(
            f"  Swiping Block {block_id} ({width}x{height}) to ({placement.row}, {placement.col})..."
        )
        _ = device.swipe(start_x_px, start_y_px, end_x_px, end_y_px)
        time.sleep(0.05)  # Pause briefly between swipes
