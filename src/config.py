# config.py

# --- Configuration Constants ---

# Window and Capture
WINDOW_TITLE = "Pixel 7 Pro"

# Grid Analysis
GRID_TOP_LEFT = (112, 508)
GRID_CELL_SIZE = 86
GRID_EMPTY_COLOR_HEX = "#1F2245"
GRID_COLOR_TOLERANCE = 40

# Block Analysis
BLOCK_CELL_SIZE = 39
BLOCK_ROI_SIZE = 240  # Generous 200x200 pixel search area
BLOCK_CENTERS = [(229, 1410), (459, 1410), (689, 1410)]
BLOCK_BG_COLORS_HEX = ["#3C4F8E", "#303E80"]  # Normal and shadow backgrounds
BLOCK_COLOR_TOLERANCE = 35
