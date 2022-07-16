from __future__ import annotations
from enum import Enum
import random as r
from math import exp
from copy import deepcopy
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

BELTS = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]
# PLAYER_MAPPING = {True: Piece.O, False: Piece.X}

class Board:
    def __init__(self, prev_player: Piece, state: list[Piece]) -> None:
        self.state = state
        self.prev_player = prev_player

    @classmethod
    def from_setup(cls) -> Board:
        return Board(Piece.O, [Piece.BLANK, Piece.BLANK, Piece.BLANK, Piece.BLANK, Piece.BLANK, Piece.BLANK, Piece.BLANK, Piece.BLANK, Piece.BLANK])

    def won(self) -> bool:
        for belt_i in BELTS:
            belt = {self.state[i] for i in belt_i}
            belt.add(self.prev_player)
            if len(belt) == 1:
                return True
        return False

    def tie(self) -> bool:
        return not Piece.BLANK in self.state

    def step(self) -> list[Board]:
        assert not self.over()
        out: list[Board] = list()
        for i in range(len(self.state)):
            if self.state[i] == Piece.BLANK:
                new_state = self.state.copy()
                new_state[i] = self.prev_player.negate()
                out.append(Board(self.prev_player.negate(), new_state))
        return out
    
    def over(self) -> bool:
        return self.tie() or self.won()
    
    def __str__(self):
        return "\n".join("".join(a) for a in zip(*(iter([str(a) for a in self.state]),) * 3)) + "\n"
    
    def __hash__(self):
        return hash(tuple(self.state))
    
    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Board):
            return self.state == __o.state
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

# board = Board.from_setup()
# board = Board(Piece.X, [Piece.O, Piece.BLANK, Piece.BLANK, Piece.X, Piece.X, Piece.BLANK, Piece.O, Piece.BLANK, Piece.X]) # only 1 move ties
# board = Board(Piece.O, [Piece.O, Piece.X, Piece.O, Piece.BLANK, Piece.BLANK, Piece.X, Piece.BLANK, Piece.X, Piece.BLANK])
# board = Board(Piece.O, [Piece.O, Piece.O, Piece.BLANK, Piece.X, Piece.X, Piece.BLANK, Piece.O, Piece.BLANK, Piece.X]) # x win in 1
# print(board)
# print(make_move(board))


# while True:
#     # print(eval_board(board))
#     print(board)
#     board = make_move(board)
#     if board.over():
#         print(eval_board(board))
#         print(board)
#         break

EPSILON = 2**-20

Array = list[float]
Node = list[float]
Layer = list[Node]
Net = list[Layer]

def dot(a: Node, b: Node) -> float:
    assert len(a) == len(b)
    return sum((a[i]*b[i] for i in range(len(a))))

def sigmoid(n: float) -> float:
    return 1 / (1+exp(-n))

def random() -> float:
    return 5 - 10*r.random()


def str_node(node: Node) -> str:
    return "%.5f" % node[0] + " {" + ", ".join(("%.5f" % i for i in node[1:])) + "}"

def eval_node(node: Node, prev: Array) -> float:
    return sigmoid(node[0] + dot(node[1:], prev))

def new_node(weight_size: int, f: Callable[[], float]) -> Node:
    return list(f() for i in range(1 + weight_size))


def new_net(input_size: int, layer_sizes: list[int], f: Callable[[], float] = random) -> Net:
    return list(list(new_node(layer_sizes[i - 1] if i > 0 else input_size, f) for j in range(layer_sizes[i])) for i in range(len(layer_sizes)))

def str_net(net: Net) -> str:
    return "\n".join(", ".join(str_node(node) for node in layer) for layer in net)

def get_input_size(net: Net) -> int:
    return len(net[0][0]) - 1

def get_layer_sizes(net: Net) -> list[int]:
    return [len(net[i]) for i in range(len(net))]

def eval_net(net: Net, inp: Array) -> Array:
    state: list[Array] = [inp]
    for layer in net:
        state.append(list(eval_node(node, state[-1]) for node in layer))
    return state[-1]

def test_net(net: Net) -> float:
    BATCH_SIZE = 100
    first_index = r.randrange(0, len(oracle) - BATCH_SIZE)
    error: float = 0
    for inp, out in oracle[first_index:first_index+BATCH_SIZE]:
        test = eval_net(net, inp)
        for i in range(len(out)):
            error += (test[i] - out[i]) ** 2
    return error/BATCH_SIZE

def gradient_net(net: Net) -> Net:
    """Returns the normalized gradient of the net
    
    Output isn't literally a Net, just the derivatives.
    """
    gradient = new_net(get_input_size(net), get_layer_sizes(net), lambda: 0)
    error = test_net(net)
    def derivative(layer_i: int, node_i: int, val_i: int) -> float:
        new_node = deepcopy(node)
        new_node[val_i] += EPSILON
        new_net = deepcopy(net)
        new_net[layer_i][node_i] = new_node
        new_error = test_net(new_net)
        return (new_error - error) / EPSILON
    
    for layer_i in range(len(net)):
        layer = net[layer_i]
        for node_i in range(len(layer)):
            node = layer[node_i]
            for val_i in range(len(node)):
                gradient[layer_i][node_i][val_i] = derivative(layer_i, node_i, val_i)

    return gradient

def normalize(net: Net, r: float = 1) -> tuple[float, Net]:
    length: float = 0
    for layer_i in range(len(net)):
        layer = net[layer_i]
        for node_i in range(len(layer)):
            node = layer[node_i]
            for val_i in range(len(node)):
                length += node[val_i]**2
    new_net = deepcopy(net)
    for layer_i in range(len(net)):
        layer = net[layer_i]
        for node_i in range(len(layer)):
            node = layer[node_i]
            for val_i in range(len(node)):
                new_net[layer_i][node_i][val_i] *= r / length
    return length, new_net

def train_net(net: Net) -> Net:
    error = test_net(net)
    if False:
        # random net
        STEP_SIZE = 2**-4
        random_bias = .005
        i = 0
        while True:
            i += 1
            new_net = deepcopy(net)
            for layer_i in range(len(net)):
                layer = net[layer_i]
                for node_i in range(len(layer)):
                    node = layer[node_i]
                    for val_i in range(len(node)):
                        new_net[layer_i][node_i][val_i] += random() * STEP_SIZE / (i**.5)
            if test_net(new_net) < error or r.random() < random_bias:
                return new_net
    elif False:
        # gradient decent
        STEP_SIZE = 2**-5
        length, normalized = normalize(gradient_net(net), STEP_SIZE)
        print("length", length)
        new_net = deepcopy(net)
        for layer_i in range(len(net)):
            layer = net[layer_i]
            for node_i in range(len(layer)):
                node = layer[node_i]
                for val_i in range(len(node)):
                    new_net[layer_i][node_i][val_i] -= normalized[layer_i][node_i][val_i]
        return new_net
    else:
        # random derivative decent
        STEP_SIZE = 2**-10
        new_net = deepcopy(net)
        layer_i = r.randrange(0, len(net))
        layer = net[layer_i]
        node_i = r.randrange(0, len(layer))
        node = layer[node_i]
        val_i = r.randrange(0, len(node))
        new_net[layer_i][node_i][val_i] += EPSILON
        derivative = (test_net(new_net) - error) / EPSILON

        new_net = deepcopy(net)
        new_net[layer_i][node_i][val_i] -= derivative * STEP_SIZE
        return new_net

def board_to_input(board: Board) -> Array:
    # first input is whose turn it is, other inputs are the board state where 0: x, .5: blank, 1: o
    out: Array = [int(board.prev_player == Piece.X)]
    for tile in board.state:
        if tile == Piece.X:
            out.append(0)
        elif tile == Piece.BLANK:
            out.append(.5)
        else:
            out.append(1)
        # this would be the 28d input
        # out.append()
        # out.append(tile == Piece.X)
        # out.append(tile == Piece.O)
    return out

eval_board(Board.from_setup())
oracle: list[tuple[Array, Array]] = list()
for board, evaluation in _eval_cash.items():
    oracle.append((board_to_input(board), [(evaluation+1)/2]))
print("genned oracle")

# net = new_net(10, [16, 16, 3, 1])
# net = new_net(10, [10, 3, 1])
net = new_net(10, [10, 10, 1])


print(str_net(net))
best_net = net
best_net_eval = test_net(best_net)

for i in range(250):
    net = train_net(net)
    net_eval = test_net(net)
    if net_eval < best_net_eval:
        best_net = net
        best_net_eval = net_eval
    print(i, net_eval)
print(str_net(best_net))
print(best_net_eval)
