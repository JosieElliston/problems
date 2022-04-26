import timeit
UP_TO = 10**4

start = timeit.default_timer()
is_prime = [True for i in range(UP_TO)]
p = 2
while (p <= UP_TO**.5):
	if (is_prime[p] == True):
		for i in range(p ** 2, UP_TO, p):
			is_prime[i] = False
	p += 1
is_prime[0]= False
is_prime[1]= False
primes = list(filter(lambda a : is_prime[a], range(len(is_prime))))
primes = list(filter(lambda a: 1000 < a < 10000, primes))
stop = timeit.default_timer()
print('Time to gen is_prime and primes:', stop - start)

def sorted_int(n: int) -> str:
	return "".join(sorted(list(str(n))))

groups: dict[str, list[int]] = dict()

for p in primes:
	key = sorted_int(p)
	if groups.get(key):
		groups[key].append(p)
	else:
		groups[key] = [p]
	
def works(group: list[int]) -> bool:
	if len(group) < 3:
		return False
	spacing = group[1] - group[0]
	
	for i in range(1, len(group) - 1):
		if group[i + 1] - group[i] != spacing:
			return False
	return True

print(groups)

new = []
for key in groups:
	if works(groups[key]):
		new.append(groups[key])
print(new)