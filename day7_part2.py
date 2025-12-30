import sys, os, time

class Day7Part2:
    DEBUG = False
    start_time = time.time()
    last_progress_time = start_time

    @staticmethod
    def parse_input(input_text):
        return input_text.splitlines()

    @staticmethod
    def find_item_indices(line, item): # item = beams (|) or splitters (^)
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

    @staticmethod
    def print_progress(count):
        now = time.time()
        if now - Day7Part2.last_progress_time > 2.0:
            rate = count / (now - Day7Part2.start_time)
            print(f"{count:,} - {rate:,.0f} / sec", end="\r")
            Day7Part2.last_progress_time = now

    @staticmethod
    def iterate(all_beams, all_splitters, n, count, indent):
        Day7Part2.print_progress(count)
        if Day7Part2.DEBUG:
            print("\n")
            print(f"{indent}n: {n}, count: {count}, len(all_beams): {len(all_beams)}")
        if n == len(all_beams):
            if Day7Part2.DEBUG:
                print(f"{indent}Hit end of input")
            return count

        # find the single incoming beam index on the previous row (or -1 if none)
        prev_beam_idx = all_beams[n-1]
        splitters = all_splitters[n]

        if prev_beam_idx == -1 and Day7Part2.DEBUG:
            print(f"Error: Beams should be 1. Was 0.")

        if splitters:
            no_splitter = True
            for splitter in splitters:
                if splitter == prev_beam_idx:
                    no_splitter = False

                    # propagate left (same timeline)
                    left_beams = all_beams.copy()
                    left_beams[n] = splitter - 1
                    count = Day7Part2.iterate(left_beams, all_splitters, n+1, count, indent+'  ')

                    # propagate right (new timeline, count + 1)
                    right_beams = all_beams.copy()
                    right_beams[n] = splitter + 1
                    count = Day7Part2.iterate(right_beams, all_splitters, n+1, count+1, indent+'  ')
            if no_splitter:
                # no matching splitter, propagate straight down
                if prev_beam_idx == -1:
                    return count
                new_beams = all_beams.copy()
                new_beams[n] = prev_beam_idx
                count = Day7Part2.iterate(new_beams, all_splitters, n+1, count, indent)
        else:
            # no splitters on this row, propagate down
            if prev_beam_idx == -1:
                return count
            new_beams = all_beams.copy()
            new_beams[n] = prev_beam_idx
            count = Day7Part2.iterate(new_beams, all_splitters, n+1, count, indent)

        return count

    @staticmethod
    def iterate_tachyon_beam(lines):
        return Day7Part2.iterate_tachyon_beam_optimized(lines)
    #     all_splitters = [Day7Part2.find_item_indices(line,'^') for line in lines]
    #     start = lines[0].find('S')
    #     if start == -1:
    #         return 0
    #     lines[1] = lines[1][:start] + '|' + lines[1][start+1:]
    #     timeline_count = Day7Part2.iterate(lines, all_splitters, 2, 1, '')
    #     return timeline_count

    @staticmethod
    def iterate_tachyon_beam_optimized(lines):
        # lightweight optimized entry that reuses the recursive iterate implementation
        all_splitters = [Day7Part2.find_item_indices(line, '^') for line in lines]
        start = lines[0].find('S')
        if start == -1:
            return 0
        # Populate the indexes of all the beams
        all_beams = [0, start]
        for i in range(2, len(lines)):
            all_beams.append(0)
        print(f"len(lines): {len(lines)}, len(all_beams): {len(all_beams)}") if Day7Part2.DEBUG else None
        return Day7Part2.iterate(all_beams, all_splitters, 2, 1, '')


if __name__ == "__main__":
    if len(sys.argv) == 2:
        input_filename = sys.argv[1]
    else:
        if os.path.exists("day7_input_gayle.txt"):
            input_filename = "day7_input_gayle.txt"
        elif os.path.exists("day7_input_dean.txt"):
            input_filename = "day7_input_dean.txt"
        else:
            print(f"Usage: python {sys.argv[0]} <input_filename>")
            sys.exit(1)

    input_text = open(input_filename).read()
    lines = Day7Part2.parse_input(input_text)
    result = Day7Part2.iterate_tachyon_beam_optimized(lines)
    print(f"Day 7 Part 2 result: {result}")

