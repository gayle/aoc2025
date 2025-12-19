import sys, os

class Day3Part1:

    @staticmethod
    def parse_input(input_filename):
        lines = open(input_filename).readlines()
        return lines
    
    @staticmethod
    def max_joltage(line):
        line = line.strip()
        first_digit, second_digit = '0', '0'
        for n, digit in enumerate(line):
            if int(digit) > int(first_digit) and n < len(line) - 1:
                first_digit = digit
                second_digit = '0'
            elif int(first_digit + digit) > int(first_digit + second_digit):
                second_digit = digit
        return int(first_digit + second_digit)

    @staticmethod
    def total_output_joltage(input_filename):
        lines = Day3Part1.parse_input(input_filename)
        total = 0
        for line in lines:
            total += Day3Part1.max_joltage(line)
        return total
    
if __name__ == "__main__":
    # If no filename is provided, try common input filenames before failing.
    if len(sys.argv) == 2:
        input_filename = sys.argv[1]
    else:
        # prefer Gayle's input if present, otherwise Dean's input
        if os.path.exists("day3_input_gayle.txt"):
            input_filename = "day3_input_gayle.txt"
        elif os.path.exists("day3_input_dean.txt"):
            input_filename = "day3_input_dean.txt"
        else:
            print("Usage: python day3_part1.py <input_filename>")
            sys.exit(1)
    result = Day3Part1.total_output_joltage(input_filename)
    print(f"Day 3 Part 1 result: {result}")
