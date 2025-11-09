"""Solver for block placement optimization."""

from dataclasses import dataclass
from copy import deepcopy
import itertools


@dataclass
class Placement:
    """Represents placing a single block at a specific grid location."""

    block_id: int
    row: int
    col: int


@dataclass
class Solution:
    """Represents a complete solution, including all placements and the outcome."""

    placements: list[Placement]
    lines_cleared: int
    final_grid: list[list[int]]


def _is_valid_placement(
    grid: list[list[int]], block_shape: list[list[int]], row: int, col: int
) -> bool:
    """
    Checks if a block can be placed at a given position without collision or
    going out of bounds.

    Args:
        grid: The current 8x8 grid state.
        block_shape: The 2D list representing the block's shape.
        row: The target top row for the placement.
        col: The target left column for the placement.

    Returns:
        True if the placement is valid, False otherwise.
    """
    block_height = len(block_shape)
    block_width = len(block_shape[0]) if block_shape else 0

    # Check if the block fits within the grid boundaries.
    if row < 0 or col < 0 or row + block_height > 8 or col + block_width > 8:
        return False

    # Check for collisions with existing blocks on the grid.
    for row_offset in range(block_height):
        for col_offset in range(block_width):
            if block_shape[row_offset][col_offset] == 1:  # Part of the block
                if grid[row + row_offset][col + col_offset] == 1:  # Grid is occupied
                    return False

    return True


def _place_block(
    grid: list[list[int]], block_shape: list[list[int]], row: int, col: int
) -> list[list[int]]:
    """
    Places a block on the grid. Does not check for validity.

    Args:
        grid: The current grid state.
        block_shape: The shape of the block to place.
        row: The target top row.
        col: The target left column.

    Returns:
        A new grid object with the block placed.
    """
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
    """
    Calculates the score from clearing lines and returns the resulting grid.

    Args:
        grid: The grid state after placing a block.

    Returns:
        A tuple containing:
        - The number of lines cleared (rows and columns).
        - The new grid with the completed lines removed.
    """
    new_grid = deepcopy(grid)
    lines_cleared = 0

    # Identify and clear complete rows
    rows_to_clear = [
        row_idx for row_idx, row in enumerate(new_grid) if all(cell == 1 for cell in row)
    ]
    for row_idx in rows_to_clear:
        new_grid[row_idx] = [0] * 8
        lines_cleared += 1

    # Identify and clear complete columns
    cols_to_clear = [
        col_idx for col_idx in range(8) if all(new_grid[r][col_idx] == 1 for r in range(8))
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
    """
    Recursively finds the best placement path for a fixed order of blocks.

    Args:
        current_grid: The current state of the grid.
        ordered_blocks: A list of (block_id, block_shape) tuples in a specific
                        order to be placed.

    Returns:
        A tuple of (total score, list of placements) for the best path found,
        or None if a valid placement could not be found for any block.
    """
    if not ordered_blocks:
        # Base case: All blocks have been placed.
        final_score, _ = _calculate_score_and_clear_lines(current_grid)
        return final_score, []

    block_id, block_shape = ordered_blocks[0]
    remaining_blocks = ordered_blocks[1:]

    best_score_for_this_path = -1
    best_placements_for_this_path: list[Placement] | None = None

    # Iterate through all possible positions for the current block.
    block_height = len(block_shape)
    block_width = len(block_shape[0]) if block_shape else 0
    for r in range(8 - block_height + 1):
        for c in range(8 - block_width + 1):
            if _is_valid_placement(current_grid, block_shape, r, c):
                # If valid, place the block and clear any lines.
                grid_after_placement = _place_block(current_grid, block_shape, r, c)
                score_from_this_move, grid_after_clear = (
                    _calculate_score_and_clear_lines(grid_after_placement)
                )

                # Recursively solve for the rest of the blocks.
                future_result = _solve_recursively(grid_after_clear, remaining_blocks)

                if future_result is not None:
                    score_from_future_moves, future_placements = future_result
                    current_path_total_score = (
                        score_from_this_move + score_from_future_moves
                    )

                    if current_path_total_score > best_score_for_this_path:
                        best_score_for_this_path = current_path_total_score
                        # Combine this placement with the best future placements.
                        best_placements_for_this_path = [
                            Placement(block_id, r, c)
                        ] + future_placements

    if best_placements_for_this_path is None:
        return None  # No valid placement path found from this state.

    return best_score_for_this_path, best_placements_for_this_path


def solve(
    grid: list[list[int]], blocks: dict[int, list[list[int]]]
) -> Solution | None:
    """
    Finds the optimal placement of blocks to maximize the number of cleared lines.

    This function exhaustively checks every possible order (permutation) of the
    available blocks to find the sequence of placements that yields the highest
    score.

    Args:
        grid: The current 8x8 grid state.
        blocks: A dictionary mapping available block IDs to their shapes.

    Returns:
        A Solution object representing the best possible outcome, or None if
        no solution allows for all blocks to be placed.
    """
    best_overall_solution: Solution | None = None
    max_overall_lines_cleared = -1

    block_ids = list(blocks.keys())

    # Iterate through all permutations of block placement order.
    for block_id_permutation in itertools.permutations(block_ids):
        ordered_blocks = [
            (block_id, blocks[block_id]) for block_id in block_id_permutation
        ]

        # Find the best placement path for this specific block order.
        result = _solve_recursively(grid, ordered_blocks)

        if result is not None:
            current_lines_cleared, current_placements = result

            if current_lines_cleared > max_overall_lines_cleared:
                max_overall_lines_cleared = current_lines_cleared

                # To build the final solution, apply the placements to the
                # original grid to get the final grid state.
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

