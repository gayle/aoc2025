// Unit tests for day7_part2.c
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include "day7_part2.c"

void test_parse_input() {
    const char* input = "S..^\n..^S\n";
    char lines[2][MAX_LINE_LENGTH];
    int num_lines = 0;
    parse_input(input, lines, &num_lines);
    assert(num_lines == 2);
    assert(strcmp(lines[0], "S..^") == 0);
    assert(strcmp(lines[1], "..^S") == 0);
    printf("test_parse_input passed\n");
}

void test_find_item_indices() {
    const char* line = "S..^..^S";
    int items[MAX_LINE_LENGTH];
    int num_items = 0;
    find_item_indices(line, '^', items, &num_items);
    assert(num_items == 2);
    assert(items[0] == 3);
    assert(items[1] == 6);
    printf("test_find_item_indices passed\n");
}

int main() {
    test_parse_input();
    test_find_item_indices();
    // Add more tests as needed
    printf("All tests passed!\n");
    return 0;
}
