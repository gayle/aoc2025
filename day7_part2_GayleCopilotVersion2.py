import sys
import os
import time

# This version I asked Copilot to create from scratch based on the problem description.
start_time = time.time()
last_progress_time = start_time
timeline_count = 0

def print_progress():
    global timeline_count
    now = time.time()
    if now - last_progress_time > 2.0:
        rate = timeline_count / (now - start_time)
        print(f"{timeline_count:,} - {rate:,.0f} / sec", end="\r")
        globals()['last_progress_time'] = now

def parse_input(filename):
    with open(filename, 'r') as f:
        lines = [line.rstrip('\n') for line in f]
    return lines

def find_start(grid):
    for col, char in enumerate(grid[0]):
        if char == 'S':
            return col
    raise ValueError("No 'S' found in the first row")

def simulate_beams(grid, start_col):
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    
    def recurse(row, col):
        if row == rows:
            global timeline_count
            timeline_count += 1
            print_progress()
            # Reached the bottom, this is one timeline
            return 1
        
        # Check current position
        if grid[row][col] == '^':
            # Split: create two new timelines, left and right
            left_count = 0
            if col - 1 >= 0:
                left_count = recurse(row + 1, col - 1)
            right_count = 0
            if col + 1 < cols:
                right_count = recurse(row + 1, col + 1)
            return left_count + right_count
        else:
            # Continue downward
            return recurse(row + 1, col)
    
    # Start from row 1, col = start_col
    return recurse(1, start_col)

def main():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "day7_input_gayle.txt"
    
    if not os.path.exists(filename):
        print(f"File {filename} not found")
        sys.exit(1)
    
    grid = parse_input(filename)
    start_col = find_start(grid)
    result = simulate_beams(grid, start_col)
    print(f"Number of active timelines: {result}")

if __name__ == "__main__":
    main()