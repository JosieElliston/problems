from __future__ import annotations
import copy
from math import exp
import random
# random.seed(1)

def oracle(x1: float, x2: float) -> float:
	# like xor but analogue
	# ie (.5, .5) => 1
	return 1 - abs(x1 - 1 + x2)

def sigmoid(n: float) -> float:
	return 1 / (1+exp(-n))

Node = tuple[list[float], float] # a Node has list[weight] and a bias

def dot(a: list[float], b: list[float]) -> float:
	assert len(a) == len(b)
	return sum((a[i]*b[i] for i in range(len(a))))

class NeuralNet:
	def __init__(self, weights: list[list[list[float]]], biases: list[list[float]]) -> None: # a: Node, b: Node, c: Node # nodes: list[list[Node]]
		self.weights = weights
		self.biases = biases
		self.test = self._test()
	
	@classmethod
	def as_base(cls, input: int, hidden: list[int], output: int) -> NeuralNet:
		# parameters are the lenght of the input, hidden, and output layers
		nodes = [input] + hidden + [output]
		return NeuralNet(
			[[[random.random() for i in range(nodes[layeri - 1])] for node in range(nodes[layeri])] for layeri in range(1, len(nodes))],
			[[random.random() for i in range(layer)] for layer in nodes[1:]]
		)

	def __str__(self) -> str:
		return " ".join(("{:.7f}".format(a) for a in [self.eval(0, 0), self.eval(0, 1), self.eval(1, 0), self.eval(1, 1)])) + " " + "{:.15f}".format(self.test)

	def eval(self, x1: float, x2: float) -> float:
		# evaluates based on the current weights
		vals = [x1, x2]
		for layeri in range(len(self.weights)):
			layer_weights = self.weights[layeri]
			layer_biases = self.biases[layeri]
			new_vals: list[float] = [0 for i in range(len(layer_weights))]
			for nodei in range(len(layer_weights)):
				node_weights = layer_weights[nodei]
				node_bias = layer_biases[nodei]
				new_vals[nodei] = sigmoid(dot(vals, node_weights) + node_bias)
			vals = new_vals

		assert len(vals) == 1
		return vals[0]

	def error(self, x1: float, x2: float) -> float:
		# returns the square difference between evaluating the oracle and evaluating self
		return (oracle(x1, x2) - self.eval(x1, x2)) ** 2
	
	def _test(self) -> float:
		# returns the sum of the errors of the input space with step sizes of 1 / PRECISION
		# if PRECISION is 1, it tests the boolean xor
		PRECISION: int = 3
		out: float = 0
		for i in range(PRECISION + 1):
			for j in range(PRECISION + 1):
				out += self.error(i / PRECISION, j / PRECISION)
		# return sum((self.error(i / PRECISION, j / PRECISION) for j in range(PRECISION + 1) for i in range(PRECISION + 1)))
		return out
	
	def train_step(self) -> NeuralNet:
		def random_step() -> NeuralNet:
			def rand_offset(x: float) -> float:
				return x + (.5 - random.random())
			while True:
				testing = NeuralNet(
					[[[rand_offset(weight) for weight in node] for node in layer] for layer in self.weights],
					[[rand_offset(bias) for bias in layer] for layer in self.biases]
				)
				if testing.test < self.test:
					return testing
			# only change one var
			while True:
				layeri = random.randrange(0, len(self.weights))
				nodei = random.randrange(0, len(self.weights[layeri]))
				if random.random() > .5:
					weighti = random.randrange(0, len(self.weights[layeri][nodei]))
					new_weights = copy.deepcopy(self.weights)
					new_weights[layeri][nodei][weighti] = rand_offset(new_weights[layeri][nodei][weighti])
					testing = NeuralNet(
						new_weights,
						self.biases
					)
				else:
					new_biases = copy.deepcopy(self.biases)
					new_biases[layeri][nodei] = rand_offset(new_biases[layeri][nodei])
					testing = NeuralNet(
						self.weights,
						new_biases
					)
				if testing.test < self.test:
					return testing

		def dertivative_step() -> NeuralNet:
			EPSILON = 2 ** -16
			def get_dtdw() -> list[list[list[float]]]:
				dtdw: list[list[list[float]]] = list()
				for layeri in range(len(self.weights)):
					layer = self.weights[layeri]
					layer_derivatives: list[list[float]] = list()
					for nodei in range(len(layer)):
						node = layer[nodei]
						node_derivatives: list[float] = list()
						for weighti in range(len(node)):
							new_weights = copy.deepcopy(self.weights)
							new_weights[layeri][nodei][weighti] += EPSILON
							weight_derivative = (self.test - NeuralNet(new_weights, self.biases).test) / EPSILON
							node_derivatives.append(weight_derivative)
						layer_derivatives.append(node_derivatives)
					dtdw.append(layer_derivatives)
				return dtdw

			def get_dtdb() -> list[list[float]]:
				dtdb: list[list[float]] = list()
				for layeri in range(len(self.biases)):
					layer = self.biases[layeri]
					layer_derivatives: list[float] = list()
					for nodei in range(len(layer)):
						new_biases = copy.deepcopy(self.biases)
						new_biases[layeri][nodei] += EPSILON
						node_derivative = (self.test - NeuralNet(self.weights, new_biases).test) / EPSILON
						layer_derivatives.append(node_derivative)
					dtdb.append(layer_derivatives)
				return dtdb
			
			step_multiplier = 1
			dtdw = get_dtdw()
			dtdb = get_dtdb()

			# print(dtdw)
			# print(dtdb)

			# def new_weights() -> list[list[list[float]]]:
			# 	new_weights: list[list[list[float]]] = list()
			# 	for layeri in range(len(self.weights)):
			# 		layer = self.weights[layeri]
			# 		new_layer: list[list[float]] = list()
			# 		for nodei in range(len(layer)):
			# 			node = layer[nodei]
			# 			new_node: list[float] = list()
			# 			for weighti in range(len(node)):
			# 				new_node.append(layer[nodei][weighti] + dtdw[layeri][nodei][weighti] * step_multiplier)
			# 			new_layer.append(new_node)
			# 		new_weights.append(new_layer)
			# 	return new_weights
			
			# def new_biases() -> list[list[float]]:
			# 	new_biases: list[list[float]] = list()
			# 	for layeri in range(len(self.biases)):
			# 		layer = self.biases[layeri]
			# 		new_layer: list[float] = list()
			# 		for biasi in range(len(layer)):
			# 			new_layer.append(layer[biasi] + dtdb[layeri][biasi] * step_multiplier)
			# 		new_biases.append(new_layer)
			# 	return new_biases

			# move only the thing with the max derivative

			def new_weights() -> list[list[list[float]]]:
				max_derivative = dtdw[0][0][0]
				max_layeri = 0
				max_nodei = 0
				max_weighti = 0
				for layeri in range(len(self.weights)):
					layer = self.weights[layeri]
					for nodei in range(len(layer)):
						node = layer[nodei]
						for weighti in range(len(node)):
							derivative = dtdw[layeri][nodei][weighti] ** 2
							if derivative > max_derivative:
								max_derivative = derivative
								max_layeri = layeri
								max_nodei = nodei
								max_weighti = weighti

				new_weights = copy.deepcopy(self.weights)
				new_weights[max_layeri][max_nodei][max_weighti] = self.weights[max_layeri][max_nodei][max_weighti] + dtdw[max_layeri][max_nodei][max_weighti] * step_multiplier
				# print(max_derivative ** .5)
				return new_weights
			
			def new_biases() -> list[list[float]]:
				max_derivative = dtdb[0][0]
				max_layeri = 0
				max_nodei = 0
				for layeri in range(len(self.biases)):
					layer = self.biases[layeri]
					for nodei in range(len(layer)):
						derivative = dtdb[layeri][nodei] ** 2
						if derivative > max_derivative:
							max_derivative = derivative
							max_layeri = layeri
							max_nodei = nodei

				new_biases = copy.deepcopy(self.biases)
				new_biases[max_layeri][max_nodei] = self.biases[max_layeri][max_nodei] + dtdb[max_layeri][max_nodei] * step_multiplier
				# print(max_derivative ** .5)
				return new_biases

			return NeuralNet(new_weights(), new_biases())
		# if random.random() > .9:
		# 	return dertivative_step()
		# else:
		return random_step()

net = NeuralNet.as_base(2, [2], 1)
i = 0
while True:
	print(net, i)
	# print(net.weights, net.biases)
	if net.test < .1: break
	net = net.train_step()
	i += 1

precision = 30
out: list[list[float]] = list()
for i in range(precision):
	for j in range(precision):
		a = i / precision
		b = j / precision
		out.append([a, b, net.eval(a, b)])

with open("NeuralNet/inputoutput.txt", "w") as f:
	f.write("\n".join((" ".join((str(a) for a in line)) for line in out)))
