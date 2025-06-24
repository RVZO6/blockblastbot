# solver.py

import itertools

# --- Internal Helper Functions (unchanged) ---


def _is_valid_placement(board, block, coords):
    top_r, top_c = coords
    if top_r + len(block) > 8 or top_c + len(block[0]) > 8:
        return False
    for r_offset, row_content in enumerate(block):
        for c_offset, cell in enumerate(row_content):
            if cell == "X" and board[top_r + r_offset][top_c + c_offset] == "X":
                return False
    return True


def _place_block(board, block, coords):
    new_board = [row[:] for row in board]
    top_r, top_c = coords
    for r_offset, row_content in enumerate(block):
        for c_offset, cell in enumerate(row_content):
            if cell == "X":
                new_board[top_r + r_offset][top_c + c_offset] = "X"
    return new_board


def _calculate_score_and_clear_lines(board):
    rows_to_clear = {
        r for r, row in enumerate(board) if all(cell == "X" for cell in row)
    }
    cols_to_clear = {c for c in range(8) if all(board[r][c] == "X" for r in range(8))}

    score = (len(rows_to_clear) + len(cols_to_clear)) * 10
    if score == 0:
        return 0, [row[:] for row in board]

    new_board = [row[:] for row in board]
    for r in rows_to_clear:
        new_board[r] = [" "] * 8
    for c in cols_to_clear:
        for r in range(8):
            new_board[r][c] = " "
    return score, new_board


# --- New, More Flexible Solver (with simplified recursion) ---


def _solve_recursively(board, ordered_blocks):
    """
    A recursive helper to find the best placement path for a given order of blocks.
    Returns the total score and a list of placements for this path.
    """
    # Base Case: If there are no more blocks to place, the sequence is done.
    if not ordered_blocks:
        return 0, []

    current_block = ordered_blocks[0]
    remaining_blocks = ordered_blocks[1:]

    best_path_score = -1
    best_path_placements = None

    # Try every valid placement for the current block.
    for r in range(9 - len(current_block)):
        for c in range(9 - len(current_block[0])):
            if not _is_valid_placement(board, current_block, (r, c)):
                continue

            # Place the block and calculate the score and new board state.
            board_after_place = _place_block(board, current_block, (r, c))
            score_from_this_move, board_after_clear = _calculate_score_and_clear_lines(
                board_after_place
            )

            # Recursively solve for the rest of the blocks on the new board.
            score_from_future_moves, future_placements = _solve_recursively(
                board_after_clear, remaining_blocks
            )

            # If the recursive call failed (couldn't place a subsequent block), this path is invalid.
            if future_placements is None:
                continue

            current_path_score = score_from_this_move + score_from_future_moves

            if current_path_score > best_path_score:
                best_path_score = current_path_score
                # Prepend the current move to the placements from the future moves.
                best_path_placements = [(r, c)] + future_placements

    # If best_path_placements is still None, it means no valid placement
    # for the current block allowed the rest of the sequence to complete.
    # Therefore, this entire path for the given block order is impossible.
    if best_path_placements is None:
        return -1, None

    return best_path_score, best_path_placements


def find_best_move_sequence(board, blocks):
    """
    Finds the optimal move sequence for a given list of blocks (1, 2, or 3).
    Returns a dictionary with the optimal placement order and coordinates.
    """
    best_result = {"order": None, "placements": None, "score": -1}
    num_blocks = len(blocks)

    if num_blocks == 0:
        return None

    original_indices = list(range(num_blocks))

    # Test every possible order of placing the blocks.
    for p_indices in itertools.permutations(original_indices):
        ordered_blocks = [blocks[i] for i in p_indices]

        total_score, placements_in_order = _solve_recursively(board, ordered_blocks)

        if total_score > best_result["score"]:
            best_result["score"] = total_score
            best_result["order"] = p_indices

            # Re-map the ordered placements back to their original block indices.
            final_placements = [None] * num_blocks
            for i, original_idx in enumerate(p_indices):
                final_placements[original_idx] = placements_in_order[i]
            best_result["placements"] = final_placements

    return best_result if best_result["score"] > -1 else None

