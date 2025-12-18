import pytest
import tempfile
import sys, os
from day2_part1 import Day2Part1

# Sample from the problem description page:

# 11-22,95-115,998-1012,1188511880-1188511890,222220-222224,
# 1698522-1698528,446443-446449,38593856-38593862,565653-565659,
# 824824821-824824827,2121212118-2121212124

# 11-22 has two invalid IDs, 11 and 22.
# 95-115 has one invalid ID, 99.
# 998-1012 has one invalid ID, 1010.
# 1188511880-1188511890 has one invalid ID, 1188511885.
# 222220-222224 has one invalid ID, 222222.
# 1698522-1698528 contains no invalid IDs.
# 446443-446449 has one invalid ID, 446446.
# 38593856-38593862 has one invalid ID, 38593859.
# The rest of the ranges contain no invalid IDs.

# Adding up all the invalid IDs in this example produces 1227775554.

def test_11_22():
    assert [11, 22] == Day2Part1.invalid_ids(11, 22)

def test_95_115():
    assert [99] == Day2Part1.invalid_ids(95, 115)

def test_998_1012():
    assert [1010] == Day2Part1.invalid_ids(998, 1012)

def test_1188511880_1188511890():
    assert [1188511885] == Day2Part1.invalid_ids(1188511880, 1188511890)

def test_222220_222224():
    assert [222222] == Day2Part1.invalid_ids(222220, 222224)

def test_1698522_1698528():
    assert [] == Day2Part1.invalid_ids(1698522, 1698528)

def test_446443_446449():
    assert [446446] == Day2Part1.invalid_ids(446443, 446449)

def test_38593856_38593862():
    assert [38593859] == Day2Part1.invalid_ids(38593856, 38593862)

def test_565653_565659():
    assert [] == Day2Part1.invalid_ids(565653, 565659)

def test_824824821_824824827():
    assert [] == Day2Part1.invalid_ids(824824821, 824824827)

def test_2121212118_2121212124():
    assert [] == Day2Part1.invalid_ids(2121212118, 2121212124)

