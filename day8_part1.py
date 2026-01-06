import sys, os, heapq

DEBUG = True

def parse_input(input_text):
    junctions = []
    for line in input_text.splitlines():
        x, y, z = line.strip().split(',')
        x, y, z = int(x), int(y), int(z)
        junctions.append((x, y, z))
    return junctions

def calculate_distance(j1, j2):
    # Calculate straight-line distance between two points in 3D space.
    x1, y1, z1 = j1
    x2, y2, z2 = j2
    return ((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2) ** 0.5

def closest_points(junctions, limit=1000):
    points = []
    seen = set()
    for j1 in junctions:
        for j2 in junctions:
            if j1 != j2: 
                # Also need to skip if already connected.
                pair = tuple(sorted((j1, j2)))
                if pair in seen:
                    continue
                seen.add(pair)            

                d = calculate_distance(j1, j2)
                heapq.heappush(points, (-d, (j1, j2))) # Use negative distance so the largest one is always at the front.
                if len(points) > limit:
                    heapq.heappop(points)  # Remove the farthest set of points.

    sorted_points = sorted([(-d, pts) for d, pts in points]) # Sort the list by distance (smallest first).
    if DEBUG:
        print(f"sorted_points:")
        for p in sorted_points:
            print(p)
    
    return [pts for d, pts in sorted_points] # Return just return the points, not the distance.

def calculate_result(junctions):
    # Get list of closest junction box pairs.
    closest = closest_points(junctions)

    # Connect pairs of junction boxes that are as close together as possible according to straight-line distance.
        
    # Update list of circuits.
    
    # The next two junction boxes are 431,825,988 and 425,690,689. Because these two junction boxes were already in the same circuit, nothing happens!

    # Connect together the 1000 pairs of junction boxes which are closest together.
    
    # Afterward, what do you get if you multiply together the sizes of the three largest circuits?
        
    return 0

if __name__ == "__main__":
    # If no filename is provided, try common input filenames before failing.
    if len(sys.argv) == 2:
        input_filename = sys.argv[1]
    else:
        # prefer Gayle's input if present, otherwise Dean's input
        if os.path.exists("day7_input_gayle.txt"):
            input_filename = "day7_input_gayle.txt"
        elif os.path.exists("day7_input_dean.txt"):
            input_filename = "day7_input_dean.txt"
        else:
            print(f"Usage: python {sys.argv[0]} <input_filename>")
            sys.exit(1)
  
    input_text = open(input_filename).read()
    junctions = parse_input(input_text)     
    result = calculate_result(junctions)
    print(f"Day 8 Part 1 result: {result}")

