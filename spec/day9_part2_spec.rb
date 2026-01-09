require 'pry'
require 'rspec'
require 'rspec/given'
require 'tempfile'
require_relative "../day9_part2"

describe "day9_part2" do
    context "figure_out_green_coordinates" do
        When(:green) { figure_out_green_coordinates([])}
        Then{ expect(green).to eq([]) }
    end
end
