UP_TO = 100
is_prime = [True for i in range(UP_TO + 1)]
p = 2
while (p <= UP_TO**.5+1):
	if (is_prime[p] == True):
		for i in range(p ** 2, UP_TO + 1, p):
			is_prime[i] = False
	p += 1
is_prime[0], is_prime[1] = False, False
primes = list(filter(lambda a : is_prime[a], range(len(is_prime))))
print(primes)

def prime_sum(lo_i, hi_i):
	return sum(primes[lo_i, hi_i + 1])

# """return False if doesn't work for lo_i guess
# 	return working hi_i guess otherwise"""
# def helper(lo_i, hi_i, testing):
# 	if prime_sum(lo_i, hi_i) == testing:
# 		return hi_i
# 	if prime_sum(lo_i, hi_i) > testing:
# 		hi_i 

# def works(prime_i):
# 	for lo_i in range(prime_i):
# 		if helper(lo_i, prime_i, primes[prime_i]):
# 			return lo_i, helper(lo_i, prime_i)

def helper(lo_i, testing):
	hi_i = lo_i + 1

def works(prime_i):
	for lo_i in range(prime_i):
		

for prime_i in list(range(len(primes)-1))[::-1]:
	if works(prime_i):
		print(primes[prime_i])
		break