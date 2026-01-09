import time
import src.automation as automation
import src.vision as vision
from src.solver import solve
from config import (
    BLOCK_INDICES,
    DELAY_BETWEEN_CYCLES,
    RETRY_DELAY_NO_BLOCKS,
    RETRY_DELAY_NO_SOLUTION,
)

CLR_RESET = "\033[0m"
CLR_BOLD = "\033[1m"
CLR_RED = "\033[91m"
CLR_GREEN = "\033[92m"
CLR_YELLOW = "\033[93m"
CLR_BLUE = "\033[94m"
CLR_MAGENTA = "\033[95m"
CLR_CYAN = "\033[96m"
CLR_GRAY = "\033[90m"


def _print_grid(grid: list[list[int]]) -> None:
    print(f"{CLR_BOLD}Current Grid State:{CLR_RESET}")
    for row in grid:
        row_str = " ".join(
            [
                f"{CLR_GREEN}■{CLR_RESET}" if cell else f"{CLR_GRAY}□{CLR_RESET}"
                for cell in row
            ]
        )
        print(f"  {row_str}")


def main() -> None:
    print(f"{CLR_BOLD}{CLR_BLUE}--- Block Puzzle Automation ---{CLR_RESET}")
    print("This script will run in a loop to solve and execute puzzle placements.")
    print(f"Press {CLR_BOLD}Ctrl+C{CLR_RESET} at any time to stop.")

    try:
        _ = input(f"\nPress {CLR_BOLD}Enter{CLR_RESET} to begin...")
    except KeyboardInterrupt:
        print(f"\n{CLR_RED}Exiting.{CLR_RESET}")
        return

    try:
        cycle_count = 1
        while True:
            print(f"\n{CLR_BOLD}{CLR_CYAN}----- Cycle {cycle_count} -----{CLR_RESET}")

            print(f"{CLR_CYAN}Capturing game state...{CLR_RESET}")
            current_grid = vision.grid()
            _print_grid(current_grid)

            available_blocks = vision.blocks(list(BLOCK_INDICES))
            if not available_blocks:
                print(
                    f"\n{CLR_YELLOW}No blocks detected. Retrying in {RETRY_DELAY_NO_BLOCKS} seconds...{CLR_RESET}"
                )
                time.sleep(RETRY_DELAY_NO_BLOCKS)
                continue
            print(
                f"  Detected Blocks: {CLR_BOLD}{list(available_blocks.keys())}{CLR_RESET}"
            )

            print(f"{CLR_MAGENTA}Solving for optimal placement...{CLR_RESET}")
            solution = solve(current_grid, available_blocks)

            if solution is None:
                print(
                    f"\n{CLR_YELLOW}No valid solution found. Retrying in {RETRY_DELAY_NO_SOLUTION} seconds...{CLR_RESET}"
                )
                time.sleep(RETRY_DELAY_NO_SOLUTION)
                continue

            print(
                f"  {CLR_GREEN}{CLR_BOLD}Solution found! Lines to be cleared: {solution.lines_cleared}{CLR_RESET}"
            )

            print(f"{CLR_YELLOW}Executing solution...{CLR_RESET}")
            automation.execute_solution(solution, available_blocks)
            print(f"  {CLR_GREEN}Execution complete.{CLR_RESET}")

            cycle_count += 1
            print(f"\nWaiting for next cycle... ({DELAY_BETWEEN_CYCLES}s)")
            time.sleep(DELAY_BETWEEN_CYCLES)

    except KeyboardInterrupt:
        print(f"\n\n{CLR_YELLOW}Loop stopped by user. Exiting.{CLR_RESET}")
    except Exception as e:
        print(f"\n{CLR_RED}An unexpected error occurred: {e}{CLR_RESET}")
        print("Exiting.")


if __name__ == "__main__":
    main()
