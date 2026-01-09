import time

import src.device as device
from src.solver import Placement, Solution
import config
from config import DELAY_BETWEEN_SWIPES, PICKUP_ANCHOR_CENTER_COLS, PICKUP_ANCHOR_ROW


def _get_block_dimensions(block_shape: list[list[int]]) -> tuple[int, int]:
    if not block_shape or not block_shape[0]:
        return 0, 0
    return len(block_shape[0]), len(block_shape)


def _get_pickup_anchor_in_grid_units(
    block_id: int, block_shape: list[list[int]]
) -> tuple[float, float]:
    width, height = _get_block_dimensions(block_shape)
    pickup_row = PICKUP_ANCHOR_ROW - (height / 2.0)
    anchor_center_col = PICKUP_ANCHOR_CENTER_COLS[block_id]
    return anchor_center_col - (width / 2.0), pickup_row


def _get_target_anchor_in_grid_units(placement: Placement) -> tuple[int, int]:
    return placement.col, placement.row


def _calculate_swipe_path_normalized(
    finger_start_normalized: tuple[float, float],
    block_travel_vector_normalized: tuple[float, float],
    block_pickup_y_normalized: float,
) -> tuple[tuple[float, float], tuple[float, float]]:
    start_x, start_y = finger_start_normalized
    block_delta_x, block_delta_y = block_travel_vector_normalized

    y_sensitivity_factor = (
        config.SWIPE_Y_SENSITIVITY_SLOPE * block_pickup_y_normalized
    ) + config.SWIPE_Y_SENSITIVITY_INTERCEPT

    y_gain = (
        config.GRID_CELL_SIZE_NORMALIZED / y_sensitivity_factor
        if y_sensitivity_factor != 0
        else 1.0
    )
    x_gain = config.SWIPE_SENSITIVITY_X

    finger_delta_x = block_delta_x / x_gain if x_gain != 0 else 0
    finger_delta_y = block_delta_y / y_gain if y_gain != 0 else 0

    return finger_start_normalized, (start_x + finger_delta_x, start_y + finger_delta_y)


def execute_solution(
    solution: Solution, available_blocks: dict[int, list[list[int]]]
) -> None:
    try:
        output = device.adb("shell", "wm", "size").decode("utf-8").strip()
        size_str = output.split(":")[1].strip()
        screen_width, screen_height = map(int, size_str.split("x"))
    except Exception as e:
        print(f"Error getting screen dimensions: {e}")
        return

    for placement in solution.placements:
        block_id = placement.block_id
        block_shape = available_blocks.get(block_id)

        if not block_shape:
            continue

        finger_start_normalized = config.BLOCK_CENTERS_NORMALIZED[block_id - 1]

        pickup_anchor_col, pickup_anchor_row = _get_pickup_anchor_in_grid_units(
            block_id, block_shape
        )
        target_anchor_col, target_anchor_row = _get_target_anchor_in_grid_units(
            placement
        )

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

        block_travel_x_norm = block_target_x_norm - block_pickup_x_norm
        block_travel_y_norm = block_target_y_norm - block_pickup_y_norm

        _, finger_end = _calculate_swipe_path_normalized(
            finger_start_normalized,
            (block_travel_x_norm, block_travel_y_norm),
            block_pickup_y_norm,
        )

        start_x_px = int(finger_start_normalized[0] * screen_width)
        start_y_px = int(finger_start_normalized[1] * screen_height)
        end_x_px = int(finger_end[0] * screen_width)
        end_y_px = int(finger_end[1] * screen_height)

        width, height = _get_block_dimensions(block_shape)
        print(
            f"  \033[93mSwiping Block {block_id}\033[0m ({width}x{height}) to (\033[1m{placement.row}, {placement.col}\033[0m)..."
        )
        device.swipe(start_x_px, start_y_px, end_x_px, end_y_px)
        time.sleep(DELAY_BETWEEN_SWIPES)
