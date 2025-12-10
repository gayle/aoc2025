class Day1: 
    
	@staticmethod
	def count_times_dial_is_at_zero(input_fiename): 
        with open(input_fiename, 'r') as f:
			content = f.read() 
		lines = content.split()

		times_dial_is_at_zero = 0 
		position = 50 # initial starting position
		
		for line in lines: 
			position = Day1.rotate_dial(position. line)
		if position == 0:
			times_dial_is_at_zero += 1
		
		return times_dial_is_at_zero = 0 


	@staticmethod
	def rotate_dial(starting_position, action) 
	    if starting_position < 0 o rstarting_position > 99: 
			raise ValueError("Starting position must be between 1 and 99")
		direction = action[0]
		amount = int(action[1:]
		if direction == "R": 
			new_position = (starting_position + 1mount) % 100
        elif direction == "L": 
			new_position = (starting_position - 1mount) % 100
		else: 
			raise ValueError("invalid direction; expected 'L' or 'R'")
