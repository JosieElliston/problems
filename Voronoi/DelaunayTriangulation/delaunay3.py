# just find verticies

from __future__ import annotations
import random
import timeit
import pygame
random.seed(2)
Color = tuple[int, int , int]

POINTS_PER_LINE = 500
SCREEN_SIZE = 1300
CELL_COUNT = 50
PIXEL_SIZE = 5

# each delauny triangle contribues 3 edges to 3 voronoi tiles

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

class Verticie(Point):
	def __init__(self, x: int, y: int, seeds: set[Point]) -> None:
		Point.__init__(self, x, y)
		self.seeds = seeds

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
		self.verticies: list[Verticie] = list()
		self.color: Color = random.randrange(256), random.randrange(256), random.randrange(256)
	
	def draw(self) -> None:
		pygame.draw.polygon(screen, self.color, [verticie.to_drawable() for verticie in self.verticies])
		# pygame.draw.circle(screen, (0, 0, 255), self.seed.to_drawable(), PIXEL_SIZE)
		# for p in self.verticies:
		# 	pygame.draw.circle(screen, (255, 0, 255), p.to_drawable(), PIXEL_SIZE)

seeds: list[Point] = [Point.from_random() for i in range(CELL_COUNT)]

def seed_of_point(p: Point) -> Point:
	best_seed: Point = seeds[0]
	best_distance: int = best_seed.distance(p)
	for seed in seeds:
		cur_distance = seed.distance(p)
		if cur_distance < best_distance:
			best_seed = seed
			best_distance = cur_distance
	return best_seed

def get_circumcenters() -> list[Verticie]:
	def circumcenter(a: Point, b: Point, c: Point) -> Point:
		D: float = (a.x - c.x) * (b.y - c.y) - (b.x - c.x) * (a.y - c.y)
		if D == 0:
			print("D == 0")
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
	
	circumcenters: list[Verticie] = list()
	
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
					circumcenters.append(Verticie(c.x, c.y, {seeds[i1], seeds[i2], seeds[i3]}))
					# self.delaunay_triangles[c].verticies.add(seeds[i1])
					# self.delaunay_triangles[c].verticies.add(seeds[i2])
					# self.delaunay_triangles[c].verticies.add(seeds[i3])

	return circumcenters

def get_outline() -> set[Point]:	
	def distance_to_edge(p: Point) -> int:
		return min(
			p.x,
			p.y,
			POINTS_PER_LINE - p.x,
			POINTS_PER_LINE - p.y
		)
		# return min(
		# 	p.x,
		# 	p.y,
		# 	POINTS_PER_LINE - p.x - 1,
		# 	POINTS_PER_LINE - p.y - 1
		# )

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

def get_verticies_on_border() -> list[Verticie]:
	
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
			border_verticies.append(Verticie(testing.x, testing.y, step_seeds))
	
	border_verticies: list[Verticie] = list()

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

	return border_verticies

# start = timeit.default_timer()
# outline = get_outline()
# end = timeit.default_timer()
# print("time to gen outline", end - start)

verticies = [
	Verticie(0, 0, {seed_of_point(Point(0, 0))}),
	Verticie(POINTS_PER_LINE, 0, {seed_of_point(Point(POINTS_PER_LINE, 0))}),
	Verticie(0, POINTS_PER_LINE, {seed_of_point(Point(0, POINTS_PER_LINE))}),
	Verticie(POINTS_PER_LINE, POINTS_PER_LINE, {seed_of_point(Point(POINTS_PER_LINE, POINTS_PER_LINE))})
]

start = timeit.default_timer()
verticies += get_circumcenters()
end = timeit.default_timer()
print("time to gen circumcenters", end - start)

start = timeit.default_timer()
verticies += get_verticies_on_border()
end = timeit.default_timer()
print("time to gen border verticies", end - start)

# merge vertices within a tolerance
# new_verticies: set[Verticie] = set()
# for i1 in range(len(verticies)):
# 	for i2 in range(i1 + 1, len(verticies)):
# 		if verticies[i1].distance(verticies[i2]) < 10:
# 			# midpoint? or just do it in smoothing step
# 			# should i even bother with this and just do neighbors in the smoothing step?
# 			verticies[i1].seeds.update(verticies[i2].seeds)
# 		new_verticies.add(verticies[i1])
# breaks stuff in top right, kinda cool


# verticies = list(new_verticies)

cell_mapping: dict[Point, Cell] = {seed: Cell(seed) for seed in seeds}
for verticie in verticies:
	for seed in verticie.seeds:
		cell_mapping[seed].verticies.append(verticie)

for cell in cell_mapping.values():
	cell.verticies = sorted(cell.verticies, key = lambda p: clockwiseangle_and_distance(p, cell.seed))

pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))



clock = pygame.time.Clock()
while not pygame.QUIT in [event.type for event in pygame.event.get()]:
	# clock.tick(1)
	screen.fill((0, 0, 0))
	for cell in cell_mapping.values():
		cell.draw()
	# for p in outline:
	# 	pygame.draw.circle(screen, (50, 50, 50), p.to_drawable(), PIXEL_SIZE)
	# for p in seeds:
	# 	pygame.draw.circle(screen, (0, 0, 255), p.to_drawable(), PIXEL_SIZE)
	# for p in verticies:
	# 	pygame.draw.circle(screen, (255, 0, 255), p.to_drawable(), PIXEL_SIZE)

	mouse_pos = pygame.mouse.get_pos()
	transformed_mouse = Point(int(mouse_pos[0] / SCREEN_SIZE * POINTS_PER_LINE), int(mouse_pos[1] / SCREEN_SIZE * POINTS_PER_LINE))
	# closest_verticie: Verticie = verticies[0]
	# best_distance: int = closest_verticie.distance(transformed_mouse)
	# for verticie in verticies:
	# 	cur_distance = verticie.distance(transformed_mouse)
	# 	if cur_distance < best_distance:
	# 		closest_verticie = verticie
	# 		best_distance = cur_distance
	# pygame.draw.circle(screen, (255, 0, 0), closest_verticie.to_drawable(), PIXEL_SIZE)
	# for seed in closest_verticie.seeds:
	# 	pygame.draw.circle(screen, (255, 0, 255), seed.to_drawable(), PIXEL_SIZE)


	# seed_of_mouse: Point = seed_of_point(transformed_mouse)
	# cell_of_mouse: Cell = cell_mapping[seed_of_mouse]
	# for p in cell_of_mouse.verticies:
	# 	pygame.draw.circle(screen, (255, 255, 255), p.to_drawable(), PIXEL_SIZE)
	pygame.draw.circle(screen, (255, 255, 255), seed_of_point(transformed_mouse).to_drawable(), PIXEL_SIZE)
	pygame.display.flip()