import sys
import os

DEBUG = False

class Day2Part2:

    @staticmethod
    def parse_input(input_filename):
        with open(input_filename, "r") as f:
            data = f.read()
        ranges = data.split(",")
        input_ranges = []
        for range in ranges:
            start, end = range.split("-")[0:2]
            # start, end = int(start), int(end)
            input_ranges.append((start, end))
        return input_ranges
    
    @staticmethod
    def invalid_id(n):
        sn = str(n) # 565656
        print("sn: ", sn) if DEBUG else None
        length = len(sn) # 6
        if length == 1:
            return False
        seq = ''
        for j in range(1, length//2 + 1): # j = 1,2,3
            dup = True
            for i in range(length): # i = 0,1,2,3,4,5
                seq = sn[i:i+j] 
                print(f"i: {i}, j: {j}, seq: {seq}, sn[{j}:{j+len(seq)}]: {sn[j:j+len(seq)]}") if DEBUG else None
                for k in range(10):
                    start = j+k*len(seq)
                    end = start + len(seq)
                    if start >= length:
                        break
                    print(f"i: {i}, j: {j}, k: {k}, start: {start}, end: {end}, seq: {seq}, sn[{start}:{end}]: {sn[start:end]}") if DEBUG else None
                    if seq == sn[start:end]:
                        dup = dup and True
                        print(f"dup: {dup}") if DEBUG else None
                    else:
                        dup = False
                        print(f"dup: {dup}, breaking k loop") if DEBUG else None
                        break
                if dup == True:
                    return True
                else:
                    print("breaking i loop") if DEBUG else None
                    break
        return dup

    @staticmethod
    def invalid_ids(start, end):
        invalid_ids = []
        for n in range(int(start), int(end) + 1):
            if Day2Part2.invalid_id(n):
                invalid_ids.append(n)
        return invalid_ids

    @staticmethod
    def sum_of_invalid_ids(input_filename):
        input_ranges = Day2Part2.parse_input(input_filename)
        total = 0
        for i, j in input_ranges:
            invalid_ids = Day2Part2.invalid_ids(i, j)
            # print(f"invalid_ids for range {i}-{j}: {invalid_ids}")
            total += sum(invalid_ids)
        return total

if __name__ == "__main__":
    # If no filename is provided, try common input filenames before failing.
    if len(sys.argv) == 2:
        input_filename = sys.argv[1]
    else:
        # prefer Gayle's input if present, otherwise Dean's input
        if os.path.exists("day2_input_gayle.txt"):
            input_filename = "day2_input_gayle.txt"
        elif os.path.exists("day2_input_dean.txt"):
            input_filename = "day2_input_dean.txt"
        else:
            print("Usage: python day2_part2.py <input_filename>")
            sys.exit(1)
    result = Day2Part2.sum_of_invalid_ids(input_filename)
    print(f"Day 2 Part 1 result: {result}")
