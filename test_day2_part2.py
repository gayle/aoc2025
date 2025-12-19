import pytest
import tempfile
import sys, os
from day2_part2 import Day2Part2

# Sample from the problem description page:

# 11-22,95-115,998-1012,1188511880-1188511890,222220-222224,
# 1698522-1698528,446443-446449,38593856-38593862,565653-565659,
# 824824821-824824827,2121212118-2121212124

# 11-22 still has two invalid IDs, 11 and 22.
# 95-115 now has two invalid IDs, 99 and 111.
# 998-1012 now has two invalid IDs, 999 and 1010.
# 1188511880-1188511890 still has one invalid ID, 1188511885.
# 222220-222224 still has one invalid ID, 222222.
# 1698522-1698528 still contains no invalid IDs.
# 446443-446449 still has one invalid ID, 446446.
# 38593856-38593862 still has one invalid ID, 38593859.
# 565653-565659 now has one invalid ID, 565656.
# 824824821-824824827 now has one invalid ID, 824824824.
# 2121212118-2121212124 now has one invalid ID, 2121212121.

# Adding up all the invalid IDs in this example produces 4174379265.

# Invalid ids

def test_11():
    assert True == Day2Part2.invalid_id(11)

def test_111():
    assert True == Day2Part2.invalid_id(111)

def test_1010():
    assert True == Day2Part2.invalid_id(1010)

def test_1188511885():
    assert True == Day2Part2.invalid_id(1188511885)

def test_222222():
    assert True == Day2Part2.invalid_id(222222)

def test_565656():
    assert True == Day2Part2.invalid_id(565656)

def test_824824824():
    assert True == Day2Part2.invalid_id(824824824)

# Valid ids

def test_1():
    assert False == Day2Part2.invalid_id(1)
def test_110():
    assert False == Day2Part2.invalid_id(110)

def test_824824825():
    assert False == Day2Part2.invalid_id(824824825)

def test_824825824():
    assert False == Day2Part2.invalid_id(824825824)

def test_full_input():
    input = "11-22,95-115,998-1012,1188511880-1188511890,222220-222224,1698522-1698528,446443-446449,38593856-38593862,565653-565659,824824821-824824827,2121212118-2121212124"
    # On Windows the default NamedTemporaryFile can't be reopened by name
    # by another open() call; create the file with delete=False and
    # remove it after the assertion.
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
        tmp.write(input)
        tmp.flush()
        tmp_name = tmp.name
    try:
        assert 4174379265 == Day2Part2.sum_of_invalid_ids(tmp_name)
    finally:
        try:
            os.unlink(tmp_name)
        except Exception:
            pass
    