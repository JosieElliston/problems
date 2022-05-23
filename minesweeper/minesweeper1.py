from __future__ import annotations
import pygame
import random

Color = tuple[int, int, int]

X_SIZE: int = 30
Y_SIZE: int = 16
BOMB_COUNT: int = X_SIZE * Y_SIZE // 5
SCREEN_SCALE: int = 30

def to_screen(a: int) -> float:
	return a * SCREEN_SCALE

def to_internal(a: float) -> int:
	return int(a / SCREEN_SCALE)

class Cell:
	def __init__(self, x: int, y: int) -> None:
		self.x: int = x
		self.y: int = y
		self.screen_x = to_screen(x)
		self.screen_y = to_screen(y)
		self.color = (165, 217, 76) if (x + y) % 2 == 0 else (146, 203, 57)
		self.is_bomb: bool = False
		self.revealed: bool = False
		self.adjacent: int = 0
		self.neighbors: list[tuple[int, int]] = list()

	# __eq__
	def draw(self) -> None:
		pygame.display.update(pygame.draw.rect(
			screen,
			self.color,
			pygame.Rect(
				self.screen_x,
				self.screen_y,
				SCREEN_SCALE,
				SCREEN_SCALE
			)
		))
		if self.is_bomb:
			pygame.display.update(pygame.draw.rect(
				screen,
				(255, 0, 0),
				pygame.Rect(
					self.screen_x,
					self.screen_y,
					SCREEN_SCALE,
					SCREEN_SCALE
				)
			))
		# if self.revealed:
		# 	print(str(self.adjacent))
		# 	screen.blit(
		# 		font.render(str(self.adjacent), True, (0, 0, 0)),
		# 		(self.screen_x, self.screen_y)
		# 	)
		screen.blit(
			font.render(str(self.adjacent), True, (0, 0, 0), self.color),
			(self.screen_x, self.screen_y)
		)

	def reveal(self):
		assert self.revealed == False
		self.revealed = True
		self.color = (222, 182, 141) if (self.x + self.y) % 2 == 0 else (205, 170, 135)
		self.draw()

class Game:
	def __init__(self) -> None:
		# construct cells
		self.cells: dict[tuple[int, int], Cell] = dict()
		for y in range(Y_SIZE):
			for x in range(X_SIZE):
				self.cells[(x, y)] = Cell(x, y)
		
		# construct neighbors
		for key in self.cells:
			x = key[0] + 1
			y = key[1] + 1
			if 0 <= x < X_SIZE and 0 <= y < Y_SIZE:
				self.cells[key].neighbors.append((x, y))

			x = key[0] + 0
			y = key[1] + 1
			if 0 <= x < X_SIZE and 0 <= y < Y_SIZE:
				self.cells[key].neighbors.append((x, y))
			
			x = key[0] - 1
			y = key[1] + 1
			if 0 <= x < X_SIZE and 0 <= y < Y_SIZE:
				self.cells[key].neighbors.append((x, y))
			

			x = key[0] + 1
			y = key[1] + 0
			if 0 <= x < X_SIZE and 0 <= y < Y_SIZE:
				self.cells[key].neighbors.append((x, y))

			x = key[0] - 1
			y = key[1] + 0
			if 0 <= x < X_SIZE and 0 <= y < Y_SIZE:
				self.cells[key].neighbors.append((x, y))
			

			x = key[0] + 1
			y = key[1] - 1
			if 0 <= x < X_SIZE and 0 <= y < Y_SIZE:
				self.cells[key].neighbors.append((x, y))

			x = key[0] + 0
			y = key[1] - 1
			if 0 <= x < X_SIZE and 0 <= y < Y_SIZE:
				self.cells[key].neighbors.append((x, y))
			
			x = key[0] - 1
			y = key[1] - 1
			if 0 <= x < X_SIZE and 0 <= y < Y_SIZE:
				self.cells[key].neighbors.append((x, y))
		
		# assume first click at 0, 0
		# construct bombs
		valid_cells = self.cells.copy()
		valid_cells.pop((0, 0))
		for nkey in self.cells[(0, 0)].neighbors:
			valid_cells.pop(nkey)

		for key in random.sample(valid_cells.keys(), BOMB_COUNT):
			self.cells[key].is_bomb = True
			for nkey in self.cells[key].neighbors:
				self.cells[nkey].adjacent += 1

		self.reveal((0, 0))
	
	def draw_all(self) -> None:
		for cell in self.cells.values():
			cell.draw()
		pygame.display.flip()

	def reveal(self, key) -> None:
		if not self.cells[key].revealed:
			self.cells[key].reveal()
			if self.cells[key].adjacent == 0:
				for nkey in self.cells[key].neighbors:
					self.reveal(nkey)

pygame.init()
screen = pygame.display.set_mode((
	to_screen(X_SIZE),
	to_screen(Y_SIZE)
))
font = pygame.font.SysFont('Comic Sans MS', SCREEN_SCALE // 2)

game: Game = Game()
game.draw_all()
run: bool = True
clock = pygame.time.Clock()
while run:
	clock.tick(60)
	# a = clock.tick()
	# if a != 0:
	# 	print(a)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		elif event.type == pygame.MOUSEBUTTONDOWN:
			pos = pygame.mouse.get_pos()
			game.reveal((to_internal(pos[0]), to_internal(pos[1])))

	# game.draw_all()

	# clock.tick(30)
	# mouse_pos = pygame.mouse.get_pos()
	# if pygame.mouse.get_pressed()[0]:
	# 	if mouse_pos != prev_mouse:
	# 		prev_mouse = mouse_pos
	# 		graph.click_helper(mouse_pos)