import sys, os

class Day5Part1:
    DEBUG = False

    @staticmethod
    def parse_input(input_text):
        lines = [line.strip() for line in input_text.splitlines()]
        ranges, ids = [], []
        list = 'ranges'
        for line in lines:
            if list == 'ranges':
                if line == '':
                    list = 'ids'
                else:
                    range = line.split('-')
                    ranges.append([int(range[0]), int(range[1])])
                    print(ranges)
            else:
                ids.append(int(line))
                print(ids)
        return ranges, ids

    @staticmethod
    def fresh_ingredient_count(ranges, ids):
        count = 0
        
        

        return count

if __name__ == "__main__":
    # If no filename is provided, try common input filenames before failing.
    if len(sys.argv) == 2:
        input_filename = sys.argv[1]
    else:
        # prefer Gayle's input if present, otherwise Dean's input
        if os.path.exists("day5_input_gayle.txt"):
            input_filename = "day5_input_gayle.txt"
        elif os.path.exists("day5_input_dean.txt"):
            input_filename = "day5_input_dean.txt"
        else:
            print(f"Usage: python {sys.argv[0]} <input_filename>")
            sys.exit(1)
    print()
    input_text = open(input_filename).read()
    ranges, ids = Day5Part1.parse_input(input_text)     
    result = Day5Part1.fresh_ingredient_count(ranges, ids)
    print(f"Day 5 Part 1 result: {result}")

