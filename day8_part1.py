import sys, os, heapq

DEBUG = False

def parse_input(input_text):
    try:
        junctions = []
        for line in input_text.splitlines():
            x, y, z = line.strip().split(',')
            x, y, z = int(x), int(y), int(z)
            junctions.append((x, y, z))
        return junctions
    except ValueError:
        print(f"Error parsing line: {line}")

def calculate_distance(j1, j2):
    # Calculate straight-line distance between two points in 3D space.
    x1, y1, z1 = j1
    x2, y2, z2 = j2
    return ((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2) ** 0.5

def closest_junctions(junctions, limit=1000):
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

def connect_circuits(closest_junctions, full_junctions):
    circuits = []
    for j1, j2 in closest_junctions:
        # Check if j1 and j2 are already connected in any circuit.
        circuit1 = None
        circuit2 = None
        for circuit in circuits:
            if j1 in circuit:
                circuit1 = circuit
            if j2 in circuit:
                circuit2 = circuit

        if DEBUG:
            print(f"Connecting {j1} <-> {j2}")
            print(f"  circuit1: {circuit1}")
            print(f"  circuit2: {circuit2}")
                
        if circuit1 is None and circuit2 is None:
            # Neither junction box is in a circuit, create a new one.
            print(f"  Creating new circuit for {j1} and {j2}") if DEBUG else None
            circuits.append(set([j1, j2]))
        elif circuit1 is not None and circuit2 is None:
            # Only j1 is in a circuit, add j2 to it.
            print(f"  Adding {j2} to existing circuit for {j1}") if DEBUG else None
            circuit1.add(j2)
        elif circuit1 is None and circuit2 is not None:
            # Only j2 is in a circuit, add j1 to it.
            print(f"  Adding {j1} to existing circuit for {j2}") if DEBUG else None
            circuit2.add(j1)
        elif circuit1 is not circuit2:
            # Both junction boxes are in different circuits, merge them.
            print(f"  Merging circuits for {j1} and {j2}") if DEBUG else None
            circuit1.update(circuit2)
            circuits.remove(circuit2)
        else:
            # If both junction boxes are already in the same circuit, do nothing.
            print(f"  {j1} and {j2} are already connected in the same circuit.") if DEBUG else None
        if DEBUG:
            print(f"  New circuits:")
            for c in circuits:
                print(f"    {c}")

    # Find all junctions that were not in any closest pair
    paired_junctions = set()
    for j1, j2 in closest_junctions:
        paired_junctions.add(j1)
        paired_junctions.add(j2)
    singletons = set(full_junctions) - paired_junctions
    for singleton in singletons:
        print(f"  Adding singleton junction box {singleton} as its own circuit.") if DEBUG else None
        circuits.append(set([singleton]))

    if DEBUG:
        print(f"[connect_circuits] Final circuits:")
        for c in circuits:
            print(f"    {c}")

    circuit_lengths = sorted([len(circuit) for circuit in circuits], reverse=True) # sort with largest first
    if DEBUG:
        print(f"[connect_circuits] After sorting: {circuit_lengths}")
    
    return circuit_lengths

def calculate_result(junctions):
    # Get list of closest junction box pairs.
    closest = closest_junctions(junctions)
    if DEBUG:
        print(f"[calculate_result] Closest junction box pairs (total {len(closest)}):")
        for j1, j2 in closest:
            print(f"  {j1} <-> {j2}")

    # Connect together the 1000 pairs of junction boxes which are closest together.
    # Afterward, what do you get if you multiply together the sizes of the three largest circuits?
    circuit_lengths = connect_circuits(closest, junctions)
    if DEBUG:
        print(f"[calculate_result] circuits: {circuit_lengths}")
    return circuit_lengths[0] * circuit_lengths[1] * circuit_lengths[2]

if __name__ == "__main__":
    # If no filename is provided, try common input filenames before failing.
    if len(sys.argv) == 2:
        input_filename = sys.argv[1]
    else:
        # prefer Gayle's input if present, otherwise Dean's input
        if os.path.exists("day8_input_gayle.txt"):
            input_filename = "day8_input_gayle.txt"
        elif os.path.exists("day8_input_dean.txt"):
            input_filename = "day8_input_dean.txt"
        else:
            print(f"Usage: python {sys.argv[0]} <input_filename>")
            sys.exit(1)
  
    input_text = open(input_filename).read()
    junctions = parse_input(input_text)     
    result = calculate_result(junctions)
    print(f"Day 8 Part 1 result: {result}")

