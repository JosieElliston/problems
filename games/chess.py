from __future__ import annotations
from dataclasses import dataclass
# TODO: draw by repetition
# white is false and black is true
FILES = {1: "a", 2: "b", 3: "c", 4: "d", 5: "e", 6: "f", 7: "g", 8: "h"}

# class Piece:
#     def __init__(self, color: bool, file: int, rank: int, name: str) -> None:
#         self.color = color
#         self.file = file
#         self.rank = rank
#         self.name = name

#     def __str__(self) -> str:
#         return self.name + FILES[self.file] + str(self.rank)
    
#     def __hash__(self) -> int:
#         return hash((self.color, self.file, self.rank, self.name))
    
#     def __eq__(self, __o: object) -> bool:
#         if isinstance(__o, Piece):
#             return self.color == __o.color and self.file == __o.file and self.rank == __o.rank and self.name == __o.name
#         return False
        
#     

@dataclass
class Piece:
    color: bool
    name: str

@dataclass
class Square:
    rank: int
    file: int

# @dataclass
# class OccupiedSquare:
#     square: Square
#     piece: Piece



class Board:
    def __init__(self, state: dict[int, dict[int, Piece | None]], player: bool, move: Square | None) -> None:
        self.state = state
        self.player = player
        self.move = move # we need to know the move for en passant, but only store it if it was a relevant pawn move
    
    @classmethod
    def from_setup(cls) -> Board:
        state: dict[int, dict[int, Piece | None]] = {
            8: {1: Piece(True, "R"), 2: Piece(True, "N"), 3: Piece(True, "B"), 4: Piece(True, "Q"), 5: Piece(True, "K"), 6: Piece(True, "B"), 7: Piece(True, "N"), 8: Piece(True, "R")},
            7: {1: Piece(True, "p"), 2: Piece(True, "p"), 3: Piece(True, "p"), 4: Piece(True, "p"), 5: Piece(True, "p"), 6: Piece(True, "p"), 7: Piece(True, "p"), 8: Piece(True, "p")},
            6: {1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None},
            5: {1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None},
            4: {1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None},
            3: {1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None},
            2: {1: Piece(False, "p"), 2: Piece(False, "p"), 3: Piece(False, "p"), 4: Piece(False, "p"), 5: Piece(False, "p"), 6: Piece(False, "p"), 7: Piece(False, "p"), 8: Piece(False, "p")},
            1: {1: Piece(False, "R"), 2: Piece(False, "N"), 3: Piece(False, "B"), 4: Piece(False, "Q"), 5: Piece(False, "K"), 6: Piece(False, "B"), 7: Piece(False, "N"), 8: Piece(False, "R")},
        }
        # pieces: set[OccupiedSquare] = set()
        # piece_at: dict[Square, Piece] = dict()
        # for rank in state:
        #     rank_pieces = state[rank]
        #     for file in rank_pieces:
        #         piece = rank_pieces[file]
        #         if isinstance(piece, Piece):
        #             piece_at[Square(rank, file)] = piece
        return Board(state, False, None)        

    def step(self) -> set[Board]:
        moves: set[Board] = set()
        for rank in self.state:
            rank_pieces = self.state[rank]
            for file in rank_pieces:
                piece = rank_pieces[file]
                if isinstance(piece, Piece):
                    if piece.name == "p":
                        raise NotImplemented
                    elif piece.name == "R":
                        raise NotImplemented
                    elif piece.name == "N":
                        raise NotImplemented
                    elif piece.name == "B":
                        raise NotImplemented
                    elif piece.name == "Q":
                        raise NotImplemented
                    elif piece.name == "K":
                        raise NotImplemented
        # purge invalid moves
            # due to revealing king
        return moves

    def is_piece_on(self, rank: int, file: int) -> bool:
        for piece in self.piece_at:
            if piece.rank == rank and piece.file == file:
                return True
        return False

    def get_piece_on(self, rank: int, file: int) -> Piece:
        for piece in self.piece_at:
            if piece.rank == rank and piece.file == file:
                return piece
        raise ValueError

    def is_square_reachable(self, rank: int, file: int, color: bool) -> bool:
        raise NotImplemented
        # without_target = self.pieces.copy()
        # if self.is_piece_on(rank, file):