from argparse import ArgumentParser
from itertools import combinations
import subprocess


# this is the exact table of rotations from README.md
ROT = {
    ("I", 1): [(0, 0), (0, -1), (0, -2), (0, -3)],
    ("I", 2): [(0, 0), (-1, 0), (-2, 0), (-3, 0)],
    ("O", 1): [(0, 0), (0, 1), (1, 0), (1, 1)],
    ("S", 1): [(0, 0), (0, -1), (-1, -1), (1, 0)],
    ("S", 2): [(0, 0), (0, -1), (-1, 0), (-1, 1)],
    ("Z", 1): [(0, 0), (0, -1), (-1, 0), (1, -1)],
    ("Z", 2): [(0, 0), (0, 1), (-1, 0), (-1, -1)],
    ("L", 1): [(0, 0), (0, 1), (-1, 0), (-2, 0)],
    ("L", 2): [(0, 0), (0, 1), (0, 2), (1, 0)],
    ("L", 3): [(0, 0), (0, -1), (1, 0), (2, 0)],
    ("L", 4): [(0, 0), (0, -1), (0, -2), (-1, 0)],
    ("J", 1): [(0, 0), (0, -1), (-1, 0), (-2, 0)],
    ("J", 2): [(0, 0), (0, 1), (0, 2), (-1, 0)],
    ("J", 3): [(0, 0), (0, 1), (1, 0), (2, 0)],
    ("J", 4): [(0, 0), (0, -1), (0, -2), (1, 0)],
    ("T", 1): [(0, 0), (0, -1), (0, 1), (-1, 0)],
    ("T", 2): [(0, 0), (0, 1), (-1, 0), (1, 0)],
    ("T", 3): [(0, 0), (0, -1), (0, 1), (1, 0)],
    ("T", 4): [(0, 0), (0, -1), (-1, 0), (1, 0)],
}

var_of = {}
key_of = {}

def var(key):
    if key not in var_of:
        var_of[key] = len(var_of) + 1
        key_of[var_of[key]] = key
    return var_of[key]


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
        raise ValueError("The board cannot be empty")

    height = len(grid)
    width = len(grid[0])

    for row in grid:
        if len(row) != width:
            raise ValueError("Width of the board must be consistent")

    filled = set()

    for r, row in enumerate(grid):
        for c, char in enumerate(row):
            if char == "#":
                filled.add((r,c))
            elif char != ".":
                raise ValueError(f"Invalid character {char!r} at row {r}, column {c} in the board")
    
    for tetromino in sequence:
        if tetromino not in {"I", "O", "T", "S", "Z", "J", "L"}:
            raise ValueError(f"Invalid tetromino {tetromino!r} at the sequence")

    for r, row in enumerate(grid):
        if "." not in row:
            raise ValueError(f"Row {r} of the starting board is already full!")

    return width, height, sequence, filled

# C_t from README.md
def cells(kind, o, r, c):
    return [(r + dr, c + dc) for dr, dc in ROT[(kind, o)]]

# S_t from README
def spots(kind, width, height):
    result = []
    for (k, o) in ROT:
        if k != kind:
            continue
        for r in range(height):
            for c in range(width):
                if all(0 <= rr < height and 0 <= cc < width for rr, cc in cells(kind, o, r, c)):
                    result.append((o, r, c))
    return result

# Below_t from README
def below(kind, o, r, c):
    piece = set(cells(kind, o, r, c))
    return {(rr + 1, cc) for rr, cc in piece} - piece

# Above_t from README
def above(kind, o, r, c):
    piece = set(cells(kind, o, r, c))
    return {(r2, cc) for rr, cc in piece for r2 in range(rr)} - piece

# Cov_t from README but for all the cells at once
def covers(kind, width, height):
    cov = {}
    for o, r, c in spots(kind, width, height):
        for cell in cells(kind, o, r, c):
            cov.setdefault(cell, []).append((o, r, c))
    return cov

def encode(width, height, sequence, filled):
    clauses = []

    for t, kind in enumerate(sequence, start=1):
        piece_spots = spots(kind, width, height)

        # Rule 1 every piece locks in exactly one spot
        ps = [var(("p", t, o, r, c)) for o, r, c in piece_spots]
        clauses.append(ps)
        for x, y in combinations(ps, 2):
            clauses.append([-x, -y])

        for o, r, c in piece_spots:
            p = var(("p", t, o, r, c))
            for rr, cc in cells(kind, o, r, c):

                # Rule 2 a piece cannot lock on filled cells
                clauses.append([-p, -var(("b", t - 1, rr, cc))])

                # Rule 3 the pieces cells are filled in the in-between board
                clauses.append([-p, var(("m", t, rr, cc))])

            # Rule 5 the piece rests on the floor or on a filled cell
            if all(rr < height - 1 for rr, cc in cells(kind, o, r, c)):
                support = [var(("b", t - 1, rr, cc)) for rr, cc in below(kind, o, r, c)]
                clauses.append([-p] + support)

            # Rule 6 nothing blocks the pieces way down
            for rr, cc in above(kind, o, r, c):
                clauses.append([-p, -var(("b", t - 1, rr, cc))])

        cov = covers(kind, width, height)
        for r in range(height):
            for c in range(width):
                prev = var(("b", t - 1, r, c))
                mid = var(("m", t, r, c))
                covering = [var(("p", t, o, r0, c0)) for o, r0, c0 in cov.get((r, c), [])]

                # Rule 4a a filled cell stays filled in the in-between board
                clauses.append([-prev, mid])

                # Rule 4b a cell of the in-between board is filled only if it was filled before or the piece covers it
                clauses.append([-mid, prev] + covering)

        # Rule 7 a row is full when exactly all of its cells are filled
        for r in range(height):
            full = var(("f", t, r))
            row = [var(("m", t, r, c)) for c in range(width)]
            for cell in row:
                clauses.append([-full, cell])
            clauses.append([-cell for cell in row] + [full])

        # Rule 8 counting the full rows below each row
        clauses.append([var(("d", t, height - 1, 0))])
        for r in range(height - 2, -2, -1):
            full = var(("f", t, r + 1))
            for k in range(5):
                count = var(("d", t, r + 1, k))
                clauses.append([-count, full, var(("d", t, r, k))])
                if k < 4:
                    clauses.append([-count, -full, var(("d", t, r, k + 1))])
                else:

                    # Rule 8 the count never goes past 4
                    clauses.append([-count, -full])

        # Rule 8 each row has exactly one count
        for r in range(-1, height):
            for k1, k2 in combinations(range(5), 2):
                clauses.append([-var(("d", t, r, k1)), -var(("d", t, r, k2))])

        # Rule 9 rows that are not full shift down by the number of full rows below them
        for r in range(height):
            full = var(("f", t, r))
            for k in range(min(5, height - r)):
                count = var(("d", t, r, k))
                for c in range(width):
                    mid = var(("m", t, r, c))
                    after = var(("b", t, r + k, c))
                    clauses.append([-count, full, -mid, after])
                    clauses.append([-count, full, mid, -after])

        # Rule 10 the rows freed at the top are empty
        for k in range(1, 5):
            count = var(("d", t, -1, k))
            for j in range(min(k, height)):
                for c in range(width):
                    clauses.append([-count, -var(("b", t, j, c))])

    for r in range(height):
        for c in range(width):

            # Rule 11 frame 0 is the starting board
            start = var(("b", 0, r, c))
            clauses.append([start] if (r, c) in filled else [-start])

            # Rule 12 every cell of the last frame is empty
            clauses.append([-var(("b", len(sequence), r, c))])

    return clauses

def call_solver(clauses, output_name, solver_name, verbosity):
    with open(output_name, "w") as file:
        file.write(f"p cnf {len(var_of)} {len(clauses)}\n")
        for clause in clauses:
            file.write(" ".join(str(lit) for lit in clause) + " 0\n")

    return subprocess.run(["./" + solver_name, "-model", f"-verb={verbosity}", output_name], stdout=subprocess.PIPE)


def print_result(result, width, height, sequence):
    output = result.stdout.decode("utf-8")
    print(output)

    if result.returncode == 20:
        print("No, the board cannot be cleared with this sequence.")
        return

    if result.returncode != 10:
        print("The solver did not return a result.")
        return

    model = set()
    for line in output.split("\n"):
        if line.startswith("v"):
            model.update(lit for lit in map(int, line.split()[1:]) if lit > 0)

    print("Yes, the board can be cleared:")
    for t, kind in enumerate(sequence, start=1):
        for o, r, c in spots(kind, width, height):
            if var_of[("p", t, o, r, c)] in model:
                break
        piece = set(cells(kind, o, r, c))

        print()
        print(f"Piece {t} ({kind}): rotation {o}, pivot at row {r}, column {c}")
        for rr in range(height):
            line = ""
            for cc in range(width):
                if (rr, cc) in piece:
                    line += kind
                elif var_of[("m", t, rr, cc)] in model:
                    line += "#"
                else:
                    line += "."
            print(line)



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

    width, height, sequence, filled = load_instance(args.input)
    clauses = encode(width, height, sequence, filled)
    result = call_solver(clauses, args.output, args.solver, args.verb)
    print_result(result, width, height, sequence)