"""Main script to solve and execute block puzzle."""

import src.vision as vision
import src.automation as automation
from src.solver import solve
from config import BLOCK_INDICES
import time


def main() -> None:
    """Main execution loop."""
    print("--- Block Redo Automation ---")
    print("This script will run in a loop, solving and executing puzzles.")

    try:
        if input("Press Enter to begin the loop, or Ctrl+C to cancel: ").strip() != "":
            print("\nExiting.")
            return
    except KeyboardInterrupt:
        print("\nExiting.")
        return

    try:
        while True:
            print("\n-------------------------")
            print("Capturing game state...")

            # Get current grid state
            current_grid = vision.grid()
            print("\nCurrent Grid:")
            for row in current_grid:
                print(row)

            # Get available blocks
            available_blocks = vision.blocks(list(BLOCK_INDICES))
            print(f"\nAvailable Blocks: {list(available_blocks.keys())}")
            if not available_blocks:
                print("\nNo blocks available! Retrying in 5 seconds...")
                time.sleep(5)
                continue

            # Solve for best placement
            print("\nSolving...")
            solution = solve(current_grid, available_blocks)

            if solution is None:
                print("No valid solution found! Retrying in 5 seconds...")
                time.sleep(5)
                continue

            print(f"\nSolution found! Lines cleared: {solution.lines_cleared}")
            print("Executing solution...")
            automation.execute_solution(solution, available_blocks)
            print("\nExecution complete.")

            print("Waiting for next cycle...")
            time.sleep(0.85)

    except KeyboardInterrupt:
        print("\nLoop stopped by user. Exiting.")


if __name__ == "__main__":
    main()
