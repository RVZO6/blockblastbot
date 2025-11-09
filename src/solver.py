"""Solver for block placement optimization."""

from dataclasses import dataclass
from copy import deepcopy
import itertools


@dataclass
class Placement:
    """Represents a block placement on the grid."""

    block_id: int
    row: int
    col: int


@dataclass
class Solution:
    """Represents a solution with placements and score."""

    placements: list[Placement]
    lines_cleared: int
    final_grid: list[list[int]]


def _is_valid_placement(
    grid: list[list[int]], block_shape: list[list[int]], row: int, col: int
) -> bool:
    """
    Check if a block can be placed at the given position.

    Args:
        grid: Current grid state (0 for empty, 1 for occupied)
        block_shape: Block shape to place (0 for empty, 1 for piece)
        row: Starting row position
        col: Starting column position

    Returns:
        True if placement is valid, False otherwise
    """
    block_height = len(block_shape)
    block_width = len(block_shape[0]) if block_shape else 0

    # Check bounds
    if row < 0 or col < 0 or row + block_height > 8 or col + block_width > 8:
        return False

    # Check for collisions
    for r_offset in range(block_height):
        for c_offset in range(block_width):
            if block_shape[r_offset][c_offset] == 1:  # Block has a piece here
                if grid[row + r_offset][col + c_offset] == 1:  # Grid is occupied
                    return False

    return True


def _place_block(
    grid: list[list[int]], block_shape: list[list[int]], row: int, col: int
) -> list[list[int]]:
    """
    Place a block on the grid and return the new grid.

    Args:
        grid: Current grid state
        block_shape: Block shape to place
        row: Starting row position
        col: Starting column position

    Returns:
        New grid with block placed
    """
    new_grid = deepcopy(grid)

    for r_offset in range(len(block_shape)):
        for c_offset in range(len(block_shape[0])):
            if block_shape[r_offset][c_offset] == 1:
                new_grid[row + r_offset][col + c_offset] = 1

    return new_grid


def _calculate_score_and_clear_lines(
    grid: list[list[int]],
) -> tuple[int, list[list[int]]]:
    """
    Clear complete rows and columns from the grid and count them.

    Args:
        grid: Grid to clear lines from

    Returns:
        Tuple of (number of lines cleared, new grid with lines cleared)
    """
    new_grid = deepcopy(grid)
    lines_cleared = 0

    # Clear complete rows
    rows_to_clear = [r for r, row in enumerate(new_grid) if all(cell == 1 for cell in row)]
    for r in rows_to_clear:
        new_grid[r] = [0] * 8
        lines_cleared += 1

    # Clear complete columns
    cols_to_clear = [c for c in range(8) if all(new_grid[r][c] == 1 for r in range(8))]
    for c in cols_to_clear:
        for r in range(8):
            new_grid[r][c] = 0
        lines_cleared += 1

    return lines_cleared, new_grid


def _solve_recursively(
    current_grid: list[list[int]],
    ordered_blocks_with_ids: list[tuple[int, list[list[int]]]],
) -> tuple[int, list[Placement]] | None:
    """
    Recursively finds the best placements for an ordered list of blocks.

    Args:
        current_grid: The current state of the grid.
        ordered_blocks_with_ids: A list of (block_id, block_shape) tuples in a specific order.

    Returns:
        A tuple of (total_score, list_of_placements) or None if no valid placement
        for the current block is found.
    """
    if not ordered_blocks_with_ids:
        # All blocks placed, calculate final score and return
        final_score, _ = _calculate_score_and_clear_lines(current_grid)
        return final_score, []

    block_id, block_shape = ordered_blocks_with_ids[0]
    remaining_blocks = ordered_blocks_with_ids[1:]

    best_score_for_this_path = -1
    best_placements_for_this_path: list[Placement] | None = None

    # Try all possible positions for the current block
    for r in range(8 - len(block_shape) + 1):
        for c in range(8 - len(block_shape[0]) + 1):
            if _is_valid_placement(current_grid, block_shape, r, c):
                grid_after_placement = _place_block(current_grid, block_shape, r, c)
                score_from_this_move, grid_after_clear = _calculate_score_and_clear_lines(
                    grid_after_placement
                )

                # Recursively solve for the remaining blocks
                future_result = _solve_recursively(grid_after_clear, remaining_blocks)

                if future_result is not None:
                    score_from_future_moves, future_placements = future_result
                    current_path_total_score = score_from_this_move + score_from_future_moves

                    if current_path_total_score > best_score_for_this_path:
                        best_score_for_this_path = current_path_total_score
                        best_placements_for_this_path = [
                            Placement(block_id, r, c)
                        ] + future_placements

    if best_placements_for_this_path is None:
        return None  # No valid placement for the current block in this path

    return best_score_for_this_path, best_placements_for_this_path


def solve(grid: list[list[int]], blocks: dict[int, list[list[int]]]) -> Solution | None:
    """
    Find the best placement of blocks to maximize line clears.

    This function exhaustively checks every possible order (permutation) of the
    available blocks to find the sequence of placements that yields the highest
    score, ensuring all blocks are placed.
    """
    best_overall_solution: Solution | None = None
    max_overall_lines_cleared = -1

    block_ids = list(blocks.keys())
    
    # Iterate through all permutations of block placement order
    for p_ids in itertools.permutations(block_ids):
        ordered_blocks_with_ids = [(block_id, blocks[block_id]) for block_id in p_ids]

        # Find placements for this specific order
        result = _solve_recursively(grid, ordered_blocks_with_ids)

        if result is not None:
            current_lines_cleared, current_placements = result

            if current_lines_cleared > max_overall_lines_cleared:
                max_overall_lines_cleared = current_lines_cleared
                
                # Apply placements to get the final grid for this solution
                temp_grid = deepcopy(grid)
                for placement in current_placements:
                    temp_grid = _place_block(temp_grid, blocks[placement.block_id], placement.row, placement.col)
                
                _, final_grid_after_clearing = _calculate_score_and_clear_lines(temp_grid) # Get the grid after clearing
                
                best_overall_solution = Solution(
                    placements=current_placements,
                    lines_cleared=max_overall_lines_cleared,
                    final_grid=final_grid_after_clearing # Correctly assign the cleared grid
                )
    
    # The final_grid is already set correctly within the loop, no need for a second pass
    return best_overall_solution