GRID_CELL_SIZE_REL: float = 0.1102  # Relative to window width
GRID_EMPTY_COLOR: tuple[int, int, int] = (31, 34, 69)  # RGB for #1F2245
GRID_COLOR_TOLERANCE: int = 40

# Block configuration
BLOCK_CELL_SIZE_REL: float = 0.05  # Relative cell size for blocks (54/1080)
# Relative block centers (calculated on Pixel 7 Pro, adjusted for 3.43% top crop)
BLOCK_CENTERS_REL: tuple[tuple[float, float], ...] = (
    (0.21, 0.756),
    (0.5, 0.756),
    (0.79, 0.756),
)
BLOCK_BG_COLORS: tuple[tuple[int, int, int], ...] = (
    (60, 79, 142),  # RGB for #3C4F8E
    (48, 62, 128),  # RGB for #303E80
)
BLOCK_COLOR_TOLERANCE: int = 35
BLOCK_ROI_REL_RADIUS: float = (
    0.15  # Relative radius for block ROI (10% of window width)
)

# Data-driven parameters for swipe physics
NORMALIZED_Y_SLOPE: float = 0.011
BASE_X_GAIN: float = 1.37
BASE_Y_INTERCEPT_NORMALIZED: float = 0.028

# Grid size
GRID_SIZE: int = 8

# Block indices
BLOCK_INDICES: tuple[int, ...] = (1, 2, 3)

# Grid crop positions (adjusted for top crop)
GRID_LEFT_REL: float = 0.0583
GRID_TOP_REL: float = 0.2355
