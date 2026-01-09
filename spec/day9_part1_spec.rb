require 'pry'
require 'rspec'
require 'rspec/given'
require 'tempfile'
require_relative "../day9_part1"

describe "day9_part1" do
    context "read_file" do
        Given!(:tempfile) { Tempfile.create("test_day9_input.txt") }
        Given{ tempfile.write(<<~CSV
                    7,1
                    11,1
                    11,7
                    9,7
                    9,5
                    2,5
                    2,3
                    7,3
                CSV
            )
            tempfile.close
        }
        When{ @coordinates = read_file(tempfile.path) }
        Then{ expect(@coordinates[0]).to eq([7, 1]) }
    end

    context "calc_area" do
        When(:area) { calc_area([7, 1], [11, 7]) }
        Then{ expect(area).to eq(35) }
    end

    context "find_largest_rectangle_area" do
        Given!(:coordinates) { [[7, 1], [11, 1], [11, 7], [9, 7], [9, 5], [2, 5], [2, 3], [7, 3]] }
        When{ @area = find_largest_rectangle_area(coordinates) }
        Then{ expect(@area).to eq(50) } 
    end

end
