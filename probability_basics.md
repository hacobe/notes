# Probablity basics

A **sample space** is the set of possible outcomes of an experiment.

A **realization** or an **outcome** is an element of a sample space.

An **event** is a subset of a sample space, i.e., a set of realizations.

A **probability distribution** is a function P that assigns a real number (i.e., a **probability**) to each event A in sample space S these 3 axioms are met:

1) Non-negativity: P(A) >= 0 for every A in S
2) Countable additivity: If A_1, A_2, ... are disjoint, then P(union of A_i) = sum P(A_i)
3) P(S) = 1

This definition isn't quite right, because sometimes it isn't possible to assign a probability to every event in the sample space. For example, we cannot assign a probability that meets these axioms when the sample space is the entire real line. Instead, we replace S in the definition above with a subset T of the power set of S, where T meets the following criteria:
1) the empty set and the sample space must be in T
2) If A is in T, then the complement of A should also be in T (we want to assign probabilities to an event occurring and to the event not occurring)
3) If A_1, A_2, ... are in T, then the union of A_1, A_2, ... are also in T.

We can think of this as "reasonable" sets where we can actually assign a probability to them that follows the axioms. If these criteria are met, then T is called a **sigma algebra**. The sets in it are **measurable**. The pair (S, T) is called a **measurable space**. The triple consisting of the S, T and the probability measure (or probability distribution, i.e., the function mapping an event to a real number) is called a **probability space**. Note that the difference between a probability measure and a more general notion of measure is that a probability measure requires that P(T) = 1. For a measure, we only require that the measure of the empty set is 0. If P(T) = 1, then the probability of the empty set must also be 0. When S is the real line, we take T to be the smallest sigma algebra that all the open subsets (or equivalently all the closed subsets). This is called the **Borel sigma algebra**.

You can interpret a probability as a frequency (**frequentist**) or as a degree of belief (**Bayesian**).

The **conditional probability** of A given B is P(A | B) = P(A n B) / P(B).

Two events A and B are **independent** if P(A | B) = P(A).

*Independence is a symmetric relationship*. If P(A | B) = P(A), then P(B | A) = P(B n A) / P(A) = P(A n B) / P(A) = (P(A | B) * P(B)) / P(A) = P(B). If A is independent of B, then B is independent of A and vice versa. An equivalent definition of independence is then P(B | A) = P(B).
 
If P(A | B) = P(A), then P(A n B) = P(A | B) * P(B) = P(A)P(B). If P(A n B) = P(A)P(B), then P(A | B) = P(A). Another definition of independence is that P(A n B) = P(A)P(B).

*Disjoint events with positive probability are not independent.* If A and B have positive probability, then P(A)P(B) > 0, but P(AnB) must be equal to 0, because the events are disjoint, so P(AnB) cannot equal P(A)P(B), so they cannot be independent. Consider the event A consisting of the realization of a 6 sided die landing on 1 and the realization of the die landing on 2. And consider the event B consisting of the realization of the die landing on 3 and the die landing on 6. These events are disjoint. The realizations that appear in one do not appear in the other. They also each have positive probability. P(A n B) = 0. P(A) = P(the die landing on 1 or 2) = 2/6 = 1/3. P(B) = P(the die landing on 3 or 6) = 2/6 = 1/3. P(A)P(B) = 1/6.

*Independence depends on probabilities not just whether 2 events are overlapping*. Except in the case described above, you cannot tell whether 2 events are independent by looking at a Venn diagram. In particular, if two events are not disjoint, i.e., they are overlapping, then that is not enough information to determine whether they are independent or not. Consider a red ball and a blue ball in an urn. Consider defining probabilities to simulate drawing a ball from the urn, putting it back and then drawing the ball again. Define the event A = {RR, RG} and the event B = {RR, GR}. P(A) = 1/2 and P(B) = 1/2. P(A n B) = 1/4. P(A)P(B) = 1/4. They are overlapping, but still independent. Now change the probabilities to simulate drawing a ball from the urn, putting it back and then always drawing the red ball. P(A) = 1/4. P(B) = 1/2. P(A n B) = 1/4. P(A)P(B) = 1/8. They are overlapping and dependent. If you know A occurred, then you would know that B occurred also. P(B | A) = 1.

**Bayes theorem** is (P(A | B)P(A)) / P(B).

*Medical testing*. Suppose there is a test that is 90% accurate if you have the disease and 90% accurate if you're healthy. Suppose also that the prevalence of the disease 1%. You take the test and you test positive. What is the chance that you have the disease? Let D = 1 if you have the disease and 0 otherwise. Let T = 1 if you test positive and 0 otherwise. By Bayes rule, we have that P(D = 1 | T = 1) = (P(T = 1 | D = 1)P(D = 1)) / P(T = 1). (P(T = 1 | D = 1)P(D = 1)) = 0.9 * 0.01 = 0.009. P(T=1) = P(D=0)P(T = 1 | D = 0) + P(D = 1)P(T = 1 | D = 1) = (1 - 0.01) * (1 - 0.9) + 0.01 * 0.9 = 0.108. So P(D = 1 | T = 1) is around 0.08.

The **Principle of Inclusion and Exclusion** is that |A u B| = |A| + |B| - |A n B|.

For probability, we have that P(A u B) = P(A) + P(B) - P(A n B).

The **Law of total probability** is that P(B) = P(A_1) P(B | A_1) + ... + P(A_k) P(B | A_k) for any event B when A_1, ..., A_k is a partition of the sample space.

## Sources

* Chapter 1, "Probability", All of statistics, Wasserman
* [Probability Theory - Part 2 - Probability Measures](https://www.youtube.com/watch?v=u5IouBwYji4&list=PLBh2i93oe2qswFOC98oSFc37-0f4S3D4z&index=2)
* https://math.stackexchange.com/questions/1073744/distinguishing-probability-measure-function-and-distribution