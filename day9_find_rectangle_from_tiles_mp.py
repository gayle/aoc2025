"""Find largest rectangle using multiprocessing for speed."""

# Workflow (run once):
# 1. ./pypy day9_fill_green_tiles.py day9_input_dean.txt
# 2. ./pypy day9_fill_green_tiles_build_index.py day9_green_tiles_dean_filled_indexed.txt
# 3. ./pypy day9_extract_corners.py day9_green_tiles_dean_filled_indexed.txt

# Then find rectangles (can rerun with different thresholds):
# python day9_find_rectangle_from_tiles_mp.py day9_green_tiles_dean_filled_indexed.txt

import sys
import os
import time
import common
import psutil
from datetime import datetime, timedelta
from multiprocessing import Pool, Manager, cpu_count

# Enable unicode output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

DEFAULT_MIN_AREA_THRESHOLD = 100_000_000  # Default minimum area
MIN_AREA_THRESHOLD = DEFAULT_MIN_AREA_THRESHOLD  # Will be set from command line

def load_file_index(indexed_file):
    """Load pre-built index mapping y -> file offset from .idx file."""
    index_file = indexed_file.rsplit('.', 1)[0] + '.idx'
    
    if not os.path.exists(index_file):
        print(f"Error: Index file '{index_file}' not found.")
        print(f"Run: python day9_fill_green_tiles_build_index.py {indexed_file}")
        sys.exit(1)
    
    print(f"Loading file index from {index_file}...")
    start_time = time.time()
    
    index = {}  # y -> file offset
    
    with open(index_file, 'r') as f:
        for line in f:
            y_str, offset_str = line.strip().split(':', 1)
            y = int(y_str)
            offset = int(offset_str)
            index[y] = offset
    
    elapsed = time.time() - start_time
    print(f"✓ Loaded {len(index):,} row offsets in {elapsed:.1f}s\n")
    
    return index

def load_corners_from_file(indexed_file):
    """Load pre-extracted corners from .corners file."""
    corners_file = indexed_file.rsplit('.', 1)[0] + '.corners'
    
    if not os.path.exists(corners_file):
        print(f"Error: Corners file '{corners_file}' not found.")
        print(f"Run: python day9_extract_corners.py {indexed_file}")
        sys.exit(1)
    
    print(f"Loading corners from {corners_file}...")
    start_time = time.time()
    
    corners = []
    bounding_box = None
    
    # Get file size for progress tracking
    file_size = os.path.getsize(corners_file)
    
    with open(corners_file, 'r') as f:
        # Skip comment line
        f.readline()
        
        # Read bounding box
        bbox_line = f.readline().strip()
        min_x, max_x, min_y, max_y = map(int, bbox_line.split(','))
        bounding_box = (min_x, max_x, min_y, max_y)
        
        # Read corners
        i = 0
        while True:
            line = f.readline()
            if not line:
                break
            
            x_str, y_str = line.strip().split(',')
            corners.append((int(x_str), int(y_str)))
            i += 1
            
            if i % 100_000 == 0:
                # Check memory while loading
                mem = psutil.virtual_memory()
                mem_avail_mb = mem.available / (1024**2)
                if mem_avail_mb < 200:
                    print(f"\n\n⚠ Low memory warning: {mem_avail_mb:.0f}MB free (< 200MB)")
                    print("Terminating to prevent system instability...")
                    sys.exit(1)
                
                # Calculate progress metrics
                file_pos = f.tell()
                percent = (file_pos / file_size) * 100 if file_size > 0 else 0
                elapsed = time.time() - start_time
                rate = i / elapsed if elapsed > 0 else 0
                eta_seconds = ((file_size - file_pos) / file_pos) * elapsed if file_pos > 0 else 0
                end_time = datetime.now() + timedelta(seconds=eta_seconds)
                end_time_str = end_time.strftime("%I:%M%p").lstrip('0').lower()
                
                mem_avail_gb = mem.available / (1024**3)
                print(f"  {percent:.1f}% | Loaded {i:,} corners | Rate: {rate:,.0f}/s | Free RAM: {mem_avail_gb:.1f}GB | ETA: {end_time_str}", end='\r', flush=True)
    
    elapsed = time.time() - start_time
    print(f"\n✓ Loaded {len(corners):,} corners in {elapsed:.1f}s")
    print(f"  Bounding box: x=[{bounding_box[0]}, {bounding_box[1]}], y=[{bounding_box[2]}, {bounding_box[3]}]\n")
    
    return corners, bounding_box

def load_row_from_file(indexed_file, file_index, y):
    """Load a single row from file using the index."""
    if y not in file_index:
        return None
    
    with open(indexed_file, 'r') as f:
        f.seek(file_index[y])
        line = f.readline()
        y_str, x_str = line.strip().split(':', 1)
        return set(map(int, x_str.split(',')))

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
    batch, corners, indexed_file, file_index, progress_dict, batch_id = args
    
    max_area = 0
    max_rect = None
    checked = 0
    
    # Cache for recently used rows (limit to 100 rows per worker)
    row_cache = {}
    
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
            # Load row from cache or file
            if y not in row_cache:
                # Limit cache size
                if len(row_cache) > 100:
                    row_cache.clear()
                
                row_xs = load_row_from_file(indexed_file, file_index, y)
                if row_xs is None:
                    valid = False
                    break
                row_cache[y] = row_xs
            else:
                row_xs = row_cache[y]
            
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

def find_largest_rectangle_mp(indexed_file, file_index, corners, bounding_box, num_processes=None):
    """Find largest rectangle using multiprocessing."""
    if num_processes is None:
        num_processes = min(40, cpu_count())
    
    print(f"Finding largest rectangle with {num_processes} processes...")
    
    min_x, max_x, min_y, max_y = bounding_box
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
                if area >= MIN_AREA_THRESHOLD:
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
        batches.append((batch, corners, indexed_file, file_index, progress_dict, batch_id))
    
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
            
            # Get available memory
            mem = psutil.virtual_memory()
            mem_avail_gb = mem.available / (1024**3)
            mem_avail_mb = mem.available / (1024**2)
            
            # Check if running out of memory
            if mem_avail_mb < 200:
                print(f"\n\n⚠ Low memory warning: {mem_avail_mb:.0f}MB free (< 200MB)")
                print("Terminating to prevent system instability...")
                pool.terminate()
                pool.join()
                sys.exit(1)
            
            checked_total = sum(p.get('checked', 0) for p in progress_dict.values())
            print(f"{percent:.1f}% batches | Checked: {checked_total:,}/{len(pairs):,} | "
                  f"Best: {max_area:,} | Rate: {rate:,.0f} pairs/s | "
                  f"Free RAM: {mem_avail_gb:.1f}GB | ETA: {end_time_str}", 
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
    # Print execution info
    import platform
    print(f"Python: {platform.python_implementation()} {platform.python_version()}")
    print(f"Command: {' '.join(sys.argv)}\n")
    
    # Parse command line arguments
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
    
    # Parse optional minimum area threshold
    if len(sys.argv) >= 3:
        try:
            MIN_AREA_THRESHOLD = int(sys.argv[2])
        except ValueError:
            print(f"Error: Invalid threshold value '{sys.argv[2]}'. Must be an integer.")
            sys.exit(1)
    else:
        MIN_AREA_THRESHOLD = DEFAULT_MIN_AREA_THRESHOLD
    
    if not os.path.exists(indexed_file):
        print(f"Error: File '{indexed_file}' not found.")
        print("Run day9_fill_green_tiles.py first to generate the indexed file.")
        sys.exit(1)
    
    print(f"Using indexed tiles file: {indexed_file}")
    print(f"Minimum area threshold: {MIN_AREA_THRESHOLD:,}\n")
    
    # Load pre-built file index
    file_index = load_file_index(indexed_file)
    
    # Load pre-extracted corners and bounding box
    corners, bounding_box = load_corners_from_file(indexed_file)
    
    # Find largest rectangle using multiprocessing (workers load rows on-demand)
    max_area, max_rect = find_largest_rectangle_mp(indexed_file, file_index, corners, bounding_box)
    
    if max_rect:
        print(f"\n{'='*60}")
        print(f"RESULT: {max_area:,}")
        print(f"Rectangle: ({max_rect[0]},{max_rect[1]}) to ({max_rect[2]},{max_rect[3]})")
        print(f"{'='*60}")
        common.multibeep()

    else:
        print("\nNo valid rectangle found.")
