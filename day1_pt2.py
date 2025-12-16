class Day1Pt2:

    @staticmethod
    def count_times_dial_crosses_zero(input_filename):
        times_dial_crosses_zero = 0
        content = ''
        with open(input_filename, 'r') as f:
            content = f.read()

        lines = content.split()
        dial_position = 50 # Starting position
        for line in lines:
            encountered_zero, dial_position = Day1Pt2.rotate_dial(dial_position, line)
            times_dial_crosses_zero += encountered_zero
        return times_dial_crosses_zero

    @staticmethod
    def rotate_dial(starting_position, action):
        if starting_position < 0 or starting_position > 99:
            raise ValueError("Starting position must be between 1 and 99")
        direction = action[0]
        amount = int(action[1:])
        times_dial_crosses_zero=0
        if direction == "R":
            new_position = starting_position + amount
            times_dial_crosses_zero, dial_position  = divmod(new_position, 100)
        elif direction == "L":
            new_position = starting_position - amount
            dial_position = new_position % 100

            # THIS WORKS
            import math
            times_dial_crosses_zero = math.trunc(abs(new_position / 100))
            if (starting_position > 0 and new_position <= 0): times_dial_crosses_zero += 1

            # THE ABOVE WORKS BUT WHY CAN'T I USE DIVMOD HERE?
            # times_dial_crosses_zero, dial_position  = divmod(new_position, 100)
            # times_dial_crosses_zero = abs(times_dial_crosses_zero)
            # if (starting_position > 0 and new_position <= 0): times_dial_crosses_zero += 1

        else:
            raise ValueError("Invalid direction; expected 'L' or 'R'")
        return times_dial_crosses_zero, dial_position

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python day1_pt2.py <input_filename>")
        sys.exit(1)
    input_filename = sys.argv[1]
    result = Day1Pt2.count_times_dial_crosses_zero(input_filename)
    print(f"Day1 Part2 result: {result}")
