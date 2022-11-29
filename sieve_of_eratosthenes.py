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
		if prime[i] == False:
			i += 1
			continue

		j = i
		while i*j <= n:
			prime[i*j] = False
			j += 1

		i += 1

	return [i for i in range(len(prime)) if prime[i]]


if __name__ == "__main__":
	assert gen_primes(20) == [2, 3, 5, 7, 11, 13, 17, 19]
