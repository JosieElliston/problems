# import matplotlib as plt
# import sympy
import pygame
import math
from typing import Callable, Optional
Vals = list[float]

# match precision of riemann sum or trapezoidal sum using fewer intervals by making them unequal
# insert a two Vals where the change in derivative is maximum
# insert point either at the mid point, or scaled by the derivative or change in derivative somehow

lo: float = 0
hi: float = 1

_f: dict[float, float] = dict()
def f(x: float) -> float: # math.sin(x)
	if _f.get(x) == None:
		_f[x] = -x**3 + x**2
	return _f[x]

# exact_integral: float = 2
exact_integral: float = 0.0833333333333


def f_list(xvals: Vals) -> Vals:
	yvals: Vals = list()
	for x in xvals:
		yvals.append(f(x))
	return yvals

def slope(x1: float, y1: float, x2: float, y2: float) -> float:
	return (y1 - y2) / (x1 - x2)

def trapezoidal_sum(xvals: Vals) -> float:
	out: float = 0
	for i in range(len(xvals) - 1):
		out += ((f(xvals[i+1]) + f(xvals[i])) / 2) * (xvals[i+1] - xvals[i])
	return out

def regular_init(steps: int) -> Vals:
	# returns a list of x-values with equal steps
	delta_x: float = (hi - lo) / steps
	out: Vals = list()
	for i in range(steps + 1):
		out.append(i * delta_x)
	return out

def slope_difference(x0, y0, x1, y1, x2, y2) -> float:
	return abs(slope(x0, y0, x1, y1) - slope(x1, y1, x2, y2))

def angle_difference(x0, y0, x1, y1, x2, y2) -> float:
	m1: float = slope(x0, y0, x1, y1)
	m2: float = slope(x1, y1, x2, y2)
	return abs(math.atan(m1) - math.atan(m2))	

def dynamic_step(xvals: Vals) -> Vals:
	yvals = f_list(xvals)
	best_i = 1
	# best_slope: float = slope(xvals[0], yvals[0], xvals[1], yvals[1])
	best_slope_diff: float = angle_difference(xvals[0], yvals[0], xvals[1], yvals[1], xvals[2], yvals[2])
	for i in range(1, len(xvals) - 1):
		cur_diff = angle_difference(xvals[i-1], yvals[i-1], xvals[i], yvals[i], xvals[i+1], yvals[i+1])
		if best_slope_diff < cur_diff:
			best_i = i
			best_slope_diff = cur_diff

	xvals.insert(best_i + 1, (xvals[best_i] + xvals[best_i + 1]) / 2)
	xvals.insert(best_i, (xvals[best_i - 1] + xvals[best_i]) / 2)
	print("best_slope_diff", best_slope_diff)
	return xvals

def print_stats(xvals: Vals) -> None:
	print("sum", trapezoidal_sum(xvals))
	print("error", abs(exact_integral - trapezoidal_sum(xvals)))
	print("len(xvals)", len(xvals))
	# print("error * len(xvals)", (exact_integral - trapezoidal_sum(xvals)) * len(xvals))
	print()

def main() -> None:
	SCREEN_SIZE: int = 700
	unscalled_x_max: float = hi
	unscalled_y_max: float = .2

	pygame.init()
	screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))

	def to_drawable(x: float, y: float) -> tuple[float, float]:
		# print(x, y)
		# print(x / unscalled_x_max * SCREEN_SIZE, SCREEN_SIZE - (y / unscalled_y_max * SCREEN_SIZE))
		# print()
		assert 0 <= x <= unscalled_x_max
		assert 0 <= y <= unscalled_y_max # should have dynamic scaling and axis lines
		return x / unscalled_x_max * SCREEN_SIZE, SCREEN_SIZE - (y / unscalled_y_max * SCREEN_SIZE)
	
	def draw_Vals(xvals: Vals) -> None:
		yvals = f_list(xvals)
		for i in range(len(xvals) - 1):
			pygame.draw.aaline(screen, (255, 255, 255),
				to_drawable(xvals[i], yvals[i]),
				to_drawable(xvals[i+1], yvals[i+1])
			)
			pygame.draw.aaline(screen, (255, 255, 255),
				to_drawable(xvals[i], 0),
				to_drawable(xvals[i], yvals[i])
			)
		pygame.draw.aaline(screen, (255, 255, 255),
			to_drawable(xvals[-1], 0),
			to_drawable(xvals[-1], yvals[-1])
		)
	
	
	dynamic_xvals = regular_init(4) # 3 demonstrates edge case
	regular_xvals: Vals = regular_init(len(dynamic_xvals) - 1)

	print("dynamic_xvals:")
	print_stats(dynamic_xvals)
	print("regular_xvals")
	print_stats(regular_xvals)
	screen.fill((0, 0, 0))
	draw_Vals(dynamic_xvals)
	pygame.display.flip()

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return
			elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
				dynamic_xvals = dynamic_step(dynamic_xvals)
				print("dynamic_xvals:")
				print_stats(dynamic_xvals)

				regular_xvals = regular_init(len(dynamic_xvals) - 1)
				print("regular_xvals")
				print_stats(regular_xvals)

				screen.fill((0, 0, 0))
				draw_Vals(dynamic_xvals)
				pygame.display.flip()


		# draw_Vals(regular_x, regular_y)
		# clock.tick()




main()
pygame.quit()