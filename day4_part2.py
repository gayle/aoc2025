import sys, os
from day4_part1 import Day4Part1 # We'll reuse some methods from part 1

class Day4Part2:
    DEBUG = False

    @staticmethod
    def total_rolls_removed(input_filename):
        lines = Day4Part1.parse_input(input_filename)
        total_rolls_removed = 0
        while True:
            accessible_rolls = Day4Part1.accessible_rolls(lines)
            print() if Day4Part2.DEBUG else None
            print(f"Accessible rolls: {accessible_rolls}") if Day4Part2.DEBUG else None
            if len(accessible_rolls) == 0:
                break
            for roll in accessible_rolls:
                line = lines[roll[1]]
                lines[roll[1]] = line[:roll[0]] + "x" + line[roll[0]+1:] # replace the @ with an x
                total_rolls_removed += 1
                print(f"Total rolls removed: {total_rolls_removed}") if Day4Part2.DEBUG else None
                print(lines) if Day4Part2.DEBUG else None

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
    print()        
    result = Day4Part2.total_rolls_removed(input_filename)
    print(f"Day 4 Part 2 result: {result}")

