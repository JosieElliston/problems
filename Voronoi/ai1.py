from __future__ import annotations
import random
import pygame

# minesweeper but with structure of Brainsweeper

Point = tuple[int, int]
Color = tuple[int, int, int]

C_ROW: int = 8
""" CELLS PER ROW """
B_COUNT: int = (C_ROW * C_ROW) // 6
""" BOMB COUNT """
SCREEN_SIZE: int = 700
UNDERLAP: int = 3

COLOR_MAPPING: list[Color] = [
	(200, 200, 200),
    (22, 95, 199),
    (45, 126, 46),
    (198, 25, 36),
    (102, 0, 144),
    (246, 123, 10),
    (28, 137, 150),
    (67, 64, 60),
    (0, 0, 0)
]

class Cell:
	def __init__(self, x: int, y: int) -> None:
		self.clicked = False
		self.adjacent = 0
		self.neighbors: set[int] = set()
		self.x: int = x
		self.y: int = y
		self.rect: pygame.Rect = pygame.Rect(
			x * (SCREEN_SIZE - UNDERLAP) / C_ROW + UNDERLAP,
			y * (SCREEN_SIZE - UNDERLAP) / C_ROW + UNDERLAP,
			SCREEN_SIZE / C_ROW - UNDERLAP,
			SCREEN_SIZE / C_ROW - UNDERLAP
		)

	def draw(self) -> None:
		color: Color
		if not self.clicked:
			pygame.draw.rect(screen, (0, 0, 0), self.rect)
		elif self.adjacent == -1:
			pygame.draw.rect(screen, (100, 100, 100), self.rect)
		else:
			pygame.draw.rect(screen, COLOR_MAPPING[self.adjacent], self.rect)
	
	def draw_override(self, color: Color) -> None:
		pygame.draw.rect(screen, color, self.rect)

class Graph:
	def __init__(self) -> None:
		# self.cell_of_point: dict[Point, int] = dict()
		self.clicked = False
		self.cells: list[Cell] = list()
		for y in range(C_ROW):
			for x in range(C_ROW):
				self.cells.append(Cell(x, y))
		for i in range(len(self.cells)):
			for j in range(len(self.cells)):
				delta_x: int = abs(self.cells[i].x - self.cells[j].x)
				delta_y: int = abs(self.cells[i].y - self.cells[j].y)
				if delta_x <= 1 and delta_y <= 1 and not (delta_x == 0 and delta_y == 0):
					self.cells[i].neighbors.add(j)
	
	def draw(self):
		for cell in self.cells:
			cell.draw()
	
	def first_click(self, clicked_cell: Cell) -> None:
		valid_cells: list[Cell] = self.cells.copy()
		valid_cells.remove(clicked_cell)
		for neighbor in clicked_cell.neighbors:
			valid_cells.remove(self.cells[neighbor])
		
		random.shuffle(valid_cells)
		for i in range(B_COUNT):
			valid_cells[i].adjacent = -1
		
		for cell in self.cells:
			if cell.adjacent != -1:
				for neighbor in cell.neighbors:
					if self.cells[neighbor].adjacent == -1:
						cell.adjacent += 1

	def click(self, clicked_cell: Cell) -> None:
		if not self.clicked:
			self.first_click(clicked_cell)
			self.clicked = True

		clicked_cell.clicked = True
		if clicked_cell.adjacent == 0:
			for neighbor in clicked_cell.neighbors:
				if not self.cells[neighbor].clicked:
					self.click(self.cells[neighbor])
	
	def click_helper(self, mouse_pos: Point) -> None:
		x: int = int(mouse_pos[0] / SCREEN_SIZE * C_ROW)
		y: int = int(mouse_pos[1] / SCREEN_SIZE * C_ROW)
		self.click(self.cells[y * C_ROW + x])

screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))

graph: Graph = Graph()

pygame.init()
my_font = pygame.font.SysFont('Comic Sans MS', 30)

run: bool = True
clock = pygame.time.Clock()
prev_mouse: Point = (-1, -1)
while not pygame.QUIT in [event.type for event in pygame.event.get()]:
	clock.tick(30)
	mouse_pos = pygame.mouse.get_pos()
	if pygame.mouse.get_pressed()[0]:
		if mouse_pos != prev_mouse:
			prev_mouse = mouse_pos
			graph.click_helper(mouse_pos)
			# for cell in graph.cells:
			# 	print(cell.adjacent)
	

	screen.fill((0, 0, 0))
	graph.draw()

	# x: int = int(mouse_pos[0] / SCREEN_SIZE * C_ROW)
	# y: int = int(mouse_pos[1] / SCREEN_SIZE * C_ROW)
	# # rect: pygame.Rect = pygame.Rect(
	# # 	x * (SCREEN_SIZE - UNDERLAP) / C_ROW + UNDERLAP,
	# # 	y * (SCREEN_SIZE - UNDERLAP) / C_ROW + UNDERLAP,
	# # 	SCREEN_SIZE / C_ROW - UNDERLAP,
	# # 	SCREEN_SIZE / C_ROW - UNDERLAP
	# # )
	# # pygame.draw.rect(screen, (250, 150, 150), rect)
	# for cell in graph.cells:
	# 	if cell.x == x and cell.y == y:
	# 		cell.draw_override((250, 50, 50))
	# 		for neighbor in cell.neighbors:
	# 			neighbor.draw_override((250, 150, 150))

	font = pygame.font.Font('freesansbold.ttf', 32)
	text = font.render('GeeksForGeeks', True, (0, 0, 0))
	textRect = text.get_rect()
	textRect.center = (200, 200)
	screen.blit(text, textRect)


	pygame.display.flip()
pygame.quit()