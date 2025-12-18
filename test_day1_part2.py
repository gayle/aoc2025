import pytest
import tempfile
import sys, os
from day1_part2 import Day1Part2

def test_right_rotation():
    assert (0,12) == Day1Part2.rotate_dial(5, "R7")

def test_right_rotation_pass_99():
    assert (1,55) == Day1Part2.rotate_dial(95, "R60")

def test_right_rotation_start_at_0():
    assert (0,14) == Day1Part2.rotate_dial(0, "R14")

def test_right_rotation_end_at_0():
    assert (1,0) == Day1Part2.rotate_dial(52, "R48")

def test_right_rotation_large_number():
    assert (10,50) == Day1Part2.rotate_dial(50, "R1000")

def test_left_rotation():
    assert (0,52) == Day1Part2.rotate_dial(82, "L30")

def test_left_rotation_pass_0():
    assert (1,82) == Day1Part2.rotate_dial(50, "L68")

def test_left_rotation_start_at_0():
    assert (0,95) == Day1Part2.rotate_dial(0, "L5")

def test_left_rotation_end_at_0():
    assert (1,0) == Day1Part2.rotate_dial(55, "L55")

def test_left_rotation_large_number():
    assert (5,0) == Day1Part2.rotate_dial(50, "L450")

def test_left_rotation_larger_number():
    assert (10,50) == Day1Part2.rotate_dial(50, "L1000")

def test_invalid_input_starting_position_negative():
    try:
        Day1Part2.rotate_dial(-1, "R10")
        assert False, "Starting position must be between 0 and 99"
    except ValueError:
        pass

def test_invalid_input_starting_position_greater_than_99():
    try:
        Day1Part2.rotate_dial(100, "R10")
        assert False, "Starting position must be between 0 and 99"
    except ValueError:
        pass

def test_invalid_input_letter():
    try:
        Day1Part2.rotate_dial(50, "X10")
        assert False, "Invalid direction; expected 'L' or 'R'"
    except ValueError:
        pass

def test_count_times_dial_crosses_zero():
    test_content = """L68
    L30
    R48
    L5
    R60
    L55
    L1
    L99
    R14
    L82"""
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
        tmp.write(test_content)
        tmp.flush()  # Ensure data is written
        temp_filename = tmp.name

    try:
        result = Day1Part2.count_times_dial_crosses_zero(temp_filename)
        assert 6 == result
    finally:
        os.remove(temp_filename)

def test_count_times_dial_crosses_zero_with_R1000():
    test_content = "R1000"
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
        tmp.write(test_content)
        tmp.flush()  # Ensure data is written
        temp_filename = tmp.name

    try:
        result = Day1Part2.count_times_dial_crosses_zero(temp_filename)
        assert 10 == result
    finally:
        os.remove(temp_filename)
