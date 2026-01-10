"""Fill all green tiles in the polygon and write to file."""
import sys
import os
import time
from datetime import datetime, timedelta

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

def compute_edge_set(coords):
    """Pre-compute all points on polygon edges for O(1) lookup."""
    edge_points = set()
    n = len(coords)
    for i in range(n):
        x1, y1 = coords[i]
        x2, y2 = coords[(i + 1) % n]
        if x1 == x2:  # Vertical line
            for y in range(min(y1, y2), max(y1, y2) + 1):
                edge_points.add((x1, y))
        elif y1 == y2:  # Horizontal line
            for x in range(min(x1, x2), max(x1, x2) + 1):
                edge_points.add((x, y1))
    return edge_points

def is_green_tile(x, y, coords, edge_set):
    """Check if a tile is green (on edge or inside polygon)."""
    return (x, y) in edge_set or is_inside_polygon(x, y, coords)

def fill_green_tiles(coords, output_filename):
    """Fill all green tiles and write to file."""
    print(f"Parsing {len(coords)} red tile coordinates...")
    
    # Compute bounding box
    min_x = min(x for x, y in coords)
    max_x = max(x for x, y in coords)
    min_y = min(y for x, y in coords)
    max_y = max(y for x, y in coords)
    
    print(f"Bounding box: x=[{min_x}, {max_x}], y=[{min_y}, {max_y}]")
    
    width = max_x - min_x + 1
    height = max_y - min_y + 1
    total_points = width * height
    
    print(f"Grid size: {width} × {height} = {total_points:,} points")
    
    # Pre-compute edge set for fast lookup
    print("Computing edge points...")
    edge_set = compute_edge_set(coords)
    print(f"Edge contains {len(edge_set):,} points")
    
    # Scan all points and collect green tiles
    print(f"Scanning grid and writing to {output_filename}...")
    green_count = 0
    points_processed = 0
    start_time = time.time()
    last_update = start_time
    
    with open(output_filename, 'w') as f:
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                points_processed += 1
                
                # Update progress every 0.5 seconds
                current_time = time.time()
                if current_time - last_update >= 0.5:
                    percent = (points_processed / total_points) * 100
                    elapsed = current_time - start_time
                    rate = points_processed / elapsed if elapsed > 0 else 0
                    eta_seconds = (total_points - points_processed) / rate if rate > 0 else 0
                    end_time = datetime.now() + timedelta(seconds=eta_seconds)
                    end_time_str = end_time.strftime("%I:%M%p").lstrip('0').lower()
                    
                    print(f"\rProgress: {percent:.1f}% ({points_processed:,}/{total_points:,}) | "
                          f"Green tiles: {green_count:,} | Rate: {rate:,.0f} pts/s | ETA: {end_time_str}", 
                          end='', flush=True)
                    last_update = current_time
                    f.flush()  # Ensure writes are flushed to disk
                
                if is_green_tile(x, y, coords, edge_set):
                    f.write(f"{x},{y}\n")
                    green_count += 1
        
        # Final progress update
        elapsed = time.time() - start_time
        print(f"\rProgress: 100.0% ({total_points:,}/{total_points:,}) | "
              f"Green tiles: {green_count:,} | Completed in {elapsed:.1f}s")
    
    print(f"\n✓ Wrote {green_count:,} green tiles to {output_filename}")
    print(f"  Total time: {elapsed:.1f}s")
    print(f"  Average rate: {total_points/elapsed:,.0f} points/second")
    
    # Simple beep on completion
    try:
        import winsound
        winsound.Beep(1000, 500)  # 1kHz for 500ms
    except:
        pass  # Silently fail if sound doesn't work

if __name__ == "__main__":
    # Determine input file
    if len(sys.argv) == 2:
        input_filename = sys.argv[1]
    else:
        # Auto-detect input file
        if os.path.exists("day9_input_gayle.txt"):
            input_filename = "day9_input_gayle.txt"
        elif os.path.exists("day9_input_dean.txt"):
            input_filename = "day9_input_dean.txt"
        else:
            print("Error: No input file found. Provide filename as argument.")
            sys.exit(1)
    
    print(f"Using input file: {input_filename}")
    
    # Generate output filename
    base_name = input_filename.replace("_input_", "_green_tiles_")
    output_filename = base_name.replace(".txt", "_filled.txt")
    
    # Load red tile coordinates
    with open(input_filename, 'r') as f:
        input_text = f.read()
    
    coords = parse_input(input_text)
    
    # Fill green tiles and write to file
    fill_green_tiles(coords, output_filename)
