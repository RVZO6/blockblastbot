"""
Main script for the Block Puzzle Automation tool.

This script orchestrates the vision, solver, and automation modules to play
the block puzzle game in a continuous loop.
"""

import time

import src.automation as automation
import src.vision as vision
from src.solver import solve
from config import (
    BLOCK_INDICES,
    DELAY_BETWEEN_CYCLES,
    RETRY_DELAY_NO_BLOCKS,
    RETRY_DELAY_NO_SOLUTION,
)


def _print_grid(grid: list[list[int]]) -> None:
    """Prints the 8x8 grid to the console for visualization."""
    print("Current Grid State:")
    for row in grid:
        row_str = " ".join(["■" if cell else "□" for cell in row])
        print(f"  {row_str}")


def main() -> None:
    """
    Defines the main execution loop for the automation tool.

    This function orchestrates the vision, solver, and automation modules
    to play the block puzzle game in a continuous loop. It handles user
    interaction for starting the process and gracefully exits on
    KeyboardInterrupt or unexpected errors.
    """
    print("--- Block Puzzle Automation ---")
    print("This script will run in a loop to solve and execute puzzle placements.")
    print("Press Ctrl+C at any time to stop.")

    try:
        input("\nPress Enter to begin...")
    except KeyboardInterrupt:
        print("\nExiting.")
        return

    try:
        cycle_count = 1
        while True:
            print(f"\n----- Cycle {cycle_count} -----")

            # 1. Vision: Capture the current state of the game.
            print("🔍 Capturing game state...")
            current_grid = vision.grid()
            _print_grid(current_grid)

            available_blocks = vision.blocks(list(BLOCK_INDICES))
            if not available_blocks:
                print(
                    f"\n⚠️ No blocks detected. Retrying in {RETRY_DELAY_NO_BLOCKS} seconds..."
                )
                time.sleep(RETRY_DELAY_NO_BLOCKS)
                continue
            print(f"  Detected Blocks: {list(available_blocks.keys())}")

            # 2. Solver: Find the optimal placement for the available blocks.
            print("🧠 Solving for optimal placement...")
            solution = solve(current_grid, available_blocks)

            if solution is None:
                print(
                    f"\n⚠️ No valid solution found. Retrying in {RETRY_DELAY_NO_SOLUTION} seconds..."
                )
                time.sleep(RETRY_DELAY_NO_SOLUTION)
                continue

            print(f"  Solution found! Lines to be cleared: {solution.lines_cleared}")

            # 3. Automation: Execute the solution by performing swipes.
            print("🤖 Executing solution...")
            automation.execute_solution(solution, available_blocks)
            print("  Execution complete.")

            cycle_count += 1
            print(f"\nWaiting for next cycle... ({DELAY_BETWEEN_CYCLES}s)")
            time.sleep(DELAY_BETWEEN_CYCLES)

    except KeyboardInterrupt:
        print("\n\nLoop stopped by user. Exiting.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        print("Exiting.")


if __name__ == "__main__":
    main()
