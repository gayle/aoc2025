import pytest, tempfile, sys, os
from textwrap import dedent
from day8_part1 import *

input_text = dedent('''\
    162,817,812
    57,618,57
    906,360,560
    592,479,940
    352,342,300
    466,668,158
    542,29,236
    431,825,988
    739,650,466
    52,470,668
    216,146,977
    819,987,18
    117,168,530
    805,96,715
    346,949,466
    970,615,88
    941,993,340
    862,61,35
    984,92,344
    425,690,689
''')

# This list describes the position of 20 junction boxes, one per line. Each position is given as X,Y,Z coordinates. So, the first junction box in the list is at X=162, Y=817, Z=812.

# To save on string lights, the Elves would like to focus on connecting pairs of junction boxes that are as close together as possible according to straight-line distance. In this example, the two junction boxes which are closest together are 162,817,812 and 425,690,689.

# By connecting these two junction boxes together, because electricity can flow between them, they become part of the same circuit. After connecting them, there is a single circuit which contains two junction boxes, and the remaining 18 junction boxes remain in their own individual circuits.

# Now, the two junction boxes which are closest together but aren't already directly connected are 162,817,812 and 431,825,988. After connecting them, since 162,817,812 is already connected to another junction box, there is now a single circuit which contains three junction boxes and an additional 17 circuits which contain one junction box each.

# The next two junction boxes to connect are 906,360,560 and 805,96,715. After connecting them, there is a circuit containing 3 junction boxes, a circuit containing 2 junction boxes, and 15 circuits which contain one junction box each.

# The next two junction boxes are 431,825,988 and 425,690,689. Because these two junction boxes were already in the same circuit, nothing happens!

# This process continues for a while, and the Elves are concerned that they don't have enough extension cables for all these circuits. They would like to know how big the circuits will be.

# After making the ten shortest connections, there are 11 circuits: one circuit which contains 5 junction boxes, one circuit which contains 4 junction boxes, two circuits which contain 2 junction boxes each, and seven circuits which each contain a single junction box. Multiplying together the sizes of the three largest circuits (5, 4, and one of the circuits of size 2) produces 40.

def test_parse_input():
    junctions = parse_input(input_text)
    assert len(junctions) == 20
    assert junctions[0] == (162,817,812)
    assert junctions[1] == (57,618,57)
    assert junctions[2] == (906,360,560)
    assert junctions[3] == (592,479,940)
    assert junctions[4] == (352,342,300)
    assert junctions[5] == (466,668,158)
    assert junctions[6] == (542,29,236)
    assert junctions[7] == (431,825,988)
    assert junctions[8] == (739,650,466)
    assert junctions[9] == (52,470,668)
    assert junctions[10] == (216,146,977)
    assert junctions[11] == (819,987,18)
    assert junctions[12] == (117,168,530)
    assert junctions[13] == (805,96,715)
    assert junctions[14] == (346,949,466)
    assert junctions[15] == (970,615,88)
    assert junctions[16] == (941,993,340)
    assert junctions[17] == (862,61,35)
    assert junctions[18] == (984,92,344)
    assert junctions[19] == (425,690,689)

def test_closest_junctions():
    junctions = parse_input(input_text)
    closest = closest_junctions(junctions, 10)
    assert len(closest) == 10
    # The two junction boxes which are closest together are 162,817,812 and 425,690,689
    assert closest[0] == ((162,817,812), (425,690,689))
    # Now, the two junction boxes which are closest together but aren't already directly connected are 162,817,812 and 431,825,988.
    assert closest[1] == ((162,817,812), (431,825,988))
    # The next two junction boxes to connect are 906,360,560 and 805,96,715.
    assert closest[2] == ((906,360,560), (805,96,715))
    # The next two junction boxes are 431,825,988 and 425,690,689.
    assert closest[3] == ((431,825,988), (425,690,689))
    # The rest of the assertions are based on the debug output:
    # sorted_points:
    # (333.6555109690233, ((862, 61, 35), (984, 92, 344)))
    # (338.33858780813046, ((52, 470, 668), (117, 168, 530)))
    # (344.3893145845266, ((819, 987, 18), (941, 993, 340)))
    # (347.59890678769403, ((906, 360, 560), (739, 650, 466)))
    # (350.786259708102, ((346, 949, 466), (425, 690, 689)))
    # (352.936254867646, ((906, 360, 560), (984, 92, 344)))
    assert closest[4] == ((862, 61, 35), (984, 92, 344))
    assert closest[5] == ((52, 470, 668), (117, 168, 530))
    assert closest[6] == ((819, 987, 18), (941, 993, 340))
    assert closest[7] == ((906, 360, 560), (739, 650, 466))
    assert closest[8] == ((346, 949, 466), (425, 690, 689))
    assert closest[9] == ((906, 360, 560), (984, 92, 344))
    
def test_connect_circuits():
    junctions = parse_input(input_text)
    closest = closest_junctions(junctions, 10)
    assert len(closest) == 10
    circuit_sizes = connect_circuits(closest, junctions)

    # After making the ten shortest connections, there are 11 circuits: one circuit which contains 5 junction boxes, one circuit which contains 4 junction boxes, two circuits which contain 2 junction boxes each, and seven circuits which each contain a single junction box. Multiplying together the sizes of the three largest circuits (5, 4, and one of the circuits of size 2) produces 40.   
    assert circuit_sizes == [5,4,2,2,1,1,1,1,1,1,1]    
        