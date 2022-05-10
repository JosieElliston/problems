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
# import seaborn
from typing import Optional
from xmlrpc.client import Boolean
import pygame
import itertools
import shapely.geometry
# INFINITY = 10000
random.seed(0)

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
		_y_int[a] = a[0][1] - (a[0][0] * slope(a))
	return _y_int[a]
	

_slope: dict[Line, float] = dict()
def slope(a: Line) -> float:
	if _slope.get(a) == None:
		if (a[0][0] - a[1][0]) != 0:
			_slope[a] = (a[0][1] - a[1][1]) / (a[0][0] - a[1][0])
		else:
			# _slope[a] = INFINITY
			raise ValueError
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
		# assert x * slope(a) + y_int(a) == x * slope(b) + y_int(b)
		_intersection[(a, b)] = (x, x * slope(a) + y_int(a))
	return _intersection[(a, b)]

def closest(a: Point, b: Line) -> Point:
	return intersection(b, any_line(-1/slope(b), a))

def distance(a: Point, b: Line) -> float:
	return length((a, closest(a, b)))

def segment_intersection(segment: Line, line: Line) -> bool:
	""" returns whether segment intserects line """
	if segment[0][0] < segment[1][0]:
		return segment[0][0] < intersection(segment, line)[0] < segment[1][0]
	return segment_intersection((segment[1], segment[0]), line)

def count_segment_intersect(segment: Line, lines: set[Line]) -> int: # TODO: fix including origin line in count
	# count: int = 0
	# for line in lines:
	# 	if segment_intersection(ray, line):
	# 		count += 1
	# return count
	""" returns how many times segment intersects with any line in lines """
	return sum([segment_intersection(segment, line) for line in lines])

def intersection_combinations(lines: set[Line]) -> set[Point]:
	""" returns a set of all the intersection points in a set of lines """
	return set(intersection(pair[0], pair[1]) for pair in (itertools.combinations(lines, 2)))

def horizontal_intersection(tool: Line, target_y: int) -> Point:
	""" returns the point where tool intersects with the horizontal line at y = target_y """
	return (target_y - y_int(tool)) / slope(tool), target_y
	# if target_y == 0:
	# 	return y_int(tool) / slope(tool)
	# elif target_y == 1:
	# 	return 
	# else:
	# 	raise ValueError

def vertical_intersection(tool: Line, target_x: int) -> Point:
	""" returns the point where tool intersects the vertical line passing through x = target_x """
	return target_x, slope(tool) * target_x + y_int(tool)
	# if target_x == 0:
	# 	return 0, y_int(tool)
	# elif target_x == 1:
	# 	return 1, y_int(tool) + slope(tool)
	# else:
	# 	raise ValueError

def intersection_with_boundery(tools: set[Line]) -> set[Point]:
	""" returns a set of all the intersections between tools and the 1x1 bounding box """
	out: set[Point] = set()
	for tool in tools:
		possible: set[Point] = set()
		possible.add(vertical_intersection(tool, 0))
		possible.add(vertical_intersection(tool, 1))
		possible.add(horizontal_intersection(tool, 0))
		possible.add(horizontal_intersection(tool, 1))
		possible = set(filter(lambda point: (0 <= point[0] <= 1) and (0 <= point[1] <= 1), possible))
		out.update(possible)
	return out

def transformed_point(point: Point, scale: int) -> Point:
	return point[0] * scale, point[1] * scale

class Cell:
	# PALLETE = seaborn.color_palette("muted", as_cmap=True)
	# PALLETE = sns.color_palette("Spectral", as_cmap=True)
	# PALLETE = ((int(a*256) for a in b) for b in PALLETE)
	# all_cells: set[Cell] = set()

	def __init__(self, origin: Point, seeds: list[Point]) -> None:
		print("origin", origin)
		self.seeds = seeds.copy()
		self.seeds.remove(origin)
		self.origin = origin
		self.neighbors: set[Cell] = set()
		self.color = (random.randrange(256), random.randrange(256), random.randrange(256))
		# self.color: Color = (0, 0, 0)
		# self.color = random.choice(Cell.PALLETE)

		# perp_bisect: dict[Point, Line] = {seed: perpendicular_bisector(self.origin, seed) for seed in self.seeds}
		# print("\nperp_bisect", perp_bisect)
		# perp_bisect.update({(0, 0): ((0, 0), (1, 0)), (0, 0): ((1, 0), (1, 1)), (0, 0): ((1, 1), (0, 1)), (0, 0): ((0, 1), (0, 0))})
		# print("perp_bisect", perp_bisect)
		# self.verticies: set[Point] = all_intersections(set(perp_bisect.values()))
		# print("\nself.verticies before filter", len(self.verticies), self.verticies)
		# self.verticies = set(filter(lambda verticie: count_segment_intersect((verticie, self.origin), set(perp_bisect.values())) == 0, self.verticies))
		# print("\nself.verticies after filter", len(self.verticies), self.verticies)

		perp_bisect_lines: set[Line] = {perpendicular_bisector(self.origin, seed) for seed in self.seeds}
		print("\nperp_bisect", perp_bisect_lines)
		# perp_bisect_lines.update({((0, 0), (1, 0)), ((1, 0), (1, 1)), ((1, 1), (0, 1)), ((0, 1), (0, 0))})
		# print("perp_bisect", perp_bisect_lines)
		self.verticies: set[Point] = intersection_combinations(perp_bisect_lines)
		print("\nself.verticies before intersection_with_boundery", self.verticies)
		self.verticies.update(intersection_with_boundery(perp_bisect_lines))
		print("\nself.verticies before filter", len(self.verticies), self.verticies)
		self.verticies = set(filter(lambda verticie: count_segment_intersect((verticie, self.origin), perp_bisect_lines) == 0, self.verticies))
		print("\nself.verticies after filter", len(self.verticies), self.verticies)

		# neighboring_origins: set[Point] = set(perp_bisect.keys())

		def pleaseletmecompressthis() -> None:



			# def edges(self):
			# 	if len(self._edges) == 0:
			# 		# perp_bisect: set[Line] = set()
			# 		# for seed in self.seeds:
			# 		# 	perp_bisect.add(perpendicular_bisector(self.origin, seed))
					
			# 		perp_bisect: dict[Point, Line] = {seed: perpendicular_bisector(self.origin, seed) for seed in self.seeds}
			# 		# trimmed_perp_bisect: set[Line] = set()
			# 		# for target in perp_bisect:				
			# 		# 	trimmed_perp_bisect.add(min(trim(target, perp_bisect.copy().remove(target)), key = lambda segment: distance(self.origin, segment)))
			# 		# trimmed_perp_bisect: set[Line] = {min(trim(target, perp_bisect.copy().remove(target)), key = lambda segment: distance(self.origin, segment)) for target in perp_bisect}

			# 		# purged_perp_bisect: dict[Point, Line] = dict()
			# 		# for seed in self.seeds:
			# 		# 	if count_intersections((seed, self.origin), perp_bisect.values().remove(perp_bisect[seed])) == 1:
			# 		# 		purged_perp_bisect[seed] = perp_bisect[seed]

			# 		purged_perp_bisect = filter(lambda a: count_segment_intersect((self.origin, perp_bisect[a]), perp_bisect.values()), perp_bisect)

			# 		# btw if something changes and we need to pair an edge with which cell it is shared with, that's easy to do here
			# 		print(list(purged_perp_bisect))
			# 		print(dict(purged_perp_bisect))
			# 		self._edges = purged_perp_bisect.values()
			# 		self.neighboring_origins = purged_perp_bisect.keys()

			# 	return self._edges


			# def verticies(self):
			# 	if len(self._verticies) == 0:
			# 		for target in self.edges():
			# 			for tool in self.edges():
			# 				pass
			# 				# intersections of all edges
			# 	return self._verticies

			# def neighbors(self) -> set[Cell]:
			# 	if len(self._neighbors) == 0:
			# 		for cell in Cell.all_cells:
			# 			if cell.origin in self.neighboring_origins:
			# 				self._neighbors.add(cell)
			# 		self._neighbors.remove(self)
			# 	return self._neighbors
			
			# def color(self) -> Color:
			# 	if self._color == (0, 0, 0):
			# 		self._color = random.choice(Cell.PALLETE)
			# 	return self._color

				# else:
				# 	for cell in self.neighbors():
				# 		if cell.color() == self._color:
				# 			self._color = random.choice(Cell.PALLETE)
			pass
	
	def draw(self, screen, scale: int) -> None:
		pygame.draw.polygon(screen, self.color, [transformed_point(point, scale) for point in self.verticies])
		pygame.draw.circle(screen, (0, 0, 0), transformed_point(self.origin, scale), 4, width=0)


def main(CELL_NUMBER: int) -> None:
	SCREEN_SIZE = 700
	seeds: list[Point] = [(random.random(), random.random()) for i in range(CELL_NUMBER)]
	print("\nseeds", len(seeds), seeds)
	cells: set[Cell] = {Cell(origin, seeds) for origin in seeds}
	print("\nseeds", len(seeds), seeds)
	screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))

	run: Boolean = True
	while run:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
		screen.fill((255, 255, 255))
		for cell in cells: cell.draw(screen, SCREEN_SIZE)
		pygame.display.flip()

def test_segment_intersect2() -> None:
	if segment_intersection(((0.747,0.382), (0.375,0.64)), ((0.916,0.652), (0.198,0.154))):
		print("1 worked")
	else:
		print("1 failed")
	
	if segment_intersection(((0.747,0.382), (0.375,0.64)), ((0.587,0.39), (0.198,0.154))):
		print("2 worked")
	else:
		print("2 failed")
	
	if segment_intersection(((0.916,0.652), (0.198,0.154)), ((0.747,0.382), (0.375,0.64))):
		print("3 worked")
	else:
		print("3 failed")
	
	if not segment_intersection(((0.587,0.39), (0.198,0.154)), ((0.747,0.382), (0.375,0.64))):
		print("4 worked")
	else:
		print("4 failed")

def test_segment_intersect() -> None:
	if segment_intersection(((0.375,0.64), (0.747,0.382)), ((0.916,0.652), (0.198,0.154))):
		print("1 worked")
	else:
		print("1 failed")
	
	if segment_intersection(((0.375,0.64), (0.747,0.382)), ((0.587,0.39), (0.198,0.154))):
		print("2 worked")
	else:
		print("2 failed")
	
	if segment_intersection(((0.198,0.154), (0.916,0.652)), ((0.747,0.382), (0.375,0.64))):
		print("3 worked")
	else:
		print("3 failed")
	
	if not segment_intersection(((0.198,0.154), (0.587,0.39)), ((0.747,0.382), (0.375,0.64))):
		print("4 worked")
	else:
		print("4 failed")

def test_count_segment_intersect() -> None:
	pass

# main(5)
# test_count_segment_intersect()
test_segment_intersect2()
test_segment_intersect()