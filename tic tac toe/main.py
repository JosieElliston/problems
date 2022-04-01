from dataclasses import dataclass
BELTS = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]
@dataclass
class Board:
	state: tuple
	
	def __init__(self, state = ("*", "*", "*", "*", "*", "*", "*", "*", "*")) -> None:
		self.state = state

	def __iter__(self):
		return iter(self.state)

	def won(self, player: str) -> bool:
		for belt in BELTS:
			if player == self.state[belt[0]] == self.state[belt[1]] == self.state[belt[2]]:
				return True
		return False
	
	def tie(self) -> bool:
		return not "*" in self.state
	
	def __getitem__(self, i):
		return self.state[i]
	
	def __str__(self):
		return "\n".join("".join(a) for a in zip(*(iter(self.state),) * 3)) + "\n"
	
	def __hash__(self):
		return hash(self.state)

class Game:
	# @staticmethod
	# def state_to_str(state: Board) -> str:
	# 	return "\n".join("".join(a) for a in zip(*(iter(state),) * 3))

	# @staticmethod
	# def won(state: Board, player: str) -> bool:
	# 	for belt in [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]:
	# 		if player == state[belt[0]] == state[belt[1]] == state[belt[2]]:
	# 			return True
	# 	return False
	
	# @staticmethod
	# def tie(state: Board) -> bool:
	# 	return not "*" in state
	
	@staticmethod
	def after_move(state: Board, pos: int, player: str) -> Board:
		return Board(state[:pos] + (player,) + state[pos:])

class AI_simple:

	lookup: dict[tuple[Board, str], Board] = dict()

	@classmethod
	def get_move(cls, state: Board, player: str) -> Board:
		if cls.lookup.get((state, player)) != None:
			return cls.lookup[(state, player)]

		# win if possible
		for move in range(9):
			if state[move] == "*" and Board.won(Game.after_move(state, move, player), player):
				cls.lookup[(state, player)] = Game.after_move(state, move, player)
				return cls.lookup[(state, player)]

		# block if possible
		for belt in BELTS:
			belt_letters = [state[belt[a]] for a in range(3)]
			if belt_letters.count("*") == 1 & belt_letters.count(player) == 0: # must contain 1 "*" and 2 not "player" <==> 0 "player"
				cls.lookup[(state, player)] = Game.after_move(state, belt[belt_letters.index("*")], player)
				return cls.lookup[(state, player)]


		# go in order corner, center, edge


		# return Board() # error

class UI:

	def __init__(self, ai_version) -> None:
		ai = ai_version()
		board = Board()
		print(board)
		while True:
			board = ai.get_move(board, "x")
			print(board)
			board = Game.after_move(board, int(input("pos")), "o")
			print(board)


UI(AI_simple)