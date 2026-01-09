require 'pry'
require 'rspec'
require 'rspec/given'
require 'tempfile'
require_relative "../day9_part2"

describe "day9_part2" do
    context "figure_out_green_coordinates" do
        Given!(:red_coordinates) { [[7, 1], [11, 1], [11, 7], [9, 7], [9, 5], [2, 5], [2, 3], [7, 3]] }
        Given!(:expected_green_coordinates) { [
            [8, 1], [9, 1], [10, 1],
            [7, 2], [8, 2], [9, 2], [10, 2], [11, 2],
            [2, 3], [3, 3], [4, 3], [5, 3], [7, 3], [8, 3], [9, 3], [10, 3], [11, 3], [12, 3],
            [2, 4], [3, 4], [4, 4], [5, 4], [6, 4], [7, 4], [8, 4], [9, 4], [10, 4], [11, 4], [12, 4], [13, 4],
            [2, 5], [3, 5], [4, 5], [5, 5], [6, 5], [7, 5], [9, 5], [10, 5], [11, 5], [12, 5],
            [9, 6], [10, 6], [11, 6],
            [9, 7], [11, 7]
        ] } 
        When(:green_coordinates) { figure_out_green_coordinates([])}
        Then{ expect(green_coordinates).to eq(expected_green_coordinates) }
    end
end
