# Tetris Fill - SAT Reduction

Decides if a partially filled Tetris board can be cleared completely by a given sequence of tetrominos. We encode the question as a SAT and solve it with the Glucose SAT Solver

## Problem Description

### Question

Given a width, a height, a sequence of tetrominos and an initial starting board by rotating/moving the pieces can we fully clear the board such that the last piece fills the last remaining gap which clears everything?

### Rules of the game

1. The pieces arrive one by one in the given sequence and they are placed only once and they are replaced with the next tetromino in the sequence. And also we dont have the "hold" feature which exists in the modern tetris games

2. The game is "offline" which means that the whole sequence of pieces are known in advance

3. All the pieces start in the starting zone where they can move horizontally and rotate freely without colliding with already filled cells

4. While the piece is falling it can be moved horizontally and downwards and rotated 90 degrees either clockwise or counterclockwise only if the movement does not collide with any other filled slot

5. The piece locks in a position where it can not move any further down and it never moves again

6. After a piece locks, every full row is removed and all rows sit above it shift down. Cells do not fall any further than that which means that gravity does not apply always.

The answer is yes if, after the last piece the board is completely empty. A solution lists where each piece locked.

### Parameters


* $W, H$  width and height of the board, including the spawn zone
* $n$  number of pieces
* $\tau_1, \dots, \tau_n$  type of each piece, one of I, O, T, S, Z, L, j
* $F_0$ | set of cells that are filled at the start 

A cell is written $(r, c)$. Row 0 is the top row and $r$ increases downward, up to $H-1$ at the bottom. Column 0 is the leftmost column and $c$ increases to the right, up to $W-1$. Rows $0$ to $3$ are the spawn zone

### Variables

Each step $t$ goes through two boards: the **in-between board** right after piece $t$ locks, and **frame $t$** after full rows have been removed.

$$\text{frame } t-1 \;\xrightarrow{\ \text{piece } t \text{ locks}\ }\; \text{in-between board } t \;\xrightarrow{\ \text{full rows removed}\ }\; \text{frame } t$$

| Variable | Meaning | Indices |
|---|---|---|
| $p(t,o,r,c)$ | piece $t$ locks in rotation $o$ with its pivot at row $r$, column $c$ | $t \in \lbrace 1, \dots, n \rbrace$, $(o, r, c) \in S_t$ |
| $b(t,r,c)$ | cell $(r, c)$ is filled in frame $t$ | $t \in \lbrace 0, \dots, n \rbrace$, all cells $(r, c)$ |
| $m(t,r,c)$ | cell $(r, c)$ is filled in the in-between board $t$ | $t \in \lbrace 1, \dots, n \rbrace$, all cells $(r, c)$ |
| $f(t,r)$ | row $r$ is full in the in-between board $t$ | $t \in \lbrace 1, \dots, n \rbrace$, $r \in \lbrace 0, \dots, H-1 \rbrace$ |
| $d(t,r,k)$ | exactly $k$ of the rows below row $r$ are full in the in-between board $t$ | $t \in \lbrace 1, \dots, n \rbrace$, $r \in \lbrace 0, \dots, H-1 \rbrace$, $k \in \lbrace 0, \dots, 4 \rbrace$ |

**Frame 0** is the starting board. Since a piece covers at most four rows, at most four rows can be full at once, so $k$ never exceeds 4.

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

> #TODO write all the remaining constraints