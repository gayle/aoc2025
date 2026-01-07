import sys, os, time

DEBUG = True
count = 0
start_progress_time = time.time()
last_progress_time = time.time()

def print_progress():
    global count, last_progress_time
    count += 1
    now = time.time()
    if now - last_progress_time > 1.0:
        last_progress_time = now
        print(f"Count: {count:,}, Rate: {count / (now - start_progress_time):,.0f}/sec", end="\r")

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
    # In your list, every red tile is connected to the red tile before and after it by a straight line of green tiles. The list wraps, so the first red tile is also connected to the last red tile. Tiles that are adjacent in your list will always be on either the same row or the same column.

    # Start by filling in the green tiles connecting the red tiles.
    start = time.time()
    print(f"\nFilling green tiles...") if DEBUG else None
    green_tiles = set()
    for i, coord in enumerate(coords):
        next_coord = coords[(i + 1) % len(coords)]
        x1, y1 = coord
        x2, y2 = next_coord
        if x1 == x2:  # Vertical line
            for y in range(min(y1, y2), max(y1, y2) + 1):
                green_tiles.add((x1, y))
        elif y1 == y2:  # Horizontal line
            for x in range(min(x1, x2), max(x1, x2) + 1):
                green_tiles.add((x, y1))
        else:
            print(f"Error: Non-straight line between {coord} and {next_coord}") 
    print(f"\nFilled green tiles in {time.time() - start:,.0f} seconds") if DEBUG else None
    
    # Next, fill in the inner area of green tiles.
    print(f"\nFilling inner green tiles...") if DEBUG else None
    start = time.time()
    min_x = min(x for x, y in coords)
    max_x = max(x for x, y in coords)
    min_y = min(y for x, y in coords)
    max_y = max(y for x, y in coords)
    for x in range(min_x, max_x + 1):
        for y in range(min_y, max_y + 1):
            if (x, y) not in coords:
                # Check if this tile is inside the polygon formed by red tiles
                inside = True
                for i in range(len(coords)):
                    print_progress() if DEBUG else None
                    x1, y1 = coords[i]
                    x2, y2 = coords[(i + 1) % len(coords)]
                    if (y1 > y) != (y2 > y) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
                        inside = not inside
                if inside:
                    green_tiles.add((x, y))
    print(f"\nFilled inner green tiles in {time.time() - start:,.0f} seconds") if DEBUG else None

    # Now, find the largest rectangle with red tiles at opposite corners and only red/green tiles inside.
    print(f"\nFinding largest rectangle...") if DEBUG else None
    start = time.time()
    max_area = 0
    for x1, y1 in coords:
        for x2, y2 in coords:
            if x1 < x2 and y1 < y2:
                valid_rectangle = True
                for x in range(x1, x2 + 1):
                    for y in range(y1, y2 + 1):
                        print_progress() if DEBUG else None
                        if (x, y) not in coords and (x, y) not in green_tiles:
                            valid_rectangle = False
                            break
                    if not valid_rectangle:
                        break
                if valid_rectangle:
                    area = (x2 - x1 + 1) * (y2 - y1 + 1)
                    if area > max_area:
                        print(f"\nNew max area {area} found between ({x1},{y1}) and ({x2},{y2})") if DEBUG else None
                        max_area = area
    print(f"\nFound largest rectangle in {time.time() - start:,.0f} seconds") if DEBUG else None

    return max_area

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
    print(f"Day 9 Part 2 result: {result}")
