# Block Puzzle Automation Tool

## Description
This project is a Python-based automation tool designed for a block puzzle game. It leverages computer vision to analyze the game state from screenshots, calculates the optimal placement of blocks to clear lines and maximize scores, and then automates the block placement by simulating swipe gestures on an Android device.

The core logic is divided into three main components:
*   **Vision (`src/vision.py`):** Responsible for capturing and interpreting the game state, including the main grid and available blocks.
*   **Solver (`src/solver.py`):** Determines the best possible placement for available blocks by exhaustively searching all permutations, aiming for optimal line clearing.
*   **Automation (`src/automation.py`):** Executes the calculated solution by simulating swipe gestures on the device screen using the Android Debug Bridge (ADB).

The `main.py` script orchestrates this entire process in a continuous loop.

## Methodology
The tool employs a modular design, separating concerns into distinct Python modules. Configuration parameters, such as screen coordinates and color values, are centralized in `config.py`. The solver utilizes a brute-force approach to guarantee the best possible outcome for a given set of blocks, though this can be computationally intensive. Device interaction is handled via ADB, making the tool primarily compatible with Android devices.

## Dependencies
*   **Python:** Version 3.13 or higher.
*   **Pillow:** Python Imaging Library (PIL Fork) for image processing.
*   **Android Debug Bridge (ADB):** Required for device communication and interaction (screenshots, swipes).
*   **uv:** Used for managing Python dependencies and virtual environments.

## Installation
1.  **Install Python 3.13 or higher.**
2.  **Install `uv`** if you haven't already (e.g., `pip install uv`).
3.  **Install project dependencies:**
    ```bash
    uv sync
    ```
4.  **Ensure ADB is installed and configured** on your system to communicate with your Android device.

## Usage
1.  **Connect an Android device** to your computer with USB debugging enabled.
2.  **Verify ADB connection:** Ensure your device is recognized by ADB (run `adb devices`).
3.  **Run the main script:**
    ```bash
    python main.py
    ```
    The script will prompt you to press Enter to begin and will run in a continuous loop until interrupted (e.g., by `Ctrl+C`).
