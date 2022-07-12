# delaunay4 but with fixed point arithmetic

# just find verticies

from __future__ import annotations
import random
import timeit
from typing import Collection
import pygame
import math
random.seed(2)
Color = tuple[int, int, int]

# POINTS_PER_LINE = 1000
SCREEN_SIZE = 1300
CELL_COUNT = 50
POINT_SIZE = 5
PRECISION = 1/500

# number on domain [0, 1]
class fixed:
	MIN = 0
	MAX = 2**32

	def __init__(self, val: int) -> None:
		self.val = val

	@classmethod
	def random(cls) -> fixed:
		return fixed(random.randint(cls.MIN, cls.MAX))
	
	def __float__(self) -> float:
		return self.val / fixed.MAX
	
	@classmethod
	def average(cls, vals: Collection[fixed]) -> fixed:
		raise NotImplemented

class Point:
	def __init__(self, x: float, y: float) -> None:
		assert -.1 <= x <= 1.1
		assert -.1 <= y <= 1.1
		self.x = x
		self.y = y
	
	def to_drawable(self) -> tuple:
		return self.x * SCREEN_SIZE, self.y * SCREEN_SIZE
	
	def distance(self, other: Point) -> float:
		return (self.x - other.x) ** 2 + (self.y - other.y) ** 2
	
	def __str__(self) -> str:
		return "(" + str(self.x) + ", " + str(self.y) + ")"
	
	@classmethod
	def random(cls) -> Point: # TODO change to fixed
		return Point(
			random.random(),
			random.random()
		)
	
	# @classmethod
	# def from_midpoint(cls, p1: Point, p2: Point) -> Point:
	# 	return Point(
	# 		(p1.x + p2.x) // 2,
	# 		(p1.y + p2.y) // 2
	# 	)

	@classmethod
	def from_average(cls, points: list[Point]) -> Point:
		x = sum(p.x for p in points) / len(points)
		y = sum(p.y for p in points) / len(points)
		return Point(x, y)

def clockwiseangle_and_distance(point: Point, origin: Point) -> float:
	refvec = [0, 1]
	# Vector between point and the origin: v = p - o
	vector = [point.x-origin.x, point.y-origin.y]

	dotprod  = vector[0]*refvec[0] + vector[1]*refvec[1]     # x1*x2 + y1*y2
	diffprod = refvec[1]*vector[0] - refvec[0]*vector[1]     # x1*y2 - y1*x2
	angle = math.atan2(diffprod, dotprod)
	# Negative angles represent counter-clockwise angles so we need to subtract them 
	# from 2*pi (360 degrees)
	if angle < 0:
		return 2*math.pi+angle
	# I return first the angle because that's the primary sorting criterium
	# but if two vectors have the same angle then the shorter distance should come first.
	return angle

class Cell:
	def __init__(self, seed: Point) -> None:
		self.seed: Point = seed
		self.verticies: list[Point] = list()
		self.color: Color = random.randrange(256), random.randrange(256), random.randrange(256)
	
	def draw(self) -> None:
		pygame.draw.polygon(screen, self.color, [verticie.to_drawable() for verticie in self.verticies])
		# pygame.draw.circle(screen, (0, 0, 255), self.seed.to_drawable(), PIXEL_SIZE)
		# for p in self.verticies:
		# 	pygame.draw.circle(screen, (255, 0, 255), p.to_drawable(), PIXEL_SIZE)

def is_collinear_or_coaxial(c: Point, points: list[Point]) -> bool:
	# if len(points) < 2:
	# 	return False
	
	for i in range(len(points)):
		a: Point = points[i]
		if c.x == a.x:
			return True
		if c.y == a.y:
			return True
		for j in range(i + 1, len(points)):
			b: Point = points[j]
			if (a.x - c.x) * (b.y - c.y) - (b.x - c.x) * (a.y - c.y) == 0:
				return True
	return False

# seeds: list[Point] = [Point.from_random() for i in range(CELL_COUNT)]
start = timeit.default_timer()
seeds: list[Point] = list()

for i in range(CELL_COUNT):
	while True:
		p = Point.random()
		if not is_collinear_or_coaxial(p, seeds):
			break
	seeds.append(p)

end = timeit.default_timer()
print("time to gen seeds", end - start)
start = timeit.default_timer()
verticies: list[Point] = [
	Point(0, 0),
	Point(1, 0),
	Point(0, 1),
	Point(1, 1)
]

def seed_of_point(p: Point) -> Point:
	best_seed: Point = seeds[0]
	best_distance: float = best_seed.distance(p)
	for seed in seeds:
		cur_distance = seed.distance(p)
		if cur_distance < best_distance:
			best_seed = seed
			best_distance = cur_distance
	return best_seed

def circumcenter(a: Point, b: Point, c: Point) -> tuple[float, float]:
	D: float = (a.x - c.x) * (b.y - c.y) - (b.x - c.x) * (a.y - c.y)
	# it might be ok to change this to integer division
	return (
		(((a.x - c.x) * (a.x + c.x) + (a.y - c.y) * (a.y + c.y)) / 2 * (b.y - c.y) - ((b.x - c.x) * (b.x + c.x) + (b.y - c.y) * (b.y + c.y)) / 2 * (a.y - c.y)) / D,
		(((b.x - c.x) * (b.x + c.x) + (b.y - c.y) * (b.y + c.y)) / 2 * (a.x - c.x) - ((a.x - c.x) * (a.x + c.x) + (a.y - c.y) * (a.y + c.y)) / 2 * (b.x - c.x)) / D
	)

# check whether any point in pruned_points is contained in the circle defined by r and c
def not_point_in_circle(r: float, center: Point, pruned_points: list[Point]) -> bool:
	for p in pruned_points:
		if center.distance(p) < r:
			return False
	return True

for i1 in range(len(seeds)):
	for i2 in range(i1 + 1, len(seeds)):
		for i3 in range(i2 + 1, len(seeds)):
			c_tup = circumcenter(seeds[i1], seeds[i2], seeds[i3])
			if 0 < c_tup[0] < 1 and 0 < c_tup[1] < 1:
				c: Point = Point(c_tup[0], c_tup[1])
				r: float = (seeds[i3].x - c.x) ** 2 + (seeds[i3].y - c.y) ** 2

				pruned_points: list[Point] = seeds.copy()
				pruned_points.pop(i3)
				pruned_points.pop(i2)
				pruned_points.pop(i1)

				if not_point_in_circle(r, c, pruned_points):
					verticies.append(c)
end = timeit.default_timer()
print("time for inner verticies", end - start)

def check_and_add(testing: Point, transformed1: Point, transformed2: Point) -> None:
	step_seeds: set[Point] = {seed_of_point(p) for p in {testing, transformed1, transformed2}}

	if len(step_seeds) == 0:
		raise ValueError
	if len(step_seeds) > 2:
		raise ValueError
	if len(step_seeds) == 2:
		verticies.append(Point(testing.x, testing.y))

start = timeit.default_timer()

for i in range(1, int(1 / PRECISION), 2): # step = 2
	coord = PRECISION * i
	testing = Point(coord, 0)
	transformed1 = Point(coord - PRECISION, 0)
	transformed2 = Point(coord + PRECISION, 0)
	check_and_add(testing, transformed1, transformed2)

	testing = Point(coord, 1)
	transformed1 = Point(coord - PRECISION, 1)
	transformed2 = Point(coord + PRECISION, 1)
	check_and_add(testing, transformed1, transformed2)

	testing = Point(0, coord)
	transformed1 = Point(0, coord - PRECISION)
	transformed2 = Point(0, coord + PRECISION)
	check_and_add(testing, transformed1, transformed2)

	testing = Point(1, coord)
	transformed1 = Point(1, coord - PRECISION)
	transformed2 = Point(1, coord + PRECISION)
	check_and_add(testing, transformed1, transformed2)


end = timeit.default_timer()
print("time for border verticies", end - start)

cell_mapping: dict[Point, Cell] = {seed: Cell(seed) for seed in seeds}

# add a verticie to cells which are within the tolerance
start = timeit.default_timer()
BELONGING_TOLERANCE = 4 # max(4, MERGING_TOLERANCE // 2)
for verticie in verticies:
	verticie_seeds: set[Point] = set()
	verticie_seeds.add(seed_of_point(verticie))
	for i in range(BELONGING_TOLERANCE):
		cur_tollerence = (i + 1) * PRECISION
		verticie_seeds.add(seed_of_point(Point(verticie.x + cur_tollerence, verticie.y)))
		verticie_seeds.add(seed_of_point(Point(verticie.x - cur_tollerence, verticie.y)))
		verticie_seeds.add(seed_of_point(Point(verticie.x, verticie.y + cur_tollerence)))
		verticie_seeds.add(seed_of_point(Point(verticie.x, verticie.y - cur_tollerence)))
		verticie_seeds.add(seed_of_point(Point(verticie.x + cur_tollerence, verticie.y + cur_tollerence)))
		verticie_seeds.add(seed_of_point(Point(verticie.x + cur_tollerence, verticie.y - cur_tollerence)))
		verticie_seeds.add(seed_of_point(Point(verticie.x - cur_tollerence, verticie.y + cur_tollerence)))
		verticie_seeds.add(seed_of_point(Point(verticie.x - cur_tollerence, verticie.y - cur_tollerence)))
	for seed in verticie_seeds:
		cell_mapping[seed].verticies.append(verticie)
end = timeit.default_timer()
print("time to distribite verticies", end - start)
for cell in cell_mapping.values():
	# print(cell.verticies)
	# print()
	assert len(cell.verticies) == len(set(cell.verticies))

for cell in cell_mapping.values():
	cell.verticies = sorted(cell.verticies, key = lambda p: clockwiseangle_and_distance(p, cell.seed))

pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
# clock = pygame.time.Clock()
while not pygame.QUIT in [event.type for event in pygame.event.get()]:
	# clock.tick(1)
	screen.fill((0, 0, 0))
	for cell in cell_mapping.values():
		cell.draw()
	# for p in outline:
	# 	pygame.draw.circle(screen, (50, 50, 50), p.to_drawable(), PIXEL_SIZE)
	# for p in seeds:
	# 	pygame.draw.circle(screen, (0, 0, 255), p.to_drawable(), POINT_SIZE)
	# for p in verticies:
	# 	pygame.draw.circle(screen, (255, 0, 255), p.to_drawable(), POINT_SIZE)

	mouse_pos = pygame.mouse.get_pos()
	transformed_mouse = Point(mouse_pos[0] / SCREEN_SIZE, mouse_pos[1] / SCREEN_SIZE)
	# closest_verticie: Point = verticies[0]
	# best_distance: int = closest_verticie.distance(transformed_mouse)
	# for verticie in verticies:
	# 	cur_distance = verticie.distance(transformed_mouse)
	# 	if cur_distance < best_distance:
	# 		closest_verticie = verticie
	# 		best_distance = cur_distance
	# pygame.draw.circle(screen, (255, 0, 0), closest_verticie.to_drawable(), PIXEL_SIZE)
	# for seed in closest_verticie.seeds:
	# 	pygame.draw.circle(screen, (255, 0, 255), seed.to_drawable(), PIXEL_SIZE)


	seed_of_mouse: Point = seed_of_point(transformed_mouse)
	cell_of_mouse: Cell = cell_mapping[seed_of_mouse]
	for p in cell_of_mouse.verticies:
		pygame.draw.circle(screen, (255, 255, 255), p.to_drawable(), POINT_SIZE)
	
	# pygame.draw.circle(screen, (255, 255, 255), seed_of_point(transformed_mouse).to_drawable(), PIXEL_SIZE)

	
	pygame.display.flip()