"""Fill all green tiles in the polygon and write to indexed file."""

# Step 1: Generate indexed file (once).
# Note: Use PyPy for this step because it's faster.
# ./pypy day9_fill_green_tiles.py day9_input_dean.txt

# Step 2: Find largest rectangle (rerun as needed).
# Note: Use PyPy for speed.
# ./pypy day9_find_rectangle_from_tiles.py day9_green_tiles_dean_filled_indexed.txt

import sys, os, time, psutil, winsound
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
    """Fill all green tiles and write to indexed file format (streaming to save memory)."""
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
    
    # Scan row by row and write immediately (streaming to avoid memory issues)
    print(f"Scanning grid and writing to {output_filename}...")
    start_time = time.time()
    last_update = start_time
    points_processed = 0
    total_green = 0
    rows_written = 0
    
    with open(output_filename, 'w') as f:
        # Process y values (rows) in order
        for y in range(min_y, max_y + 1):
            # Collect all green x values for this row
            row_xs = []
            for x in range(min_x, max_x + 1):
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
                    
                    # Get available memory
                    mem = psutil.virtual_memory()
                    mem_avail_gb = mem.available / (1024**3)
                    
                    print(f"\rScanning: {percent:.1f}% ({points_processed:,}/{total_points:,}) | "
                          f"Green: {total_green:,} | Rate: {rate:,.0f} pts/s | "
                          f"Mem: {mem_avail_gb:.1f}GB | ETA: {end_time_str}", 
                          end='', flush=True)
                    last_update = current_time
                
                if is_green_tile(x, y, coords, edge_set):
                    row_xs.append(x)
            
            # Write this row if it has green tiles
            if row_xs:
                f.write(f"{y}:{','.join(map(str, row_xs))}\n")
                total_green += len(row_xs)
                rows_written += 1
                f.flush()  # Ensure data is written periodically
    
    elapsed = time.time() - start_time
    print(f"\rScanning: 100.0% ({total_points:,}/{total_points:,}) | "
          f"Green: {total_green:,} | Completed in {elapsed:.1f}s")
    
    print(f"\n{'='*60}")
    print(f"✓ Wrote {total_green:,} green tiles in {rows_written:,} rows")
    print(f"  Total time: {elapsed:.1f}s ({total_points/elapsed:,.0f} pts/s)")
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

    winsound.PlaySound("c:\\windows\\media\\tada.wav", winsound.SND_FILENAME)