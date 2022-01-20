# Modular exponentiation

Suppose you want to calculate $5^7 \mod 3$ and you have to work with unsigned 8 bit integers.

The largest integer we can use is 255 ($= 2^7 + 2^6 + \cdots + 2^1 + 2^0 = 2^8 - 1$).

$5^7 = 78125$, but our calculator will tell us it equals 45, because of overflow.

$78125 \mod 3 = 2$, while $45 \mod 3 = 0$, so we won't get the right answer.

But we can break down the problem as follows:

$5^7 \mod 3 = 5 \cdot (5^6 \mod 3) \mod 3$

$5^6 \mod 3 = (5^3 \mod 3)^2 \mod 3$

$5^3 \mod 3 = 5 \cdot (5^2 \mod 3 ) \mod 3$

$5^2 \mod 3 = (5^1 \mod 3)^2 \mod 3$

$5^1 \mod 3 = 5 \cdot (5^0 \mod 3) \mod 3$

And then solve each subproblem without ever needing to store an integer larger than 255:

$5^1 \mod 3 = 5 \cdot (5^0 \mod 3) \mod 3 = 2$

$5^2 \mod 3 = 2^2 \mod 3 = 1$

$5^3 \mod 3 = 5 \cdot 1 \mod 3 = 2$

$5^6 \mod 3 = 2^2 \mod 3 = 1$

$5^7 \mod 3 = 5 \cdot 1 \mod 3 = 2$

## Sources

* https://web.archive.org/web/20191224022818/https://superuser.com/questions/452498/how-can-computers-calculate-exponential-math-without-overflow-errors