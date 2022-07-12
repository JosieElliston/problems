# just find verticies

from __future__ import annotations
import random
import timeit
import pygame
random.seed(2)
Color = tuple[int, int, int]

POINTS_PER_LINE = 1000
SCREEN_SIZE = 700
CELL_COUNT = 100
POINT_SIZE = 5


import math

class Point:
	def __init__(self, x: int, y: int) -> None:
		self.x: int = x
		self.y: int = y
	
	def to_drawable(self) -> tuple:
		return self.x * SCREEN_SIZE / POINTS_PER_LINE, self.y * SCREEN_SIZE / POINTS_PER_LINE
	
	def distance(self, other: Point) -> int:
		return (self.x - other.x) ** 2 + (self.y - other.y) ** 2
	
	def __str__(self) -> str:
		return "(" + str(self.x) + ", " + str(self.y) + ")"
	
	@classmethod
	def from_random(cls) -> Point:
		return Point(
			int(random.random() * POINTS_PER_LINE),
			int(random.random() * POINTS_PER_LINE)
		)
	
	# @classmethod
	# def from_midpoint(cls, p1: Point, p2: Point) -> Point:
	# 	return Point(
	# 		(p1.x + p2.x) // 2,
	# 		(p1.y + p2.y) // 2
	# 	)

	@classmethod
	def from_average(cls, points: list[Point]) -> Point:
		x = sum(p.x for p in points) // len(points)
		y = sum(p.y for p in points) // len(points)
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
		p = Point.from_random()
		if not is_collinear_or_coaxial(p, seeds):
			break
	seeds.append(p)

end = timeit.default_timer()
print("time to gen seeds", end - start)
start = timeit.default_timer()
verticies: list[Point] = [
	Point(0, 0),
	Point(POINTS_PER_LINE, 0),
	Point(0, POINTS_PER_LINE),
	Point(POINTS_PER_LINE, POINTS_PER_LINE)
]

def seed_of_point(p: Point) -> Point:
	best_seed: Point = seeds[0]
	best_distance: int = best_seed.distance(p)
	for seed in seeds:
		cur_distance = seed.distance(p)
		if cur_distance < best_distance:
			best_seed = seed
			best_distance = cur_distance
	return best_seed

def circumcenter(a: Point, b: Point, c: Point) -> Point:
	D: float = (a.x - c.x) * (b.y - c.y) - (b.x - c.x) * (a.y - c.y)
	# it might be ok to change this to integer division
	return Point(
		int((((a.x - c.x) * (a.x + c.x) + (a.y - c.y) * (a.y + c.y)) / 2 * (b.y - c.y) - ((b.x - c.x) * (b.x + c.x) + (b.y - c.y) * (b.y + c.y)) / 2 * (a.y - c.y)) / D),
		int((((b.x - c.x) * (b.x + c.x) + (b.y - c.y) * (b.y + c.y)) / 2 * (a.x - c.x) - ((a.x - c.x) * (a.x + c.x) + (a.y - c.y) * (a.y + c.y)) / 2 * (b.x - c.x)) / D)
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
			c: Point = circumcenter(seeds[i1], seeds[i2], seeds[i3])
			r: float = (seeds[i3].x - c.x) ** 2 + (seeds[i3].y - c.y) ** 2

			pruned_points: list[Point] = seeds.copy()
			pruned_points.pop(i3)
			pruned_points.pop(i2)
			pruned_points.pop(i1)

			if not_point_in_circle(r, c, pruned_points) and 0 < c.x < POINTS_PER_LINE and 0 < c.y < POINTS_PER_LINE:
				verticies.append(c) # {seeds[i1], seeds[i2], seeds[i3]}
				# self.delaunay_triangles[c].verticies.add(seeds[i1])
				# self.delaunay_triangles[c].verticies.add(seeds[i2])
				# self.delaunay_triangles[c].verticies.add(seeds[i3])
end = timeit.default_timer()
print("time for inner verticies", end - start)

def get_outline() -> set[Point]:	
	def distance_to_edge(p: Point) -> int:
		return min(
			p.x,
			p.y,
			POINTS_PER_LINE - p.x,
			POINTS_PER_LINE - p.y
		)

	outline: set[Point] = set()

	for x in range(0, POINTS_PER_LINE, 2):
		for y in range(0, POINTS_PER_LINE, 2):
			testing: Point = Point(x, y)
			step_seeds: set[Point] = set()
			step_seeds.add(seed_of_point(testing))
			step_seeds.add(seed_of_point(Point(testing.x + 1, testing.y)))
			step_seeds.add(seed_of_point(Point(testing.x - 1, testing.y)))
			step_seeds.add(seed_of_point(Point(testing.x, testing.y + 1)))
			step_seeds.add(seed_of_point(Point(testing.x, testing.y - 1)))
			if len(step_seeds) == 0:
				raise ValueError
			if distance_to_edge(testing) == 0:
				if len(step_seeds) > 2:
					raise ValueError
				elif len(step_seeds) == 1:
					outline.add(testing)
			else:
				if len(step_seeds) > 3:
					raise ValueError
				if len(step_seeds) == 2:
					outline.add(testing)
	return outline

	
def check_and_add(testing: Point, transformed1: Point, transformed2: Point) -> None:
	# step_seeds: set[Point] = set()
	# step_seeds.add(cell_of_point(testing))
	# step_seeds.add(cell_of_point(Point(testing.x + 1, testing.y)))
	# step_seeds.add(cell_of_point(Point(testing.x - 1, testing.y)))
	# step_seeds.add(cell_of_point(Point(testing.x, testing.y + 1)))
	# step_seeds.add(cell_of_point(Point(testing.x, testing.y - 1)))
	step_seeds: set[Point] = {seed_of_point(p) for p in {testing, transformed1, transformed2}}

	if len(step_seeds) == 0:
		raise ValueError
	if len(step_seeds) > 2:
		raise ValueError
	if len(step_seeds) == 2:
		verticies.append(Point(testing.x, testing.y))

start = timeit.default_timer()

for i in range(1, POINTS_PER_LINE, 2): # step = 2
	testing = Point(i, 0)
	transformed1 = Point(i - 1, 0)
	transformed2 = Point(i + 1, 0)
	check_and_add(testing, transformed1, transformed2)

	testing = Point(i, POINTS_PER_LINE)
	transformed1 = Point(i - 1, POINTS_PER_LINE)
	transformed2 = Point(i + 1, POINTS_PER_LINE)
	check_and_add(testing, transformed1, transformed2)

	testing = Point(0, i)
	transformed1 = Point(0, i - 1)
	transformed2 = Point(0, i + 1)
	check_and_add(testing, transformed1, transformed2)

	testing = Point(POINTS_PER_LINE, i)
	transformed1 = Point(POINTS_PER_LINE, i - 1)
	transformed2 = Point(POINTS_PER_LINE, i + 1)
	check_and_add(testing, transformed1, transformed2)


end = timeit.default_timer()
print("time for border verticies", end - start)


cell_mapping: dict[Point, Cell] = {seed: Cell(seed) for seed in seeds}

# MERGING_TOLERANCE = 4
# # merge verticies which are within the step size
# merged_verticies = set(verticies)

# def merge_pass() -> None:
# 	for p1 in prev_merged_verticies:
# 		for p2 in prev_merged_verticies:
# 			if p1 != p2 and p1.distance(p2) <= MERGING_TOLERANCE:
# 				merged_verticies.remove(p1)
# 				merged_verticies.remove(p2)
# 				merged_verticies.add(Point.from_average([p1, p2]))
# 				return

# while True:
# 	prev_merged_verticies = merged_verticies.copy()
# 	merge_pass()
# 	if len(merged_verticies) == len(prev_merged_verticies):
# 		break
# verticies = list(merged_verticies)
# # groups of verticies which are within a distance of each other
# # verticies come from merging the groups 
# verticie_groups: list[list[Point]] = list()
# for i1 in range(len(verticies)):
# 	p1 = verticies[i1]
# 	# if not [p1 in group for group in verticie_groups]:
# 	group = [p1]
# 	for i2 in range(i1 + 1, len(verticies)):
# 		p2 = verticies[i2]
# 		# should be if any point in group in close to p2, not just if p1 is close to p2
# 		if p1.distance(p2) <= MERGING_TOLERANCE:
# 			group.append(p2)
# 	verticie_groups.append(group)
# print([[str(p) for p in g] for g in verticie_groups if len(g) > 1])
# merged_verticies: list[Point] = list()
# for group in verticie_groups:
# 	merged_verticies.append(Point.from_average(group))
# verticies = merged_verticies

# add a verticie to cells which are within the tolerance
start = timeit.default_timer()
BELONGING_TOLERANCE = 4 # max(4, MERGING_TOLERANCE // 2)
for verticie in verticies:
	verticie_seeds: set[Point] = set()
	verticie_seeds.add(seed_of_point(verticie))
	for i in range(BELONGING_TOLERANCE):
		cur_tollerence = i + 1
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
	for p in seeds:
		pygame.draw.circle(screen, (0, 0, 255), p.to_drawable(), POINT_SIZE)
	for p in verticies:
		pygame.draw.circle(screen, (255, 0, 255), p.to_drawable(), POINT_SIZE)

	mouse_pos = pygame.mouse.get_pos()
	transformed_mouse = Point(int(mouse_pos[0] / SCREEN_SIZE * POINTS_PER_LINE), int(mouse_pos[1] / SCREEN_SIZE * POINTS_PER_LINE))
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