import pytest, tempfile, sys, os
from textwrap import dedent
from day9_part1 import *

# The movie theater has a big tile floor with an interesting pattern. Elves here are redecorating the theater by switching out some of the square tiles in the big grid they form. Some of the tiles are red; the Elves would like to find the largest rectangle that uses red tiles for two of its opposite corners. They even have a list of where the red tiles are located in the grid (your puzzle input).

input_text = dedent('''\
    7,1
    11,1
    11,7
    9,7
    9,5
    2,5
    2,3
    7,3''')

# Ultimately, the largest rectangle you can make in this example has area 50. One way to do this is between 2,5 and 11,1:

# ..............
# ..OOOOOOOOOO..
# ..OOOOOOOOOO..
# ..OOOOOOOOOO..
# ..OOOOOOOOOO..
# ..OOOOOOOOOO..
# ..............
# .........#.#..
# ..............

# Using two red tiles as opposite corners, what is the largest area of any rectangle you can make?

def test_find_result():
    coords = parse_input(input_text)
    result = find_result(coords)
    assert result == 50
