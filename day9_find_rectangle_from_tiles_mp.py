"""Find largest rectangle using multiprocessing for speed."""

# Step 1: Generate indexed file (once).
# Note: Use PyPy for this step because it's faster.
# ./pypy day9_fill_green_tiles.py day9_input_dean.txt

# Step 2: Find rectangle with multiprocessing (rerun as needed).
# Note: Use CPython for this because it handles multiprocessing better.
# python day9_find_rectangle_from_tiles_mp.py day9_green_tiles_dean_filled_indexed.txt

import sys
import os
import time
import winsound
from datetime import datetime, timedelta
from multiprocessing import Pool, Manager, cpu_count

MIN_AREA_THRESHOLD = 8_000_000  # Skip rectangles smaller than 8M area

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

def check_rectangle(args):
    """Check a single rectangle in a worker process."""
    area, i, j, corners, rows = args
    
    # Skip if too small
    if area < MIN_AREA_THRESHOLD:
        return 0, None
    
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
        return area, (min_rx, min_ry, max_rx, max_ry)
    else:
        return 0, None

def check_rectangle_batch(args):
    """Check a batch of rectangles in a worker process."""
    batch, corners, rows, progress_dict, batch_id = args
    
    max_area = 0
    max_rect = None
    checked = 0
    
    for area, i, j in batch:
        checked += 1
        
        # Skip if too small
        if area < MIN_AREA_THRESHOLD:
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
            for x in range(min_rx, max_rx + 1):
                if x not in row_xs:
                    valid = False
                    break
            
            if not valid:
                break
        
        if valid and area > max_area:
            max_area = area
            max_rect = (min_rx, min_ry, max_rx, max_ry)
    
    # Update progress
    progress_dict[batch_id] = {'checked': len(batch), 'max_area': max_area}
    
    return max_area, max_rect

def find_largest_rectangle_mp(rows, num_processes=None):
    """Find largest rectangle using multiprocessing."""
    if num_processes is None:
        num_processes = min(40, cpu_count())
    
    print(f"\nFinding largest rectangle with {num_processes} processes...")
    
    min_x, max_x, min_y, max_y = get_bounding_box(rows)
    print(f"Bounding box: x=[{min_x}, {max_x}], y=[{min_y}, {max_y}]")
    
    corners = extract_corners(rows)
    print(f"Total corner candidates: {len(corners):,}")
    
    # Sort corners by potential area (descending)
    print("Sorting pairs by potential area...")
    pairs = []
    for i in range(len(corners)):
        for j in range(i + 1, len(corners)):
            x1, y1 = corners[i]
            x2, y2 = corners[j]
            if x1 != x2 and y1 != y2:
                area = abs(x2 - x1 + 1) * abs(y2 - y1 + 1)
                # Filter out small rectangles early
                if area >= MIN_AREA_THRESHOLD and area <= 100_000_000:
                    pairs.append((area, i, j))
    
    pairs.sort(reverse=True)
    print(f"Valid rectangle pairs (>= {MIN_AREA_THRESHOLD:,} area): {len(pairs):,}")
    
    if len(pairs) == 0:
        print("No rectangles meet the minimum area threshold.")
        return 0, None
    
    # Split into batches for workers
    batch_size = max(1, len(pairs) // (num_processes * 4))
    batches = []
    manager = Manager()
    progress_dict = manager.dict()
    
    for batch_id, i in enumerate(range(0, len(pairs), batch_size)):
        batch = pairs[i:i + batch_size]
        batches.append((batch, corners, rows, progress_dict, batch_id))
    
    print(f"Split into {len(batches)} batches ({batch_size:,} pairs per batch)")
    print("\nChecking rectangles...\n")
    
    start_time = time.time()
    last_update = start_time
    
    # Process batches in parallel
    pool = Pool(processes=num_processes)
    result_iterator = pool.imap_unordered(check_rectangle_batch, batches)
    
    max_area = 0
    max_rect = None
    completed = 0
    
    for area, rect in result_iterator:
        completed += 1
        if area > max_area:
            max_area = area
            max_rect = rect
            print(f"\n✓ New best: {max_area:,} at {max_rect}")
        
        # Progress update
        current_time = time.time()
        if current_time - last_update >= 1.0:
            percent = (completed / len(batches)) * 100
            elapsed = current_time - start_time
            rate = sum(p.get('checked', 0) for p in progress_dict.values()) / elapsed if elapsed > 0 else 0
            eta_seconds = (len(pairs) - sum(p.get('checked', 0) for p in progress_dict.values())) / rate if rate > 0 else 0
            end_time = datetime.now() + timedelta(seconds=eta_seconds)
            end_time_str = end_time.strftime("%I:%M%p").lstrip('0').lower()
            
            checked_total = sum(p.get('checked', 0) for p in progress_dict.values())
            print(f"Progress: {percent:.1f}% batches ({completed}/{len(batches)}) | "
                  f"Checked: {checked_total:,}/{len(pairs):,} | "
                  f"Best: {max_area:,} | Rate: {rate:,.0f} pairs/s | ETA: {end_time_str}", 
                  end='\r', flush=True)
            last_update = current_time
    
    pool.close()
    pool.join()
    
    elapsed = time.time() - start_time
    print(f"\n\n✓ Search complete in {elapsed:.1f}s")
    print(f"  Checked {len(pairs):,} pairs")
    print(f"  Rate: {len(pairs)/elapsed:,.0f} pairs/second")
    
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
    print(f"Minimum area threshold: {MIN_AREA_THRESHOLD:,}")
    
    # Load indexed tiles
    rows = load_indexed_tiles(indexed_file)
    
    # Find largest rectangle using multiprocessing
    max_area, max_rect = find_largest_rectangle_mp(rows)
    
    if max_rect:
        print(f"\n{'='*60}")
        print(f"RESULT: {max_area:,}")
        print(f"Rectangle: ({max_rect[0]},{max_rect[1]}) to ({max_rect[2]},{max_rect[3]})")
        print(f"{'='*60}")
        winsound.PlaySound("c:\\windows\\media\\tada.wav", winsound.SND_FILENAME)
    else:
        print("\nNo valid rectangle found.")
