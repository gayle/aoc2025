import sys, os

class Day3Part2:
    DEBUG = True

    @staticmethod
    def parse_input(input_filename):
        lines = open(input_filename).readlines()
        return lines
    
    @staticmethod
    def max_joltage(line):
        line = line.strip() # example: 811111111111119
        print("line: %s" % line) if Day3Part2.DEBUG else None
        joltage = '0' * 12 # max 12 digits
        for n, digit in enumerate(line):
            if n < len(joltage):
                new_n = n
            else:
                new_n = len(joltage) - 1
            temp_joltage = joltage[0:new_n] + digit + joltage[new_n+1:]
            print("temp_joltage: %s, joltage: %s" % (temp_joltage, joltage)) if Day3Part2.DEBUG else None
            if int(temp_joltage) > int(joltage):
                joltage = temp_joltage
        print("returning joltage: %s" % joltage) if Day3Part2.DEBUG else None
        return int(joltage)
    
    '''
    I've got logic that works for 987654321111111 and 811111111111119, but fails for 234234234234278.
    I realize that I need to loop starting from index 0 to replace the new digit before comparing if it's larger.
    So, the first iteration, n is 0, so we end up with 200000000000. The second iteration, n is 1, so where looking at 3,
    but I need a nested loop to check start at index 0, if 300000000000 is greater, which it is. The next iteration, n is 2, 
    so I'm looking at 4, and 400000000000 is greater. Then n is 3, 200000000000 is not greater, so I iterate the innermost loop
    to look at 420000000000, which is greater. Next iteration, n is 4, and 320000000000 is not great, but then 430000000000 is greater.
    Next round n is 5, which points to 4, and 430000000000 is the same, so we try 440000000000, which is greater, but here's where
    it gets interesting. The length of the line is 15, and we are on index 5, and 15 - 5 == 10. The joltage current like has 2 non-zero
    digits, and 10 + 2 == 12, so if we replace 43 with 44, there won't be enough digits left to meet a length of 12. So I have to leave 
    the 43 and try 434000000000, which becomes the new joltage. I think this logic will make sure that all the rest of the digits in the
    line can replace earlier ones. There may be a way to short-circuit the logic once we hit this point, but it may not be worth the trouble.
    '''

    @staticmethod
    def total_output_joltage(input_filename):
        lines = Day3Part2.parse_input(input_filename)
        total = 0
        for line in lines:
            total += Day3Part2.max_joltage(line)
        return total
    
if __name__ == "__main__":
    # If no filename is provided, try common input filenames before failing.
    print(sys.argv)
    if len(sys.argv) == 2:
        input_filename = sys.argv[1]
    else:
        # prefer Gayle's input if present, otherwise Dean's input
        if os.path.exists("day3_input_gayle.txt"):
            input_filename = "day3_input_gayle.txt"
        elif os.path.exists("day3_input_dean.txt"):
            input_filename = "day3_input_dean.txt"
        else:
            print(f"Usage: python {sys.argv[0]} <input_filename>")
            sys.exit(1)
    result = Day3Part2.total_output_joltage(input_filename)
    print(f"Day 3 Part 2 result: {result}")
