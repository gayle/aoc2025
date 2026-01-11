"""Build index file mapping y coordinates to file offsets for efficient row lookup."""

# Usage: ./pypy day9_fill_green_tiles_build_index.py day9_green_tiles_dean_filled_indexed.txt
# Creates: day9_green_tiles_dean_filled_indexed.idx

import sys
import os
import time

def build_index_file(indexed_file):
    """Build index file mapping y -> file offset."""
    index_file = indexed_file.rsplit('.', 1)[0] + '.idx'
    
    print(f"Building index from {indexed_file}...")
    print(f"Output: {index_file}")
    start_time = time.time()
    
    file_size = os.path.getsize(indexed_file)
    row_count = 0
    
    with open(indexed_file, 'r') as f_in, open(index_file, 'w') as f_out:
        while True:
            offset = f_in.tell()
            line = f_in.readline()
            if not line:
                break
            
            row_count += 1
            if row_count % 1_000 == 0:
                percent = (offset / file_size) * 100 if file_size > 0 else 0
                print(f"  {percent:.1f}% | Indexed {row_count:,} rows...", end='\r', flush=True)
            
            # Extract y coordinate
            y_str = line.split(':', 1)[0]
            
            # Write y:offset to index file
            f_out.write(f"{y_str}:{offset}\n")
    
    elapsed = time.time() - start_time
    index_size = os.path.getsize(index_file)
    index_size_mb = index_size / (1024**2)
    
    print(f"\n✓ Indexed {row_count:,} rows in {elapsed:.1f}s")
    print(f"  Index file size: {index_size_mb:.2f} MB")
    print(f"  Index file: {index_file}")
    
    return index_file

if __name__ == "__main__":
    # Print Python implementation and command line
    print(f"Python: {sys.executable}")
    print(f"Command: {' '.join(sys.argv)}")
    print()
    if len(sys.argv) < 2:
        print("Usage: python day9_fill_green_tiles_build_index.py <indexed_tiles_file>")
        print("Example: python day9_fill_green_tiles_build_index.py day9_green_tiles_dean_filled_indexed.txt")
        sys.exit(1)
    
    indexed_file = sys.argv[1]
    
    if not os.path.exists(indexed_file):
        print(f"Error: File '{indexed_file}' not found.")
        sys.exit(1)
    
    build_index_file(indexed_file)
