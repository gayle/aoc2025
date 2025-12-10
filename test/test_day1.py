# python -m pytest python/test/test_day1.py
from python.src.day1 import Day1 
import tempfile 
import os

class TestDay1: 

	def test_right_rotation(self): 
		assert 12 == Day1.rotate_dial(5, "R7")

	def test_right_rotation_pass_99(self): 
		assert 55 == Day1.rotate_dial(95, "R60")

	def test_right_rotation_start_at_0(self): 
		assert 14 == Day1.rotate_dial(0, "R14")

	def test_right_rotation_end_at_0(self): 
		assert 0 == Day1.rotate_dial(52, "R48")

	def test_right_rotation_large_number(self): 
		assert 0 == Day1.rotate_dial(50, "R450")

	def test_left_rotation(self): 
		assert 52 == Day1.rotate_dial(82, "L30")

	def test_left_rotation_pass_0(self): 
		assert 82 == Day1.rotate_dial(50, "L68")

	def test_left_rotation_start_at_0(self): 
		assert 95 == Day1.rotate_dial(0, "L5")

	def test_left_rotation_end_at_0(self): 
		assert 0 == Day1.rotate_dial(55, "L55")

	def test_left_rotation_large_number(self): 
		assert 0 == Day1.rotate_dial(50, "L450")

	def test_invalid_input_starting_position_negative(self): 
		try: 
			Day1.rotate(dial(-1, "R10")
			assert False, "Starting position must be between 0 and 99"
		except ValueError: 
			pass

	def test_invalid_input_starting_position_greater_than_99(self): 
		try: 
			Day1.rotate(dial(100, "R10")
			assert False, "Starting position must be between 0 and 99"
		except ValueError: 
			pass

	def test_invalid_input_letter(self): 
		try: 
			Day1.rotate(dial(50, "X10")
			assert False, "Invalid direction; expected 'L' or 'R'"
		except ValueError: 
			pass

	def test_count_times_dial_is_at_zero(self): 
		test_content = """
		L68
		L30
		R48
		L5
		R60
		L55
		L1
		L99
		R14
		L82
        """

        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp: 
			tmp.write(test_content)
			tmp.flush()
			temp_filename = tmp.name

        try:
			result = Day1.count_times_dial_is_at_zero(temp_filename)
			assert 3 == result
        finally: 
			os.remove(temp_filename)
