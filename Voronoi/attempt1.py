# https://en.wikipedia.org/wiki/Voronoi_diagram
import pygame
import random

Point = tuple[float, float]
Color = tuple[int, int, int]
Cell = tuple[Point, Color]

def manhattan_distance(a: Point, b: Point) -> float:
	return abs(a[0] - b[0]) + abs(a[1] - b[1])

def euclidean_distance(a: Point, b: Point) -> float:
	return ((a[0] - b[0])**2 + (a[1] - b[1])**2)**.5

def chebyshev_distance(a: Point, b: Point) -> float:
	return max(abs(b[0] - a[0]), abs(b[1] - a[1]))

def distance(a: Point, b: Point) -> float:
	return manhattan_distance(a, b)
	# return euclidean_distance(a, b)
	# return chebyshev_distance(a, b)


RESOLUTION = 2
SCREEN_SIZE = 500
TILE_COUNT = 10
points: list[Point] = [(random.random() * SCREEN_SIZE, random.random() * SCREEN_SIZE) for i in range(TILE_COUNT)]
cells: list[Cell] = [(a, (int(random.random() * 255), int(random.random() * 255), int(random.random() * 255))) for a in points]
run: bool = True
pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
while run:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

	
	screen.fill((255, 255, 255))
	for x in range(0, SCREEN_SIZE, RESOLUTION):
		for y in range(0, SCREEN_SIZE, RESOLUTION):
			best_distance = distance((x, y), points[0])
			best_point = points[0]
			best_point_i = 0
			for i in range(len(points)):
				if distance((x, y), points[i]) < best_distance:
					best_distance = distance((x, y), points[i])
					best_point = (x, y)
					best_point_i = i
					
			pygame.draw.circle(screen, cells[best_point_i][1], (x, y), RESOLUTION, width=0)

	for point in points:
		pygame.draw.circle(screen, (0, 0, 0), point, 4, width=0)

	

	pygame.display.flip()