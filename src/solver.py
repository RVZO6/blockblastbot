# solver.py

import itertools


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

    line_clears = len(rows_to_clear) + len(cols_to_clear)
    if line_clears == 0:
        return 0, [row[:] for row in board]

    new_board = [row[:] for row in board]
    for r in rows_to_clear:
        new_board[r] = [" "] * 8
    for c in cols_to_clear:
        for r in range(8):
            new_board[r][c] = " "
    return line_clears, new_board


def _solve_recursively(board, ordered_blocks):
    if not ordered_blocks:
        return 0, []

    current_block = ordered_blocks[0]
    remaining_blocks = ordered_blocks[1:]

    best_path_score = -1
    best_path_placements = None

    for r in range(9 - len(current_block)):
        for c in range(9 - len(current_block[0])):
            if not _is_valid_placement(board, current_block, (r, c)):
                continue

            board_after_place = _place_block(board, current_block, (r, c))
            score_from_this_move, board_after_clear = _calculate_score_and_clear_lines(
                board_after_place
            )
            score_from_future_moves, future_placements = _solve_recursively(
                board_after_clear, remaining_blocks
            )
            if future_placements is None:
                continue

            current_path_score = score_from_this_move + score_from_future_moves
            if current_path_score > best_path_score:
                best_path_score = current_path_score
                best_path_placements = [(r, c)] + future_placements

    if best_path_placements is None:
        return -1, None
    return best_path_score, best_path_placements


def find_best_move_sequence(board, blocks):
    best_result = {"order": None, "placements": None, "line_clears": -1}
    num_blocks = len(blocks)
    if num_blocks == 0:
        return None

    original_indices = list(range(num_blocks))
    for p_indices in itertools.permutations(original_indices):
        ordered_blocks = [blocks[i] for i in p_indices]
        total_score, placements_in_order = _solve_recursively(board, ordered_blocks)

        if total_score > best_result["line_clears"]:
            best_result["line_clears"] = total_score
            best_result["order"] = p_indices
            final_placements = [None] * num_blocks
            for i, original_idx in enumerate(p_indices):
                final_placements[original_idx] = placements_in_order[i]
            best_result["placements"] = final_placements

    return best_result if best_result["line_clears"] > -1 else None

