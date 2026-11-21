# Tetris CLear - SAT Reduction

Decides if a partially filled Tetris board can be cleared completely by a given sequence of tetrominos. We encode the question as a SAT and solve it with the Glucose SAT Solver

## Problem Description

### Question

Given a width, a height, a sequence of tetrominos and an initial starting board by rotating/moving the pieces can we fully clear the board such that the last piece fills the last remaining gap which clears everything?

### Rules of the game

1. The pieces arrive one by one in the given sequence and they are placed only once and they are replaced with the next tetromino in the sequence. And also we dont have the "hold" feature which exists in the modern tetris games

2. The game is "offline" which means that the whole sequence of pieces are known in advance

3. Before a piece is dropped we choosew its rotation and column it is droped in. The piece drops from above the board

4. The piece falls straight down it cannot move horizontaly nor rotate during its fall.

5. The piece locks in a position where it can not move any further down and it never moves again

6. After a piece locks, every full row is removed and all rows sit above it shift down. Cells do not fall any further than that which means that gravity does not apply always.

The answer is yes if, after the last piece the board is completely empty. A solution lists where each piece locked.

### Parameters


* $W, H$  width and height of the board
* $n$  number of pieces
* $\tau_1, \dots, \tau_n$  type of each piece, one of I, O, T, S, Z, L, j
* $F_0$ | set of cells that are filled at the start 

The starting board must not contain a full row.

A cell is written $(r, c)$. Row 0 is the top row and $r$ increases downward, up to $H-1$ at the bottom. Column 0 is the leftmost column and $c$ increases to the right, up to $W-1$.


### Pieces and Rotation

- Every piece has a pivot cell, which is the cell we use to say where the piece is. A rotation is described by where its 4 cells sit relative to the pivot, as $(\Delta r, \Delta c)$, with down and right being +1, and the pivot itself is $(0,0)$.

- Number of rotations is denoted as $k(\tau)$: 1 for O, 2 for I, S and Z, 4 for T, L and J.

### Table of rotations

| Piece | Rotation | Cells $(\Delta r, \Delta c)$ |
|---|---|---|
| I | 1 | (0,0), (0,−1), (0,−2), (0,−3) |
| I | 2 | (0,0), (−1,0), (−2,0), (−3,0) |
| O | 1 | (0,0), (0,1), (1,0), (1,1) |
| S | 1 | (0,0), (0,−1), (−1,−1), (1,0) |
| S | 2 | (0,0), (0,−1), (−1,0), (−1,1) |
| Z | 1 | (0,0), (0,−1), (−1,0), (1,−1) |
| Z | 2 | (0,0), (0,1), (−1,0), (−1,−1) |
| L | 1 | (0,0), (0,1), (−1,0), (−2,0) |
| L | 2 | (0,0), (0,1), (0,2), (1,0) |
| L | 3 | (0,0), (0,−1), (1,0), (2,0) |
| L | 4 | (0,0), (0,−1), (0,−2), (−1,0) |
| J | 1 | (0,0), (0,−1), (−1,0), (−2,0) |
| J | 2 | (0,0), (0,1), (0,2), (−1,0) |
| J | 3 | (0,0), (0,1), (1,0), (2,0) |
| J | 4 | (0,0), (0,−1), (0,−2), (1,0) |
| T | 1 | (0,0), (0,−1), (0,1), (−1,0) |
| T | 2 | (0,0), (0,1), (−1,0), (1,0) |
| T | 3 | (0,0), (0,−1), (0,1), (1,0) |
| T | 4 | (0,0), (0,−1), (−1,0), (1,0) |

$D(\tau, o)$ is the set of offsets of piece type $\tau$ in rotation $o$, from the table.

$$C_t(o, r, c) = \lbrace (r + \Delta r,\ c + \Delta c) : (\Delta r, \Delta c) \in D(\tau_t, o) \rbrace$$

the cells covered by piece t at that spot

$$S_t = \lbrace (o, r, c) : 1 \le o \le k(\tau_t),\ C_t(o, r, c) \subseteq \lbrace 0, \dots, H-1 \rbrace \times \lbrace 0, \dots, W-1 \rbrace \rbrace$$

all spots where the whole piece fits inside the board

$$\mathrm{Cov}_t(r, c) = \lbrace (o, r_0, c_0) \in S_t : (r, c) \in C_t(o, r_0, c_0) \rbrace$$

all spots of piece t that cover cell $(r,c)$

$$\mathrm{Below}_t(o,r,c) = \lbrace (r'+1,\ c') : (r',c') \in C_t(o,r,c) \rbrace \setminus C_t(o,r,c)$$

the cells that are directly under piece t at that spot, not counting the cells of the piece itself

$$\mathrm{Above}_t(o,r,c) = \lbrace (r'',c') : (r',c') \in C_t(o,r,c),\ 0 \le r'' < r' \rbrace \setminus C_t(o,r,c)$$

the cells above piece $t$ at that spot in its columns, up to the top of the board, not counting the cells of the piece itself

### Variables

For each piece $t$:

1. We start from frame $t-1$.
2. Piece $t$ locks, so the resulting board is the in-between board $t$.
3. Full rows are removed, so we get a clean frame $t$.

- **$p(t,o,r,c)$:** means that piece $t$ locks in rotation $o$ with its pivot at row $r$, column $c$, for $t \in \lbrace 1, \dots, n \rbrace$ and $(o, r, c) \in S_t$.
- **$b(t,r,c)$:** cell $(r, c)$ is filled in frame $t$, for $t \in \lbrace 0, \dots, n \rbrace$ and every cell $(r, c)$.
- **$m(t,r,c)$:** cell $(r, c)$ is filled in the in-between board $t$, for $t \in \lbrace 1, \dots, n \rbrace$ and every cell $(r, c)$.
- **$f(t,r)$:** row $r$ is full in the in-between board $t$, for $t \in \lbrace 1, \dots, n \rbrace$ and $r \in \lbrace 0, \dots, H-1 \rbrace$.
- **$d(t,r,k)$:** exactly $k$ of the rows below row $r$ are full in the in-between board $t$, for $t \in \lbrace 1, \dots, n \rbrace$, $r \in \lbrace -1, 0, \dots, H-1 \rbrace$ and $k \in \lbrace 0, \dots, 4 \rbrace$. Row $-1$ is an imaginary row above the board, so $d(t,-1,k)$ means that exactly $k$ rows are full in total.


**Frame 0** is our starting board. We know that frame $t-1$ never has a full row and in every later frame the full rows were already removed. So the only rows that can become full in the in-between board $t$ are rows that piece $t$ touches. A piece touches at most 4 rows with aa vertical "I" tetromino so at most four rows can be full at once and $k$ never exceeds 4.

## Constraints

Unless stated otherwise, each constraint holds for all valid indices of the variables involved: pieces $t \in \lbrace 1, \dots, n \rbrace$, spots in $S_t$, and cells of the board.

### 1. Every piece locks in exactly one spot

*At least one spot.*

$$\bigvee_{(o,r,c) \in S_t} p(t,o,r,c)$$

*At most one spot,* where $(o,r,c) \neq (o',r',c')$:

$$\neg \left( p(t,o,r,c) \land p(t,o',r',c') \right) \quad \equiv \quad \neg p(t,o,r,c) \lor \neg p(t,o',r',c')$$

### 2. A piece cannot lock on cells that are already filled

Where $(r',c') \in C_t(o,r,c)$:

$$p(t,o,r,c) \rightarrow \neg b(t-1,r',c') \quad \equiv \quad \neg p(t,o,r,c) \lor \neg b(t-1,r',c')$$

### 3. When a piece locks, its cells are filled in the in-between board

Where $(r',c') \in C_t(o,r,c)$:

$$p(t,o,r,c) \rightarrow m(t,r',c') \quad \equiv \quad \neg p(t,o,r,c) \lor m(t,r',c')$$

### 4a. A filled cell stays filled in the in-between board

$$b(t-1,r,c) \rightarrow m(t,r,c) \quad \equiv \quad \neg b(t-1,r,c) \lor m(t,r,c)$$

### 4b. A cell of the in-between board is filled only if it was filled before or the new piece covers it.

$$m(t,r,c) \rightarrow b(t-1,r,c) \lor \bigvee_{(o,r_0,c_0) \in \mathrm{Cov}_t(r,c)} p(t,o,r_0,c_0) \quad \equiv \quad \neg m(t,r,c) \lor b(t-1,r,c) \lor \bigvee_{(o,r_0,c_0) \in \mathrm{Cov}_t(r,c)} p(t,o,r_0,c_0)$$

### 5. Locking: the piece rests on the floor or on a filled cell

Where the piece does not touch the floor, i.e. every $(r',c') \in C_t(o,r,c)$ has $r' < H-1$:

$$p(t,o,r,c) \rightarrow \bigvee_{(r'',c'') \in \mathrm{Below}_t(o,r,c)} b(t-1,r'',c'') \quad \equiv \quad \neg p(t,o,r,c) \lor \bigvee_{(r'',c'') \in \mathrm{Below}_t(o,r,c)} b(t-1,r'',c'')$$

### 6. Dropping: nothing blocks the piece's way down

The piece is dropped straight down from above the board, so every cell above it must be empty. Where $(r'',c'') \in \mathrm{Above}_t(o,r,c)$:

$$p(t,o,r,c) \rightarrow \neg b(t-1,r'',c'') \quad \equiv \quad \neg p(t,o,r,c) \lor \neg b(t-1,r'',c'')$$

### 7. A row is full exactly when all its cells are filled

$$f(t,r) \leftrightarrow \bigwedge_{c=0}^{W-1} m(t,r,c)$$

If the row is full, every cell is filled, for each column $c$:

$$f(t,r) \rightarrow m(t,r,c) \quad \equiv \quad \neg f(t,r) \lor m(t,r,c)$$

If every cell is filled, the row is full:

$$\left( \bigwedge_{c=0}^{W-1} m(t,r,c) \right) \rightarrow f(t,r) \quad \equiv \quad \bigvee_{c=0}^{W-1} \neg m(t,r,c) \lor f(t,r)$$

### 8. Counting the full rows below each row

We count from the bottom up. The bottom row has nothing below it:

$$d(t,H-1,0)$$

Going up one row, the count stays the same if the row below is not full, and goes up by one if it is full, for $r < H-1$:

$$\neg d(t,r+1,k) \lor f(t,r+1) \lor d(t,r,k)$$

$$\neg d(t,r+1,k) \lor \neg f(t,r+1) \lor d(t,r,k+1) \qquad (k \le 3)$$

Each row has exactly one count, for $k \neq k'$:

$$\neg d(t,r,k) \lor \neg d(t,r,k')$$

### 9. Rows that are not full shift down by the number of full rows below them

If row $r$ is not full and exactly $k$ rows below it are full, then row $r$ of the in-between board becomes row $r+k$ of frame $t$. For every column $c$ and every $k$ with $r + k \le H-1$:

$$d(t,r,k) \land \neg f(t,r) \rightarrow \left( b(t,r+k,c) \leftrightarrow m(t,r,c) \right)$$

The $\leftrightarrow$ splits into two directions, which gives two clauses:

$$\neg d(t,r,k) \lor f(t,r) \lor \neg m(t,r,c) \lor b(t,r+k,c)$$

$$\neg d(t,r,k) \lor f(t,r) \lor m(t,r,c) \lor \neg b(t,r+k,c)$$

### 10. The rows freed at the top are empty

If $k$ rows are cleared, the top $k$ rows of frame $t$ receive nothing in rule 9, so they are empty. For every column $c$ and every row $j < k$:

$$d(t,-1,k) \rightarrow \neg b(t,j,c) \quad \equiv \quad \neg d(t,-1,k) \lor \neg b(t,j,c)$$

### 11. Start: frame 0 is the starting board

For every cell $(r,c)$:

$$b(0,r,c) \quad \text{if } (r,c) \in F_0, \qquad \neg b(0,r,c) \quad \text{if } (r,c) \notin F_0$$

### 12. Goal: every cell of the last frame is empty

For every cell $(r,c)$:

$$\neg b(n,r,c)$$

## Usage

The script runs on Linux and needs Python 3. The repository includes a Linux build of `glucose-syrup` 4.2.1, which must stay in the same folder as `tetris.py`. If it doesn't run, make it executable first with `chmod +x glucose-syrup`.

```
python3 tetris.py -i input.in -o formula.cnf -v 0
```

- `-i` the instance file (default `input.in`)
- `-o` where the CNF formula is written (default `formula.cnf`)
- `-s` the solver binary (default `glucose-syrup`)
- `-v` the solver's verbosity, 0 or 1 (default 1)

### Input format

The first line is the piece sequence, separated by spaces, using the letters `I`, `O`, `T`, `S`, `Z`, `L` and `J`. The remaining lines are the board, one line per row from the top, where `#` is a filled cell and `.` is empty. Empty lines are ignored.

The script rejects the input if the rows have different lengths, if it contains any other character or piece letter, or if a row of the starting board is already full.

Example: a 4×5 board with a 2×2 block in the bottom-left corner, and one O piece.

```
O
....
....
....
##..
##..
```

### Output

The script first prints the solver's own output, then the answer. If the board cannot be cleared, it prints:

```
No, the board cannot be cleared with this sequence.
```

Otherwise it lists, for each piece, its rotation and the position of its pivot, and draws the board right after that piece locks, before full rows are removed. The new piece is drawn with its letter, and cells that were already filled with `#`. For the example above:

```
Yes, the board can be cleared:

Piece 1 (O): rotation 1, pivot at row 3, column 2
....
....
....
##OO
##OO
```
