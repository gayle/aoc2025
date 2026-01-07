import sys, os, time
import numpy

DEBUG = True
count = 0
start_progress_time = time.time()
last_progress_time = time.time()

def print_progress():
    if not DEBUG:
        return
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
    
    # Next, fill in the inner area of green tiles using scanline fill (optimized for axis-aligned polygons)
    print(f"\nFilling inner green tiles (scanline fill)...") if DEBUG else None
    start = time.time()
    min_x = min(x for x, y in coords)
    max_x = max(x for x, y in coords)
    min_y = min(y for x, y in coords)
    max_y = max(y for x, y in coords)
    # Precompute vertical segments for each scanline
    scanline_xs = {y: [] for y in range(min_y + 1, max_y)}
    for i in range(len(coords)):
        x1, y1 = coords[i]
        x2, y2 = coords[(i + 1) % len(coords)]
        # Ignore horizontal edges
        if y1 == y2:
            continue
        # For each scanline y between y1 and y2 (exclusive), compute intersection
        y_start, y_end = sorted([y1, y2])
        for y in range(max(min_y + 1, y_start + 1), min(max_y, y_end + 1)):
            dy = y2 - y1
            dx = x2 - x1
            x_cross = x1 + ((y - y1) * dx) // dy
            scanline_xs[y].append(x_cross)

    total_scanlines = max_y - min_y - 1
    for idx, y in enumerate(range(min_y + 1, max_y)):
        if DEBUG and total_scanlines > 0 and idx % max(1, total_scanlines // 100) == 0:
            percent = (idx + 1) * 100 // total_scanlines
            print(f"Scanline fill progress: {percent}% complete", end="\r")
        x_crossings = scanline_xs[y]
        x_crossings.sort()
        for i in range(0, len(x_crossings), 2):
            if i+1 >= len(x_crossings):
                break
            # Only fill strictly inside, not including border
            x_start = x_crossings[i] + 1
            x_end = x_crossings[i+1]
            for x in range(x_start, x_end):
                if (x, y) not in coords:
                    green_tiles.add((x, y))
    if DEBUG:
        print("Scanline fill progress: 100% complete")
    print(f"\nFilled inner green tiles in {time.time() - start:,.0f} seconds") if DEBUG else None

    # Now, find the largest rectangle with red tiles at opposite corners and only red/green tiles inside.
    print(f"\nFinding largest rectangle...") if DEBUG else None
    start = time.time()
    max_area = 0
    # Use numpy for grid operations
    print(f"\nBuilding numpy grid...") if DEBUG else None
    min_x = min(x for x, y in coords)
    max_x = max(x for x, y in coords)
    min_y = min(y for x, y in coords)
    max_y = max(y for x, y in coords)
    width = max_x - min_x + 1
    height = max_y - min_y + 1
    from scipy.sparse import dok_matrix
    print(f"\nBuilding sparse grid...") if DEBUG else None
    grid = dok_matrix((width, height), dtype=bool)
    for x, y in green_tiles:
        grid[x - min_x, y - min_y] = True
    for x, y in coords:
        grid[x - min_x, y - min_y] = True

    print(f"\nFinding largest rectangle with sparse grid (non-empty rows/cols)...") if DEBUG else None
    max_area = 0
    # Find non-empty rows and columns
    non_empty_rows = set()
    non_empty_cols = set()
    for (x, y) in grid.keys():
        if grid[x, y]:
            non_empty_cols.add(x)
            non_empty_rows.add(y)
    non_empty_cols = sorted(non_empty_cols)
    non_empty_rows = sorted(non_empty_rows)

    # Only iterate over non-empty rows and columns
    # Try all pairs of red tiles as opposite corners
    for i in range(len(coords)):
        x1, y1 = coords[i]
        for j in range(i + 1, len(coords)):
            x2, y2 = coords[j]
            # Rectangle must be axis-aligned
            if x1 == x2 or y1 == y2:
                continue
            min_rx, max_rx = min(x1, x2), max(x1, x2)
            min_ry, max_ry = min(y1, y2), max(y1, y2)
            valid = True
            for x in range(min_rx, max_rx + 1):
                for y in range(min_ry, max_ry + 1):
                    if (x, y) == (x1, y1) or (x, y) == (x2, y2):
                        continue
                    gx, gy = x - min_x, y - min_y
                    if gx < 0 or gx >= width or gy < 0 or gy >= height:
                        valid = False
                        break
                    if not grid.get((gx, gy), False):
                        valid = False
                        break
                if not valid:
                    break
            if valid:
                area = (max_rx - min_rx + 1) * (max_ry - min_ry + 1)
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
    try:
        input_text = open(input_filename).read()
        coords = parse_input(input_text)     
        result = find_result(coords)
        print(f"Day 9 Part 2 result: {result}")
    except KeyboardInterrupt as e:
        print_progress() # Leave the count and rate display visible
