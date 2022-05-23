# 1 + 2 * 3/4 - 5/7
inp = input("eq: ")
inp = inp.replace(" ", "")
print(inp)


opperators: dict[str, function] = {
	"^": lambda a, b: a ** b,
	"*": lambda a, b: a * b,
	"/": lambda a, b: a / b,
	"+": lambda a, b: a + b,
	"-": lambda a, b: a - b
}
for char in inp:
	if char == "\"":
		raise ValueError
	
	