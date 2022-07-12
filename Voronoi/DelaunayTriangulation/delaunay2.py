from __future__ import annotations
from collections import defaultdict
import random
import timeit
import pygame
SIZE = 700
POINT_COUNT_SQRT = 5

# each delauny triangle contribues 3 edges to 3 voronoi tiles

import math


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

class Point:
	def __init__(self, x: int, y: int) -> None:
		self.x: int = x
		self.y: int = y
	
	def __add__(self, other: Point) -> Point:
		return Point(self.x + other.x, self.y + other.y)
	
	def __floordiv__(self, divisor: int) -> Point:
		return Point(self.x // divisor, self.y // divisor)

	# def __truediv__(self, divisor: int) -> Point:
	# 	return Point(self.x / divisor, self.y / divisor)
	
	def to_tuple(self) -> tuple:
		return self.x, self.y
	
	def __str__(self) -> str:
		return "(" + str(self.x) + ", " + str(self.y) + ")"
	
	def __hash__(self) -> int:
		# return hash((self.x, self.y))
		return (self.x << 8) ^ self.y

class Edge:
	def __init__(self, p1: Point, p2: Point) -> None:
		# if p1 == p2:
		# 	raise ValueError

		# mp1 = magnitude(p1)
		# mp2 = magnitude(p2)
		# if mp1 == mp2:
		# 	if p1.x > p2.x:
		# 		p1, p2 = p2, p1
		# elif mp1 > mp2:
		# 	p1, p2 = p2, p1
		if hash(p1) > hash(p2):
			p1, p2 = p2, p1

		self.p1 = p1
		self.p2 = p2
	
	def midpoint(self) -> Point:
		return (self.p1 + self.p2) // 2
		# return Point(
		# 	(self.p1.x + self.p2.x) // 2,
		# 	(self.p1.y + self.p2.y) // 2
		# )
	
	def __str__(self) -> str:
		return "(" + str(self.p1) + ", " + str(self.p2) + ")"

	def __hash__(self) -> int:
		# return hash((self.p1, self.p2))
		return (hash(self.p1) << 16) ^ hash(self.p2)

	def __eq__(self, other: object) -> bool:
		if not isinstance(other, Edge):
			return NotImplemented
		return self.p1 == other.p1 and self.p2 == other.p2
		# return (self.p1 == other.p1 and self.p2 == other.p2) or (self.p1 == other.p2 and self.p2 == other.p1)

class Polygon:
	def __init__(self) -> None: #, seed: Point
		# seed is a delaunay veriticie
		# self.seed = seed
		self.verticies: set[Point] = set() # the angle at a vertex may be 180
		# self.edges: set[Edge] = set()
		self.neighbors: set[Polygon] = set()
	
	# def getVerticies(self) -> set[Point]:
	# 	verticies: set[Point] = set()
	# 	for edge in self.edges:
	# 		verticies.add(edge.p1)
	# 		verticies.add(edge.p2)
	# 	return verticies

	def getCentroid(self) -> Point:
		return Point(
			sum(p.x for p in self.verticies) // len(self.verticies),
			sum(p.y for p in self.verticies) // len(self.verticies)
		)

	def getEdges(self) -> list[Edge]:
		verticies = list(self.verticies)
		verticies.sort(key = lambda p: clockwiseangle_and_distance(p, self.getCentroid()))
		edges: list[Edge] = list()
		for i in range(len(verticies) - 1):
			edges.append(Edge(verticies[i], verticies[i + 1]))
		edges.append(Edge(verticies[-1], verticies[0]))
		return edges
		
	def draw(self, screen, color = (255, 255, 255)) -> None:
		for p in self.verticies:
			pygame.draw.circle(screen, color, p.to_tuple(), 3)
		for e in self.getEdges():
			pygame.draw.aaline(screen, color, e.p1.to_tuple(), e.p2.to_tuple())

class Graph:
	@staticmethod
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
	
	@staticmethod
	def circumcenter(a: Point, b: Point, c: Point) -> Point:
		D: float = (a.x - c.x) * (b.y - c.y) - (b.x - c.x) * (a.y - c.y)
		if D == 0:
			print("D == 0")
		return Point(
			int((((a.x - c.x) * (a.x + c.x) + (a.y - c.y) * (a.y + c.y)) / 2 * (b.y - c.y) -  ((b.x - c.x) * (b.x + c.x) + (b.y - c.y) * (b.y + c.y)) / 2 * (a.y - c.y)) / D),
			int((((b.x - c.x) * (b.x + c.x) + (b.y - c.y) * (b.y + c.y)) / 2 * (a.x - c.x) -  ((a.x - c.x) * (a.x + c.x) + (a.y - c.y) * (a.y + c.y)) / 2 * (b.x - c.x)) / D)
		)
	
	@staticmethod
	def square_distance(p1: Point, p2: Point) -> float:
		return (p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2
	
	@staticmethod
	# check whether any point in pruned_points is contained in the circle defined by r and c
	def not_point_in_circle(r: float, center: Point, pruned_points: list[Point]) -> bool:
		for p in pruned_points:
			if Graph.square_distance(center, p) < r:
				return False
		return True

	def __init__(self) -> None:
		self.delaunay_vertices: list[Point] = list()
		# create self.delaunay_vertices s.t. each are inside a box with sides lengths (SIZE / POINT_COUNT_SQRT) and none are collinear
		for y in range(POINT_COUNT_SQRT):
			for x in range(POINT_COUNT_SQRT):
				while True:
					p = Point(
						int(((1 - random.random()) + x) * (SIZE / POINT_COUNT_SQRT)),
						int(((1 - random.random()) + y) * (SIZE / POINT_COUNT_SQRT))
					)
					if not Graph.is_collinear_or_coaxial(p, self.delaunay_vertices):
						break
				self.delaunay_vertices.append(p)
		# for i in range(POINT_COUNT_SQRT**2):
		# 	while True:
		# 		p = Point(
		# 			1 + random.randint(0, SIZE - 1),
		# 			1 + random.randint(0, SIZE - 1)
		# 		)
		# 		if not Graph.is_collinear_or_coaxial(p, self.delaunay_vertices):
		# 			break
		# 	self.delaunay_vertices.append(p)
		# construct delaunay_edge_to_voronoi_vertices
		# each delaunay edge has two circumcenters (equivalently voronoi vertexes)
		# the voronoi vertexes have a voronoi edge between them
		# the two tiles that the voronoi edge defines are neighbors
		self.delaunay_triangles: dict[Point, Polygon] = defaultdict(Polygon)
		self.voronoi_polygons: dict[Point, Polygon] = defaultdict(Polygon)
		
		for i1 in range(len(self.delaunay_vertices)):
			for i2 in range(i1 + 1, len(self.delaunay_vertices)):
				for i3 in range(i2 + 1, len(self.delaunay_vertices)):
					c: Point = Graph.circumcenter(self.delaunay_vertices[i1], self.delaunay_vertices[i2], self.delaunay_vertices[i3])
					r: float = (self.delaunay_vertices[i3].x - c.x) ** 2 + (self.delaunay_vertices[i3].y - c.y) ** 2

					pruned_points: list[Point] = self.delaunay_vertices.copy()
					pruned_points.pop(i3)
					pruned_points.pop(i2)
					pruned_points.pop(i1)

					if Graph.not_point_in_circle(r, c, pruned_points):
						self.delaunay_triangles[c].verticies.add(self.delaunay_vertices[i1])
						self.delaunay_triangles[c].verticies.add(self.delaunay_vertices[i2])
						self.delaunay_triangles[c].verticies.add(self.delaunay_vertices[i3])
						
						# self.delaunay_triangles[c].edges.add(Edge(
						# 	self.delaunay_vertices[i1],
						# 	self.delaunay_vertices[i2]
						# ))
						# self.delaunay_triangles[c].edges.add(Edge(
						# 	self.delaunay_vertices[i1],
						# 	self.delaunay_vertices[i3]
						# ))
						# self.delaunay_triangles[c].edges.add(Edge(
						# 	self.delaunay_vertices[i3],
						# 	self.delaunay_vertices[i2]
						# ))
		
		# # add the edge between the circumcenter of the delaunay triagle and the midpoint of the two relevent edges
		# for circumcenter, delaunay_triangle in self.delaunay_triangles.items():
		# 	for voronoi_seed in delaunay_triangle.getVerticies():
		# 		other_verticies = list(delaunay_triangle.getVerticies())
		# 		other_verticies.remove(voronoi_seed)
				
		# 		self.voronoi_polygons[voronoi_seed].edges.add(Edge(
		# 			circumcenter,
		# 			Edge(voronoi_seed, other_verticies[0]).midpoint()
		# 		))
		# 		self.voronoi_polygons[voronoi_seed].edges.add(Edge(
		# 			circumcenter,
		# 			Edge(voronoi_seed, other_verticies[1]).midpoint()
		# 		))

		for circumcenter, delaunay_triangle in self.delaunay_triangles.items():
			for voronoi_seed in delaunay_triangle.verticies:
				self.voronoi_polygons[voronoi_seed].verticies.add(circumcenter)
				for voronoi_seed2 in delaunay_triangle.verticies:
					self.voronoi_polygons[voronoi_seed2].neighbors.add(self.voronoi_polygons[voronoi_seed])
		
		# new_dict = self.voronoi_polygons.copy()

		# for key, value in self.voronoi_polygons.items():
		# 	for verticie in value.verticies:
		# 		if not (0 < verticie.x < SIZE - 0) or not (0 < verticie.y < SIZE - 0):
		# 			new_dict.pop(key)
		# 			break
		# self.voronoi_polygons = new_dict

def draw(graph: Graph) -> None:
	

	pygame.init()
	screen = pygame.display.set_mode((SIZE, SIZE))
	screen.fill((0, 0, 0))
	for p in graph.delaunay_vertices:
		pygame.draw.circle(screen, (0, 0, 255), p.to_tuple(), 3)
	for d in graph.delaunay_triangles.values():
		d.draw(screen, (0, 0, 255))
	for v in graph.voronoi_polygons.values():
		v.draw(screen)

	pygame.draw.aaline(screen, (255, 0, 0),
		(0, 0),
		(SIZE - 0, 0)
	)
	pygame.draw.aaline(screen, (255, 0, 0),
		(SIZE - 0, SIZE - 0),
		(SIZE - 0, 0)
	)
	pygame.draw.aaline(screen, (255, 0, 0),
		(SIZE - 0, SIZE - 0),
		(0, SIZE - 0)
	)
	pygame.draw.aaline(screen, (255, 0, 0),
		(0, 0),
		(0, SIZE - 0)
	)


	
	pygame.display.flip()
	clock = pygame.time.Clock()
	while not pygame.QUIT in [event.type for event in pygame.event.get()]:
		clock.tick(1)

graph = Graph()
for polygon in graph.voronoi_polygons.values():
	for p in polygon.verticies:
		print(p)


draw(graph)