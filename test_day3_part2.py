import pytest, tempfile, sys, os
from day3_part2 import Day3Part2

# Consider again the example from before:

# 987654321111111
# 811111111111119
# 234234234234278
# 818181911112111
# Now, the joltages are much larger:

# In 987654321111111, the largest joltage can be found by turning on everything except some 1s at the end to produce 987654321111.
# In the digit sequence 811111111111119, the largest joltage can be found by turning on everything except some 1s, producing 811111111119.
# In 234234234234278, the largest joltage can be found by turning on everything except a 2 battery, a 3 battery, and another 2 battery near the start to produce 434234234278.
# In 818181911112111, the joltage 888911112111 is produced by turning on everything except some 1s near the front.
# The total output joltage is now much larger: 987654321111 + 811111111119 + 434234234278 + 888911112111 = 3121910778619.

def test_987654321111111():
    assert Day3Part2().max_joltage('987654321111111') == 987654321111

def test_811111111111119():
    assert Day3Part2().max_joltage('811111111111119') == 811111111119

def test_234234234234278():
    assert Day3Part2().max_joltage('234234234234278') == 434234234278

def test_818181911112111():
    assert Day3Part2().max_joltage('818181911112111') == 888911112111

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
        assert Day3Part2.total_output_joltage(tmp_name) == 3121910778619
    finally:
        try:
            os.unlink(tmp_name)
        except Exception:
            pass
