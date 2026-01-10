import sys, os, time
from copy import deepcopy

# This took Dean's version and asked Copilot to optimize it.
# The main change is to avoid making deep copies of the entire grid on each branch.
class Day7Part2:
    DEBUG = False
    start_time = time.time()
    last_progress_time = start_time

    @staticmethod
    def print_progress(count):
        now = time.time()
        if now - Day7Part2.last_progress_time > 2.0:
            rate = count / (now - Day7Part2.start_time)
            print(f"{count:,} - {rate:,.0f} / sec", end="\r") # progress indicator
            Day7Part2.last_progress_time = now

    @staticmethod
    def parse_input(input_text):
        # return list of lists for efficient in-place edits
        return [list(line) for line in input_text.splitlines()]
    
    # .......S.......
    # .......|.......
    # .......^.......
    # ...............
    # ......^.^......
    # ...............
    # .....^.^.^.....
    # ...............
    # ....^.^...^....
    # ...............
    # ...^.^...^.^...
    # ...............
    # ..^...^.....^..
    # ...............
    # .^.^.^.^.^...^.
    # ...............

    @staticmethod
    def iterate(lines, splitters_by_row, n, count):
        Day7Part2.print_progress(count)
        if n == len(lines):
            return count

        # find previous beam position (expect at most one)
        try:
            prev_pos = lines[n-1].index('|')
        except ValueError:
            return count

        # check if a splitter exists at the beam column
        splitters = splitters_by_row[n]
        # if there are splitters at positions matching prev_pos, branch
        branched = False
        for splitter in splitters:
            if splitter == prev_pos:
                branched = True
                # left branch: place beam at splitter-1
                left_pos = splitter - 1
                if 0 <= left_pos < len(lines[n]):
                    orig = lines[n][left_pos]
                    lines[n][left_pos] = '|'
                    count = Day7Part2.iterate(lines, splitters_by_row, n+1, count)
                    lines[n][left_pos] = orig
                # right branch: place beam at splitter+1 (this increases timeline count)
                right_pos = splitter + 1
                if 0 <= right_pos < len(lines[n]):
                    orig = lines[n][right_pos]
                    lines[n][right_pos] = '|'
                    count = Day7Part2.iterate(lines, splitters_by_row, n+1, count+1)
                    lines[n][right_pos] = orig

        if not branched:
            # propagate straight down at prev_pos
            orig = lines[n][prev_pos]
            lines[n][prev_pos] = '|'
            count = Day7Part2.iterate(lines, splitters_by_row, n+1, count)
            lines[n][prev_pos] = orig

        return count

    @staticmethod
    def iterate_tachyon_beam(lines):
        # lines: list of list(chars)
        # locate start
        start = None
        for i, ch in enumerate(lines[0]):
            if ch == 'S':
                start = i
                break
        if start is None:
            raise ValueError('No start S found')

        # place initial beam on row 1
        orig = lines[1][start]
        lines[1][start] = '|'

        # precompute splitter positions per row for fast lookup
        splitters_by_row = [[i for i, ch in enumerate(row) if ch == '^'] for row in lines]

        timeline_count = Day7Part2.iterate(lines, splitters_by_row, 2, 1)

        # restore original (not strictly necessary)
        lines[1][start] = orig
        return timeline_count

if __name__ == "__main__":
    # If no filename is provided, try common input filenames before failing.
    if len(sys.argv) == 2:
        input_filename = sys.argv[1]
    else:
        # prefer Gayle's input if present, otherwise Dean's input
        if os.path.exists("day7_input_gayle.txt"):
            input_filename = "day7_input_gayle.txt"
        elif os.path.exists("day7_input_dean.txt"):
            input_filename = "day7_input_dean.txt"
        else:
            print(f"Usage: python {sys.argv[0]} <input_filename>")
            sys.exit(1)
  
    input_text = open(input_filename).read()
    lines = Day7Part2.parse_input(input_text)     
    result = Day7Part2.iterate_tachyon_beam(lines)
    print(f"Day 7 Part 2 result: {result}")

