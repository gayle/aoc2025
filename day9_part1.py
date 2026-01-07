import sys, os

def parse_input(input_text):
    try:
        coords = []
        for line in input_text.splitlines():
            x, y = line.strip().split(',')
            x, y = int(x), int(y)
            coords.append((x, y))
        return coords
    except ValueError:
        print(f"Error parsing line: {line}")

def find_result(coords):
    return 0

if __name__ == "__main__":
    # If no filename is provided, try common input filenames before failing.
    if len(sys.argv) == 2:
        input_filename = sys.argv[1]
    else:
        # Prefer Gayle's input if present, otherwise Dean's input
        if os.path.exists("day9_input_gayle.txt"):
            input_filename = "day9_input_gayle.txt"
        elif os.path.exists("day9_input_dean.txt"):
            input_filename = "day9_input_dean.txt"
        else:
            print(f"Usage: python {sys.argv[0]} <input_filename>")
            sys.exit(1)
  
    input_text = open(input_filename).read()
    coords = parse_input(input_text)     
    result = find_result(coords)
    print(f"Day 9 Part 1 result: {result}")
