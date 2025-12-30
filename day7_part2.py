import sys, os, time
from copy import deepcopy

class Day7Part2:
    DEBUG = False
    start_time = time.time()
    last_progress_time = start_time
    
    @staticmethod
    def parse_input(input_text):
        return input_text.splitlines()

    @staticmethod
    def find_item_indices(line, item): # item = beams (|) or splitters (^)
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
    @staticmethod
    def print_progress(count):
        now = time.time()
        if now - Day7Part2.last_progress_time > 2.0:
            rate = count / (now - Day7Part2.start_time)
            print(f"{count:,} - {rate:,.0f} / sec", end="\r") # progress indicator
            Day7Part2.last_progress_time = now
        
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
    def iterate(lines, all_splitters, n, count, indent):
        Day7Part2.print_progress(count)
        if Day7Part2.DEBUG:
            print("\n")
            if n == 12 and count == 12:
                print('-'*100)
            print(f"{indent}n: {n}, count: {count}, len(lines): {len(lines)}")
        if n == len(lines):
            if Day7Part2.DEBUG:
                print(f"{indent}Hit end of input")
                for i in range(n):
                    print(f"{indent}{str(i).zfill(2)} {lines[i]}")
                print(f"{indent}1 Returning count {count}")
                print('-'*100)
            return count
        prev_beams = Day7Part2.find_item_indices(lines[n-1], '|')
        splitters = all_splitters[n] # Day7Part2.find_item_indices(lines[n], '^')
        if Day7Part2.DEBUG:
            for i in range(n-1):
                print(f"{indent}{str(i).zfill(2)} {lines[i]}")
            print(f"{indent}{str(n-1).zfill(2)} {lines[n-1]}, prev_beams: {prev_beams}")
            print(f"{indent}{str(n).zfill(2)} {lines[n]},  splitters: {splitters}")
        if len(prev_beams) != 1:
            print(f"Error: Beams should be 1. Was {len(prev_beams)}.")
        if splitters:
            no_splitter = True
            for splitter in splitters:
                if splitter in prev_beams:
                    no_splitter = False
                    # Optimization idea: Instead of using deepcopy, create left_lines with index 0 through n-1 as blank, then 
                    # copy n (modified) and the rest as is. I don't think I need to make a copy of all the [n+1:] lines, because
                    # they will get copied when I modify them later.
                    left_lines = ['.'] * n # We don't need the lines before row n
                    left_lines.append(lines[n][0:splitter-1] + '|' + lines[n][splitter:])
                    for line in lines[n+1:]:
                        left_lines.append(line) # Carry over the rest of the lines as-is
                    if Day7Part2.DEBUG:
                        print(f"{indent}Recursing left")
                    # Recursing left uses the same timeline, so we don't increase the count
                    count = Day7Part2.iterate(left_lines, all_splitters, n+1, count, indent+'  ') # propagate left
                    if Day7Part2.DEBUG:
                        print(f"{indent}Returned from recursing left, n: {n}")
                    
                    right_lines = ['.'] * n # We don't need the lines before row n
                    right_lines.append(lines[n][0:splitter+1] + '|' + lines[n][splitter+2:])
                    for line in lines[n+1:]:
                        right_lines.append(line) # Carry over the rest of the lines as-is
                    if Day7Part2.DEBUG:
                        print(f"{indent}Recursing right")
                    # Recursing right starts a new timeline, so we increase the count
                    count = Day7Part2.iterate(right_lines, all_splitters, n+1, count+1, indent+'  ') # propagate right
                    if Day7Part2.DEBUG:
                        print(f"{indent}Returned from recursing right, n: {n}")
            if no_splitter: # We didn't hit a splitter, so propagate down
                lines[n] = lines[n][0:prev_beams[0]] + '|' + lines[n][prev_beams[0]+1:]
                if Day7Part2.DEBUG:
                    print(f"{indent}1 Iterating down:")
                count = Day7Part2.iterate(lines, all_splitters, n+1, count, indent)
        else: # There were no splitters, so propagate down
            lines[n] = lines[n][0:prev_beams[0]] + '|' + lines[n][prev_beams[0]+1:]
            if Day7Part2.DEBUG:
                print(f"{indent}2 Iterating down:")
            count = Day7Part2.iterate(lines, all_splitters, n+1, count, indent)
        if Day7Part2.DEBUG:
            print(f"{indent}2 n:{n}, Returning count: {count}")
            print('-'*100)
        return count

    @staticmethod
    def iterate_tachyon_beam(lines):
        all_splitters = [Day7Part2.find_item_indices(line,'^') for line in lines]
        print(f"all_splitters: {all_splitters}") if Day7Part2.DEBUG else None
        start = lines[0].find('S')
        lines[1] = lines[1][:start] + '|' + lines[1][start+1:]
        timeline_count = Day7Part2.iterate(lines, all_splitters, 2, 1, '') # Start count at 1, since there's 1 timeline to start
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

