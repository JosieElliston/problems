from __future__ import annotations
import random
import timeit
from typing import Collection
import pygame
import math
random.seed(0)
Color = tuple[int, int, int]

SCREEN_SIZE = 700
CELL_COUNT = 100
POINT_SIZE = 5
PRECISION = 1/500

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
	def from_average(cls, points: Collection[Point]) -> Point:
		if len(points) == 1:
			for point in points:
				return point
		x = sum(p.x for p in points) / len(points)
		y = sum(p.y for p in points) / len(points)
		return Point(x, y)

class Verticie(Point):
	def __init__(self, x: float, y: float, seeds: set[Point]):
		super().__init__(x, y)
		self.seeds = seeds
	
	@classmethod
	def from_midpoint(cls, v1: Verticie, v2: Verticie) -> Verticie:
		# if either point is on the border, return a point on the border
		if v1.x == 0 or v1.x == 1 or v1.y == 0 or v1.y == 1:
			return Verticie(v1.x, v1.y, v1.seeds | v2.seeds)
		elif v2.x == 0 or v2.x == 1 or v2.y == 0 or v2.y == 1:
			return Verticie(v2.x, v2.y, v1.seeds | v2.seeds)
		else:
			return Verticie(
				(v1.x + v2.x) / 2,
				(v1.y + v2.y) / 2,
				v1.seeds | v2.seeds
			)

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
		self.neighbors: set[Point] = set()
	
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

seeds: list[Point] = [Point.random() for i in range(CELL_COUNT)]
# start = timeit.default_timer()
# seeds: list[Point] = list()

# for i in range(CELL_COUNT):
# 	while True:
# 		p = Point.random()
# 		if not is_collinear_or_coaxial(p, seeds):
# 			break
# 	seeds.append(p)

# end = timeit.default_timer()
# print("time to gen seeds", end - start)
start = timeit.default_timer()
def seed_of_point(p: Point) -> Point:
	best_seed: Point = seeds[0]
	best_distance: float = best_seed.distance(p)
	for seed in seeds:
		cur_distance = seed.distance(p)
		if cur_distance < best_distance:
			best_seed = seed
			best_distance = cur_distance
	return best_seed

verticies: list[Verticie] = [
	Verticie(0, 0, {seed_of_point(Point(0, 0))}),
	Verticie(1, 0, {seed_of_point(Point(1, 0))}),
	Verticie(0, 1, {seed_of_point(Point(0, 1))}),
	Verticie(1, 1, {seed_of_point(Point(1, 1))})
]



# def circumcenter(a: Point, b: Point, c: Point) -> tuple[float, float]:
# 	d: float = (a.x - c.x) * (b.y - c.y) - (b.x - c.x) * (a.y - c.y)
# 	return (
# 		(((a.x - c.x) * (a.x + c.x) + (a.y - c.y) * (a.y + c.y)) / 2 * (b.y - c.y) - ((b.x - c.x) * (b.x + c.x) + (b.y - c.y) * (b.y + c.y)) / 2 * (a.y - c.y)) / d,
# 		(((b.x - c.x) * (b.x + c.x) + (b.y - c.y) * (b.y + c.y)) / 2 * (a.x - c.x) - ((a.x - c.x) * (a.x + c.x) + (a.y - c.y) * (a.y + c.y)) / 2 * (b.x - c.x)) / d
# 	)

# check whether any point in pruned_points is contained in the circle defined by r and c
def not_point_in_circle(r: float, center: Point, pruned_points: list[Point]) -> bool:
	for p in pruned_points:
		if center.distance(p) < r:
			return False
	return True

for i1 in range(len(seeds)):
	for i2 in range(i1 + 1, len(seeds)):
		for i3 in range(i2 + 1, len(seeds)):
			a, b, c = seeds[i1], seeds[i2], seeds[i3]
			d: float = (a.x - c.x) * (b.y - c.y) - (b.x - c.x) * (a.y - c.y)
			if d != 0:
				circumcenter_x = (((a.x - c.x) * (a.x + c.x) + (a.y - c.y) * (a.y + c.y)) / 2 * (b.y - c.y) - ((b.x - c.x) * (b.x + c.x) + (b.y - c.y) * (b.y + c.y)) / 2 * (a.y - c.y)) / d
				circumcenter_y = (((b.x - c.x) * (b.x + c.x) + (b.y - c.y) * (b.y + c.y)) / 2 * (a.x - c.x) - ((a.x - c.x) * (a.x + c.x) + (a.y - c.y) * (a.y + c.y)) / 2 * (b.x - c.x)) / d

				if 0 < circumcenter_x < 1 and 0 < circumcenter_y < 1:
					circumcenter = Verticie(circumcenter_x, circumcenter_y, {seeds[i1], seeds[i2], seeds[i3]})
					r: float = (seeds[i3].x - circumcenter.x) ** 2 + (seeds[i3].y - circumcenter.y) ** 2

					pruned_points: list[Point] = seeds.copy()
					pruned_points.pop(i3)
					pruned_points.pop(i2)
					pruned_points.pop(i1)

					if not_point_in_circle(r, circumcenter, pruned_points):
						verticies.append(circumcenter)
end = timeit.default_timer()
print("time for inner verticies", end - start)

def check_and_add(testing: Point, transformed1: Point, transformed2: Point) -> None:
	step_seeds: set[Point] = {seed_of_point(p) for p in {testing, transformed1, transformed2}}

	if len(step_seeds) == 0:
		raise ValueError
	if len(step_seeds) > 2:
		raise ValueError
	if len(step_seeds) == 2:
		verticies.append(Verticie(testing.x, testing.y, step_seeds))

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

start = timeit.default_timer()
# if two verticies are within the belonging tolerance, merge them

BELONGING_TOLERANCE = 1/10000
def merge_verticies() -> None:
	for i1 in range(len(verticies)):
		v1 = verticies[i1]
		for i2 in range(i1 + 1, len(verticies)):
			v2 = verticies[i2]
			if v1 != v2 and v1.distance(v2) < BELONGING_TOLERANCE:
				verticies.append(Verticie.from_midpoint(v1, v2))
				verticies.remove(v1)
				verticies.remove(v2)
				return

unmerged_verticies = verticies.copy()
while True:
	prev_len = len(verticies)
	merge_verticies()
	if prev_len == len(verticies):
		break

for verticie in verticies:
	for seed in verticie.seeds:
		cell_mapping[seed].verticies.append(verticie)
		for neighbor in verticie.seeds:
			if neighbor != seed:
				cell_mapping[seed].neighbors.add(neighbor)

end = timeit.default_timer()
print("time to distribute verticies", end - start)


# print(" ".join(map(str, sorted(verticies, key = lambda p: p.x + p.y, reverse = True))))

assert len(verticies) == len(set(verticies))

# sort verticies so that drawing works
for cell in cell_mapping.values():
	assert len(cell.verticies) == len(set(cell.verticies))
	cell.verticies = sorted(cell.verticies, key = lambda p: clockwiseangle_and_distance(p, cell.seed))

pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
while not pygame.QUIT in [event.type for event in pygame.event.get()]:
	screen.fill((0, 0, 0))
	
	for cell in cell_mapping.values():
		cell.draw()
	for p in seeds:
		pygame.draw.circle(screen, (0, 0, 255), p.to_drawable(), POINT_SIZE)
	# show the difference with merging
	if True in pygame.key.get_pressed():
		for p in unmerged_verticies:
			pygame.draw.circle(screen, (255, 0, 255), p.to_drawable(), POINT_SIZE)
	else:
		for p in verticies:
			pygame.draw.circle(screen, (255, 0, 255), p.to_drawable(), POINT_SIZE)
	
	# draw stuff from mouse pos
	mouse_pos = pygame.mouse.get_pos()
	transformed_mouse = Point(mouse_pos[0] / SCREEN_SIZE, mouse_pos[1] / SCREEN_SIZE)
	seed_of_mouse: Point = seed_of_point(transformed_mouse)
	cell_of_mouse: Cell = cell_mapping[seed_of_mouse]
	pygame.draw.circle(screen, (255, 255, 255), cell_of_mouse.seed.to_drawable(), POINT_SIZE)
	# for p in cell_of_mouse.verticies:
	# 	pygame.draw.circle(screen, (255, 255, 255), p.to_drawable(), POINT_SIZE)
	for p in cell_of_mouse.neighbors:
		pygame.draw.circle(screen, (255, 255, 255), p.to_drawable(), POINT_SIZE)
	
	
	
	pygame.display.flip()