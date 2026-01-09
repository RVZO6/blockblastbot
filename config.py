# config.py

from typing import Final

"""
Configuration parameters for the block puzzle automation tool.

All values with a `_NORMALIZED` suffix are relative to the screen dimensions,
where 1.0 corresponds to the full width or height of the screen. This allows
the script to adapt to different screen resolutions.
"""

# -----------------------------------------------------------------------------
# Grid Properties
# -----------------------------------------------------------------------------
GRID_SIZE: Final[int] = 8  # The grid is 8x8 cells.
GRID_CELL_SIZE_NORMALIZED: Final[float] = (
    0.1102  # Cell size as a fraction of screen width.
)

# The (x, y) position of the top-left corner of the grid, normalized.
GRID_LEFT_NORMALIZED: Final[float] = 0.0583
GRID_TOP_NORMALIZED: Final[float] = 0.2355

# The RGB color of an empty cell in the grid.
GRID_EMPTY_COLOR: Final[tuple[int, int, int]] = (31, 34, 69)  # #1F2245
# The tolerance for color matching when identifying empty cells.
GRID_COLOR_TOLERANCE: Final[int] = 40


# -----------------------------------------------------------------------------
# Block Properties
# -----------------------------------------------------------------------------
BLOCK_INDICES: Final[tuple[int, ...]] = (1, 2, 3)  # The three block slots.
BLOCK_CELL_SIZE_NORMALIZED: Final[float] = (
    0.05  # Block cell size as a fraction of screen width.
)
BLOCK_COLOR_TOLERANCE: Final[int] = 35  # Color tolerance for detecting block pixels.

# The radius of the Region of Interest (ROI) used to scan for a block,
# normalized to the screen width.
BLOCK_ROI_RADIUS_NORMALIZED: Final[float] = 0.15

# The normalized (x, y) coordinates of the center of each block's resting position.
# These values were determined empirically from a screenshot.
BLOCK_CENTERS_NORMALIZED: Final[tuple[tuple[float, float], ...]] = (
    (0.21, 0.756),  # Block 1 (left)
    (0.5, 0.756),  # Block 2 (center)
    (0.79, 0.756),  # Block 3 (right)
)

# The background colors of the block selection area. These are used to
# distinguish a block's shape from the background.
BLOCK_BACKGROUND_COLORS: Final[tuple[tuple[int, int, int], ...]] = (
    (60, 79, 142),  # #3C4F8E
    (48, 62, 128),  # #303E80
)


# -----------------------------------------------------------------------------
# Automation & Swipe Physics
# -----------------------------------------------------------------------------
# The relationship between the block's travel distance on the screen and the
# finger's swipe distance is not 1:1. We use a sensitivity model to calculate
# the required finger swipe to achieve the desired block movement.

# For the X-axis, the sensitivity is constant. A lower value means a longer
# swipe is needed for the same block movement (i.e., less sensitive).
# finger_swipe_delta_x = block_travel_delta_x / SWIPE_SENSITIVITY_X
SWIPE_SENSITIVITY_X: Final[float] = 1.37

# For the Y-axis, sensitivity changes linearly with the block's vertical start
# position. This accounts for the game's physics, where blocks picked up from
# lower on the screen require a different swipe length.
# The formula is:
# y_sensitivity = (slope * block_start_y) + intercept
# finger_swipe_delta_y = block_travel_delta_y / y_sensitivity
SWIPE_Y_SENSITIVITY_SLOPE: Final[float] = 0.011
SWIPE_Y_SENSITIVITY_INTERCEPT: Final[float] = 0.028


# -----------------------------------------------------------------------------
# Timing & Delays
# -----------------------------------------------------------------------------
# Delay between consecutive swipe operations (in seconds).
DELAY_BETWEEN_SWIPES: Final[float] = 0.05

# Delay between automation cycles (in seconds).
DELAY_BETWEEN_CYCLES: Final[float] = 0.85

# Delay to wait when no blocks are detected (in seconds) before retrying.
RETRY_DELAY_NO_BLOCKS: Final[float] = 5.0

# Delay to wait when no valid solution is found (in seconds) before retrying.
RETRY_DELAY_NO_SOLUTION: Final[float] = 5.0


# -----------------------------------------------------------------------------
# Swipe Duration Configuration
# -----------------------------------------------------------------------------
# Base duration for a swipe gesture (in milliseconds).
SWIPE_BASE_DURATION_MS: Final[int] = 100

# Additional milliseconds per pixel of swipe distance.
SWIPE_DURATION_PER_PIXEL: Final[float] = 0.3


# -----------------------------------------------------------------------------
# Pickup Anchor Positions (in grid units)
# -----------------------------------------------------------------------------
# When a block is "picked up" from the selection area, it's conceptually
# positioned below the grid. These values define where each block appears
# when picked up, measured in grid cell units.

# The horizontal center position of each block slot in grid units.
# Block 1 (left): center at column 1.5
# Block 2 (center): center at column 4.0
# Block 3 (right): center at column 6.5
PICKUP_ANCHOR_CENTER_COLS: Final[dict[int, float]] = {
    1: 1.5,
    2: 4.0,
    3: 6.5,
}

# The vertical position where blocks appear when picked up, measured in grid units.
# The grid has 8 rows (0-7), so row 8.0 is just below the grid.
PICKUP_ANCHOR_ROW: Final[float] = 8.0
