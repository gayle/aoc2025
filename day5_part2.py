import sys, os
from day5_part1 import Day5Part1

class Day5Part2:
    DEBUG = False

    @staticmethod
    def merge_ranges(ranges):
        """
        Merges a list of overlapping ranges (represented as tuples of [start, end], 
        note: end is inclusive here for simplicity with tuples) into non-overlapping ones.
        """
        if not ranges:
            return []

        # Sort ranges based on the start point
        sorted_ranges = sorted(ranges, key=lambda x: x[0])
        merged = []

        for current_start, current_end in sorted_ranges:
            # If the merged list is empty or the current range does not overlap 
            # with the last merged range, append it as is.
            if not merged or current_start > merged[-1][1]:
                merged.append([current_start, current_end])
            # Otherwise, there is an overlap. Merge the current range by updating 
            # the end point of the last merged range if the current range extends further.
            else:
                merged[-1][1] = max(merged[-1][1], current_end)
                
        return [tuple(r) for r in merged]

    @staticmethod
    def fresh_ingredient_id_count(ranges, ids):
        merged_ranges = Day5Part2.merge_ranges(ranges)
        count = 0
        for r in merged_ranges:
            count += r[1] - r[0] + 1
            print(f"count = {count}") if Day5Part2.DEBUG else None
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
  
    input_text = open(input_filename).read()
    ranges, ids = Day5Part1.parse_input(input_text)     

    # merged_ranges = Day5Part2.merge_ranges(ranges)
    # print(f"Merged ranges: {merged_ranges}")

    result = Day5Part2.fresh_ingredient_id_count(ranges, ids)
    print(f"Day 5 Part 2 result: {result}")

