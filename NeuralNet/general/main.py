# simple neural net that outputs the input
# TODO: cash net evaluation on a node layer, calculating the gradient uses lots of recalculations, reset cash in gradient? don't update the cash for nodes that are changed in the derivative. only cash the original nodes
# TODO: problems:
    # output the single inputted node (only 1 activated input node)
    # output the last inputted node (many activated input nodes)
    # compression algorithm
    # evolution training
    # "convolutional"
    # is a number prime?

from __future__ import annotations
import random as r
from math import exp
from copy import deepcopy
from typing import Callable

from sympy import isprime
# from keras.datasets import mnist


r.seed(0)
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

# def add_net(net1: Net, net2: Net) -> Net:
#     out = deepcopy(net1)

def test_net(net: Net) -> float:
    error: float = 0
    for inp, out in oracle:
        test = eval_net(net, inp)
        for i in range(len(inp)):
            error += (test[i] - out[i]) ** 2
    return error

# def do_for_each(net: Net, f: Callable[[int, int, int], float]) -> Net:
#     new_net = deepcopy(net)

# TODO: put the annoying loop in a function and pass the inside operations as an argument 
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
    # TODO: use magnitude of the gradients somehow
    random_bias = .01
    STEP_SIZE = 2**-2
    error = test_net(net)
    if TRAIN_TYPE == "random net":
        while True:
            new_net = deepcopy(net)
            for layer_i in range(len(net)):
                layer = net[layer_i]
                for node_i in range(len(layer)):
                    node = layer[node_i]
                    for val_i in range(len(node)):
                        new_net[layer_i][node_i][val_i] += random() * STEP_SIZE
            if test_net(new_net) < error or r.random() < random_bias:
                return new_net
    elif TRAIN_TYPE == "random net reducing radius":
        i = 0
        while True:
            i += 1
            new_net = deepcopy(net)
            for layer_i in range(len(net)):
                layer = net[layer_i]
                for node_i in range(len(layer)):
                    node = layer[node_i]
                    for val_i in range(len(node)):
                        new_net[layer_i][node_i][val_i] += random() * STEP_SIZE / i
            if test_net(new_net) < error or r.random() < random_bias:
                return new_net
    elif TRAIN_TYPE == "random node":
        while True:
            new_net = deepcopy(net)
            layer_i = r.randrange(0, len(net))
            layer = net[layer_i]
            node_i = r.randrange(0, len(layer))
            node = layer[node_i]
            val_i = r.randrange(0, len(node))
            new_net[layer_i][node_i][val_i] += random() * STEP_SIZE
            if test_net(new_net) < error or r.random() < random_bias:
                return new_net
    elif TRAIN_TYPE == "random node reducing radius":
        i = 0
        while True:
            i += 1
            new_net = deepcopy(net)
            layer_i = r.randrange(0, len(net))
            layer = net[layer_i]
            node_i = r.randrange(0, len(layer))
            node = layer[node_i]
            val_i = r.randrange(0, len(node))
            new_net[layer_i][node_i][val_i] += random() * STEP_SIZE / i
            if test_net(new_net) < error or r.random() < random_bias:
                return new_net
    elif TRAIN_TYPE == "gradient decent":
        # proportional to STEP_SIZE, but not length of the vector
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
    elif TRAIN_TYPE == "derivative decent":
        return NotImplemented
        # choose the val with the max derivative
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
    elif TRAIN_TYPE == "gradient bisection":
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

    return NotImplemented

# # f(x) = x
# oracle: list[tuple[Array, Array]] = list()
# precision = 100
# for i in range(precision):
#     oracle.append(([i/precision], [i/precision]))

# f(x) = is_prime(x)
oracle: list[tuple[Array, Array]] = list()
UP_TO = 2**16
for i in range(UP_TO):
    if r.random() > .5:
        oracle.append(([int(l) for l in bin(i)[2:]], [isprime(i)]))


def write_input_output():
    with open("general/input_output.txt", mode = "w") as file:
        for inp, out in oracle:
            bin doesn't return 16 digets
            file.write(str(inp[0]) + ", " + str(eval_net(net, inp)[0]) + "\n") 

# TRAIN_TYPE = "random net" #0.31955847067148196
TRAIN_TYPE = "random net reducing radius" #0.19454636119734536
# TRAIN_TYPE = "random node" #0.26367770669679086
# TRAIN_TYPE = "random node reducing radius" #0.2549962551011183
# TRAIN_TYPE = "gradient decent" #0.5747421665894348
# TRAIN_TYPE = "derivative decent" #
# TRAIN_TYPE = "gradient bisection" #

net = new_net(16, [2, 2, 1])
print(str_net(net))
# write_input_output()
for i in range(150):
    net = train_net(net)
    print(i, test_net(net))
    write_input_output()
print(str_net(net))
