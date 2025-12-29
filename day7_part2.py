import sys, os
from copy import deepcopy

class Day7Part2:
    DEBUG = True

    @staticmethod
    def parse_input(input_text):
        return input_text.splitlines()

    @staticmethod
    def find_items(line, item): # item = beams (|) or splitters (^)
        items = []
        search_start = 0
        while True:
            n = line.find(item, search_start)
            if n >= 0:
                items.append(n)
                search_start = n + 1
            else:
                break
        return items
    
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
    def iterate(lines, current_line, count, indent):
        if Day7Part2.DEBUG:
            print("\n")
            if current_line == 12 and count == 12:
                print('-'*100)
            print(f"{indent}current_line: {current_line}, count: {count}, len(lines): {len(lines)}")
        #import ipdb; ipdb.set_trace()
        print("does lines decrease?")
        if current_line == len(lines):
            if Day7Part2.DEBUG:
                print(f"{indent}Hit end of input")
                for i in range(current_line):
                    print(f"{indent}{str(i).zfill(2)} {lines[i]}")
                print(f"{indent}1 Returning count {count}")
                print('-'*100)
            return count
        prev_beams = Day7Part2.find_items(lines[current_line-1], '|')
        splitters = Day7Part2.find_items(lines[current_line], '^')
        if Day7Part2.DEBUG:
            for i in range(current_line-1):
                print(f"{indent}{str(i).zfill(2)} {lines[i]}")
            print(f"{indent}{str(current_line-1).zfill(2)} {lines[current_line-1]}, prev_beams: {prev_beams}")
            print(f"{indent}{str(current_line).zfill(2)} {lines[current_line]},  splitters: {splitters}")
        if len(prev_beams) > 1:
            print(f"Error: Beams should be 1. Was {len(prev_beams)}.")
        if splitters:
            no_splitter = True
            for splitter in splitters:
                if splitter in prev_beams:
                    no_splitter = False
                    left_lines = deepcopy(lines)
                    left_lines[current_line] = lines[current_line][0:splitter-1] + '|' + lines[current_line][splitter:]
                    if Day7Part2.DEBUG:
                        print(f"{indent}Recursing left")
                    # Recursing left uses the same timeline, so we don't increase the count
                    count = Day7Part2.iterate(left_lines, current_line+1, count, indent+'  ') # propagate left
                    if Day7Part2.DEBUG:
                        print(f"{indent}Returned from recursing left, current_line: {current_line}")
                    right_lines = deepcopy(lines)
                    right_lines[current_line] = lines[current_line][0:splitter+1] + '|' + lines[current_line][splitter+2:]
                    if Day7Part2.DEBUG:
                        print(f"{indent}Recursing right")
                    # Recursing right starts a new timeline, so we increase the count
                    count = Day7Part2.iterate(right_lines, current_line+1, count+1, indent+'  ') # propagate right
                    if Day7Part2.DEBUG:
                        print(f"{indent}Returned from recursing right, current_line: {current_line}")
            if no_splitter: # We didn't hit a splitter, so propagate down
                lines[current_line] = lines[current_line][0:prev_beams[0]] + '|' + lines[current_line][prev_beams[0]+1:]
                if Day7Part2.DEBUG:
                    print(f"{indent}1 Iterating down:")
                count = Day7Part2.iterate(lines, current_line+1, count, indent)
        else: # There were no splitters, so propagate down
            lines[current_line] = lines[current_line][0:prev_beams[0]] + '|' + lines[current_line][prev_beams[0]+1:]
            if Day7Part2.DEBUG:
                print(f"{indent}2 Iterating down:")
            count = Day7Part2.iterate(lines, current_line+1, count, indent)
        if Day7Part2.DEBUG:
            print(f"{indent}2 current_line:{current_line}, Returning count: {count}")
            print('-'*100)
        return count

    @staticmethod
    def iterate_tachyon_beam(lines):
        start = lines[0].find('S')
        lines[1] = lines[1][:start] + '|' + lines[1][start+1:]
        current_line = 2
        count = 1 # start with 1 timeline
        timeline_count = Day7Part2.iterate(lines, current_line, count, '') # Start count at 1, since there's 1 timeline to start
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

