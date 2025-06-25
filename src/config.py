# config.py

# --- Vision & Capture Configuration ---
WINDOW_TITLE = "Pixel 7 Pro"
GRID_TOP_LEFT = (112, 508)
GRID_CELL_SIZE = 86
GRID_EMPTY_COLOR_HEX = "#1F2245"
GRID_COLOR_TOLERANCE = 40
BLOCK_CELL_SIZE = 39
BLOCK_ROI_SIZE = 240
BLOCK_CENTERS = [(229, 1410), (459, 1410), (689, 1410)]
BLOCK_BG_COLORS_HEX = ["#3C4F8E", "#303E80"]
BLOCK_COLOR_TOLERANCE = 35

# --- Automation & Control Configuration ---
CALIBRATION_DATA = {
    # Block 0 (Corresponds to the first available block slot)
    0: {
        "anchor_pos": (441, 48),
        "start_grab_pos": (521, 714),
        "scale_x": 0.032761,
        "offset_x": -1.774507,
        # Adjusted scale_y to correct vertical overshoot. Increased from 0.032823.
        "scale_y": 0.03215,
        "offset_y": -14.362228,
    },
    # Block 1 (Corresponds to the second available block slot)
    1: {
        "anchor_pos": (441, 48),
        "start_grab_pos": (750, 714),  # <-- PLACEHOLDER
        "scale_x": 0.032761,
        "offset_x": -1.774507,
        "scale_y": 0.03315,  # Adjusted
        "offset_y": -14.362228,
    },
    # Block 2 (Corresponds to the third available block slot)
    2: {
        "anchor_pos": (441, 48),
        "start_grab_pos": (980, 714),  # <-- PLACEHOLDER
        "scale_x": 0.032761,
        "offset_x": -1.774507,
        "scale_y": 0.03315,  # Adjusted
        "offset_y": -14.362228,
    },
}
