from __future__ import annotations
import pygame

SCREEN_SIZE = 700
POINT_SIZE = 5

# camera is bottom up and sees unit square in the first quadrant
pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))

class Point:
	def __init__(self, x, y, z) -> None:
		# x, y, z in [0, 1]
		self.x = x
		self.y = y
		self.z = z
	
	def to_drawable(self) -> tuple[float, float]:
		# coords in [0, SCREEN_SIZE]
		return self.x * SCREEN_SIZE, self.y * SCREEN_SIZE
	
	def draw(self) -> None:
		pygame.draw.circle(screen, (255 * self.z, 255 * self.z, 255 * self.z), p.to_drawable(), POINT_SIZE)

points = {
	Point(.1, .1, .8),
	Point(.9, .9, .1),
	Point(.5, .5, .5)
}



while not pygame.QUIT in [event.type for event in pygame.event.get()]:
	screen.fill((0, 0, 0))
	for p in points:
		p.draw()
	pygame.display.flip()