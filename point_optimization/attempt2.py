# only with 2 points

from operator import eq
import pygame
import time
import shapely.geometry, shapely.ops
import numpy as np
import functools

Point = tuple[float, float]
Line = tuple[Point, Point]

# vertexes: list[Point] = [(0, 0), (4, 0), (6, 6), (2, 4), (0, 4)]
# vertexes: list[Point] = [(0, 0), (4, 0), (4, 4), (0, 4)]
vertexes: list[Point] = [(0, 0), (2, 0), (1, 1), (0, 1), (0, 0)]
edges: list[Line] = [(vertexes[i], vertexes[i + 1]) for i in range(len(vertexes) - 1)] + [(vertexes[-1], vertexes[0])]

def plus(a: Point, b: Point) -> Point:
	return (a[0]+b[0], a[1]+b[1])

def minus(a: Point, b: Point) -> Point:
	return (a[0]-b[0], a[1]-b[1])

def times(a: Point, b: float) -> Point:
	return (a[0]*b, a[1]*b)

def distance(a: Point, b: Point) -> float:
	return ((a[0]-b[0])**2+(a[1]-b[1])**2)**.5

def distance_r(r1: float, r2: float) -> float:
	return distance(point_from_r(r1), point_from_r(r2))

def point_from_r(r: float) -> Point:
	"""returns a point along the perimenter for 0 <= r < 1, this is continuous"""
	r %= 1
	along: float = r * (len(vertexes) - 1) % 1
	i: int = int(r * (len(vertexes) - 1))
	return plus(vertexes[i], times(minus(vertexes[i+1], vertexes[i]), along))

def area(points: list[Point]) -> float:
	return shapely.geometry.Polygon(points).area

def get_divided_shape(original: list[Point], r1: float, r2: float) -> tuple[list[Point], list[Point]]:
	# first shape is the area that r1 + epsilon is inside
	a, b = point_from_r(r1), point_from_r(r2)
	area = shapely.geometry.Polygon(original)
	line = shapely.geometry.LineString((a, b))
	after = list(shapely.ops.split(area, line).geoms)
	area1 = after[0]
	area2 = after[1]
	if shapely.geometry.Point(point_from_r(r1 + 2**-.5)).intersects(area1):
		return (list(area1.exterior.coords), list(area2.exterior.coords))
	else:
		return (list(area2.exterior.coords), list(area1.exterior.coords))

# TODO bisection
def equal_area(r1: float, lo: float = None, hi: float = None) -> float:
	"""returns the point in r representation which makes the areas created by dividing the area along the line defined by both points equal"""
	epsilon: float = 2**-6
	r2: float = .5 + r1
	while True:
		shape1, shape2 = get_divided_shape(vertexes, r1, r2)
		diff: float = area(shape1) - area(shape2)
		# print("r1", r1)
		# print("r2", r2)
		# print("area1", area(shape1))
		# print("area2", area(shape2))
		# print("diff", diff)
		# print()
		if abs(diff) < epsilon:
			return r2
		elif diff > 0:
			r2 += epsilon * .25
		else:
			r2 -= epsilon * .25

# TODO not dumb alg
def max_perimeter() -> tuple[float, float]:
	eplison: float = 2**-5
	max_r1: float = 0
	max_r2: float = equal_area(0)
	max_p: float = distance_r(max_r1, max_r2)
	r1: float
	for r1 in np.arange(0, 1, eplison):
		r2 = equal_area(r1)
		# print(r1, r2)

		if distance_r(r1, r2) > max_p:
			max_p = distance_r(r1, r2)
			max_r1 = r1
			max_r2 = r2
	# print("returned", max_r1, max_r2)
	return max_r1, max_r2

def place_points_average_vertexes() -> tuple[Point, Point]:
	r1, r2 = max_perimeter()
	area1, area2 = shapely.ops.split(shapely.geometry.Polygon(vertexes), shapely.geometry.LineString((point_from_r(r1), point_from_r(r2)))).geoms
	area1, area2 = list(area1.exterior.coords)[:-1], list(area2.exterior.coords)[:-1]
	print(area1, area2)
	point1: Point = functools.reduce(lambda a, b: (a[0] + b[0], a[1] + b[1]), area1)
	point2: Point = functools.reduce(lambda a, b: (a[0] + b[0], a[1] + b[1]), area2)
	point1 = point1[0] / len(area1), point1[1] / len(area1)
	point2 = point2[0] / len(area2), point2[1] / len(area2)
	print(point1, point2)
	return point1, point2

def place_points_centroid() -> tuple[Point, Point]:
	area1, area2 = shapely.ops.split(shapely.geometry.Polygon(vertexes), shapely.geometry.LineString((point_from_r(r1), point_from_r(r2)))).geoms
	point1 = area1.centroid.x, area1.centroid.y
	point2 = area2.centroid.x, area2.centroid.y
	return point1, point2

def place_points_representative() -> tuple[Point, Point]:
	area1, area2 = shapely.ops.split(shapely.geometry.Polygon(vertexes), shapely.geometry.LineString((point_from_r(r1), point_from_r(r2)))).geoms
	point1 = area1.representative_point().x, area1.representative_point().y
	point2 = area2.representative_point().x, area2.representative_point().y
	return point1, point2

pygame.init()
scaling: int = 200
x_size: float = max([a[0] for a in vertexes]) + 2
y_size: float = max([a[1] for a in vertexes]) + 2
x_scaled: int = int(x_size * scaling)
y_scaled: int = int(y_size * scaling)
screen = pygame.display.set_mode((x_scaled, y_scaled))

# add lookup table
def transformed(a: Point) -> Point:
	return ((a[0] + 1) * scaling, y_scaled - ((a[1] + 1) * scaling))

def draw_point(a: Point) -> None:
	pygame.draw.circle(screen, (0, 0, 0), transformed(a), 4, width=0)

def draw_point_r(r: float) -> None:
	draw_point(point_from_r(r))

def draw_line(line: Line) -> None:
	a, b = line
	draw_point(a)
	draw_point(b)
	pygame.draw.aaline(screen, (0, 0, 0), transformed(a), transformed(b), blend=1)

def draw_line_r(r1: float, r2: float) -> None:
	draw_line((point_from_r(r1), point_from_r(r2)))

running = True
while running:
	# time.sleep(.03)

	r1, r2 = max_perimeter()
	p1, p2 = place_points_centroid()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

	screen.fill((255, 255, 255))
	
	for line in edges:
		draw_line(line)

	draw_line_r(r1, r2)
	draw_point(p1)
	draw_point(p2)

	pygame.display.flip()