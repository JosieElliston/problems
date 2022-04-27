import pygame
import time
import random
import numpy

Point = tuple[float, float]
Line = tuple[Point, Point]

step = .01
random_bias = 0.4

hole_inside: Point = (2, 2)
hole_count: int = 3
vertexes: list[Point] = [(0, 0), (4, 0), (6, 6), (2, 4), (0, 4)]

holes: list[Point] = [hole_inside] * hole_count
# holes = [(a[0] + (random.random() - .5) * step, a[1] + (random.random() - .5) * step) for a in holes] 
# holes: list[Point] = [(2, 2), (2, 2), (2, 2), (2, 2), (2, 2), (2, 2)]
lines: list[Line] = [(vertexes[i], vertexes[i + 1]) for i in range(len(vertexes) - 1)] + [(vertexes[-1], vertexes[0])]

def closest_on_line(hole: Point, line: Line) -> Point:
	"""
	returns closest point on line to hole
	"""
	a = line[0]
	b = line[1]
	if a[0] != b[0]:
		if a[1] != b[1]:
			m: float = (a[1] - b[1]) / (a[0] - b[0])
			minv: float = 1/m
			x: float = (hole[1] - a[1] + m*a[0] + minv*hole[0]) / (m + minv)
			y: float = m * (x - a[0]) + a[1]
			assert y - (m * (x - b[0]) + b[1]) < .0001
			return (x, y)
		else:
			return (hole[0], a[1])
	else:
		return (a[0], hole[1])

# def v_point(hole: Point, a: Point) -> Point:
# 	"""
# 	returns vector from hole to a
# 	"""
# 	return (a[0] - hole[0], a[1] - hole[1])

# def v_abs(a: Point):
# 	return (a[0]**2 + a[1]**2)**.5

def distance(a: Point, b: Point) -> float:
	return ((a[0]-b[0])**2 + (a[1]-b[1])**2)**.5

def closest_point(hole: Point, pruned_holes: list[Point]) -> Point:
	"""
	returns the point closest to hole
	"""
	# print("\nholes", holes, "\npruned_holes", pruned_holes)
	assert len(holes) == hole_count
	assert len(pruned_holes) == hole_count - 1

	pruned_holes = pruned_holes.copy()
	for line in lines:
		pruned_holes.append(closest_on_line(hole, line))
	
	# print("pruned with lines", pruned_holes)
	assert len(pruned_holes) == hole_count - 1 + len(lines)
	
	print("closest_point to _ is _", hole, min(pruned_holes, key = lambda value: distance(hole, value)))
	return min(pruned_holes, key = lambda value: distance(hole, value))

def fitness():
	min_distances = []
	for hole in holes:
		cur_pruned = holes.copy()
		cur_pruned.remove(hole)
		min_distances.append(distance(hole, closest_point(hole, cur_pruned)))
	print("average", sum(min_distances)/len(min_distances))
	print("standard deviation", numpy.array(min_distances).std())
	print("distances", min_distances)







pygame.init()
screen_scaling: int = 100
screen_size = int(max([a[0] for a in vertexes] + [a[1] for a in vertexes]) * screen_scaling)
screen = pygame.display.set_mode((screen_size, screen_size))
running = True
while running:
	time.sleep(.01)

	# for times in range(1): #so it doesn't draw every itteration
	print("\n")
	i = random.randrange(len(holes))
	# if random.random() > random_bias:
	pruned_holes = holes.copy()
	pruned_holes.pop(i)
	closest = closest_point(holes[i], pruned_holes)
	print("holes[i]", holes[i])
	print("closest", closest)
	if closest != holes[i]:
		print("no overlap")
		# new: Point = (holes[i][0] + (step * (holes[i][0] - closest[0])), holes[i][1] + (step * (holes[i][0] - closest[1]))) # with distance scaling
		new: Point = (holes[i][0] - step * (1 if closest[0] > holes[i][0] else -1), holes[i][1] - step * (1 if closest[1] > holes [i][1] else -1)) # without distance scaling
		#what if i did repeat until the closest closest changes
		print("old", holes[i])
		print("new", new)
		if closest_point(new, pruned_holes) == closest:
			print("moved")
			holes[i] = new
		else:
			print("didn't move")
			pass
			#randomizeing here????
	else:
		print("overlap")
		holes[i] = holes[i][0] + (random.random() - .5) * step, holes[i][1] + (random.random() - .5) * step

	# else:
	# 	holes[i] = ((holes[i][0] - ((1/random_bias) * step * random.random()), holes[i][1] - ((1/random_bias) * step * random.random())))
	
	fitness()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

	screen.fill((255, 255, 255))
	for hole in holes:
		pygame.draw.circle(screen, (0, 0, 250), (hole[0] * screen_scaling, hole[1] * screen_scaling), 4, width=0)

	for line in lines:
		pygame.draw.aaline(screen, (0, 0, 0), (line[0][0] * screen_scaling, line[0][1] * screen_scaling), (line[1][0] * screen_scaling, line[1][1] * screen_scaling), blend=1)

	pygame.display.flip()