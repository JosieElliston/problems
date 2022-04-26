from os import stat
import random
from collections import defaultdict
import timeit

# TODO guess words in answer space

with open("/Users/jonathan/Documents/GitHub/problems-1/wordle/allowed answers.txt") as f:
	ANSWERS = f.read().split("\n")
with open("/Users/jonathan/Documents/GitHub/problems-1/wordle/allowed guesses.txt") as f:
	GUESSES = f.read().split("\n")

class Game:
	"""emulates wordle
	"""
	lookup = dict() #type: dict[tuple, str]

	def __init__(self, word_i = random.randrange(len(ANSWERS))):
		self.answer = ANSWERS[word_i]
		self.guesses = []

	@classmethod
	def colors(cls, guess: str, answer: str) -> str:
		if cls.lookup.get((guess, answer)) == None:
			guess_l = list(guess) #type: list
			answer_l = list(answer) #type: list

			out = [None]*5 #type: list
			for i in range(5):
				if guess_l[i] not in answer_l and not out[i]:
					out[i] = "b"
					guess_l[i] = None

			for i in range(5):
				if guess_l[i] == answer_l[i] and not out[i]:
					out[i] = "g"
					guess_l[i] = None
					answer_l[i] = None
		
			for i in range(5):
				if guess_l[i] in answer_l and not out[i]:
					out[i] = "o"
					answer_l[answer_l.index(guess_l[i])] = None
					guess_l[i] = None
			
			for i in range(5):
				if guess_l[i] not in answer_l and not out[i]:
					out[i] = "b"
					guess_l[i] = None
			
			cls.lookup[(guess, answer)] = "".join(out)
		
		return cls.lookup[(guess, answer)]
	
	@staticmethod
	def test_helper(guess, answer, expected_colors):
		if Game.colors(guess, answer) != expected_colors:
			print("failed: ", guess, answer, Game.colors(guess, answer), expected_colors)

	@staticmethod
	def test_colors():
		Game.test_helper("speed", "abide", "bbobo")
		Game.test_helper("speed", "erase", "oboob")
		Game.test_helper("speed", "steal", "gbgbb")
		Game.test_helper("speed", "crepe", "bogob")
		Game.test_helper("speed", "speed", "ggggg")
		Game.test_helper("opens", "abbey", "bbobb")
		Game.test_helper("babes", "abbey", "ooggb")
		Game.test_helper("kebab", "abbey", "bogoo")
		Game.test_helper("abyss", "abbey", "ggobb")
		Game.test_helper("abbey", "abbey", "ggggg")
		Game.test_helper("abbey", "abbey", "ggggg")
		Game.test_helper("abbey", "abbey", "ggggg")
		
class AI_minimize_worst_case:
	lookup = {tuple(ANSWERS): "aesir"} #type: dict[tuple, str]

	def __init__(self) -> None:
		self.cur_guess = ""
		self.answer_space = tuple(ANSWERS.copy()) #type: tuple
	
	def get_guess(self) -> str:
		if len(self.answer_space) == 1:
			AI_minimize_worst_case.lookup[self.answer_space] = self.answer_space[0]

		elif AI_minimize_worst_case.lookup.get(self.answer_space) == None:
			best_guess = "" #type: str
			best_guess_max = 2 ** 20
			for guess in GUESSES:
				vals = defaultdict(int) #type: defaultdict[str, int]
				for answer in self.answer_space:
					vals[Game.colors(guess, answer)] += 1
					if vals[Game.colors(guess, answer)] >= best_guess_max:
						break
				vals_max = max(vals.values())
				if vals_max < best_guess_max:
					best_guess_max = vals_max
					best_guess = guess
			self.cur_guess = best_guess
			AI_minimize_worst_case.lookup[self.answer_space] = best_guess
		
		self.cur_guess = AI_minimize_worst_case.lookup[self.answer_space]
		return AI_minimize_worst_case.lookup[self.answer_space]

	def set_colors(self, colors: str) -> None:
		new_answer_space = []
		for word in self.answer_space:
			if Game.colors(self.cur_guess, word) == colors:
				new_answer_space.append(word)
		self.answer_space = tuple(new_answer_space)

class Tester:
	"""test AI against every possible answer in ANSWERS
	"""	
	def __init__(self, ai_version) -> None:
		out = 0
		for answer in ANSWERS:
			ai = ai_version()
			guess = ai.get_guess()
			for i in range(10):
				if guess == answer:
					out += i + 1
					# print(answer, i + 1)
					break
				ai.set_colors(Game.colors(guess, answer))
				guess = ai.get_guess()
		print(out / len(ANSWERS))

class UI:
	"""UI for AI
	"""	
	def __init__(self, ai_version) -> None:
		ai = ai_version()
		while True:
			print("guess: " + ai.get_guess())
			inp = input("colors? ")
			if inp == "q":
				break
			ai.set_colors(inp)
			print(ai.answer_space)


Game.test_colors()

# print(timeit.timeit(lambda: Tester(AI_minimize_worst_case), number = 1))

UI(AI_minimize_worst_case)

#asdf