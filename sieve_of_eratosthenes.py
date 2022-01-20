"""Sieve of Eratosthenes

Sources:
* https://www.geeksforgeeks.org/python-program-for-sieve-of-eratosthenes/
"""

def gen_primes(n):
	prime = [True for i in range(n + 1)]
	prime[0]= False
	prime[1]= False

	i = 2
	while (i * i <= n):
		if not is_prime[i]:
			continue

		j = i
		while i*j <= n:
			is_prime[i*j] = False
			j += 1

		i += 1

	return [i for i in range(len(prime)) if prime[i]]