# https://en.wikipedia.org/wiki/Voronoi_diagram
from __future__ import annotations
import pygame
import random
random.seed(0)
import timeit

Point = tuple[float, float]
Color = tuple[int, int, int]

POINTS_PER_LINE = 100
SCREEN_SIZE = 500
CELL_COUNT = 20
CENTROID_STEPS = 1

def drawable(p: Point):
	return p[0] * SCREEN_SIZE / POINTS_PER_LINE, p[1] * SCREEN_SIZE / POINTS_PER_LINE

def distance(a: Point, b: Point) -> float:
	return ((a[0] - b[0])**2 + (a[1] - b[1])**2)**.5

def relitive_distance(a: Point, b: Point) -> float:
	return (a[0] - b[0])**2 + (a[1] - b[1])**2

def distance_overestimate(a: Point, b: Point) -> float:
	return abs(a[0] - b[0]) + abs(a[1] - b[1])

def centroid(cell: Cell) -> Point:
	out: Point = 0, 0
	for point in cell.area:
		out = out[0] + point[0] / len(cell.area), out[1] + point[1] / len(cell.area)
	return out

class Cell:
	def __init__(self, seed) -> None:
		self.seed = seed
		self.color: Color = random.randrange(256), random.randrange(256), random.randrange(256)
		self.neighbors: set[Cell] = set()
		self.area: list[Point] = list()
		self.perimeter: set[Point] = set()
		
def closest(p: Point, cells: list[Cell]) -> Cell:
	best_cell: Cell = cells[0]
	best_distance = relitive_distance(p, best_cell.seed)
	for cell in cells:
		# if distance_overestimate(p, other) < best_distance:
		cur_distance = relitive_distance(p, cell.seed)
		if cur_distance < best_distance:
			best_cell = cell
			best_distance = cur_distance
	return best_cell

def gen_cells(seeds: list[Point]) -> list[Cell]:
	start = timeit.default_timer()
	cells: list[Cell] = [Cell(seed) for seed in seeds]
	for i in range(POINTS_PER_LINE):
		for j in range(POINTS_PER_LINE):
			p: Point = (i, j)
			closest(p, cells).area.append(p)
	end = timeit.default_timer()
	print("gen_cells in", end - start)
	return cells

def main() -> None:
	seeds: list[Point] = [(random.randrange(POINTS_PER_LINE), random.randrange(POINTS_PER_LINE)) for i in range(CELL_COUNT)]
	cells = gen_cells(seeds)
	for i in range(CENTROID_STEPS):
		seeds = [centroid(cell) for cell in cells]
		cells = gen_cells(seeds)

	cell_by_point: dict[Point, Cell] = dict()
	for cell in cells:
		for point in cell.area:
			cell_by_point[point] = cell
	

	outline: set[Point] = set()
	for point in cell_by_point:
		test_points: list[Point] = [
			(point[0] - 1, point[1]),
			(point[0] + 1, point[1]),
			(point[0], point[1] - 1),
			(point[0], point[1] + 1)
		]
		test_points = list(filter(lambda point: 0 < point[0] < POINTS_PER_LINE and 0 < point[1] < POINTS_PER_LINE, test_points))
		for testing in test_points:
			if cell_by_point[testing] != cell_by_point[point]:
				cell_by_point[point].neighbors.add(cell_by_point[testing])
				cell_by_point[point].perimeter.add(testing)
				outline.add(testing)

	
	pygame.init()
	screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
	run: bool = True
	clock = pygame.time.Clock()
	while not pygame.QUIT in [event.type for event in pygame.event.get()]:
		# print(clock.tick())
		screen.fill((255, 255, 255))
		for cell in cells:
			for point in cell.area:
				pygame.draw.circle(screen, cell.color, drawable(point), SCREEN_SIZE / POINTS_PER_LINE)
			for point in cell.perimeter:
				pygame.draw.circle(screen, (0, 0, 0), drawable(point), SCREEN_SIZE / POINTS_PER_LINE)
			pygame.draw.circle(screen, (0, 0, 0), drawable(cell.seed), SCREEN_SIZE / POINTS_PER_LINE)
		
		# for point in cells[0].area:
		# 	pygame.draw.circle(screen, (0, 0, 0), drawable(point), SCREEN_SIZE / POINTS_PER_LINE)
		# for neighbor in cells[0].neighbors:
		# 	for point in neighbor.area:
		# 		pygame.draw.circle(screen, (100, 100, 100), drawable(point), SCREEN_SIZE / POINTS_PER_LINE)
		
		pygame.display.flip()

main()