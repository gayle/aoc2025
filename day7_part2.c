// C conversion of day7_part2.py.

// In Developer Powershell for VS 2019:
// > cl day7_part2.c
// > day7_part2.exe day7_input_dean.txt

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

// Full data is 142x142
#define MAX_LINES 150
#define MAX_LINE_LENGTH 150

// Globals for progress
int DEBUG = 0;
double start_time = 0;
double last_progress_time = 0;

void parse_input(const char* input_text, char lines[][MAX_LINE_LENGTH], int* num_lines);
void find_item_indices(const char* line, char item, int* items, int* num_items);
void print_progress(long count);
long iterate(int* all_beams, int** all_splitters, int n, long count, int num_lines);
long iterate_tachyon_beam(char lines[][MAX_LINE_LENGTH], int num_lines);

void parse_input(const char* input_text, char lines[][MAX_LINE_LENGTH], int* num_lines) {
    // Split input_text into lines, store in lines array, set num_lines
    int line_idx = 0, char_idx = 0;
    const char* p = input_text;
    while (*p) {
        if (*p == '\n' || *p == '\r') {
            if (char_idx > 0) {
                lines[line_idx][char_idx] = '\0';
                line_idx++;
                char_idx = 0;
            }
            // Handle \r\n or \n\r
            if ((*p == '\r' && *(p+1) == '\n') || (*p == '\n' && *(p+1) == '\r')) {
                p++;
            }
        } else {
            if (char_idx < MAX_LINE_LENGTH-1) {
                lines[line_idx][char_idx++] = *p;
            }
        }
        p++;
    }
    if (char_idx > 0) {
        lines[line_idx][char_idx] = '\0';
        line_idx++;
    }
    *num_lines = line_idx;
}

void find_item_indices(const char* line, char item, int* items, int* num_items) {
    // Find all indices of 'item' in 'line', store in 'items', set 'num_items'
    int idx = 0;
    int found = 0;
    while (line[idx] != '\0') {
        if (line[idx] == item) {
            items[found++] = idx;
        }
        idx++;
    }
    *num_items = found;
}

void print_progress(long count) {
    // Print progress every 2 seconds: count, elapsed time, and rate
    double now = (double)clock() / CLOCKS_PER_SEC;
    if (start_time == 0) {
        start_time = now;
        last_progress_time = now;
    }
    double elapsed = now - start_time;
    if (now - last_progress_time > 2.0) {
        double rate = (elapsed > 0) ? (count / elapsed) : 0.0;
        printf("%ld splits in %.0f secs: %.0f / sec\r", count, elapsed, rate);
        fflush(stdout);
        last_progress_time = now;
    }
}

long iterate(int* all_beams, int** all_splitters, int n, long count, int num_lines) {
    // Stub: recursive logic
    return 0;
}

long iterate_tachyon_beam(char lines[][MAX_LINE_LENGTH], int num_lines) {
    // Stub: optimized entry point
    return 0;
}

int main(int argc, char* argv[]) {
    // Print out the contents of argv
    printf("argc = %d\n", argc);
    for (int i = 0; i < argc; ++i) {
        printf("argv[%d] = %s\n", i, argv[i]);
    }
    return 0;
}
