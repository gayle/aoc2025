"""Find largest rectangle using sampled validation (every 1000th point)."""

# Workflow (run once):
# 1. ./pypy day9_fill_green_tiles.py day9_input_dean.txt
# 2. ./pypy day9_fill_green_tiles_build_index.py day9_green_tiles_dean_filled_indexed.txt
# 3. ./pypy day9_extract_corners.py day9_green_tiles_dean_filled_indexed.txt

# Then find rectangles with sampled validation:
# ./pypy day9_find_rectangle_from_tiles_sampled.py day9_green_tiles_dean_filled_indexed.txt

import sys
import os
import time
import common
import psutil
from datetime import datetime, timedelta

# Enable unicode output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

DEFAULT_MIN_AREA_THRESHOLD = 1_190_747_376  # Max area from previous runs that was not the right answer.
MIN_AREA_THRESHOLD = DEFAULT_MIN_AREA_THRESHOLD  # Will be set from command line
SAMPLE_INTERVAL = 50_000  # Check every 50_000th point

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

def load_corners_metadata(indexed_file):
    """Load just the bounding box metadata from corners file."""
    corners_file = indexed_file.rsplit('.', 1)[0] + '.corners'
    
    if not os.path.exists(corners_file):
        print(f"Error: Corners file '{corners_file}' not found.")
        print(f"Run: python day9_extract_corners.py {indexed_file}")
        sys.exit(1)
    
    with open(corners_file, 'r') as f:
        # Skip comment line
        f.readline()
        
        # Read bounding box
        bbox_line = f.readline().strip()
        min_x, max_x, min_y, max_y = map(int, bbox_line.split(','))
        bounding_box = (min_x, max_x, min_y, max_y)
    
    return corners_file, bounding_box

def stream_corners_batch(corners_file, start_pos, batch_size=50000):
    """Stream a batch of corners from file starting at position."""
    corners_set = set()  # Use set to deduplicate
    
    with open(corners_file, 'r') as f:
        f.seek(start_pos)
        
        count = 0
        while count < batch_size:
            line = f.readline()
            if not line:
                break
            
            # Skip metadata lines
            if line.startswith('#') or ',' not in line:
                continue
                
            parts = line.strip().split(',')
            if len(parts) == 2:
                corners_set.add((int(parts[0]), int(parts[1])))
                count += 1
        
        end_pos = f.tell()
    
    return list(corners_set), end_pos

def filter_corners_by_location(corners, bounding_box, min_area_threshold):
    """Filter corners that could potentially form rectangles >= min_area_threshold."""
    min_x, max_x, min_y, max_y = bounding_box
    
    # Calculate minimum dimensions needed
    min_dimension = int(min_area_threshold ** 0.5)
    
    filtered = []
    for x, y in corners:
        # Check if this corner could form a large enough rectangle
        max_width = max(x - min_x, max_x - x)
        max_height = max(y - min_y, max_y - y)
        
        max_possible_area = (max_width + 1) * (max_height + 1)
        
        if max_possible_area >= min_area_threshold:
            filtered.append((x, y))
    
    return filtered

def load_row_from_file(indexed_file, file_index, y):
    """Load a single row from file using the index."""
    if y not in file_index:
        return None
    
    with open(indexed_file, 'r') as f:
        f.seek(file_index[y])
        line = f.readline()
        
        # Handle empty or malformed lines
        if not line or ':' not in line:
            return None
        
        parts = line.strip().split(':', 1)
        if len(parts) != 2:
            return None
            
        y_str, x_str = parts
        return set(map(int, x_str.split(',')))

def check_rectangle_sampled(indexed_file, file_index, min_rx, max_rx, min_ry, max_ry, row_cache):
    """Check rectangle validity by sampling every SAMPLE_INTERVAL points."""
    # Calculate all points in rectangle
    points = []
    for y in range(min_ry, max_ry + 1):
        for x in range(min_rx, max_rx + 1):
            points.append((x, y))
    
    total_points = len(points)
    
    # Sample every SAMPLE_INTERVAL points
    for i in range(0, total_points, SAMPLE_INTERVAL):
        x, y = points[i]
        
        # Load row if not in cache
        if y not in row_cache:
            if len(row_cache) > 100:
                row_cache.clear()
            row_xs = load_row_from_file(indexed_file, file_index, y)
            if row_xs is None:
                return False
            row_cache[y] = row_xs
        else:
            row_xs = row_cache[y]
        
        # Check if point is green
        if x not in row_xs:
            return False
    
    return True

def find_largest_rectangle(indexed_file, file_index, corners_file, bounding_box, output_file=None):
    """Find largest rectangle by streaming corners from file in batches."""
    print(f"Finding rectangles using SAMPLED validation (every {SAMPLE_INTERVAL}th point)...")
    print("⚠ WARNING: This finds CANDIDATES only - full validation needed for actual answer!\n")
    
    # Open output file if specified
    outf = None
    if output_file:
        outf = open(output_file, 'w')
        outf.write(f"# Rectangle Candidates (Sampled Validation - Every {SAMPLE_INTERVAL}th point)\n")
        outf.write(f"# Format: area,min_x,min_y,max_x,max_y\n")
        outf.flush()
        print(f"Writing candidates to: {output_file}\n")
    
    min_x, max_x, min_y, max_y = bounding_box
    print(f"Bounding box: x=[{min_x}, {max_x}], y=[{min_y}, {max_y}]")
    
    # Get file size and estimate corner count
    file_size = os.path.getsize(corners_file)
    with open(corners_file, 'r') as f:
        f.readline()  # Skip comment
        f.readline()  # Skip bounding box
        data_start = f.tell()
    
    estimated_corners = (file_size - data_start) // 20  # Rough estimate
    print(f"Estimated corners: ~{estimated_corners:,}")
    
    # Process corners in batches
    BATCH_SIZE = 500000
    
    # Estimate total batches
    estimated_batches = (estimated_corners + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"Estimated batches: ~{estimated_batches}\n")
    
    max_area = 0
    max_rect = None
    checked = 0
    candidates_found = []
    start_time = time.time()
    last_update = start_time
    
    batch_num = 0
    
    # Cache for recently used rows
    row_cache = {}
    
    # First batch position (after metadata)
    pos_i = data_start
    
    print("Checking rectangles in batches...\n")
    
    while True:
        # Load batch i
        batch_i_raw, new_pos_i = stream_corners_batch(corners_file, pos_i, BATCH_SIZE)
        if not batch_i_raw:
            break
        
        # Filter corners by location
        batch_i = filter_corners_by_location(batch_i_raw, bounding_box, MIN_AREA_THRESHOLD)
        
        if not batch_i:
            pos_i = new_pos_i
            continue
        
        batch_num += 1
        
        # Display batch start info
        mem = psutil.virtual_memory()
        mem_avail_gb = mem.available / (1024**3)
        print(f"\nBatch {batch_num}/{estimated_batches}: {len(batch_i):,} corners (filtered from {len(batch_i_raw):,}) | Free RAM: {mem_avail_gb:.1f}GB")
        
        # Check pairs within this batch
        batch_pairs = len(batch_i) * (len(batch_i) - 1) // 2
        batch_evaluated = 0
        for idx1 in range(len(batch_i)):
            corner1 = batch_i[idx1]
            x1, y1 = corner1
            for idx2 in range(idx1 + 1, len(batch_i)):
                corner2 = batch_i[idx2]
                x2, y2 = corner2
                
                batch_evaluated += 1
                
                # Quick filters
                if x1 == x2 or y1 == y2:
                    continue
                
                # Calculate area
                area = abs(x2 - x1 + 1) * abs(y2 - y1 + 1)
                if area < MIN_AREA_THRESHOLD or area <= max_area:
                    continue
                
                checked += 1
                
                # Progress update every 50K evaluations
                if True: # batch_evaluated % 10 == 0:
                    current_time = time.time()
                    elapsed = current_time - start_time
                    batch_percent = (batch_evaluated / batch_pairs) * 100 if batch_pairs > 0 else 0
                    
                    mem = psutil.virtual_memory()
                    mem_avail_gb = mem.available / (1024**3)
                    mem_avail_mb = mem.available / (1024**2)
                    
                    if mem_avail_mb < 200:
                        print(f"\n\n⚠ Low memory warning: {mem_avail_mb:.0f}MB free (< 200MB)")
                        print("Terminating to prevent system instability...")
                        sys.exit(1)
                    
                    print(f"Batch {batch_num} (within) {batch_percent:.1f}% | Eval: {batch_evaluated:,}/{batch_pairs:,} | "
                          f"Candidates: {len(candidates_found)} | RAM: {mem_avail_gb:.1f}GB", 
                          end='\r', flush=True)
                    last_update = current_time
                
                # Check rectangle validity (SAMPLED)
                min_rx, max_rx = min(x1, x2), max(x1, x2)
                min_ry, max_ry = min(y1, y2), max(y1, y2)
                
                valid = check_rectangle_sampled(indexed_file, file_index, min_rx, max_rx, min_ry, max_ry, row_cache)
                
                if valid:
                    max_area = area
                    max_rect = (min_rx, min_ry, max_rx, max_ry)
                    candidates_found.append((area, max_rect))
                    print(f"\n✓ Candidate: {area:,} at ({min_rx},{min_ry})-({max_rx},{max_ry})")
                    if outf:
                        outf.write(f"{area},{min_rx},{min_ry},{max_rx},{max_ry}\n")
                        outf.flush()
        
        # Check pairs between batch i and all subsequent batches
        pos_j = new_pos_i
        batch_j_num = batch_num
        cross_batch_start_time = time.time()
        cross_batches_processed = 0
        
        print(f"  Cross-checking batch {batch_num} with subsequent batches...")
        
        while True:
            batch_j_raw, new_pos_j = stream_corners_batch(corners_file, pos_j, BATCH_SIZE)
            if not batch_j_raw:
                break
            
            # Filter batch j corners
            batch_j = filter_corners_by_location(batch_j_raw, bounding_box, MIN_AREA_THRESHOLD)
            
            if not batch_j:
                pos_j = new_pos_j
                continue
            
            batch_j_num += 1
            cross_batches_processed += 1
            cross_pairs = len(batch_i) * len(batch_j)
            cross_evaluated = 0
            
            # Show which subsequent batch we're checking
            cross_elapsed = time.time() - cross_batch_start_time
            cross_rate = cross_batches_processed / cross_elapsed if cross_elapsed > 0 else 0
            cross_eta_str = "?"
            if cross_rate > 0 and estimated_corners > 0:
                remaining_batches = max(0, (estimated_corners // BATCH_SIZE) - batch_j_num)
                cross_eta_sec = remaining_batches / cross_rate
                cross_eta_str = str(timedelta(seconds=int(cross_eta_sec)))
            
            print(f"  Checking batch {batch_num}×{batch_j_num} ({cross_batches_processed:,} cross-batches done, "
                  f"{cross_rate:.1f} batches/s, ETA: {cross_eta_str})")
            
            for idx1 in range(len(batch_i)):
                corner1 = batch_i[idx1]
                x1, y1 = corner1
                for idx2 in range(len(batch_j)):
                    corner2 = batch_j[idx2]
                    x2, y2 = corner2
                    
                    cross_evaluated += 1
                    
                    # Quick filters
                    if x1 == x2 or y1 == y2:
                        continue
                    
                    # Calculate area
                    area = abs(x2 - x1 + 1) * abs(y2 - y1 + 1)
                    if area < MIN_AREA_THRESHOLD or area <= max_area:
                        continue
                    
                    checked += 1
                    
                    # Progress update every 50K evaluations
                    if cross_evaluated % 50000 == 0:
                        current_time = time.time()
                        elapsed = current_time - start_time
                        cross_percent = (cross_evaluated / cross_pairs) * 100 if cross_pairs > 0 else 0
                        
                        mem = psutil.virtual_memory()
                        mem_avail_gb = mem.available / (1024**3)
                        mem_avail_mb = mem.available / (1024**2)
                        
                        if mem_avail_mb < 200:
                            print(f"\n\n⚠ Low memory warning: {mem_avail_mb:.0f}MB free (< 200MB)")
                            print("Terminating to prevent system instability...")
                            sys.exit(1)
                        
                        print(f"Batch {batch_num}×{batch_j_num} {cross_percent:.1f}% | Eval: {cross_evaluated:,}/{cross_pairs:,} | "
                              f"Candidates: {len(candidates_found)} | RAM: {mem_avail_gb:.1f}GB", 
                              end='\r', flush=True)
                        last_update = current_time
                    
                    # Check rectangle validity (SAMPLED)
                    min_rx, max_rx = min(x1, x2), max(x1, x2)
                    min_ry, max_ry = min(y1, y2), max(y1, y2)
                    
                    valid = check_rectangle_sampled(indexed_file, file_index, min_rx, max_rx, min_ry, max_ry, row_cache)
                    
                    if valid:
                        max_area = area
                        max_rect = (min_rx, min_ry, max_rx, max_ry)
                        candidates_found.append((area, max_rect))
                        print(f"\n✓ Candidate: {area:,} at ({min_rx},{min_ry})-({max_rx},{max_ry})")
                        if outf:
                            outf.write(f"{area},{min_rx},{min_ry},{max_rx},{max_ry}\n")
                            outf.flush()
            
            pos_j = new_pos_j
        
        # Move to next batch
        pos_i = new_pos_i
        
        # Progress update after completing batch
        current_time = time.time()
        elapsed = current_time - start_time
        rate = checked / elapsed if elapsed > 0 else 0
        
        percent = (batch_num / estimated_batches) * 100 if estimated_batches > 0 else 0
        eta_seconds = ((estimated_batches - batch_num) / batch_num) * elapsed if batch_num > 0 else 0
        end_time = datetime.now() + timedelta(seconds=eta_seconds)
        end_time_str = end_time.strftime("%I:%M%p").lstrip('0').lower()
        
        mem = psutil.virtual_memory()
        mem_avail_gb = mem.available / (1024**3)
        mem_avail_mb = mem.available / (1024**2)
        
        if mem_avail_mb < 200:
            print(f"\n⚠ Low memory warning: {mem_avail_mb:.0f}MB free (< 200MB)")
            print("Terminating to prevent system instability...")
            sys.exit(1)
        
        print(f"{percent:.1f}% | Batch {batch_num}/{estimated_batches} | Checked: {checked:,} | "
              f"Candidates: {len(candidates_found)} | Rate: {rate:,.0f} pairs/s | "
              f"Free RAM: {mem_avail_gb:.1f}GB | ETA: {end_time_str}")
        last_update = current_time
    
    elapsed = time.time() - start_time
    print(f"\n✓ Search complete in {elapsed:.1f}s")
    print(f"  Checked {checked:,} pairs")
    print(f"  Found {len(candidates_found)} candidates")
    
    # Close output file
    if outf:
        outf.close()
        print(f"  Candidates written to: {output_file}")
    
    return candidates_found

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
        sys.exit(1)
    
    print(f"Using indexed tiles file: {indexed_file}")
    print(f"Minimum area threshold: {MIN_AREA_THRESHOLD:,}")
    print(f"Sample interval: Every {SAMPLE_INTERVAL}th point\n")
    
    # Load pre-built file index
    file_index = load_file_index(indexed_file)
    
    # Load corners metadata (bounding box only)
    corners_file, bounding_box = load_corners_metadata(indexed_file)
    
    print(f"Corners file: {corners_file}")
    print(f"Bounding box: x=[{bounding_box[0]}, {bounding_box[1]}], y=[{bounding_box[2]}, {bounding_box[3]}]\n")
    
    # Generate output filename
    base_name = indexed_file.rsplit('.', 1)[0]
    output_file = f"{base_name}_candidates.txt"
    
    # Find candidates using sampled validation
    candidates = find_largest_rectangle(indexed_file, file_index, corners_file, bounding_box, output_file)
    
    if candidates:
        print(f"\n{'='*60}")
        print(f"FOUND {len(candidates)} CANDIDATE RECTANGLES:")
        print(f"{'='*60}")
        
        # Sort by area (descending)
        candidates.sort(reverse=True)
        
        for area, rect in candidates:
            print(f"  Area: {area:,} | Rectangle: ({rect[0]},{rect[1]}) to ({rect[2]},{rect[3]})")
        
        print(f"\n{'='*60}")
        print(f"LARGEST CANDIDATE: {candidates[0][0]:,}")
        print(f"Rectangle: ({candidates[0][1][0]},{candidates[0][1][1]}) to ({candidates[0][1][2]},{candidates[0][1][3]})")
        print(f"{'='*60}")
        print(f"\n⚠ IMPORTANT: These are CANDIDATES only!")
        print(f"Run full validation to confirm actual answer.")
        
        # Write summary to file
        with open(output_file, 'a') as f:
            f.write(f"\n# SUMMARY: Found {len(candidates)} candidates\n")
            f.write(f"# Largest: {candidates[0][0]}\n")
        
        common.multibeep()
    else:
        print("\nNo candidates found.")
