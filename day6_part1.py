import sys, os

class Day6Part1:
    DEBUG = False

    @staticmethod
    def parse_input(input_text):
        lines = [line.strip() for line in input_text.splitlines()]
        problems = []
        for line in lines:
            split = line.split()
            for n, s in enumerate(split):
                if s.isdigit():
                    if n >= len(problems):
                        problems.append(int(s))
                else:
                    problems[n] = s
        return problems

if __name__ == "__main__":
    # If no filename is provided, try common input filenames before failing.
    if len(sys.argv) == 2:
        input_filename = sys.argv[1]
    else:
        # prefer Gayle's input if present, otherwise Dean's input
        if os.path.exists("day6_input_gayle.txt"):
            input_filename = "day6_input_gayle.txt"
        elif os.path.exists("day6_input_dean.txt"):
            input_filename = "day6_input_dean.txt"
        else:
            print(f"Usage: python {sys.argv[0]} <input_filename>")
            sys.exit(1)
  
    input_text = open(input_filename).read()
    problems = Day6Part1.parse_input(input_text)     
    result = Day6Part1.total_result(problems)
    print(f"Day 6 Part 1 result: {result}")

