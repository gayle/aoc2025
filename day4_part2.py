import sys, os
from day4_part1 import Day4Part1 # We'll reuse some methods from part 1

class Day4Part2:
    DEBUG = False

    @staticmethod
    def total_rolls_removed(input_filename):
        accessible_rolls = Day4Part1.accessible_rolls(input_filename)
        total_rolls_removed = 0
        
        for roll in accessible_rolls:
            pass

        return total_rolls_removed

if __name__ == "__main__":
    # If no filename is provided, try common input filenames before failing.
    if len(sys.argv) == 2:
        input_filename = sys.argv[1]
    else:
        # prefer Gayle's input if present, otherwise Dean's input
        if os.path.exists("day4_input_gayle.txt"):
            input_filename = "day4_input_gayle.txt"
        elif os.path.exists("day4_input_dean.txt"):
            input_filename = "day4_input_dean.txt"
        else:
            print(f"Usage: python {sys.argv[0]} <input_filename>")
            sys.exit(1)
    result = Day4Part2.total_rolls_removed(input_filename)
    print(f"Day 4 Part 2 result: {result}")

