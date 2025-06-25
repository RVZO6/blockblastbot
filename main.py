# main.py

import sys
import time
from src.capture import capture_window_as_pil
from src.vision import analyze_grid_from_image, analyze_available_blocks
from src.solver import find_best_move_sequence
from src.automator import Automator  # <-- IMPORT THE NEW CLASS


def print_grid(grid, title=""):
    """A helper function to print grids and blocks for verification."""
    if not grid or not any(grid):
        print(f"--- {title}: (Empty or invalid) ---")
        return
    if title:
        print(f"--- {title} ---")
    max_cols = max(len(row) for row in grid)
    for row in grid:
        padded_row = row + [" "] * (max_cols - len(row))
        printable_row = [cell if cell == "X" else "." for cell in padded_row]
        print(" ".join(printable_row))
    print("-" * (len(title) + 6 if title else 6))


if __name__ == "__main__":
    print("--- Block Blast Bot: Vision, Solver & Automation ---")

    # 1. Capture and Analyze
    print("\n[1/3] Capturing and analyzing game state...")
    game_image = capture_window_as_pil()
    if not game_image:
        sys.exit("Could not capture window. Exiting.")

    board_state = analyze_grid_from_image(game_image)
    if not board_state:
        sys.exit("Failed to analyze grid. Exiting.")
    print_grid(board_state, title="Detected Board State")

    available_blocks = analyze_available_blocks(game_image)
    indexed_blocks = [
        (i, block) for i, block in enumerate(available_blocks) if block and any(block)
    ]
    if not indexed_blocks:
        sys.exit("Error: Could not detect any blocks. Exiting.")

    valid_blocks = [block for i, block in indexed_blocks]
    block_names_map = {0: "Block 1", 1: "Block 2", 2: "Block 3"}
    for i, (original_idx, block) in enumerate(indexed_blocks):
        print_grid(block, f"Detected Block (Original Position {original_idx + 1})")

    # 2. Find the best move sequence
    print(
        f"\n[2/3] Calculating optimal move sequence for {len(valid_blocks)} block(s)..."
    )
    result = find_best_move_sequence(board_state, valid_blocks)

    if not result:
        print("\n--- RESULT: No valid move sequence found. ---")
        sys.exit()

    print(
        f"\n--- RESULT: Optimal Sequence Found! (Line Clears: {result['line_clears']}) ---"
    )
    for i, original_block_idx in enumerate(result["order"]):
        block_name = block_names_map[original_block_idx]
        placement = result["placements"][original_block_idx]
        print(
            f"Move {i + 1}: Place '{block_name}' at (row={placement[0] + 1}, col={placement[1] + 1})"
        )

    # 3. Execute the moves using the Automator
    print("\n[3/3] Executing automated moves...")
    try:
        automator = Automator()
        # Give user a moment to switch to the game window
        print("Starting automation in 3...")
        time.sleep(1)
        print("2...")
        time.sleep(1)
        print("1...")
        time.sleep(1)

        for i, original_block_idx in enumerate(result["order"]):
            placement = result["placements"][original_block_idx]
            print(f"\nExecuting Move {i + 1}...")
            automator.execute_move(
                block_index=original_block_idx,
                target_row=placement[0],
                target_col=placement[1],
            )
            # Wait for game animations (line clear, etc.) to complete
            time.sleep(0.5)

        print("\n--- All moves executed successfully! ---")

    except Exception as e:
        sys.exit(f"\nAn error occurred during automation: {e}")

