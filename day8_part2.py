import sys, os

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
    x1, y1, z1 = j1
    x2, y2, z2 = j2
    return ((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2) ** 0.5

class UnionFind:
    def __init__(self, elements):
        self.parent = {e: e for e in elements}
        self.count = len(elements)
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        self.parent[py] = px
        self.count -= 1
        return True

def find_last_connection(junctions):
    # Build all unique pairs and their distances
    pairs = []
    seen = set()
    for i, j1 in enumerate(junctions):
        for j2 in junctions[i+1:]:
            pair = tuple(sorted((j1, j2)))
            if pair in seen:
                continue
            seen.add(pair)
            d = calculate_distance(j1, j2)
            pairs.append((d, j1, j2))
    pairs.sort()  # shortest distance first

    uf = UnionFind(junctions)
    last_pair = None
    for d, j1, j2 in pairs:
        if uf.union(j1, j2):
            last_pair = (j1, j2)
            if uf.count == 1:
                break
    if last_pair:
        x1, _, _ = last_pair[0]
        x2, _, _ = last_pair[1]
        return x1 * x2
    return None

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
    result = find_last_connection(junctions)
    print(f"Day 8 Part 2 result: {result}")
