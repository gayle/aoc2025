import sys, os

DEBUG = False

def parse_input(input_text):
    junctions = []
    for line in input_text.splitlines():
        x, y, z = line.strip().split(',')
        x, y, z = int(x), int(y), int(z)
        junctions.append((x, y, z))
    return junctions

def calculate_result(junctions):
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

