"""Floyd cycle detection in a linked list.

Sources:
* https://leetcode.com/problems/linked-list-cycle/
"""

def floyd(head):
	# It's a race so they both start at the start line
	slow = head
	fast = head
	while slow and fast and fast.next:
		# Iterate before the if statement
		slow = slow.next
		fast = fast.next.next

		if slow == fast:
			return True
	return False
