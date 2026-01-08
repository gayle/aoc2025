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

def is_green_tile(x, y, coords):
    """Check if a tile is green (on edge or inside polygon)."""
    return is_on_polygon_edge(x, y, coords) or is_inside_polygon(x, y, coords)

def find_largest_rectangle(coords):
    max_area = 0
    total = len(coords) * (len(coords) - 1) // 2
    checked = 0
    last_percent = -1
    
    for i in range(len(coords)):
        x1, y1 = coords[i]
        for j in range(i + 1, len(coords)):
            checked += 1
            percent = checked * 100 // total
            if percent != last_percent:
                print(f"Rectangle search progress: {percent}%", end="\r")
                last_percent = percent
            
            x2, y2 = coords[j]
            if x1 == x2 or y1 == y2:
                continue
            
            min_rx, max_rx = min(x1, x2), max(x1, x2)
            min_ry, max_ry = min(y1, y2), max(y1, y2)
            
            valid = True
            for x in range(min_rx, max_rx + 1):
                for y in range(min_ry, max_ry + 1):
                    if (x, y) == (x1, y1) or (x, y) == (x2, y2):
                        continue
                    if not is_green_tile(x, y, coords):
                        valid = False
                        break
                if not valid:
                    break
            
            if valid:
                area = (max_rx - min_rx + 1) * (max_ry - min_ry + 1)
                if area > max_area:
                    max_area = area
    
    print("\nRectangle search progress: 100% complete")
    return max_area

# Example usage:
if __name__ == "__main__":
    with open("day9_input_dean.txt") as f:
        input_text = f.read()
    coords = parse_input(input_text)
    print(f"Number of vertices: {len(coords)}")
    result = find_largest_rectangle(coords)
    print(f"Largest rectangle area: {result}")
