"""Find largest rectangle using pre-computed indexed green tiles file."""
# Step 1: Generate indexed file (once)
# python day9_fill_green_tiles.py day9_input_dean.txt

# Step 2: Find rectangle (rerun as needed)
# pypy day9_find_rectangle_from_tiles.py day9_green_tiles_dean_filled_indexed.txt

import sys
import os
import time
from datetime import datetime, timedelta

def load_indexed_tiles(indexed_file):
    """Load tiles from indexed format into memory-efficient structure."""
    print(f"Loading indexed tiles from {indexed_file}...")
    start_time = time.time()
    
    rows = {}
    row_count = 0
    
    with open(indexed_file, 'r') as f:
        for line in f:
            row_count += 1
            if row_count % 10_000 == 0:
                print(f"  Loaded {row_count:,} rows...", end='\r', flush=True)
            
            y_str, x_str = line.strip().split(':', 1)
            y = int(y_str)
            rows[y] = set(map(int, x_str.split(',')))
    
    elapsed = time.time() - start_time
    total_tiles = sum(len(x_set) for x_set in rows.values())
    print(f"\n✓ Loaded {total_tiles:,} tiles in {row_count:,} rows in {elapsed:.1f}s")
    
    return rows

def is_green_tile_fast(x, y, rows):
    """Check if tile is green using indexed structure."""
    return y in rows and x in rows[y]

def get_bounding_box(rows):
    """Get bounding box from indexed rows."""
    min_y = min(rows.keys())
    max_y = max(rows.keys())
    
    min_x = float('inf')
    max_x = float('-inf')
    for x_set in rows.values():
        if x_set:
            min_x = min(min_x, min(x_set))
            max_x = max(max_x, max(x_set))
    
    return min_x, max_x, min_y, max_y

def extract_corners(rows):
    """Extract potential corner points from green tiles."""
    corners = set()
    for y, x_set in rows.items():
        for x in x_set:
            corners.add((x, y))
    return list(corners)

def find_largest_rectangle(rows):
    """Find largest rectangle where all interior points are green."""
    print("\nFinding largest rectangle...")
    
    min_x, max_x, min_y, max_y = get_bounding_box(rows)
    print(f"Bounding box: x=[{min_x}, {max_x}], y=[{min_y}, {max_y}]")
    
    corners = extract_corners(rows)
    print(f"Total corner candidates: {len(corners):,}")
    
    # Generate all pairs of corners
    total_pairs = len(corners) * (len(corners) - 1) // 2
    print(f"Total pairs to check: {total_pairs:,}")
    
    max_area = 0
    max_rect = None
    checked = 0
    start_time = time.time()
    last_update = start_time
    
    # Sort corners by potential area (descending)
    print("Sorting pairs by potential area...")
    pairs = []
    for i in range(len(corners)):
        for j in range(i + 1, len(corners)):
            x1, y1 = corners[i]
            x2, y2 = corners[j]
            if x1 != x2 and y1 != y2:
                area = abs(x2 - x1 + 1) * abs(y2 - y1 + 1)
                pairs.append((area, i, j))
    
    pairs.sort(reverse=True)
    print(f"Valid rectangle pairs: {len(pairs):,}")
    
    print("\nChecking rectangles...\n")
    
    for area, i, j in pairs:
        checked += 1
        
        # Progress update
        current_time = time.time()
        if current_time - last_update >= 1.0:
            percent = (checked / len(pairs)) * 100
            elapsed = current_time - start_time
            rate = checked / elapsed if elapsed > 0 else 0
            eta_seconds = (len(pairs) - checked) / rate if rate > 0 else 0
            end_time = datetime.now() + timedelta(seconds=eta_seconds)
            end_time_str = end_time.strftime("%I:%M%p").lstrip('0').lower()
            
            print(f"Progress: {percent:.1f}% ({checked:,}/{len(pairs):,}) | "
                  f"Best: {max_area:,} | Rate: {rate:,.0f} pairs/s | ETA: {end_time_str}", 
                  end='\r', flush=True)
            last_update = current_time
        
        # Skip if smaller than current best
        if area <= max_area:
            continue
        
        # Skip very large rectangles (likely to fail and take too long)
        if area > 100_000_000:
            continue
        
        x1, y1 = corners[i]
        x2, y2 = corners[j]
        
        min_rx, max_rx = min(x1, x2), max(x1, x2)
        min_ry, max_ry = min(y1, y2), max(y1, y2)
        
        # Check if rectangle is valid (all points are green)
        valid = True
        for y in range(min_ry, max_ry + 1):
            if y not in rows:
                valid = False
                break
            
            row_xs = rows[y]
            # Check if all x values in this row are present
            for x in range(min_rx, max_rx + 1):
                if x not in row_xs:
                    valid = False
                    break
            
            if not valid:
                break
        
        if valid:
            max_area = area
            max_rect = (min_rx, min_ry, max_rx, max_ry)
            print(f"\n✓ New best: {max_area:,} at ({min_rx},{min_ry})-({max_rx},{max_ry})")
    
    elapsed = time.time() - start_time
    print(f"\n\n✓ Search complete in {elapsed:.1f}s")
    print(f"  Checked {checked:,} pairs")
    print(f"  Rate: {checked/elapsed:,.0f} pairs/second")
    
    return max_area, max_rect

if __name__ == "__main__":
    # Determine indexed file
    if len(sys.argv) >= 2:
        indexed_file = sys.argv[1]
    else:
        # Auto-detect indexed tiles file
        if os.path.exists("day9_green_tiles_gayle_filled_indexed.txt"):
            indexed_file = "day9_green_tiles_gayle_filled_indexed.txt"
        elif os.path.exists("day9_green_tiles_dean_filled_indexed.txt"):
            indexed_file = "day9_green_tiles_dean_filled_indexed.txt"
        else:
            print("Error: No indexed tiles file found.")
            print("Run day9_fill_green_tiles.py first to generate the indexed file.")
            sys.exit(1)
    
    if not os.path.exists(indexed_file):
        print(f"Error: File '{indexed_file}' not found.")
        print("Run day9_fill_green_tiles.py first to generate the indexed file.")
        sys.exit(1)
    
    print(f"Using indexed tiles file: {indexed_file}")
    
    # Load indexed tiles
    rows = load_indexed_tiles(indexed_file)
    
    # Find largest rectangle
    max_area, max_rect = find_largest_rectangle(rows)
    
    if max_rect:
        print(f"\n{'='*60}")
        print(f"RESULT: {max_area:,}")
        print(f"Rectangle: ({max_rect[0]},{max_rect[1]}) to ({max_rect[2]},{max_rect[3]})")
        print(f"{'='*60}")
        
        # Play completion beep
        try:
            import winsound
            winsound.Beep(1000, 500)
        except:
            pass
    else:
        print("\nNo valid rectangle found.")
