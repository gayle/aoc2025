require_relative 'day9_common'

DEBUG=false

def figure_out_green_coordinates(red_coordinates)
    green_coordinates = []
    return green_coordinates
end

if __FILE__ == $0
    filename = ARGV[0] || 'day9_input_gayle.txt'
    red_coordinates = Day9Common.read_file(filename)
    green_coordinates = figure_out_green_coordinates(red_coordinates)
    # largest_rectangle = find_largest_rectangle_area(red_coordinates)
    # puts "largest_rectangle: #{largest_rectangle}"
end