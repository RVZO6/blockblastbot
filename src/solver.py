"""Solver for block placement optimization."""

from dataclasses import dataclass
from copy import deepcopy


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


def can_place_block(
    grid: list[list[int]], block: list[list[int]], row: int, col: int
) -> bool:
    """
    Check if a block can be placed at the given position.

    Args:
        grid: Current grid state
        block: Block shape to place
        row: Starting row position
        col: Starting column position

    Returns:
        True if placement is valid, False otherwise
    """
    block_height = len(block)
    block_width = len(block[0]) if block else 0

    # Check bounds
    if row + block_height > len(grid) or col + block_width > len(grid[0]):
        return False

    # Check for collisions
    for i in range(block_height):
        for j in range(block_width):
            if block[i][j] == 1:  # Block has a piece here
                if grid[row + i][col + j] == 1:  # Grid is occupied
                    return False

    return True


def place_block(
    grid: list[list[int]], block: list[list[int]], row: int, col: int
) -> list[list[int]]:
    """
    Place a block on the grid and return the new grid.

    Args:
        grid: Current grid state
        block: Block shape to place
        row: Starting row position
        col: Starting column position

    Returns:
        New grid with block placed
    """
    new_grid = deepcopy(grid)

    for i in range(len(block)):
        for j in range(len(block[0])):
            if block[i][j] == 1:
                new_grid[row + i][col + j] = 1

    return new_grid


def clear_lines(grid: list[list[int]]) -> tuple[list[list[int]], int]:
    """
    Clear complete rows and columns from the grid and count them.

    Args:
        grid: Grid to clear lines from

    Returns:
        Tuple of (new grid with lines cleared, number of lines cleared)
    """
    new_grid = deepcopy(grid)
    lines_cleared = 0

    # Clear complete rows
    for i in range(len(new_grid)):
        if all(cell == 1 for cell in new_grid[i]):
            new_grid[i] = [0] * len(new_grid[i])
            lines_cleared += 1

    # Clear complete columns
    for j in range(len(new_grid[0])):
        if all(new_grid[i][j] == 1 for i in range(len(new_grid))):
            for i in range(len(new_grid)):
                new_grid[i][j] = 0
            lines_cleared += 1

    return new_grid, lines_cleared


def generate_placements(
    grid: list[list[int]],
    blocks: dict[int, list[list[int]]],
    current_placements: list[Placement] | None = None,
) -> list[tuple[list[Placement], list[list[int]], int]]:
    """
    Generate all possible placements of remaining blocks.

    Args:
        grid: Current grid state
        blocks: Dictionary of remaining blocks to place
        current_placements: List of placements made so far

    Returns:
        List of (placements, final_grid, lines_cleared) tuples
    """
    if current_placements is None:
        current_placements = []

    if not blocks:
        # No more blocks to place
        cleared_grid, lines = clear_lines(grid)
        return [(current_placements, cleared_grid, lines)]

    all_solutions: list[tuple[list[Placement], list[list[int]], int]] = []

    # Try placing each remaining block
    for block_id, block in blocks.items():
        remaining_blocks = {k: v for k, v in blocks.items() if k != block_id}

        # Try all positions
        for row in range(len(grid)):
            for col in range(len(grid[0])):
                if can_place_block(grid, block, row, col):
                    new_grid = place_block(grid, block, row, col)
                    new_placements = current_placements + [
                        Placement(block_id, row, col)
                    ]

                    # Recursively place remaining blocks
                    solutions: list[tuple[list[Placement], list[list[int]], int]] = (
                        generate_placements(new_grid, remaining_blocks, new_placements)
                    )
                    all_solutions.extend(solutions)

    # Also consider not placing this block (skip it)
    if not current_placements:  # Only skip if we haven't placed anything yet
        remaining_blocks = {
            k: v for k, v in blocks.items() if k != list(blocks.keys())[0]
        }
        if remaining_blocks:
            solutions = generate_placements(grid, remaining_blocks, current_placements)
            all_solutions.extend(solutions)

    return all_solutions


def solve(grid: list[list[int]], blocks: dict[int, list[list[int]]]) -> Solution | None:
    """
    Find the best placement of blocks to maximize line clears.

    Args:
        grid: Initial grid state ({GRID_SIZE}x{GRID_SIZE})
        blocks: Dictionary of blocks to place

    Returns:
        Best solution found, or None if no valid placement exists
    """
    all_solutions = generate_placements(grid, blocks)

    if not all_solutions:
        return None

    # Find solution with most lines cleared
    best = max(all_solutions, key=lambda x: x[2])
    placements, final_grid, lines_cleared = best

    return Solution(placements, lines_cleared, final_grid)
