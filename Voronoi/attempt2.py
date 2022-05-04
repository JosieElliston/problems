# get seeds
# get perpendicular bisectors 
# give this to each cell
# for each cell, trim perpendicular bisectors by every other perpendicular bisectors
	# if trim is hard, just split and then eval which of the splited ones is closest
# gen each cell's neighbors by comparing common edges

# attempt 3
	# for each cell
	 # get perpendicular bisectors between origin and seeds
	 # trim perpendicular bisectors by each other, only keeping closest segment
	 # v1
		# for every trimmed perpendicualr bisector, draw a ray from its endpoint to the cell's origin
		# if the ray intersects another trimmed perpendicualr bisector, discard the first perpendicualr bisector (the one that genned the array)
	# v2
		# instead of endpoints, do from midpoint to cell origin
	# v3
		# for every seed, draw a ray from it to the orign
		# if this ray intersects >1 trimmed trimmed perpendicualar bisector, discard the trimmed perpendicualr bisector draw from the seed
	
from __future__ import annotations
import random
from functools import reduce
import seaborn
from typing import Optional
import pygame

# perp_bisect = set[Line] vs perp_bisect: set[Line] = set()
# don't trim, have verticies
# check if ray from origin to closest point on line passes through other lines

Point = tuple[float, float]
Line = tuple[Point, Point]
Color = tuple[int, int, int]

def any_line(m: float, p: Point) -> Line: # TODO probably don't use line with endpoints outside of [0, 1]
	return p, (p[0] + 1, p[1] + m * (p[0] + 1))

_y_int: dict[Line, float] = dict()
def y_int(a: Line) -> float:
	if _y_int.get(a) == None:
		pass
	return _y_int[a]

_slope: dict[Line, float] = dict()
def slope(a: Line) -> float:
	if _slope.get(a) == None:
		_slope[a] = (a[0][1] - a[1][1]) / (a[0][0] - a[1][0])
	return _slope[a] 

_midpoint: dict[Line, Point] = dict()
def midpoint(a: Line) -> Point:
	if _midpoint.get(a) == None:
		_midpoint[a] = (a[0][0] + a[1][0]) / 2, (a[0][1] + a[1][1]) / 2
	return _midpoint[a]



def perpendicular_bisector(a: Point, b: Point) -> Line:
	return any_line(-1/slope((a, b)), midpoint((a, b)))

def length(a: Line) -> float:
	return ((a[0][0] - a[1][0])**2 + (a[0][1] - a[1][1])**2)**.5

_intersection: dict[tuple[Line, Line], Point] = dict()
def intersection(a: Line, b: Line) -> Point:
	# https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection#Given_two_line_equations
	if _intersection.get((a, b)) == None:
		x = (y_int(b) - y_int(a)) / (slope(a) - slope(b))
		assert x * slope(a) + y_int(a) == x * slope(b) + y_int(b)
		_intersection[(a, b)] = (x, x * slope(a) + y_int(a))
	return _intersection[(a, b)]

def closest(a: Point, b: Line) -> Point:
	return intersection(b, any_line(-1/slope(b), a))

def distance(a: Point, b: Line) -> float:
	return length((a, closest(a, b)))

def segment_intersection(segment: Line, line: Line) -> bool:
	return segment[0][0] < intersection(segment, line)[0] < segment[1][0]

def count_segment_intersect(ray: Line, lines: set[Line]) -> int: # TODO: fix including origin line in count
	# count: int = 0
	# for line in lines:
	# 	if segment_intersection(ray, line):
	# 		count += 1
	# return count
	return sum([segment_intersection(ray, line) for line in lines])



class Cell:
	PALLETE = seaborn.color_palette("muted", as_cmap=True)
	# PALLETE = sns.color_palette("Spectral", as_cmap=True)
	PALLETE = ((int(a*256) for a in b) for b in PALLETE)
	all_cells: set[Cell] = set()

	def __init__(self, origin: Point, seeds: list[Point]) -> None:
		Cell.all_cells.add(self)
		self.seeds = seeds
		seeds.remove(origin)
		self.origin = origin
		self._neighbors: set[Cell] = set()
		self._edges: set[Line] = set()
		self._verticies: set[Point] = set()
		self.neighboring_origins: set[Point] = set()
		self._color: Color = (0, 0, 0)
		

	def edges(self):
		if len(self._edges) == 0:
			# perp_bisect: set[Line] = set()
			# for seed in self.seeds:
			# 	perp_bisect.add(perpendicular_bisector(self.origin, seed))
			
			perp_bisect: dict[Point, Line] = {seed: perpendicular_bisector(self.origin, seed) for seed in self.seeds}
			# trimmed_perp_bisect: set[Line] = set()
			# for target in perp_bisect:				
			# 	trimmed_perp_bisect.add(min(trim(target, perp_bisect.copy().remove(target)), key = lambda segment: distance(self.origin, segment)))
			# trimmed_perp_bisect: set[Line] = {min(trim(target, perp_bisect.copy().remove(target)), key = lambda segment: distance(self.origin, segment)) for target in perp_bisect}

			# purged_perp_bisect: dict[Point, Line] = dict()
			# for seed in self.seeds:
			# 	if count_intersections((seed, self.origin), perp_bisect.values().remove(perp_bisect[seed])) == 1:
			# 		purged_perp_bisect[seed] = perp_bisect[seed]



			purged_perp_bisect = filter(lambda a: count_segment_intersect((self.origin, perp_bisect[a]), perp_bisect.values()), perp_bisect)

			# btw if something changes and we need to pair an edge with which cell it is shared with, that's easy to do here
			print(list(purged_perp_bisect))
			print(dict(purged_perp_bisect))
			self._edges = purged_perp_bisect.values()
			self.neighboring_origins = purged_perp_bisect.keys()

		return self._edges

	def verticies(self):
		if len(self._verticies) == 0:
			for target in self.edges():
				for tool in self.edges():
					pass
					# intersections of all edges
		return self._verticies

	def neighbors(self) -> set[Cell]:
		if len(self._neighbors) == 0:
			for cell in Cell.all_cells:
				if cell.origin in self.neighboring_origins:
					self._neighbors.add(cell)
			self._neighbors.remove(self)
		return self._neighbors
	
	def color(self) -> Color:
		if self._color == (0, 0, 0):
			self._color = random.choice(Cell.PALLETE)
		return self._color

		# else:
		# 	for cell in self.neighbors():
		# 		if cell.color() == self._color:
		# 			self._color = random.choice(Cell.PALLETE)
		

def gen_cells(CELL_NUMBER: int) -> set[Cell]:
	seeds: list[Point] = [(random.random(), random.random()) for i in range(CELL_NUMBER)]
	cells: set[Cell] = {Cell(origin, seeds) for origin in seeds}

	return cells

def main(CELL_NUMBER: int) -> None:
	SCREEN_SIZE = 1000
	cells: set[Cell] = gen_cells(CELL_NUMBER)
	screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
	def draw_cell(cell: Cell) -> None:
		pygame.draw.circle(screen, (0, 0, 0), [a * SCREEN_SIZE for a in cell.origin], 4, width=0)
		pygame.draw.aaline(screen, (0, 0, 0), [a * SCREEN_SIZE for a in cell.edges()[0]], [a * SCREEN_SIZE for a in cell.edges()[1]])

	while True:
		screen.fill((255, 255, 255))
		for cell in cells: draw_cell(cell) 
		pygame.display.flip()

main(3)