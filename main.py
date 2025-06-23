# main.py

import sys
from src.capture import capture_window_as_pil
from src.vision import analyze_grid_from_image, analyze_available_blocks
from src.solver import find_best_move_sequence


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
    print("--- Block Blast Bot: Prototype 1 ---")

    # 1. Capture the game window
    print("\n[1/4] Capturing game window...")
    game_image = capture_window_as_pil()
    if not game_image:
        sys.exit("Could not capture window. Exiting.")
    print("Capture successful.")

    # 2. Analyze the main grid
    print("\n[2/4] Analyzing 8x8 grid...")
    board_state = analyze_grid_from_image(game_image)
    if not board_state:
        sys.exit("Failed to analyze grid. Exiting.")
    print_grid(board_state, title="Detected Board State")

    # 3. Analyze the available blocks
    print("\n[3/4] Analyzing available blocks...")
    available_blocks = analyze_available_blocks(game_image)

    # Create a list of blocks that were successfully detected, along with their original index.
    indexed_blocks = [
        (i, block) for i, block in enumerate(available_blocks) if block and any(block)
    ]

    if not indexed_blocks:
        sys.exit("Error: Could not detect any blocks. Exiting.")

    # Prepare data for the solver
    valid_blocks = [block for i, block in indexed_blocks]
    block_names_map = {0: "Block 1", 1: "Block 2", 2: "Block 3"}

    print(f"Successfully detected {len(valid_blocks)}/3 blocks.")
    for i, (original_idx, block) in enumerate(indexed_blocks):
        print_grid(block, f"Detected Block (Original Position {original_idx + 1})")

    # 4. Find the best move sequence
    print(
        f"\n[4/4] Calculating optimal move sequence for {len(valid_blocks)} block(s)..."
    )
    result = find_best_move_sequence(board_state, valid_blocks)

    if not result:
        print("\n--- RESULT: No valid move sequence found. ---")
    else:
        print(
            f"\n--- RESULT: Optimal Sequence Found! (Total Score: {result['score']}) ---"
        )

        # This new loop prints the moves IN THE CORRECT ORDER.
        for i, original_block_idx in enumerate(result["order"]):
            # Get the name and placement for the block at this step in the sequence.
            block_name = block_names_map[original_block_idx]
            placement = result["placements"][original_block_idx]

            print(
                f"Move {i + 1}: Place '{block_name}' at (row={placement[0] + 1}, col={placement[1] + 1})"
            )
