"""Extract corner coordinates from indexed tiles file for efficient reuse."""

# Usage: ./pypy day9_extract_corners.py day9_green_tiles_dean_filled_indexed.txt
# Creates: day9_green_tiles_dean_filled_indexed.corners

import sys
import os
import time
import psutil

def extract_corners_to_file(indexed_file):
    """Extract corner coordinates and save to .corners file with bounding box metadata."""
    corners_file = indexed_file.rsplit('.', 1)[0] + '.corners'
    
    print(f"Extracting corners from {indexed_file}...")
    print(f"Output: {corners_file}")
    start_time = time.time()
    
    file_size = os.path.getsize(indexed_file)
    
    # First pass: write all corners to temp file (no deduplication to save memory)
    temp_file = corners_file + '.tmp'
    row_count = 0
    corner_count = 0
    min_x = float('inf')
    max_x = float('-inf')
    min_y = float('inf')
    max_y = float('-inf')
    
    print("Pass 1: Writing corners to temp file (no deduplication)...")
    with open(indexed_file, 'r') as f_in, open(temp_file, 'w') as f_out:
        while True:
            line = f_in.readline()
            if not line:
                break
            
            row_count += 1
            if row_count % 1_000 == 0:
                file_pos = f_in.tell()
                percent = (file_pos / file_size) * 100 if file_size > 0 else 0
                
                # Get available memory
                mem = psutil.virtual_memory()
                mem_avail_gb = mem.available / (1024**3)
                mem_avail_mb = mem.available / (1024**2)
                
                # Check if running out of memory
                if mem_avail_mb < 500:
                    print(f"\n\n⚠ Low memory warning: {mem_avail_mb:.0f}MB free (< 500MB)")
                    print("Terminating to prevent system instability...")
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                    sys.exit(1)
                
                print(f"  {percent:.1f}% | Row {row_count:,} | Corners written: {corner_count:,} | Free RAM: {mem_avail_gb:.1f}GB", 
                      end='\r', flush=True)
            
            y_str, x_str = line.strip().split(':', 1)
            y = int(y_str)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
            
            # Write all x coordinates for this row (duplicates OK - saves memory)
            for x in map(int, x_str.split(',')):
                f_out.write(f"{x},{y}\n")
                corner_count += 1
                min_x = min(min_x, x)
                max_x = max(max_x, x)
    
    print(f"\n  Pass 1 complete: {corner_count:,} corners written")
    print(f"  Bounding box: x=[{min_x},{max_x}], y=[{min_y},{max_y}]")
    
    print(f"\nPass 2: Writing final file with metadata...")
    # Second pass: write final file with bounding box metadata at top
    with open(temp_file, 'r') as f_in, open(corners_file, 'w') as f_out:
        # Write metadata header
        f_out.write(f"# min_x,max_x,min_y,max_y\n")
        f_out.write(f"{min_x},{max_x},{min_y},{max_y}\n")
        
        # Copy corners
        line_count = 0
        for line in f_in:
            f_out.write(line)
            line_count += 1
            if line_count % 100_000 == 0:
                # Check memory while writing
                mem = psutil.virtual_memory()
                mem_avail_mb = mem.available / (1024**2)
                if mem_avail_mb < 500:
                    print(f"\n⚠ Low memory warning: {mem_avail_mb:.0f}MB free (< 500MB)")
                    print("Terminating to prevent system instability...")
                    os.remove(temp_file)
                    if os.path.exists(corners_file):
                        os.remove(corners_file)
                    sys.exit(1)
                
                mem_avail_gb = mem.available / (1024**3)
                print(f"  Wrote {line_count:,} corners | Free RAM: {mem_avail_gb:.1f}GB", end='\r', flush=True)
    
    # Clean up temp file
    os.remove(temp_file)
    
    elapsed = time.time() - start_time
    file_size_mb = os.path.getsize(corners_file) / (1024**2)
    
    print(f"\n✓ Extracted {corner_count:,} corners in {elapsed:.1f}s")
    print(f"  Bounding box: x=[{min_x}, {max_x}], y=[{min_y}, {max_y}]")
    print(f"  File size: {file_size_mb:.2f} MB")
    print(f"  Corners file: {corners_file}")
    
    return corners_file

if __name__ == "__main__":
    # Print Python implementation and command line
    print(f"Python: {sys.executable}")
    print(f"Command: {' '.join(sys.argv)}")
    print()
    
    if len(sys.argv) < 2:
        print("Usage: python day9_extract_corners.py <indexed_tiles_file>")
        print("Example: python day9_extract_corners.py day9_green_tiles_dean_filled_indexed.txt")
        sys.exit(1)
    
    indexed_file = sys.argv[1]
    
    if not os.path.exists(indexed_file):
        print(f"Error: File '{indexed_file}' not found.")
        sys.exit(1)
    
    extract_corners_to_file(indexed_file)
