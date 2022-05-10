from __future__ import annotations
from math import perm
# from functools import lru_cache
import random
import pygame


Point = tuple[float, float]
Color = tuple[int, int, int]
INF = float("inf")


def delta_x(p1: Point, p2: Point) -> float:
	return p2[0] - p1[0]

def delta_y(p1: Point, p2: Point) -> float:
	return p2[1] - p1[1]

# def euclideian_distance(l: Point, r: Point) -> float:
# 	return (delta_x(l, r)**2 + delta_y(l, r)**2)**.5

def midpoint(p1: Point, p2: Point) -> Point:
	return (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2

class Line:
	"""def __init__(self, l: Point, r: Point, m: float, b: float):
		self.l = l
		self.r = r
		self.m = m
		self.b = b"""
		
	def __init__(self, y_int: float, x_int: float) -> None:
		self.y_int = y_int
		self.x_int = x_int

	@classmethod
	def from_point_slope(cls, p: Point, m: float) -> Line:
		return cls(
			p[1] - m * p[0] if m != INF else INF,
			p[0] - p[1] / m if m != 0 else INF
		)

	@classmethod
	def from_points(cls, p1: Point, p2: Point) -> Line:
		return Line.from_point_slope(
			p1,
			INF if p1[0] == p2[0] else delta_y(p1, p2) / delta_x(p1, p2)
		)
	
	def __str__(self) -> str:
		return "x_int: " + str(self.x_int) + " y_int: " + str(self.y_int)
	
	def y(self, x1: float) -> float:
		""" like evaluate f at x = x1 """
		assert self.y_int != INF
		if self.x_int == INF:
			return self.y_int
		else:
			return self.y_int * (1 - (x1 / self.x_int))

	def x(self, y1: float) -> float:
		assert self.x_int != INF
		if self.y_int == INF:
			return self.x_int
		else:
			return self.x_int * (1 - (y1 / self.y_int))
	
	def slope(self) -> float:
		if self.y_int == INF:
			return INF
		elif self.x_int == INF:
			return 0
		else:
			return -self.y_int / self.x_int
	
	def intersection(self, other: Line) -> Point:
		""" finds the intersection """
		# print(self, other)

		if other.slope() == self.slope():
			raise ValueError
		elif self.y_int == INF:
			return self.x_int, other.y(self.x_int)
		elif self.x_int == INF:
			return other.x(self.y_int), self.y_int
		elif other.y_int == INF:
			return other.x_int, self.y(other.x_int)
		elif other.x_int == INF:
			return self.x(other.y_int), other.y_int
		else:
			# print("and")
			x = (self.y_int - other.y_int) / (other.slope() - self.slope())
			assert abs((x * self.slope() + self.y_int) - (x * other.slope() + other.y_int)) < .0001
			return x, x * self.slope() + self.y_int

def segment_intersection(p1: Point, p2: Point, line: Line) -> bool:
	if p1[0] > p2[0]:
		return segment_intersection(p2, p1, line)
	return p1[0] < (Line.from_points(p1, p2).intersection(line))[0] < p2[0]

def count_segment_intersection(p1: Point, p2: Point, lines: set[Line]) -> int:
	return sum({segment_intersection(p1, p2, line) for line in lines})

# def intersections(target: Line, tools: set[Line] | set[Perpendicular_Bisector]) -> set[Point]:
# 	points: set[Point] = set()
# 	for tool in tools:
# 		points.add(target & tool)
# 	return points

def permutation_intersections(lines: set[Line]) -> set[Point]:
	points: set[Point] = set()
	for line1 in lines:
		other_lines = lines.copy()
		other_lines.remove(line1)
		for line2 in other_lines:
			points.add(line1.intersection(line2))
			print("line1", line1)
			print("line2", line2)
			print("intersection", line1.intersection(line2))
			print()
	return points

def two_set_intersections(lines1: set[Line], lines2: set[Line]) -> set[Point]:
	points: set[Point] = set()
	for line1 in lines1:
		for line2 in lines2:
			points.add(line1.intersection(line2))
	return points

# class Perpendicular_Bisector(Line):
# 	# the perpendicular bisector of the line segment between p1 and p2
# 	def __init__(self, p1: Point, p2: Point) -> None:
# 		m = 0 if p1[0] == p2[0] else -delta_x(p1, p2) / delta_y(p1, p2)
# 		mid = midpoint(p1, p2)
# 		super().__init__(
# 			mid[1] - m * mid[0] if m != INF else INF,
# 			mid[0] - mid[1] / m if m != 0 else INF
# 		)
# 		# self.p1 = p1
# 		# self.p2 = p2
# 		# self.mid = mid

class Voronoi_Graph:
	def __init__(self, seeds: set[Point]) -> None:
		self.seeds = seeds
		self.cells: set[Cell] = {Cell(seed, self) for seed in self.seeds}

	def draw(self, screen) -> None:
		for cell in self.cells:
			cell.draw(screen)

class Cell:
	BOUNDERIES = {Line(0, INF), Line(1, INF), Line(INF, 0), Line(INF, 1)}


	def __init__(self, origin: Point, graph: Voronoi_Graph) -> None:
		print()
		print("origin", origin)
		self.color: Color = (random.randrange(256), random.randrange(256), random.randrange(256))
		self.neighbors: set[Cell] = set()
		self.origin = origin
		self.graph = graph
		other_seeds = graph.seeds.copy()
		other_seeds.remove(self.origin)

		# perpendicular_bisectors: set[Perpendicular_Bisector] = {Perpendicular_Bisector(self.origin, seed) for seed in other_seeds}
		perpendicular_bisectors: set[Line] = {Line.from_point_slope(midpoint(self.origin, seed), 0 if self.origin[0] == seed[0] else -delta_x(self.origin, seed) / delta_y(self.origin, seed)) for seed in other_seeds}
		self.verticies: set[Point] = permutation_intersections(perpendicular_bisectors)
		self.verticies.update(two_set_intersections(Cell.BOUNDERIES, perpendicular_bisectors))
		
		# 		self.verticies = set(filter(lambda verticie: count_segment_intersection(origin, verticie, perpendicular_bisectors) == 0, self.verticies))

		self.verticies = set(filter(lambda verticie: count_segment_intersection(origin, verticie, perpendicular_bisectors.union(Cell.BOUNDERIES)) == 0, self.verticies))
	actaully this still intersects on the domain of the line
		# self.verticies.update({(0, 0), (0, 1), (1, 1), (1, 0)})
		print("self.verticies:", self.verticies)

	def gen_neighbors(self) -> None:
		# run after all cells have been generated
		for cell in Voronoi_Graph.cells:
			if len(cell.verticies & self.verticies) != 0:
				self.neighbors.add(cell)
	
	def draw(self, screen) -> None:
		draw_points: list[Point] = [(p[0] * SCREEN_SIZE, p[1] * SCREEN_SIZE) for p in self.verticies]
		# pygame.draw.polygon(screen, self.color, draw_points)
		for p1 in draw_points:
			other_verticies = draw_points.copy()
			other_verticies.remove(p1)
			for p2 in other_verticies:
				pygame.draw.aaline(screen, self.color, p1, p2)
		pygame.draw.circle(screen, (0, 0, 0), transformed_point(self.origin), 4, width=0)

random.seed(0)

SCREEN_SIZE = 700
CELL_NUMBER = 5

def transformed_point(p: Point) -> Point:
	return p[0] * SCREEN_SIZE, p[1] * SCREEN_SIZE
seeds: set[Point] = {(random.random(), random.random()) for i in range(CELL_NUMBER)}
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
graph = Voronoi_Graph(seeds)
pygame.init()
run: bool = True

screen.fill((255, 255, 255))
graph.draw(screen)
pygame.display.flip()
while run:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False