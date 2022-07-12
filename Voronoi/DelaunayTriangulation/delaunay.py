from __future__ import annotations
from collections import defaultdict
import random
import timeit
import pygame
SIZE = 700
POINT_COUNT_SQRT = 2

class Point:
	def __init__(self, x: int, y: int) -> None:
		self.x: int = x
		self.y: int = y
	
	def __add__(self, other: Point) -> Point:
		return Point(self.x + other.x, self.y + other.y)
	
	def __floordiv__(self, divisor: int) -> Point:
		return Point(self.x // divisor, self.y // divisor)
	
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

class Tile:
	def __init__(self) -> None: #, seed: Point
		# seed is a delaunay veriticie
		# self.seed = seed
		self.verticies: set[Point] = set()
		self.edges: set[Edge] = set()
		self.neighbors: set[Tile] = set()

	def draw(self, screen) -> None:
		# pygame.draw.circle(screen, (255, 255, 255), self.seed.to_tuple(), 3)
		for p in self.verticies:
			pygame.draw.circle(screen, (255, 255, 255), p.to_tuple(), 3)
		for e in self.edges:
			pygame.draw.aaline(screen, (255, 255, 255), e.p1.to_tuple(), e.p2.to_tuple())

class Graph:
	@staticmethod
	def is_collinear_or_coaxial(c: Point, points: list[Point]) -> bool:
		if len(points) < 2:
			return False
		
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
	def point_in_circle(r: float, center: Point, pruned_points: list[Point]) -> bool:
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
		self.delaunay_edge_to_voronoi_vertices: dict[Edge, set[Point]] = defaultdict(set)
		for i1 in range(len(self.delaunay_vertices)):
			for i2 in range(i1 + 1, len(self.delaunay_vertices)):
				for i3 in range(i2 + 1, len(self.delaunay_vertices)):
					c: Point = Graph.circumcenter(self.delaunay_vertices[i1], self.delaunay_vertices[i2], self.delaunay_vertices[i3])
					r: float = (self.delaunay_vertices[i3].x - c.x) ** 2 + (self.delaunay_vertices[i3].y - c.y) ** 2

					pruned_points: list[Point] = self.delaunay_vertices.copy()
					pruned_points.pop(i3)
					pruned_points.pop(i2)
					pruned_points.pop(i1)

					if Graph.point_in_circle(r, c, pruned_points):
						self.delaunay_edge_to_voronoi_vertices[Edge(self.delaunay_vertices[i1], self.delaunay_vertices[i2])].add(c)
						self.delaunay_edge_to_voronoi_vertices[Edge(self.delaunay_vertices[i2], self.delaunay_vertices[i3])].add(c)
						self.delaunay_edge_to_voronoi_vertices[Edge(self.delaunay_vertices[i1], self.delaunay_vertices[i3])].add(c)

		# use delaunay_edge_to_voronoi_vertices to construct voronoi edges, tiles, and neighbors

		self.tiles: dict[Point, Tile] = dict()
		for p in self.delaunay_vertices:
			self.tiles[p] = (Tile())
		
		# for delaunay_edge, voronoi_vertices in self.delaunay_edge_to_voronoi_vertices.items():
		# 	if len(voronoi_vertices) != 2:
		# 		print(len(voronoi_vertices))
		# 		p1, = voronoi_vertices
		# 		print("len(voronoi_vertices) != 2")
		# 		# create p2 s.t. the x is either 0 or SIZE
		# 		midpoint: Point = (delaunay_edge.p1 + delaunay_edge.p2) // 2
		# 		slope: float = (p1.y - midpoint.y) / (p1.x - midpoint.x)
		# 		p2x: int
		# 		if p1.x < SIZE // 2:
		# 			p2x = 0
		# 		else:
		# 			p2x = SIZE
		# 		p2y = int(slope * (p2x - p1.x) + p1.y)
		# 		p2 = Point(p2x, p2y)
		# 		self.delaunay_edge_to_voronoi_vertices[delaunay_edge].add(p2)
				


		for delaunay_edge, voronoi_vertices in self.delaunay_edge_to_voronoi_vertices.items():
			self.tiles[delaunay_edge.p1].neighbors.add(self.tiles[delaunay_edge.p2])
			self.tiles[delaunay_edge.p2].neighbors.add(self.tiles[delaunay_edge.p1]) # maybe redudnent
			self.tiles[delaunay_edge.p1].verticies.update(voronoi_vertices)
			
			if len(voronoi_vertices) == 3:
				print("len(voronoi_vertices) == 3")
				print([str(a) for a in voronoi_vertices])
			if len(voronoi_vertices) == 2:
				p1, p2 = voronoi_vertices
				self.tiles[delaunay_edge.p1].edges.add(Edge(p1, p2))
			

def draw(graph: Graph):
	pygame.init()
	screen = pygame.display.set_mode((SIZE, SIZE))
	screen.fill((0, 0, 0))
	for p in graph.delaunay_vertices:
		pygame.draw.circle(screen, (0, 0, 255), p.to_tuple(), 3)
	for cs in graph.delaunay_edge_to_voronoi_vertices.values():
		for c in cs:
			pygame.draw.circle(screen, (0, 0, 255), c.to_tuple(), 3)
	for e in graph.delaunay_edge_to_voronoi_vertices.keys():
		pygame.draw.aaline(screen, (0, 0, 255), e.p1.to_tuple(), e.p2.to_tuple())
	for tile in graph.tiles.values():
		tile.draw(screen)
	
	pygame.display.flip()
	clock = pygame.time.Clock()
	while not pygame.QUIT in [event.type for event in pygame.event.get()]:
		clock.tick(1)

graph = Graph()
# points: list[Point] = list()
# for voronoi_vertices in graph.delaunay_edge_to_voronoi_vertices.values():
# 	for p in voronoi_vertices:
# 		points.append(p)
# for i in range(len(points)):
# 	for j in range(i + i, len(points)):
# 		if hash(points[i]) == hash(points[j]):
# 			print("asldkjakjflsd")
# 			print(points[i])
# 			print(points[j])
# 		if (points[i]) == (points[j]):
# 			print("fdsa")
# 			print(points[i])
# 			print(points[j])
draw(graph)