from __future__ import annotations
from enum import Enum
import random as r
from math import exp
from copy import deepcopy
from timeit import timeit
from typing import Callable

class Piece(Enum):
    BLANK = 0
    X = 1
    O = 2

    def negate(self) -> Piece:
        if self == Piece.X:
            return Piece.O
        elif self == Piece.O:
            return Piece.X
        raise ValueError
    
    def __str__(self) -> str:
        if self == Piece.X:
            return "x"
        elif self == Piece.O:
            return "o"
        elif self == Piece.BLANK:
            return "."
        else:
            raise ValueError

# BELTS = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]
# # PLAYER_MAPPING = {True: Piece.O, False: Piece.X}

# class Board:
#     def __init__(self, prev_player: Piece, squares: list[Piece]) -> None:
#         self.squares = squares
#         self.prev_player = prev_player

#     @classmethod
#     def from_setup(cls) -> Board:
#         return Board(Piece.O, [Piece.BLANK, Piece.BLANK, Piece.BLANK, Piece.BLANK, Piece.BLANK, Piece.BLANK, Piece.BLANK, Piece.BLANK, Piece.BLANK])

#     def won(self) -> bool:
#         for belt_i in BELTS:
#             belt = {self.squares[i] for i in belt_i}
#             belt.add(self.prev_player)
#             if len(belt) == 1:
#                 return True
#         return False

#     def tie(self) -> bool:
#         return not Piece.BLANK in self.squares

#     def step(self) -> list[Board]:
#         assert not self.over()
#         out: list[Board] = list()
#         for i in range(len(self.squares)):
#             if self.squares[i] == Piece.BLANK:
#                 new_squares = self.squares.copy()
#                 new_squares[i] = self.prev_player.negate()
#                 out.append(Board(self.prev_player.negate(), new_squares))
#         return out
    
#     def over(self) -> bool:
#         return self.tie() or self.won()
    
#     def __str__(self):
#         return "\n".join("".join(a) for a in zip(*(iter([str(a) for a in self.squares]),) * 3)) + "\n"
    
#     def __hash__(self):
#         return hash(tuple(self.squares))
    
#     def __eq__(self, __o: object) -> bool:
#         if isinstance(__o, Board):
#             return self.squares == __o.squares
#         return False
def replace(tup: tuple, i: int, val):
    return tup[:i] + (val,) + tup[i+1:]
MOVE_BELTS = {0: ((0, 1, 2), (0, 3, 6), (0, 4, 8)), 1: ((0, 1, 2), (1, 4, 7)), 2: ((0, 1, 2), (2, 5, 8), (2, 4, 6)), 3: ((3, 4, 5), (0, 3, 6)), 4: ((3, 4, 5), (1, 4, 7), (0, 4, 8), (2, 4, 6)), 5: ((3, 4, 5), (2, 5, 8)), 6: ((6, 7, 8), (0, 3, 6), (2, 4, 6)), 7: ((6, 7, 8), (1, 4, 7)), 8: ((6, 7, 8), (2, 5, 8), (0, 4, 8))}
class Board:
    def __init__(self, squares: tuple[Piece, ...], blank_squares: int, state: Piece | None) -> None:
        self.squares = squares # the state
        assert blank_squares >= 0
        self.blank_squares = blank_squares # cash for how many blank squares exist
        self.state = state # tie, x win, o win, ongoing
    
    @classmethod
    def from_setup(cls) -> Board:
        return Board(tuple(Piece.BLANK for i in range(9)), 9, None)

    def after_move(self, move: int, player: Piece) -> Board:
        assert self.squares[move] == Piece.BLANK
        new_squares = replace(self.squares, move, player)
        new_blank_squares = self.blank_squares - 1
        if new_blank_squares == 0:
            return Board(new_squares, new_blank_squares, Piece.BLANK)
        else:
            for belt_i in MOVE_BELTS[move]:
                belt = {self.squares[i] for i in belt_i}
                if len(belt|{Piece.X}) == 1:
                    return Board(new_squares, new_blank_squares, Piece.X)
                elif len(belt|{Piece.O}) == 1:
                    return Board(new_squares, new_blank_squares, Piece.O)
            return Board(new_squares, new_blank_squares, None)
    
    def __hash__(self):
        return hash(tuple(self.squares))
    
    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Board):
            return self.squares == __o.squares
        return False

_eval_cash: dict[Board, float] = dict()
def eval_board(board: Board) -> float:
    if _eval_cash.get(board) != None:
        return _eval_cash[board]
    if board.won():
        _eval_cash[board] = 1
        return _eval_cash[board]
    elif board.tie():
        _eval_cash[board] = 0
        return _eval_cash[board]
    values: set[float] = set()
    for step_board in board.step():
        values.add(eval_board(step_board))
    _eval_cash[board] = -max(values)
    return _eval_cash[board]

def make_move(board: Board) -> Board:
    values: dict[Board, float] = dict()
    for step_board in board.step():
        values[step_board] = eval_board(step_board)
    return max(values.items(), key = lambda a: a[1])[0]

board = Board.from_setup()
# board = Board(Piece.X, [Piece.O, Piece.BLANK, Piece.BLANK, Piece.X, Piece.X, Piece.BLANK, Piece.O, Piece.BLANK, Piece.X]) # only 1 move ties
# board = Board(Piece.O, [Piece.O, Piece.X, Piece.O, Piece.BLANK, Piece.BLANK, Piece.X, Piece.BLANK, Piece.X, Piece.BLANK])
# board = Board(Piece.O, [Piece.O, Piece.O, Piece.BLANK, Piece.X, Piece.X, Piece.BLANK, Piece.O, Piece.BLANK, Piece.X]) # x win in 1
# print(board)
# print(make_move(board))
print("starting")
print("took", timeit(lambda: eval_board(board), number = 1))

# while True:
#     # print(eval_board(board))
#     print(board)
#     board = make_move(board)
#     if board.over():
#         print(eval_board(board))
#         print(board)
#         break