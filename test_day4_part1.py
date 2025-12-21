import pytest, tempfile, sys, os
from day4_part1 import Day4Part1

# The rolls of paper (@) are arranged on a large grid; the Elves even have a helpful diagram (your puzzle input) indicating where everything is located.

# For example:

# ..@@.@@@@.
# @@@.@.@.@@
# @@@@@.@.@@
# @.@@@@..@.
# @@.@@@@.@@
# .@@@@@@@.@
# .@.@.@.@@@
# @.@@@.@@@@
# .@@@@@@@@.
# @.@.@@@.@.

# The forklifts can only access a roll of paper if there are fewer than four rolls of paper in the eight adjacent positions. If you can figure out which rolls of paper the forklifts can access, they'll spend less time looking and more time breaking down the wall to the cafeteria.

# In this example, there are 13 rolls of paper that can be accessed by a forklift (marked with x):

# ..xx.xx@x.
# x@@.@.@.@@
# @@@@@.x.@@
# @.@@@@..@.
# x@.@@@@.@x
# .@@@@@@@.@
# .@.@.@.@@@
# x.@@@.@@@@
# .@@@@@@@@.
# x.x.@@@.x.
# Consider your complete diagram of the paper roll locations. How many rolls of paper can be accessed by a forklift?

lines = [
    '..@@.@@@@.',
    '@@@.@.@.@@',
    '@@@@@.@.@@',
    '@.@@@@..@.',
    '@@.@@@@.@@',
    '.@@@@@@@.@',
    '.@.@.@.@@@',
    '@.@@@.@@@@',
    '.@@@@@@@@.',
    '@.@.@@@.@.'
]

def test_0_0():
    assert Day4Part1().is_roll(0, 0, lines) == False

def test_1_0():
    assert Day4Part1().is_roll(1, 0, lines) == False

def test_2_0():
    assert Day4Part1().is_roll(2, 0, lines) == True
    assert Day4Part1().roll_is_accessible(2, 0, lines) == True

def test_accessible_rolls():
    input_txt = '''..@@.@@@@.
@@@.@.@.@@
@@@@@.@.@@
@.@@@@..@.
@@.@@@@.@@
.@@@@@@@.@
.@.@.@.@@@
@.@@@.@@@@
.@@@@@@@@.
@.@.@@@.@.
'''
    # On Windows the default NamedTemporaryFile can't be reopened by name
    # by another open() call; create the file with delete=False and
    # remove it after the assertion.
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
        tmp.write(input_txt)
        tmp.flush()
        tmp_name = tmp.name
    try:
        Day4Part1.parse_input(tmp_name)
        assert len(Day4Part1.accessible_rolls(lines)) == 13
    finally:
        try:
            os.unlink(tmp_name)
        except Exception:
            pass
