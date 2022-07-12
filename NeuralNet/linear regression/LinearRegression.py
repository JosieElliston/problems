# do linear regression, but with framework of neural net

from __future__ import annotations
import random
import timeit

with open("NeuralNet/income.data.csv") as file:
	data: list
	data = file.read().split("\n")
	data = [line.split(",") for line in data]
	data = [(float(line[1]), float(line[2])) for line in data]

data = [(0, .5), (.25, .5 + .125), (.5, .75), (.75, .75 + .125), (1, 1)]

class LinearFunction:
	def __init__(self, a: float, b: float) -> None:
		self.a = a
		self.b = b
		self.test = self._test()
	
	def __str__(self) -> str:
		return "{:10.9f}".format(f.a) + " " + "{:10.9f}".format(f.b) + " " +  "{:10.9f}".format(f.test)
		
	def eval(self, x: float) -> float:
		# evaluates based on the current coefficients
		return self.a * x + self.b
	
	def error(self, datai) -> float:
		# returns the square difference between evaluating the oracle and evaluating self
		return (data[datai][1] - self.eval(data[datai][0])) ** 2
	
	def _test(self) -> float:
		# returns the average of the errors of the input space
		return sum((self.error(i) for i in range(len(data)))) / len(data)
	
	def train_step(self) -> LinearFunction:
		# returns the improved linear function and how many iterations it took to find
		# i = 1
		# while True:
		# 	precision = 1 / i
		# 	testing = LinearFunction(self.a + (.5 - random.random()) * precision, self.b + (.5 - random.random()) * precision)
		# 	if testing.test < self.test:
		# 		return testing
		# 	i += 1
		
		EPSILON = .000001
		# how much does testing change if a is tweaked
		dtda = (self.test - LinearFunction(self.a + EPSILON, self.b).test) / EPSILON
		dtdb = (self.test -LinearFunction(self.a, self.b + EPSILON).test) / EPSILON
		# normalize derivative vector
		derivative_length: float = (dtda ** 2 + dtdb ** 2) ** .5
		delta_a = dtda / derivative_length
		delta_b = dtdb / derivative_length
		# step_multiplier = self.test ** .5
		
		return LinearFunction(self.a + (dtda), self.b + (dtda))
		return LinearFunction(self.a + delta_a * step_multiplier, self.b + delta_b * step_multiplier)

# 		# do steps in the direction of the derivative until the loss isn't minimized
# 		EPSILON = .000001
# 		dtda = (self.test - LinearFunction(self.a + EPSILON, self.b).test) / EPSILON
# 		dtdb = (self.test -LinearFunction(self.a, self.b + EPSILON).test) / EPSILON
# 		# normalize derivative vector
# 		derivative_length: float = (dtda ** 2 + dtdb ** 2) ** .5
# 		delta_a = dtda / derivative_length
# 		delta_b = dtdb / derivative_length

# 		# def get_hi() -> float:
# 			# finds an upper bound on the scaler
# 			# hi: float = 1
# 			# guess = LinearFunction(self.a + delta_a * hi, self.b + delta_b * hi)
# 			# if guess.test < self.test:
# 			# 	# guess was better than self, so increase the step until guess is worse
# 			# 	while True:
# 			# 		guess = LinearFunction(self.a + delta_a * hi, self.b + delta_b * hi)
# 			# 		if guess.test > self.test:
# 			# 			return hi
# 			# 		hi *= 2
# 			# else:
# 			# 	# guess was worse than self, so decrease the step until guess is better
# 			# 	while True:
# 			# 		guess = LinearFunction(self.a + delta_a * hi, self.b + delta_b * hi)
# 			# 		if guess.test < self.test:
# 			# 			return hi
# 			# 		hi /= 2
# 		def get_bounds() -> tuple[float, float]:
# 			lo: float = BISECT_TOLLERANCE # should relate to derivative
# 			hi: float = lo * 2
# 			while True:
# 				# print(lo, hi)
# 				lo_guess = LinearFunction(self.a + delta_a * lo, self.b + delta_b * lo)
# 				hi_guess = LinearFunction(self.a + delta_a * hi, self.b + delta_b * hi)
# 				if hi_guess.test > lo_guess.test:
# 					return lo, hi
# 				lo = hi
# 				hi *= 2

			
# 		# goal is to find the first(?) local min in the direction <delta_a, delta_b>

# 		BISECT_TOLLERANCE = 2 ** -20 # how close the previous two equaions must be to terminate # TODO: should relate to derivative
# 		# bounds on the scaler for the velctor <delta_a, delta_b>
# 		lo, hi = get_bounds()
# 		mid = (lo + hi) / 2
# 		# return LinearFunction(self.a + delta_a * mid, self.b + delta_b * mid)

# 		prev = self
# 		while True:
# 			mid = (lo + hi) / 2
# 			# print(lo, mid, hi)
# 			cur = LinearFunction(self.a + delta_a * mid, self.b + delta_b * mid)
# 			if abs(prev.test - cur.test) < BISECT_TOLLERANCE:
# 				return cur
# 			if cur.test > prev.test:
# 				lo = mid
# 			else:
# 				hi = mid
# 			prev = cur





		


# does training

# f = LinearFunction(.7138, .2043)
f = LinearFunction(0, 0)
print(f)
time: float = 0
while f.test > 2 ** -15:
	start = timeit.default_timer()
	f = f.train_step()
	end = timeit.default_timer()
	time += end - start
	print(f)
	# print()
print("took: ", time)


# finda all the points in the weight space

# precision = 100
# out: list[list[float]] = list()
# for i in range(precision):
# 	for j in range(precision):
# 		a = i / precision
# 		b = j / precision
# 		out.append([a, b, LinearFunction(a, b).test])
# print(out)
# print(len(out))
# # z_max = max(out, key = lambda p: p[2])
# # out = [line[0:2] + [line[2] ** .5] for line in out]
# with open("NeuralNet/coefficienterrors.txt", "w") as f:
# 	f.write("\n".join((" ".join((str(a) for a in line)) for line in out)))
