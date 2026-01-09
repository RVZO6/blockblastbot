# config.py

from typing import Final

# _NORMALIZED suffix values are relative to screen dimensions (1.0 = full width/height).
# This allows the script to adapt to different screen resolutions.

# Grid Properties
GRID_SIZE: Final[int] = 8
GRID_CELL_SIZE_NORMALIZED: Final[float] = 0.1102
GRID_LEFT_NORMALIZED: Final[float] = 0.0583
GRID_TOP_NORMALIZED: Final[float] = 0.2355
GRID_EMPTY_COLOR: Final[tuple[int, int, int]] = (31, 34, 69)  # #1F2245
GRID_COLOR_TOLERANCE: Final[int] = 40

# Block Properties
BLOCK_INDICES: Final[tuple[int, ...]] = (1, 2, 3)
BLOCK_CELL_SIZE_NORMALIZED: Final[float] = 0.05
BLOCK_COLOR_TOLERANCE: Final[int] = 35
BLOCK_ROI_RADIUS_NORMALIZED: Final[float] = 0.15

BLOCK_CENTERS_NORMALIZED: Final[tuple[tuple[float, float], ...]] = (
    (0.21, 0.756),  # Left
    (0.5, 0.756),  # Center
    (0.79, 0.756),  # Right
)

# Colors used to distinguish block shape from background
BLOCK_BACKGROUND_COLORS: Final[tuple[tuple[int, int, int], ...]] = (
    (60, 79, 142),  # #3C4F8E
    (48, 62, 128),  # #303E80
)

# Swipe Physics Model
# finger_swipe_delta = block_travel_delta / sensitivity
SWIPE_SENSITIVITY_X: Final[float] = 1.37

# Y sensitivity changes linearly with vertical start position: (slope * y) + intercept
SWIPE_Y_SENSITIVITY_SLOPE: Final[float] = 0.011
SWIPE_Y_SENSITIVITY_INTERCEPT: Final[float] = 0.028

# Timing & Delays (seconds)
DELAY_BETWEEN_SWIPES: Final[float] = 0.05
DELAY_BETWEEN_CYCLES: Final[float] = 0.85
RETRY_DELAY_NO_BLOCKS: Final[float] = 5.0
RETRY_DELAY_NO_SOLUTION: Final[float] = 5.0

# Swipe Duration (milliseconds)
SWIPE_BASE_DURATION_MS: Final[int] = 100
SWIPE_DURATION_PER_PIXEL: Final[float] = 0.3

# Pickup positions in grid units (row 8.0 is just below the grid)
PICKUP_ANCHOR_CENTER_COLS: Final[dict[int, float]] = {
    1: 1.5,
    2: 4.0,
    3: 6.5,
}
PICKUP_ANCHOR_ROW: Final[float] = 8.0
