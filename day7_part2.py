import sys, os

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

    '''This looks like it will need recursion. The recursion will be somewhere in the iterate_tachyon_beam method, but the challenge will be figuring out where, whether it's calling the whole method recursively, or just part of it. But then we'll have to keep a counter of each time we recurse, and bubble that up to be the final result.'''

    @staticmethod
    def iterate_tachyon_beam(lines):
        split_count = 0
        start = lines[0].find('S')
        for n, line in enumerate(lines):
            if n == 0: # npthing to do on the start line
                continue
            print("\n") if Day7Part2.DEBUG else None
            print(f"n={n}, prev_line={lines[n-1]}") if Day7Part2.DEBUG else None
            print(f"n={n}, line={line}") if Day7Part2.DEBUG else None
            prev_beams = Day7Part2.find_items(lines[n-1], '|')
            print(f"prev_beams: {prev_beams}") if Day7Part2.DEBUG else None
            if len(prev_beams) == 0: # previous line was the start line
                lines[n] = line[:start] + '|' + line[start+1:]
            else:
                splitters = Day7Part2.find_items(line, '^')
                print(f"splitters: {splitters}") if Day7Part2.DEBUG else None
                for beam in prev_beams:
                    # Check if beam is hitting a splitter. If so, split it. If not, keep it going.
                    if beam in splitters:
                        lines[n] = lines[n][:beam-1] + '|' + lines[n][beam] + '|' + lines[n][beam+2:]
                        split_count += 1
                    else:
                        lines[n] = lines[n][:beam] + '|' + lines[n][beam+1:]
            print(f"New line: {lines[n]}") if Day7Part2.DEBUG else None
        return split_count

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

