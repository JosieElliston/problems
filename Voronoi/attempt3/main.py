# find tri critical points. find neighbors by shifting around.
# tree ?????
from __future__ import annotations
import pygame
import random
random.seed(0)
import timeit

IntPoint = tuple[int, int]
Color = tuple[int, int , int]

POINTS_PER_LINE = 100
SCREEN_SIZE = 1000
CELL_COUNT = 10
# CENTROID_STEPS = 1

def drawable(p: IntPoint):
	return p[0] * SCREEN_SIZE / POINTS_PER_LINE, p[1] * SCREEN_SIZE / POINTS_PER_LINE

def distance(a: IntPoint, b: IntPoint) -> int:
	return (a[0] - b[0])**2 + (a[1] - b[1])**2

class Cell:
	def __init__(self, seed) -> None:
		self.seed = seed
		self.color: Color = random.randrange(256), random.randrange(256), random.randrange(256)
		self.neighbors: set[Cell] = set()
		# self.area: list[Point] = list()
	
	def distance(self, p: IntPoint) -> int:
		return distance(self.seed, p)
	
	def __eq__(self, other: object) -> bool:
		if not isinstance(other, Cell):
			return NotImplemented
		return self.seed == other.seed
	
	def __hash__(self) -> int:
		return hash(self.seed)
	
	def draw(self) -> None:
		pygame.draw.circle(screen, (0, 0, 255), drawable(self.seed), SCREEN_SIZE / POINTS_PER_LINE)

# def closest(p: Point, cells: list[Cell]) -> Cell:
# 	best_cell: Cell = cells[0]
# 	best_distance = relative_distance(p, best_cell.seed)
# 	for cell in cells:
# 		# if distance_overestimate(p, other) < best_distance:
# 		cur_distance = relative_distance(p, cell.seed)
# 		if cur_distance < best_distance:
# 			best_cell = cell
# 			best_distance = cur_distance
# 	return best_cell

# def gen_cells(seeds: list[Point]) -> list[Cell]:
# 	start = timeit.default_timer()
# 	cells: list[Cell] = [Cell(seed) for seed in seeds]
# 	for i in range(POINTS_PER_LINE):
# 		for j in range(POINTS_PER_LINE):
# 			p: Point = (i, j)
# 			closest(p, cells).area.append(p)
# 	end = timeit.default_timer()
# 	print("gen_cells in", end - start)
# 	return cells

seeds: list[IntPoint] = [(random.randrange(POINTS_PER_LINE), random.randrange(POINTS_PER_LINE)) for i in range(CELL_COUNT)]
cells: list[Cell] = [Cell(seed) for seed in seeds]

def distance_to_edge(p: IntPoint) -> int:
	assert min(
		p[0],
		p[1],
		POINTS_PER_LINE - p[0] - 1,
		POINTS_PER_LINE - p[1] - 1
	) >= 0
	return min(
		p[0],
		p[1],
		POINTS_PER_LINE - p[0] - 1,
		POINTS_PER_LINE - p[1] - 1
	)

def cell_of_point(p: IntPoint) -> Cell:
	best_cell: Cell = cells[0]
	best_distance: int = best_cell.distance(p)
	for cell in cells:
		cur_distance = cell.distance(p)
		if cur_distance < best_distance:
			best_cell = cell
			best_distance = cur_distance
	return best_cell

verticies: set[IntPoint] = set()
outline: set[IntPoint] = set()

for x in range(POINTS_PER_LINE):
	for y in range(POINTS_PER_LINE):
		testing: IntPoint = (x, y)
		step_cells: set[Cell] = set()
		step_cells.add(cell_of_point((testing[0], testing[1])))
		step_cells.add(cell_of_point((testing[0] + 1, testing[1])))
		step_cells.add(cell_of_point((testing[0] - 1, testing[1])))
		step_cells.add(cell_of_point((testing[0], testing[1] + 1)))
		step_cells.add(cell_of_point((testing[0], testing[1] - 1)))
		if len(step_cells) == 0:
			raise ValueError
		if distance_to_edge(testing) == 0:
			if len(step_cells) > 2:
				raise ValueError
			elif len(step_cells) == 2:
				verticies.add(testing)
			elif len(step_cells) == 1:
				outline.add(testing)
		else:
			if len(step_cells) > 3:
				raise ValueError
			elif len(step_cells) == 3:
				verticies.add(testing)
			elif len(step_cells) == 2:
				outline.add(testing)
		# CORNER

guess_points: set[IntPoint] = set()
# gen in better way
for x in range(POINTS_PER_LINE):
	for y in range(POINTS_PER_LINE):
		guess_points.add((x, y))

def step() -> None:
	for point in guess_points:
		# find three closest cells
		c



pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
while not pygame.QUIT in [event.type for event in pygame.event.get()]:
	screen.fill((0, 0, 0))
	
	# mouse_pos = pygame.mouse.get_pos()
	# cell_of_mouse: Cell = cell_by_point[(int(mouse_pos[0] / SCREEN_SIZE * POINTS_PER_LINE), int(mouse_pos[1] / SCREEN_SIZE * POINTS_PER_LINE))]
	# for neighbor in cell_of_mouse.neighbors:
	# 	for point in neighbor.perimeter:
	# 		pygame.draw.circle(screen, (0, 0, 255), drawable(point), SCREEN_SIZE / POINTS_PER_LINE)
	# for point in cell_of_mouse.perimeter:
	# 	pygame.draw.circle(screen, (255, 255, 255), drawable(point), SCREEN_SIZE / POINTS_PER_LINE)
	for p in outline:
		pygame.draw.circle(screen, (30, 30, 30), drawable(p), SCREEN_SIZE / POINTS_PER_LINE)

	for cell in cells:
		cell.draw()
	for p in verticies:
		pygame.draw.circle(screen, (100, 100, 100), drawable(p), SCREEN_SIZE / POINTS_PER_LINE)
	for p in guess_points:
		pygame.draw.circle(screen, (255, 255, 255), drawable(p), SCREEN_SIZE / POINTS_PER_LINE)

	
	pygame.display.flip()

