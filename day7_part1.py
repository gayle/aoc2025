import sys, os
from functools import reduce

class Day7Part1:
    DEBUG = False

    @staticmethod
    def parse_input(input_text):
        lines = input_text.splitlines()
        max_col_index = 0 # index of right-most column
        for line in lines:
            print(f"'{line}'") if Day7Part1.DEBUG else None
            max_col_index = len(line) if len(line) > max_col_index else max_col_index
        max_col_index -= 1
        print(f"max_col_index={max_col_index}") if Day7Part1.DEBUG else None  
        num_count = len(lines) - 1 # If there are 4 lines of input, the first 3 are numbers
        op_index = len(lines) - 1  # Index 3 is the line of operations on the numbers (+ or *)
        problems = [ [] ]
        problem_index = 0
        
        for col in range(max_col_index, -1, -1): # Step from max_col_index (14) down to 0
            digits, operation = '', ''
            for i in range(len(lines)):
                print(f"i={i}, col={col}, len(lines[{i}])={len(lines[i])}, {lines[i]}") if Day7Part1.DEBUG else None
                if col < len(lines[i]):
                    digit = lines[i][col]
                else:
                    digit = '' # some lines appear to be a character shorter
                if digit.isdigit():
                    digits += digit
                    print(f"Found digit {digit}, digits is now {digits}") if Day7Part1.DEBUG else None
                elif digit in ['+', '*']:
                    operation = digit
            if not digits: # there was nothing in this column
                print(f"Ended problem[{problem_index}]: {problems[problem_index]}") if Day7Part1.DEBUG else None
                problems.append([])
                problem_index += 1
            else:
                print(f"Appending {digits} to problems[{problem_index}]") if Day7Part1.DEBUG else None
                problems[problem_index].append(int(digits))
                if operation:
                    problems[problem_index].append(operation)
        
        return problems

    @staticmethod
    def solve_problem(problem):
        operation = problem[-1]
        numbers = problem[0:-1]
        print(f"problem: {problem} operation: {operation} numbers: {numbers}") if Day7Part1.DEBUG else None
        if operation == '*':
            result = 1
            for num in numbers:
                result *= num
        elif operation == '+':
            result = sum(numbers)
        return result

    @staticmethod
    def total_result(problems):
        total = 0
        for problem in problems:
            result = Day7Part1.solve_problem(problem)
            total += result
        return total

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
    problems = Day7Part1.parse_input(input_text)     
    result = Day7Part1.total_result(problems)
    print(f"Day 7 Part 1 result: {result}")

