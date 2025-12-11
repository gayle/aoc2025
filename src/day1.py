class Day1: 

	@staticmethod
	def count_times_dial_is_at_zero(input_fiename): 
		content=''
		with open(input_fiename, 'r') as f:
			content = f.read() 
		lines = content.split()

		times_dial_is_at_zero = 0 
		position = 50 # initial starting position
		
		for line in lines: 
			position = Day1.rotate_dial(position, line)
			if position == 0:
				times_dial_is_at_zero += 1
		
		return times_dial_is_at_zero

	@staticmethod
	def rotate_dial(starting_position, action):
		if starting_position < 0 or starting_position > 99: 
			raise ValueError("Starting position must be between 1 and 99")
		direction = action[0]
		amount = int(action[1:])
		if direction == "R":
			new_position = (starting_position + amount) % 100
		elif direction == "L": 
			new_position = (starting_position - amount) % 100
		else: 
			raise ValueError("invalid direction; expected 'L' or 'R'")
		return new_position

if __name__ == "__main__":
	import sys
	if len(sys.argv)!= 2:
		print("Usage: python day1.py <input_filename>")
		sys.exit(1)
	input_filename = sys.argv[1]
	result = Day1.count_times_dial_is_at_zero(input_filename)
	print(result)
