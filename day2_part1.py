class Day2Part1:

    @staticmethod
    def parse_input(input_filename):
        input = open(input_filename).read()
        ranges = input.split(",")
        for range in ranges:
            start, end = range.split("-")[0:2]
            start, end = int(start), int(end)
            print(f"Range: {start} to {end}")                

    @staticmethod
    def contains_invalid_id(start, end):
        for i in range(start, end + 1):
            s = str(i)
            # print(S)
            for c in s:
                # Detect if s consists of two duplicate sets of numbers, like 123123
                pass
        return True
            