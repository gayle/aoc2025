import pytest
import tempfile
import sys, os
from day3_part1 import Day3Part1

# 987654321111111
# 811111111111119
# 234234234234278
# 818181911112111

# You'll need to find the largest possible joltage each bank can produce. In the above example:

# In 987654321111111, you can make the largest joltage possible, 98, by turning on the first two batteries.
# In 811111111111119, you can make the largest joltage possible by turning on the batteries labeled 8 and 9, producing 89 jolts.
# In 234234234234278, you can make 78 by turning on the last two batteries (marked 7 and 8).
# In 818181911112111, the largest joltage you can produce is 92.

# The total output joltage is the sum of the maximum joltage from each bank, so in this example, the total output joltage is 98 + 89 + 78 + 92 = 357.

def test_987654321111111():
    assert 98 == Day3Part1.max_joltage("987654321111111")

def test_811111111111119():
    assert 89 == Day3Part1.max_joltage("811111111111119")

def test_234234234234278():
    assert 78 == Day3Part1.max_joltage("234234234234278")

def test_818181911112111():
    assert 92 == Day3Part1.max_joltage("818181911112111")

def test_total_output_joltage():
    input = '''
    987654321111111
    811111111111119
    234234234234278
    818181911112111
    '''.strip()

    # On Windows the default NamedTemporaryFile can't be reopened by name
    # by another open() call; create the file with delete=False and
    # remove it after the assertion.
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
        tmp.write(input)
        tmp.flush()
        tmp_name = tmp.name
    try:
        assert 357 == Day3Part1.total_output_joltage(tmp_name)
    finally:
        try:
            os.unlink(tmp_name)
        except Exception:
            pass
