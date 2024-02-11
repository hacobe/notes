"""Calculator.

Algorithm:
1) Tokenize the expression (e.g., " 2 + 3 * 4  " -> ["2", "+", "3", "*", "4"])
2) Add zeros to handle negation (e.g., ["-", "5", "*", "6"] -> ["0", "-", "5", "*", "6"])
3) Convert infix tokens to postfix tokens (e.g., ["7", "+", "8"] -> ["7", "8", "+"])
4) Evaluate the postfix tokens

Step (3) uses the shunting yard algorithm, where we iterate through
the infix tokens:
* If the token is a number, we push it to the output
* If the token is (, we push it to the operator stack
* If the token is ), then we pop off operators from the operator stack
  and push them to the output until we encounter a (. At that point,
  we pop off the ( from the operator stack and do not push it to the output.
* If the token is any other operator, then we pop off operators from
  the operator stack to the output until we encounter a ( or we encounter
  an operator with a lower precedence than the current operator.
  After that, the current operator is added to the operator stack.
* When we have processed all the infix tokens, we pop off operators from the
  operator stack and push them to the output until the operator stack is empty.

This implementation does not handle:
* Floats
* Functions like exp, log, etc.
* Exponentiation
* Implicit multiplication notation like (x+1)(x-1)
* Scientific notation
* Mathematical constants like e and pi
* Invalid inputs

It passes the test suite for:
* https://leetcode.com/problems/basic-calculator/
* https://leetcode.com/problems/basic-calculator-ii/
* https://leetcode.com/problems/basic-calculator-iii/

Sources:
* https://github.com/charon25/ShuntingYard/blob/master/shunting_yard
* https://en.wikipedia.org/wiki/Shunting_yard_algorithm

Additional sources:
* https://stackoverflow.com/questions/35257594/shunting-yard-vs-recursive-descent-parser
* https://web.archive.org/web/20240211152617/https://tomekkorbak.com/2020/03/25/implementing-shunting-yard-parsing/
* https://web.archive.org/web/20240211152608/https://palit.me/blog/4-ways-calculator-part-1
* https://leetcode.com/problems/basic-calculator/solutions/1456850/python-basic-calculator-i-ii-iii-easy-solution-detailed-explanation/
* https://leetcode.com/problems/basic-calculator/solutions/3992010/shunting-yard-algorithm-simple-and-concise/
* https://leetcode.com/problems/basic-calculator/solutions/248196/infix-postfix-then-evaluate/
* https://leetcode.com/problems/basic-calculator-iii/solutions/2253393/python-solution-easy-understanding-postfix-infix-expression-tree-o-n/
"""
def tokenize(expr):
	"""Tokenize the given expression.

	* Removes whitespace
	* Each integer is a token (e.g., "9", "123")
	* Each operation is a token (e.g., "(", "*")
	* Does not handle floats
	"""
	tokens = []
	i = 0
	while i < len(expr):
		if expr[i].isdigit():
			j = i
			while j < len(expr) and expr[j].isdigit():
				j += 1
			tokens.append(expr[i:j])
			i = j
		elif expr[i] in "()+-*/":
			tokens.append(expr[i])
			i += 1
		else:
			i += 1
	return tokens


def insert_zero(infix_tokens):
	tokens = []
	for i, token in enumerate(infix_tokens):
		if token == "-" and (i == 0 or infix_tokens[i-1] == "("):
			tokens.extend(["0", "-"])
		else:
			tokens.append(token)
	return tokens


def infix_to_postfix(infix_tokens):
	# Order of operations conventions:
	# * Parentheses
	# * Exponentiation
	# * Multiplication and Division
	# * Addition and Subtraction
	precedence = {
		"*": 1,
		"/": 1,
		"+": 0,
		"-": 0
	}

	postfix_tokens = []
	op_stack = []
	for token in infix_tokens:
		if token.isdigit():
			postfix_tokens.append(token)
		elif token == "(":
			op_stack.append(token)
		elif token == ")":
			while op_stack[-1] != "(":
				postfix_tokens.append(op_stack.pop())
			op_stack.pop()
		else:
			while op_stack:
				op = op_stack[-1]

				if op == "(":
					break

				if precedence[op] < precedence[token]:
					break

				postfix_tokens.append(op_stack.pop())

			op_stack.append(token)

	while op_stack:
		postfix_tokens.append(op_stack.pop())

	return postfix_tokens


def evaluate(expr):
	infix_tokens = insert_zero(tokenize(expr))
	postfix_tokens = infix_to_postfix(infix_tokens)
	stack = []
	value = 0
	for token in postfix_tokens:
		if token.isdigit():
			stack.append(token)
		else:
			a = int(stack.pop())
			b = int(stack.pop())
			if token == "+":
				value = a + b
			elif token == "-":
				value = b - a
			elif token == "*":
				value = a * b
			elif token == "/":
				sign = 1 if (b / a) > 0 else -1
				value = sign * (abs(b) // abs(a))
			stack.append(str(value))
	assert len(stack) == 1
	return int(stack[0])


if __name__ == "__main__":
	assert evaluate(" -3 + 5 *  41 + 3 +     (2 * 5 + 7) + (-3)   ") == 219
	assert evaluate(" 2-1 + 2 ") == 3
	assert evaluate("4/2") == 2
	assert evaluate("2 * 3 + 4") == 10
	assert evaluate("2 + 3 * 4") == 14
	assert evaluate("(2 + 3) * 4") == 20
