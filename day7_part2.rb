require 'time'

$start_time = Time.now
$last_progress_time = $start_time
$timeline_count = 0

def print_progress
  now = Time.now
  if now - $last_progress_time > 2.0
    rate = $timeline_count / (now - $start_time)
    print "#{$timeline_count.to_s.reverse.gsub(/(\d{3})(?=\d)/, '\\1,').reverse} - #{rate.round}/sec\r"
    $last_progress_time = now
  end
end

def parse_input(filename)
  File.readlines(filename).map(&:chomp)
end

def find_start(grid)
  grid[0].each_char.with_index do |char, col|
    return col if char == 'S'
  end
  raise "No 'S' found in the first row"
end

def simulate_beams(grid, start_col)
  rows = grid.size
  cols = grid[0].size

  recurse = lambda do |row, col|
    if row == rows
      $timeline_count += 1
      print_progress
      return 1
    end

    if col < 0 || col >= cols
      return 0
    end

    if grid[row][col] == '^'
      left_count = col - 1 >= 0 ? recurse.call(row + 1, col - 1) : 0
      right_count = col + 1 < cols ? recurse.call(row + 1, col + 1) : 0
      return left_count + right_count
    else
      return recurse.call(row + 1, col)
    end
  end

  return recurse.call(1, start_col)
end

def main
  filename = ARGV[0] || "day7_input_gayle.txt"
  unless File.exist?(filename)
    puts "File #{filename} not found"
    exit 1
  end

  grid = parse_input(filename)
  start_col = find_start(grid)
  result = simulate_beams(grid, start_col)
  puts "\nNumber of active timelines: #{result}"
end

main if __FILE__ == $0