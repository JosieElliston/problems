from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from copy import deepcopy


def replace(tup: tuple, i: int, val):
    return tup[:i] + (val,) + tup[i+1:]

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

@dataclass
class Move:
    board: int
    square: int
    player: Piece

# lookup table of belts
# BELTS: tuple[tuple[int, ...], ...] = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))
# lookup table of the move and what belts it's contained in
# MOVE_BELTS: dict[int, tuple[tuple[int, ...], ...]] = {move: tuple(filter(lambda belt: move in belt, BELTS)) for move in range(9)}
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

class MetaBoard:
    def __init__(self, player: Piece, available_board: int, boards: list[list[Piece]], meta_board: list[Piece]) -> None:
        # self.prev_move = prev_move
        self.player = player
        self.available_board = available_board
        self.boards = boards
        self.meta_board = meta_board
    
    @classmethod
    def from_setup(cls) -> MetaBoard:
        return MetaBoard(
            Piece.O,
            -1,
            [[Piece.BLANK for j in range(9)] for i in range(9)],
            [Piece.BLANK for i in range(9)]
        )

    def __str__(self) -> str:
        out = ""
        for board_y in range(3):
            for row in range(3):
                for board_x in range(3):
                    board = self.boards[board_y*3 + board_x]
                    for column in range(3):
                        out += str(board[row*3 + column])
                    out += " "
                out += "\n"
            out += "\n"
        return out

    def after_move(self, move: Move) -> MetaBoard:
        raise NotImplemented
        assert self.player != move.player
        assert self.boards[move.board][move.square] == Piece.BLANK
        if self.meta_board[move.square] == Piece.BLANK:
            available_board = move.square
        else:
            available_board = -1
        new_boards = deepcopy(self.boards)
        new_boards[move.board][move.square] = move.player
        
        return MetaBoard(move.player, available_board, )
    
    def get_moves(self) -> list[Move]:
        raise NotImplemented
        if self.meta_board[self.prev_move.board] == Piece.Blank:
            pass

    def after_moves(self) -> list[MetaBoard]:
        return [self.after_move(move) for move in self.get_moves()]

game = MetaBoard.from_setup()
print(game)
game.boards[1][5] = Piece.X
print(game)