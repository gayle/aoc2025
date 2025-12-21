import sys, os

class Day4Part1:
    DEBUG = False

    @staticmethod
    def parse_input(input_filename):
        lines = open(input_filename).readlines()
        lines = [line.strip() for line in lines]
        return lines
    
    @staticmethod
    def is_roll(x, y, lines):
        if x >= 0 and y >= 0 and x < len(lines[0]) and y < len(lines):
            print(f"'{lines[y][x]}' at ({x},{y})") if Day4Part1.DEBUG else None
            return lines[y][x] == '@'
        else:
            return False

    @staticmethod
    def roll_is_accessible(x, y, lines): # 0, 0 is upper left corner
        if not Day4Part1.is_roll(x, y, lines):
            return False
        else:
            adj_count = 0
            adjacent_cells = [
                (x-1, y-1), (x, y-1), (x+1, y-1), 
                (x-1, y), (x+1, y), 
                (x-1, y+1), (x, y+1), (x+1, y+1)
            ]
            for cell in adjacent_cells:
                if Day4Part1.is_roll(cell[0], cell[1], lines):
                    adj_count += 1
            print("adj_count = " + str(adj_count) + " at (" + str(x) + ", " + str(y) + ")") if Day4Part1.DEBUG else None
            return adj_count < 4
    
    @staticmethod
    def accessible_rolls(input_filename):
        lines = Day4Part1.parse_input(input_filename)
        accessible_rolls = []
        for y in range(len(lines)):
            for x in range(len(lines[y])):
                if Day4Part1.roll_is_accessible(x, y, lines):
                    accessible_rolls.append((x, y))
        return accessible_rolls
    
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
    result = len(Day4Part1.accessible_rolls(input_filename))
    print(f"Day 4 Part 1 result: {result}")

