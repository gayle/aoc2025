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
    def iterate(lines, all_splitters, current_line, current_column, indent):
        if Day7Part2.DEBUG:
            print("\n")
            if current_line == 12 and count == 12:
                print('-'*100)
            print(f"{indent}current_line: {current_line}, count: {count}, len(lines): {len(lines)}")

        if current_line == len(lines):
            if Day7Part2.DEBUG:
                print(f"{indent}Hit end of input current_line: {current_line}")
            count = 1
        elif current_column in all_splitters[current_line]: 
            if Day7Part2.DEBUG:
                print(f"{indent}Iterating left and right, count: {count} lines[current_line]: {lines[current_line]} current_column: {current_column}")
            count_left = Day7Part2.iterate(lines, all_splitters, current_line+1, current_column-1, indent+'  ') # left
            count_right = Day7Part2.iterate(lines, all_splitters, current_line+1, current_column+1, indent+'  ') # right
            if Day7Part2.DEBUG:
                print(f"{indent}count_left: {count_left}, count_right: {count_right}")
            count = (count_left + count_right)
        else: 
            if Day7Part2.DEBUG:
                print(f"{indent}No splitters at this point, moving down, count: {count} lines[current_line]: {lines[current_line]} current_column: {current_column}")
            count = Day7Part2.iterate(lines, all_splitters, current_line+1, current_column, indent+'  ')

        if Day7Part2.DEBUG:
            print(f"{indent}returning count: {count}")

        # Day7Part2.print_progress(count) # This doesn't work w/ the current implementation :( 
        # print(".", end="") if current_line == 142 else None # simple progress indicator, every time it gets to the last line of the file.  This is still a lot and is not very useful. 
        return count

    @staticmethod
    def iterate_tachyon_beam(lines):
        st_time = time.time()
        all_splitters = [Day7Part2.find_item_indices(line,'^') for line in lines]
        print(f"all_splitters: {all_splitters}") if Day7Part2.DEBUG else None
        start = lines[0].find('S')
        lines[1] = lines[1][:start] + '|' + lines[1][start+1:]
        current_line = 2
        current_column = start
        timeline_count = Day7Part2.iterate(lines, all_splitters, current_line, current_column, '') # Start count at 1, since there's 1 timeline to start

        e_time = time.time()
        print(f"iterate_tachyon_beam took {e_time - st_time} seconds")
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

