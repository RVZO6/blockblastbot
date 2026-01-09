# Project Overview

This project is a Python-based automation tool for a block puzzle game. It uses computer vision to analyze the game state from screenshots and then calculates the optimal placement of blocks to clear lines and maximize the score. The tool then automates the placement of the blocks by simulating swipe gestures on the screen.

The core logic is divided into three main components:

* **Vision (`src/vision.py`):** Captures and interprets the game state, including the main grid and the available blocks.
* **Solver (`src/solver.py`):** Determines the best possible placement for the available blocks by exhaustively searching all permutations.
* **Automation (`src/automation.py`):** Executes the solution by simulating swipe gestures on the device screen using the Android Debug Bridge (ADB).

The main entry point is `main.py`, which orchestrates the entire process in a continuous loop.

## Building and Running

This project requires Python 3.13+ and the Pillow library. It also requires the Android Debug Bridge (ADB) to be installed and configured to communicate with an Android device. The project's dependencies and virtual environment are managed using `uv` by Astral.

**Installation:**

1. **Install Python 3.13 or higher.**
2. **Install dependencies using uv:**

    ```bash
    uv sync
    ```

**Running the application:**

1. **Connect an Android device** with USB debugging enabled.
2. **Ensure ADB is running** and the device is recognized (`adb devices`).
3. **Run the main script:**

    ```bash
    python main.py
    ```

## Development Conventions

* The code is structured into modules with specific responsibilities (vision, solver, automation).
* Configuration parameters, such as screen coordinates and color values, are stored in `config.py`.
* The solver uses a brute-force approach to find the optimal solution, which may be computationally expensive but guarantees the best outcome for a given set of blocks.
* The automation relies on ADB for device interaction, which means it is primarily designed for Android devices.
