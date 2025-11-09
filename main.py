"""Main script to solve and execute block puzzle."""

import src.vision as vision
import src.util as util
import src.automation as automation
from src.solver import solve
from config import BLOCK_INDICES


def main() -> None:
    """Main execution loop."""
    print("Capturing game state...")

    # Get current grid state
    current_grid = vision.grid()
    print("\nCurrent Grid:")
    for row in current_grid:
        print(row)

    # Get available blocks
    available_blocks = vision.blocks(list(BLOCK_INDICES))
    print(f"\nAvailable Blocks: {list(available_blocks.keys())}")
    for block_id, block_data in available_blocks.items():
        print(f"\nBlock {block_id}:")
        for row in block_data:
            print(row)

    if not available_blocks:
        print("\nNo blocks available!")
        return

    # Solve for best placement
    print("\nSolving...")
    solution = solve(current_grid, available_blocks)

    if solution is None:
        print("No valid solution found!")
        return

    print(f"\nSolution found! Lines cleared: {solution.lines_cleared}")
    print("\nPlacements:")
    for placement in solution.placements:
        print(
            f"  Block {placement.block_id} at row={placement.row}, col={placement.col}"
        )

    print("\nFinal Grid:")
    for row in solution.final_grid:
        print(row)

    print("\nReady to execute solution.")
    try:
        if input("Press Enter to execute swipes, or Ctrl+C to cancel: ").strip() == "":
            automation.execute_solution(solution, available_blocks)
            print("\nExecution complete.")
        else:
            print("\nExecution cancelled by user.")
    except KeyboardInterrupt:
        print("\nExecution cancelled by user.")


if __name__ == "__main__":
    main()
