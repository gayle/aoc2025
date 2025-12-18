import pytest
import tempfile
import sys, os
from day2_part1 import Day2Part1

def test_right_rotation():
    assert True == Day2Part1.contains_invalid_id(1, 2)
