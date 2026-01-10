module Day9Common
  def self.read_file(file_path)
    coordinates = []
    File.open(file_path, "r") do |file|
      lines = File.readlines(file_path).map(&:chomp)
      coordinates = lines.map { |line| line.split(",").map { |s| s.to_i } }
    end
    return coordinates
  end
end