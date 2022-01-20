"""Dining philosophers

https://leetcode.com/problems/the-dining-philosophers

The Resource Hierarchy solution:
* Starting from philosopher 0 number each fork from 0 to 4 clockwise
* Each philosopher picks up the smaller fork first. 
  For every philosopher that is the fork to the right except for the first
  philosopher where the smaller fork is the fork to the left.

Sources:
* https://en.wikipedia.org/wiki/Dining_philosophers_problem
* https://leetcode.com/problems/the-dining-philosophers/discuss/628017/python-with-5-locks
  ("Philosopher 0 wants their right fork first while other philosophers want the left one first, so no deadlock.")
"""

import threading


class DiningPhilosophers:

    def __init__(self):
        self.forks = [threading.Lock() for _ in range(5)]
    
    # call the functions directly to execute, for example, eat()
    def wantsToEat(self,
                   philosopher: int,
                   pickLeftFork: 'Callable[[], None]',
                   pickRightFork: 'Callable[[], None]',
                   eat: 'Callable[[], None]',
                   putLeftFork: 'Callable[[], None]',
                   putRightFork: 'Callable[[], None]') -> None:
        l = philosopher
        r = (philosopher + 1) % 5
        if philosopher == 0:
            first, second = l, r
        else:
            first, second = r, l
            
        with self.forks[first]:
            with self.forks[second]:
                pickLeftFork()
                pickRightFork()
                eat()
                putLeftFork()
                putRightFork()