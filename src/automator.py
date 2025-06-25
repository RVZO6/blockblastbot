# src/automator.py

import pyautogui
import time
from . import config


class Automator:
    """Handles all mouse control actions based on calibrated data."""

    def __init__(self):
        self.calibration_data = config.CALIBRATION_DATA
        # Configure pyautogui for more reliable automation
        pyautogui.PAUSE = 0.05
        pyautogui.FAILSAFE = True

    def _get_mouse_pos_for_grid_cell(self, block_index, target_row, target_col):
        """
        Calculates the absolute mouse (x, y) position needed to place a block
        at a specific grid cell.
        """
        try:
            const = self.calibration_data[block_index]
        except KeyError:
            raise ValueError(
                f"No calibration data found for block index {block_index}."
            )

        anchor_x, anchor_y = const["anchor_pos"]

        # Apply the inverse formula: mouse_pos = (logical_pos - offset) / scale
        relative_mouse_x = (target_col - const["offset_x"]) / const["scale_x"]
        relative_mouse_y = (target_row - const["offset_y"]) / const["scale_y"]

        # Convert to absolute screen coordinates
        end_mouse_x = round(relative_mouse_x + anchor_x)
        end_mouse_y = round(relative_mouse_y + anchor_y)

        return (end_mouse_x, end_mouse_y)

    def execute_move(self, block_index, target_row, target_col):
        """
        Executes a full drag-and-drop sequence for a given block.

        Args:
            block_index (int): The index of the block to move (0, 1, or 2).
            target_row (int): The target grid row (0-7).
            target_col (int): The target grid column (0-7).
        """
        start_pos = self.calibration_data[block_index]["start_grab_pos"]
        end_pos = self._get_mouse_pos_for_grid_cell(block_index, target_row, target_col)

        print(
            f"  > Executing move for block {block_index + 1}: {start_pos} -> {end_pos}"
        )

        try:
            # Move to start position
            pyautogui.moveTo(start_pos[0], start_pos[1], duration=0.15)
            # Grab the block
            pyautogui.mouseDown()
            time.sleep(0.1)  # Brief pause to ensure grab is registered
            # Drag to end position
            pyautogui.moveTo(end_pos[0], end_pos[1], duration=0.3)
            time.sleep(0.1)
            # Release the block
            pyautogui.mouseUp()
        except Exception as e:
            print(f"An error occurred during pyautogui execution: {e}")
            # SAFETY: Always ensure the mouse is released
            pyautogui.mouseUp()
            raise
