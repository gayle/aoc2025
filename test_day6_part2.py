import pytest, tempfile, sys, os
from day6_part2 import Day6Part2

# Here's the example worksheet again:

# 123 328  51 64 
#  45 64  387 23 
#   6 98  215 314
# *   +   *   +  

# Reading the problems right-to-left one column at a time, the problems are now quite different:

# The rightmost problem is 4 + 431 + 623 = 1058
# The second problem from the right is 175 * 581 * 32 = 3253600
# The third problem from the right is 8 + 248 + 369 = 625
# Finally, the leftmost problem is 356 * 24 * 1 = 8544
# Now, the grand total is 1058 + 3253600 + 625 + 8544 = 3263827.

# Solve the problems on the math worksheet again. What is the grand total found by adding together all of the answers to the individual problems?

input_text = '''123 328  51 64
 45 64  387 23
  6 98  215 314
*   +   *   +
'''

def test_solve_problem0():
    problems = Day6Part2.parse_input(input_text)
    assert problems[0] == [4, 431, 623, '+']
    assert Day6Part2.solve_problem(problems[0]) == 1058

def test_solve_problem1():
    problems = Day6Part2.parse_input(input_text)
    assert problems[1] == [175, 581, 32, '*']
    assert Day6Part2.solve_problem(problems[1]) == 3253600

def test_solve_problem2():
    problems = Day6Part2.parse_input(input_text)
    assert problems[2] == [8, 248, 369, '+']
    assert Day6Part2.solve_problem(problems[2]) == 625

def test_solve_problem3():
    problems = Day6Part2.parse_input(input_text)
    assert problems[3] == [356, 24, 1, '*']
    assert Day6Part2.solve_problem(problems[3]) == 8544

def test_total_result():
    problems = Day6Part2.parse_input(input_text)
    assert Day6Part2.total_result(problems) == 3263827
