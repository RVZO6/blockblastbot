from dataclasses import dataclass
from copy import deepcopy
import itertools


@dataclass
class Placement:
    block_id: int
    row: int
    col: int


@dataclass
class Solution:
    placements: list[Placement]
    lines_cleared: int
    final_grid: list[list[int]]


def _is_valid_placement(
    grid: list[list[int]], block_shape: list[list[int]], row: int, col: int
) -> bool:
    block_height = len(block_shape)
    block_width = len(block_shape[0]) if block_shape else 0

    if row < 0 or col < 0 or row + block_height > 8 or col + block_width > 8:
        return False

    for row_offset in range(block_height):
        for col_offset in range(block_width):
            if block_shape[row_offset][col_offset] == 1:
                if grid[row + row_offset][col + col_offset] == 1:
                    return False

    return True


def _place_block(
    grid: list[list[int]], block_shape: list[list[int]], row: int, col: int
) -> list[list[int]]:
    new_grid = deepcopy(grid)
    block_height = len(block_shape)
    block_width = len(block_shape[0]) if block_shape else 0

    for row_offset in range(block_height):
        for col_offset in range(block_width):
            if block_shape[row_offset][col_offset] == 1:
                new_grid[row + row_offset][col + col_offset] = 1

    return new_grid


def _calculate_score_and_clear_lines(
    grid: list[list[int]],
) -> tuple[int, list[list[int]]]:
    new_grid = deepcopy(grid)
    lines_cleared = 0

    rows_to_clear = [
        row_idx
        for row_idx, row in enumerate(new_grid)
        if all(cell == 1 for cell in row)
    ]
    for row_idx in rows_to_clear:
        new_grid[row_idx] = [0] * 8
        lines_cleared += 1

    cols_to_clear = [
        col_idx
        for col_idx in range(8)
        if all(new_grid[r][col_idx] == 1 for r in range(8))
    ]
    for col_idx in cols_to_clear:
        for row_idx in range(8):
            new_grid[row_idx][col_idx] = 0
        lines_cleared += 1

    return lines_cleared, new_grid


def _solve_recursively(
    current_grid: list[list[int]],
    ordered_blocks: list[tuple[int, list[list[int]]]],
) -> tuple[int, list[Placement]] | None:
    if not ordered_blocks:
        final_score, _ = _calculate_score_and_clear_lines(current_grid)
        return final_score, []

    block_id, block_shape = ordered_blocks[0]
    remaining_blocks = ordered_blocks[1:]

    best_score_for_this_path = -1
    best_placements_for_this_path: list[Placement] | None = None

    block_height = len(block_shape)
    block_width = len(block_shape[0]) if block_shape else 0
    for r in range(8 - block_height + 1):
        for c in range(8 - block_width + 1):
            if _is_valid_placement(current_grid, block_shape, r, c):
                grid_after_placement = _place_block(current_grid, block_shape, r, c)
                score_from_this_move, grid_after_clear = (
                    _calculate_score_and_clear_lines(grid_after_placement)
                )

                future_result = _solve_recursively(grid_after_clear, remaining_blocks)

                if future_result is not None:
                    score_from_future_moves, future_placements = future_result
                    current_path_total_score = (
                        score_from_this_move + score_from_future_moves
                    )

                    if current_path_total_score > best_score_for_this_path:
                        best_score_for_this_path = current_path_total_score
                        best_placements_for_this_path = [
                            Placement(block_id, r, c)
                        ] + future_placements

    if best_placements_for_this_path is None:
        return None

    return best_score_for_this_path, best_placements_for_this_path


def solve(grid: list[list[int]], blocks: dict[int, list[list[int]]]) -> Solution | None:
    best_overall_solution: Solution | None = None
    max_overall_lines_cleared = -1

    block_ids = list(blocks.keys())

    for block_id_permutation in itertools.permutations(block_ids):
        ordered_blocks = [
            (block_id, blocks[block_id]) for block_id in block_id_permutation
        ]

        result = _solve_recursively(grid, ordered_blocks)

        if result is not None:
            current_lines_cleared, current_placements = result

            if current_lines_cleared > max_overall_lines_cleared:
                max_overall_lines_cleared = current_lines_cleared

                final_grid_state = deepcopy(grid)
                for placement in current_placements:
                    final_grid_state = _place_block(
                        final_grid_state,
                        blocks[placement.block_id],
                        placement.row,
                        placement.col,
                    )

                _, final_grid_after_clearing = _calculate_score_and_clear_lines(
                    final_grid_state
                )

                best_overall_solution = Solution(
                    placements=current_placements,
                    lines_cleared=max_overall_lines_cleared,
                    final_grid=final_grid_after_clearing,
                )

    return best_overall_solution
