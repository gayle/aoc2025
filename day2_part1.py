import sys

class Day2Part1:

    @staticmethod
    def parse_input(input_filename):
        input = open(input_filename).read()
        ranges = input.split(",")
        input_ranges = []
        for range in ranges:
            start, end = range.split("-")[0:2]
            start, end = int(start), int(end)
            input_ranges.append((start, end))
        return input_ranges
    
    @staticmethod
    def invalid_ids(start, end):
        invalid_ids = []
        for n in range(start, end + 1):
            sn = str(n)
            # print("sn: ", sn)
            length = len(sn)
            # print("length: ", length)
            halfway = int(length/2)
            # print("sn[0:halfway]: ", sn[0:halfway])
            # print("sn[halfway:length]: ", sn[halfway:length])
            if sn[0:halfway] == sn[halfway:length]:
                # print("Invalid ID:", n)
                invalid_ids.append(n)
        # print("invalid_ids: ", invalid_ids)
        return invalid_ids

    @staticmethod
    def sum_of_invalid_ids(input_filename):
        input_ranges = Day2Part1.parse_input(input_filename)
        total = 0
        for i, j in input_ranges:
            invalid_ids = Day2Part1.invalid_ids(i, j)
            total += sum(invalid_ids)
        return total

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python day2_pt1.py <input_filename>")
        sys.exit(1)
    input_filename = sys.argv[1]
    result = Day2Part1.sum_of_invalid_ids(input_filename)
    print(f"Day 2 Part 1 result: {result}")
