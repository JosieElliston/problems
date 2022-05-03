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
from random import random
# perp_bisect = set[Line] vs perp_bisect: set[Line] = set()
# don't trim, have verticies
# check if ray from origin to closest point on line passes through other lines

Point = tuple[float, float]
Line = tuple[Point, Point]

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

def intersection(a: Line, b: Line) -> Point:
	# https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection#Given_two_line_equations
	x = (y_int(b) - y_int(a)) / (slope(a) - slope(b))
	assert x * slope(a) + y_int(a) == x * slope(b) + y_int(b)
	return x, x * slope(a) + y_int(a)

def closest(a: Point, b: Line) -> Point:
	return intersection(b, any_line(-1/slope(b), a))

def distance(a: Point, b: Line) -> float:
	return length((a, closest(a, b)))

def intersect_count(ray: Line, lines: itterable[Line]) -> int: # TODO: fix including origin line in count

class Cell:
	def __init__(self, origin: Point, seeds: list[Point]) -> None:
		self.origin = origin
		self._neighbors: set[Cell] = set()
		self._edges: set[Line] = set()
		self._verticies: set[Point] = set()
		self.neighboring_origins: set[Point] = set()

	def edges(self):
		if self._edges == None:
			# perp_bisect: set[Line] = set()
			# for seed in self.seeds:
			# 	perp_bisect.add(perpendicular_bisector(self.origin, seed))
			
			perp_bisect: dict[Point, Line] = {seed: perpendicular_bisector(self.origin, seed) for seed in self.seeds.remove(self.origin)}
			# trimmed_perp_bisect: set[Line] = set()
			# for target in perp_bisect:				
			# 	trimmed_perp_bisect.add(min(trim(target, perp_bisect.copy().remove(target)), key = lambda segment: distance(self.origin, segment)))
			# trimmed_perp_bisect: set[Line] = {min(trim(target, perp_bisect.copy().remove(target)), key = lambda segment: distance(self.origin, segment)) for target in perp_bisect}

			# purged_perp_bisect: dict[Point, Line] = dict()
			# for seed in self.seeds:
			# 	if count_intersections((seed, self.origin), perp_bisect.values().remove(perp_bisect[seed])) == 1:
			# 		purged_perp_bisect[seed] = perp_bisect[seed]


			# btw if something changes and we need to pair an edge with which cell it is shared with, that's easy to do here

			filter(lambda a: intersect_count((self.origin, perp_bisect[a]), perp_bisect.values()), perp_bisect)



			self.edges = purged_perp_bisect.values()
			self.neighboring_origins = purged_perp_bisect.keys()

		return self._edges

	def verticies(self):
		if self._verticies == None:
			for target in self.edges():
				for tool in self.edges():
					pass
					# intersections of all edges
		return self._verticies

	def neighbors(self, cells: set[Cell]) -> set[Cell]:
		if self._neighbors == None:
			for cell in cells:
				if cell.origin in self.neighboring_origins:
					self._neighbors.add(cell)
		return self._neighbors


def gen_cells(CELL_NUMBER: int) -> set[Cell]:
	seeds: list[Point] = [(random(), random()) for i in range(CELL_NUMBER)]
	cells: set[Cell] = {Cell(origin, seeds) for origin in seeds}

	return cells

def main(CELL_NUMBER: int) -> None:
	cells: set[Cell] = gen_cells(CELL_NUMBER)
