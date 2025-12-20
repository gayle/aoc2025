import sys, os

class Day3Part2:
    DEBUG = True

    @staticmethod
    def parse_input(input_filename):
        lines = open(input_filename).readlines()
        return lines
    
    @staticmethod
    def max_joltage(line):
        line = line.strip() # example: 811111111111119
        print("line: %s" % line) if Day3Part2.DEBUG else None
        joltage = '0' * 12 # max 12 digits
        for i, digit in enumerate(line):
            new_i = i
            print("new_i: %d, digit: %s" % (new_i, digit)) if Day3Part2.DEBUG else None
            joltage_non_zero_length = len(joltage.replace('0', ''))
            print("len(line)[%d] - 1 - new_i[%d] + joltage_non_zero_length[%d]: %d" % (len(line), new_i, joltage_non_zero_length, len(line) - 1 - new_i + joltage_non_zero_length)) if Day3Part2.DEBUG else None
            if len(line) - 1 - new_i + joltage_non_zero_length < len(joltage): # We can't replace any more existing digits
                joltage = joltage[0:i] + digit + joltage[joltage_non_zero_length+1:]
            else:
                if joltage_non_zero_length == 0:
                    joltage = digit + joltage[1:]
                else:
                    for j in range(joltage_non_zero_length + 1):
                        if j == len(joltage):
                            temp_joltage = joltage[0:j-1] + digit
                        else:
                            temp_joltage = joltage[0:j] + digit + '0' * (len(joltage) - j - 1)
                        print(f"i: {i}, j: {j}, digit: {digit}, joltage: {joltage}({len(joltage)}), temp_joltage: {temp_joltage}({len(temp_joltage)})") if Day3Part2.DEBUG else None
                        print(f"temp_joltage.count('0'): {temp_joltage.count('0')}, len(line) - i - 1: {len(line) - j - 1}") if Day3Part2.DEBUG else None
                        if temp_joltage.count('0') > len(line) - i - 1:
                            pass
                        elif temp_joltage > joltage:
                            print(f"temp_joltage {temp_joltage} is > than joltage {joltage}") if Day3Part2.DEBUG else None
                            joltage = temp_joltage
                            break
            print(f"joltage {joltage}({len(joltage)})\n") if Day3Part2.DEBUG else None
            if len(joltage) > 12:
                break

                #     print("in if") if Day3Part2.DEBUG else None
                #     temp_joltage = joltage[0:joltage_non_zero_length - 1] + digit
                # elif joltage_non_zero_length > 0:
                #     print("in elif") if Day3Part2.DEBUG else None
                #     print("joltage[0:joltage_non_zero_length]: %s, len: %d, joltage[joltage_non_zero_length + 1:]: %s, len: %d" % (
                #         joltage[0:joltage_non_zero_length], 
                #         len(joltage[0:joltage_non_zero_length]), 
                #         joltage[joltage_non_zero_length + 1:], 
                #         len(joltage[joltage_non_zero_length + 1:])
                #         )
                #     ) if Day3Part2.DEBUG else None
                #     print("joltage[0:joltage_non_zero_length - 1]: %s, len: %d, digit: %s, joltage[joltage_non_zero_length:]: %s, len: %d" % (
                #         joltage[0:joltage_non_zero_length - 1], 
                #         len(joltage[0:joltage_non_zero_length - 1]), 
                #         digit, 
                #         joltage[joltage_non_zero_length:], 
                #         len(joltage[joltage_non_zero_length:])
                #         )
                #     ) if Day3Part2.DEBUG else None
                #     temp_joltage = joltage[0:joltage_non_zero_length - 1] + digit + joltage[joltage_non_zero_length:]
                #     if int(temp_joltage) > int(joltage):
                #         print(f"temp_joltage {temp_joltage} is > than joltage {joltage}") if Day3Part2.DEBUG else None
                #         joltage = temp_joltage
                #     else:
                #         temp_joltage = joltage[0:joltage_non_zero_length] + digit + joltage[joltage_non_zero_length + 1:]
                #         if int(temp_joltage) > int(joltage):
                #             print(f"temp_joltage {temp_joltage} is > than joltage {joltage}") if Day3Part2.DEBUG else None
                #             joltage = temp_joltage
                # else: # joltage_non_zero_length == 0
                #     print("in else") if Day3Part2.DEBUG else None
                #     temp_joltage = digit + joltage[1:]
            #     print("joltage[0:joltage_non_zero_length]: %s" % joltage[0:joltage_non_zero_length]) if Day3Part2.DEBUG else None
            #     print("i: %d, new_i: %d, joltage_non_zero_length: %d, temp_joltage: %s(len %d), joltage: %s(len %d)" % (i, new_i, joltage_non_zero_length, temp_joltage, len(temp_joltage), joltage, len(joltage))) if Day3Part2.DEBUG else None
            #     if int(temp_joltage) > int(joltage):
            #         joltage = temp_joltage
            # print("joltage: %s, length: %d\n" % (joltage, len(joltage))) if Day3Part2.DEBUG else None

        print("returning joltage: %s" % joltage) if Day3Part2.DEBUG else None
        return int(joltage)
    
    @staticmethod
    def total_output_joltage(input_filename):
        lines = Day3Part2.parse_input(input_filename)
        total = 0
        for line in lines:
            total += Day3Part2.max_joltage(line)
            input("Press Enter...") if Day3Part2.DEBUG else None
        return total
    
if __name__ == "__main__":
    # If no filename is provided, try common input filenames before failing.
    print(sys.argv)
    if len(sys.argv) == 2:
        input_filename = sys.argv[1]
    else:
        # prefer Gayle's input if present, otherwise Dean's input
        if os.path.exists("day3_input_gayle.txt"):
            input_filename = "day3_input_gayle.txt"
        elif os.path.exists("day3_input_dean.txt"):
            input_filename = "day3_input_dean.txt"
        else:
            print(f"Usage: python {sys.argv[0]} <input_filename>")
            sys.exit(1)
    result = Day3Part2.total_output_joltage(input_filename)
    print(f"Day 3 Part 2 result: {result}")
