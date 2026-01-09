DEBUG=false

def read_file(file_path)
    coordinates = []
    File.open(file_path, "r") do |file|
        lines = File.readlines(file_path).map(&:chomp)
        coordinates = lines.map{|line| line.split(",").map{|s| s.to_i } }
    end
    return coordinates
end

def calc_area(coordinate1, coordinate2)
    width = (coordinate2[0] - coordinate1[0]).abs + 1
    height = (coordinate2[1] - coordinate1[1]).abs + 1
    return width * height
end

def find_largest_rectangle_area(coordinates)
    max_area = 0
    while !coordinates.empty? do 
        first_coordinate = coordinates.shift
        coordinates.each do |second_coordinate| 
            area = calc_area(first_coordinate, second_coordinate)
            puts "area: #{area} with coords: #{first_coordinate}, #{second_coordinate}" if DEBUG
            if area > max_area
                max_area = area
                puts "new max_area: #{max_area} with coords: #{first_coordinate}, #{second_coordinate}" if DEBUG
            end
        end
    end
    return max_area
end

if __FILE__ == $0
    filename = ARGV[0] || 'day9_input_gayle.txt'
    coordinates = read_file(filename)
    largest_rectangle = find_largest_rectangle_area(coordinates)
    puts "largest_rectangle: #{largest_rectangle}"
end