"""Fill all green tiles in the polygon and write to indexed file."""
# Step 1: Generate indexed file (once)
# python day9_fill_green_tiles.py day9_input_dean.txt

# Step 2: Find rectangle (rerun as needed)
# pypy day9_find_rectangle_from_tiles.py day9_green_tiles_dean_filled_indexed.txt

import sys
import os
import time
from datetime import datetime, timedelta
from collections import defaultdict

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

def fill_green_tiles_indexed(coords, output_filename):
    """Fill all green tiles and write to indexed file format."""
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
    
    # Scan all points and organize by row
    print(f"Scanning grid and collecting green tiles...")
    rows = defaultdict(list)
    points_processed = 0
    start_time = time.time()
    last_update = start_time
    
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
                
                print(f"\rScanning: {percent:.1f}% ({points_processed:,}/{total_points:,}) | "
                      f"Rate: {rate:,.0f} pts/s | ETA: {end_time_str}", 
                      end='', flush=True)
                last_update = current_time
            
            if is_green_tile(x, y, coords, edge_set):
                rows[y].append(x)
    
    elapsed_scan = time.time() - start_time
    total_green = sum(len(xs) for xs in rows.values())
    print(f"\rScanning: 100.0% ({total_points:,}/{total_points:,}) | "
          f"Found {total_green:,} green tiles in {elapsed_scan:.1f}s")
    
    # Write indexed format
    print(f"\nWriting indexed format to {output_filename}...")
    write_start = time.time()
    last_update = write_start
    rows_written = 0
    total_rows = len(rows)
    
    with open(output_filename, 'w') as f:
        for y in sorted(rows.keys()):
            rows_written += 1
            
            # Update progress every 0.5 seconds
            current_time = time.time()
            if current_time - last_update >= 0.5:
                percent = (rows_written / total_rows) * 100
                elapsed = current_time - write_start
                rate = rows_written / elapsed if elapsed > 0 else 0
                eta_seconds = (total_rows - rows_written) / rate if rate > 0 else 0
                end_time = datetime.now() + timedelta(seconds=eta_seconds)
                end_time_str = end_time.strftime("%I:%M%p").lstrip('0').lower()
                
                print(f"\rWriting: {percent:.1f}% ({rows_written:,}/{total_rows:,}) | "
                      f"Rate: {rate:,.0f} rows/s | ETA: {end_time_str}", 
                      end='', flush=True)
                last_update = current_time
            
            x_values = sorted(rows[y])
            f.write(f"{y}:{','.join(map(str, x_values))}\n")
    
    elapsed_write = time.time() - write_start
    print(f"\rWriting: 100.0% ({total_rows:,}/{total_rows:,}) | "
          f"Completed in {elapsed_write:.1f}s")
    
    total_elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"✓ Wrote {total_green:,} green tiles to {output_filename}")
    print(f"  Scan time: {elapsed_scan:.1f}s ({total_points/elapsed_scan:,.0f} pts/s)")
    print(f"  Write time: {elapsed_write:.1f}s ({total_rows/elapsed_write:,.0f} rows/s)")
    print(f"  Total time: {total_elapsed:.1f}s")
    print(f"{'='*60}")
    
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
    
    # Generate output filename (indexed format)
    base_name = input_filename.replace("_input_", "_green_tiles_")
    output_filename = base_name.replace(".txt", "_filled_indexed.txt")
    
    # Load red tile coordinates
    with open(input_filename, 'r') as f:
        input_text = f.read()
    
    coords = parse_input(input_text)
    
    # Fill green tiles and write to indexed file
    fill_green_tiles_indexed(coords, output_filename)

