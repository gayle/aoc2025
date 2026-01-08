from multiprocessing import Pool, cpu_count, Manager
import itertools

def parse_input(input_text):
    coords = []
    for line in input_text.splitlines():
        line = line.strip()
        if not line:
            continue
        x, y = map(int, line.split(','))
        coords.append((x, y))
    return coords

def is_on_polygon_edge(x, y, coords):
    """Check if point (x, y) is on the polygon edge."""
    n = len(coords)
    for i in range(n):
        x1, y1 = coords[i]
        x2, y2 = coords[(i + 1) % n]
        # Check if point is on line segment
        if x1 == x2:  # Vertical line
            if x == x1 and min(y1, y2) <= y <= max(y1, y2):
                return True
        elif y1 == y2:  # Horizontal line
            if y == y1 and min(x1, x2) <= x <= max(x1, x2):
                return True
    return False

def is_inside_polygon(x, y, coords):
    """Check if point (x, y) is inside polygon using ray casting."""
    n = len(coords)
    inside = False
    for i in range(n):
        x1, y1 = coords[i]
        x2, y2 = coords[(i + 1) % n]
        if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
            inside = not inside
    return inside

def is_green_tile(x, y, coords, cache=None):
    """Check if a tile is green (on edge or inside polygon)."""
    if cache is not None and (x, y) in cache:
        return cache[(x, y)]
    
    result = is_on_polygon_edge(x, y, coords) or is_inside_polygon(x, y, coords)
    
    if cache is not None:
        cache[(x, y)] = result
    
    return result

def check_rectangle_batch(args):
    """Check a batch of rectangle pairs."""
    pairs, coords, coord_set = args
    max_area = 0
    max_rect = None
    cache = {}
    
    for i, j in pairs:
        x1, y1 = coords[i]
        x2, y2 = coords[j]
        
        # Skip if corners don't form a proper rectangle
        if x1 == x2 or y1 == y2:
            continue
        
        min_rx, max_rx = min(x1, x2), max(x1, x2)
        min_ry, max_ry = min(y1, y2), max(y1, y2)
        
        area = (max_rx - min_rx + 1) * (max_ry - min_ry + 1)
        
        # Skip if this rectangle is smaller than current max
        if area <= max_area:
            continue
        
        # Check the other two corners first (fast rejection)
        if (min_rx, max_ry) not in coord_set and not is_green_tile(min_rx, max_ry, coords, cache):
            continue
        if (max_rx, min_ry) not in coord_set and not is_green_tile(max_rx, min_ry, coords, cache):
            continue
        
        # Check all points in rectangle
        valid = True
        for x in range(min_rx, max_rx + 1):
            for y in range(min_ry, max_ry + 1):
                # Skip the corners we're using
                if (x, y) == (x1, y1) or (x, y) == (x2, y2):
                    continue
                if (x, y) not in coord_set and not is_green_tile(x, y, coords, cache):
                    valid = False
                    break
            if not valid:
                break
        
        if valid:
            if area > max_area:
                max_area = area
                max_rect = (min_rx, min_ry, max_rx, max_ry)
    
    return max_area, max_rect

def find_largest_rectangle(coords, num_processes=None):
    if num_processes is None:
        num_processes = cpu_count()
    
    print(f"Using {num_processes} processes")
    
    # Create a set of coord tuples for O(1) lookup
    coord_set = set(coords)
    
    # Generate all pairs
    pairs = [(i, j) for i in range(len(coords)) for j in range(i + 1, len(coords))]
    total = len(pairs)
    print(f"Total rectangle pairs to check: {total}")
    
    # Split pairs into batches for each process
    batch_size = max(1, total // (num_processes * 4))  # 4x batches for better load balancing
    batches = []
    for i in range(0, len(pairs), batch_size):
        batch = pairs[i:i + batch_size]
        batches.append((batch, coords, coord_set))
    
    print(f"Split into {len(batches)} batches")
    
    # Process batches in parallel
    max_area = 0
    max_rect = None
    completed = 0
    
    with Pool(processes=num_processes) as pool:
        for result in pool.imap_unordered(check_rectangle_batch, batches):
            area, rect = result
            if area > max_area:
                max_area = area
                max_rect = rect
            completed += 1
            percent = completed * 100.0 / len(batches)
            print(f"Progress: {percent:.2f}% (max area: {max_area})", end="\r")
    
    print(f"\nRectangle search progress: 100.00% complete")
    if max_rect:
        print(f"Best rectangle: ({max_rect[0]},{max_rect[1]}) to ({max_rect[2]},{max_rect[3]})")
    return max_area

# Example usage:
if __name__ == "__main__":
    with open("day9_input_dean.txt") as f:
        input_text = f.read()
    coords = parse_input(input_text)
    print(f"Number of vertices: {len(coords)}")
    result = find_largest_rectangle(coords)
    print(f"Largest rectangle area: {result}")
