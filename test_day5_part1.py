import pytest, tempfile, sys, os
from day5_part1 import Day5Part1

# The Elves in the kitchen explain the situation: because of their complicated new inventory management system, they can't figure out which of their ingredients are fresh and which are spoiled. When you ask how it works, they give you a copy of their database (your puzzle input).

# The database operates on ingredient IDs. It consists of a list of fresh ingredient ID ranges, a blank line, and a list of available ingredient IDs. For example:

# 3-5
# 10-14
# 16-20
# 12-18

# 1
# 5
# 8
# 11
# 17
# 32
# The fresh ID ranges are inclusive: the range 3-5 means that ingredient IDs 3, 4, and 5 are all fresh. The ranges can also overlap; an ingredient ID is fresh if it is in any range.

# The Elves are trying to determine which of the available ingredient IDs are fresh. In this example, this is done as follows:

# Ingredient ID 1 is spoiled because it does not fall into any range.
# Ingredient ID 5 is fresh because it falls into range 3-5.
# Ingredient ID 8 is spoiled.
# Ingredient ID 11 is fresh because it falls into range 10-14.
# Ingredient ID 17 is fresh because it falls into range 16-20 as well as range 12-18.
# Ingredient ID 32 is spoiled.
# So, in this example, 3 of the available ingredient IDs are fresh.

# Process the database file from the new inventory management system. How many of the available ingredient IDs are fresh?

input = '''3-5
10-14
16-20
12-18

1
5
8
11
17
32
'''

def test_parse_input():
    fresh_ranges, available_ids = Day5Part1.parse_input(input)
    assert fresh_ranges == [[3, 5], [10, 14], [16, 20], [12, 18]]
    assert available_ids == [1, 5, 8, 11, 17, 32]

def test_fresh_ingredient_count():
    ranges, ids = Day5Part1.parse_input(input)
    assert Day5Part1.fresh_ingredient_count(ranges, ids) == 3
