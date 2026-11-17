from argparse import ArgumentParser


def load_instance(path_to_input_file):

    sequence = []
    grid = []

    with open(path_to_input_file, "r") as file:
        sequence = file.readline().strip().split()

        for line in file:
            clean_line = line.strip()

            if clean_line:
                grid.append(clean_line)

    if not grid:
        raise ValueError("The board cannot be empty!")

    height = len(grid)
    width = len(grid[0])

    for row in grid:
        if len(row) != width:
            raise ValueError("Width of the board must be consistent!")

    filled = set()

    for r, row in enumerate(grid):
        for c, char in enumerate(row):
            if char == "#":
                filled.add((r,c))
            elif char != ".":
                raise ValueError(f"Invalid character {char!r} at row {r}, column {c} in the board!")
    
    for tetromino in sequence:
        if tetromino not in {"I", "O", "T", "S", "Z", "J", "L"}:
            raise ValueError(f"Invalid tetromino {tetromino!r} at the sequence")

    return width, height, sequence, filled




if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument(
        "-i",
        "--input",
        default="input.in",
        type=str,
        help="The instance file",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="formula.cnf",
        type=str,
        help="Output file for the CNF formula"
    )
    parser.add_argument(
        "-s",
        "--solver",
        default="glucose-syrup",
        type=str,
        help="The SAT solver which is being used"
    )
    parser.add_argument(
        "-v",
        "--verb",
        default=1,
        type=int,
        choices=range(0,2),
        help="The verbosity of the SAT solver being used"
    )
    args = parser.parse_args()

    print(load_instance("input.in"))