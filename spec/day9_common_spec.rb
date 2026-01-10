require 'pry'
require 'rspec'
require 'rspec/given'
require 'tempfile'
require_relative "../day9_common"

describe "day9_common" do
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
        When(:coordinates) { Day9Common.read_file(tempfile.path) }
        Then{ expect(coordinates[0]).to eq([7, 1]) }
    end
end
