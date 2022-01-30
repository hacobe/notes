def get_bit(num, i):
	mask = 1 << i
	return (num & mask) != 0

def set_bit(num, i):
	mask = 1 << i
	return num | mask

def clear_bit(num, i):
	mask = ~(1 << i)
	return num & mask