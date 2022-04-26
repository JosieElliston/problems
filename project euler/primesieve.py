import timeit
UP_TO = 10**6

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
stop = timeit.default_timer()
print('Time to gen is_prime and primes:', stop - start)