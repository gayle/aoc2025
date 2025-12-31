// C conversion of day7_part2.py.

// In Developer Powershell for VS 2019:
// cl day7_part2.c; .\day7_part2.exe day7_input_dean.txt

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

void format_with_commas(long n, char *out, size_t out_size);
void parse_input(const char* input_text, char lines[][MAX_LINE_LENGTH], int* num_lines);
void find_item_indices(const char* line, char item, int* items, int* num_items);
void print_progress(unsigned long long count);
long iterate(int* all_beams, int** all_splitters, int n, long count, int num_lines);
unsigned long long iterate_tachyon_beam(char lines[][MAX_LINE_LENGTH], int num_lines);

// Helper to format long with commas
void format_with_commas(long n, char* out, size_t out_size) {
    char buf[32];
    snprintf(buf, sizeof(buf), "%ld", n);
    int len = strlen(buf);
    int commas = (len - 1) / 3;
    int out_idx = 0, buf_idx = 0;
    int first_group = len % 3;
    if (first_group == 0) first_group = 3;
    for (int i = 0; i < len; ++i) {
        if (i > 0 && (i - first_group) % 3 == 0) {
            if (out_idx < out_size - 1) out[out_idx++] = ',';
        }
        if (out_idx < out_size - 1) out[out_idx++] = buf[i];
    }
    out[out_idx] = '\0';
}

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
    // Print progress every 2 seconds: count, elapsed time, and rate, with commas (portable)
    double now = (double)clock() / CLOCKS_PER_SEC;
    if (start_time == 0) {
        start_time = now;
        last_progress_time = now;
    }
    double elapsed = now - start_time;
    if (now - last_progress_time > 2.0) {
        double rate = (elapsed > 0) ? (count / elapsed) : 0.0;
        char count_str[32], elapsed_str[32], rate_str[32];
        format_with_commas(count, count_str, sizeof(count_str));
        format_with_commas((long)elapsed, elapsed_str, sizeof(elapsed_str));
        format_with_commas((long)rate, rate_str, sizeof(rate_str));
        printf("%s splits in %s secs: %s / sec\r", count_str, elapsed_str, rate_str);
        fflush(stdout);
        last_progress_time = now;
    }
}

long iterate(int* all_beams, int** all_splitters, int n, long count, int num_lines) {
    // In-place backtracking version (no array copies)
    if (count % 1000000 == 0) {
        print_progress(count);
    }
    if (n == num_lines) {
        return count;
    }
    int prev_beam_idx = all_beams[n-1];
    int* splitters = all_splitters[n];
    int num_splitters = 0;
    while (num_splitters < MAX_LINE_LENGTH && splitters[num_splitters] != -1) num_splitters++;

    if (num_splitters > 0) {
        int no_splitter = 1;
        for (int i = 0; i < num_splitters; ++i) {
            int splitter = splitters[i];
            if (splitter == prev_beam_idx) {
                no_splitter = 0;
                // propagate left (same timeline)
                int old_val = all_beams[n];
                all_beams[n] = splitter - 1;
                count = iterate(all_beams, all_splitters, n+1, count, num_lines);
                // propagate right (new timeline, count + 1)
                all_beams[n] = splitter + 1;
                count = iterate(all_beams, all_splitters, n+1, count+1, num_lines);
                all_beams[n] = old_val; // backtrack
            }
        }
        if (no_splitter) {
            if (prev_beam_idx == -1) {
                return count;
            }
            int old_val = all_beams[n];
            all_beams[n] = prev_beam_idx;
            count = iterate(all_beams, all_splitters, n+1, count, num_lines);
            all_beams[n] = old_val; // backtrack
        }
    } else {
        if (prev_beam_idx == -1) {
            return count;
        }
        int old_val = all_beams[n];
        all_beams[n] = prev_beam_idx;
        count = iterate(all_beams, all_splitters, n+1, count, num_lines);
        all_beams[n] = old_val; // backtrack
    }
    return count;
}

unsigned long long iterate_tachyon_beam(char lines[][MAX_LINE_LENGTH], int num_lines) {
    // Find all splitters for each line
    int* all_splitters[MAX_LINES];
    int num_splitters[MAX_LINES];
    for (int i = 0; i < num_lines; ++i) {
        all_splitters[i] = (int*)malloc(MAX_LINE_LENGTH * sizeof(int));
        find_item_indices(lines[i], '^', all_splitters[i], &num_splitters[i]);
        // Initialize unused elements to -1
        for (int j = num_splitters[i]; j < MAX_LINE_LENGTH; ++j) {
            all_splitters[i][j] = -1;
        }
    }

    // Find the start index 'S' in the first line
    int start = -1;
    for (int i = 0; lines[0][i] != '\0'; ++i) {
        if (lines[0][i] == 'S') {
            start = i;
            break;
        }
    }
    if (start == -1) {
        for (int i = 0; i < num_lines; ++i) free(all_splitters[i]);
        return 0;
    }

    // Prepare all_beams array
    int all_beams[MAX_LINES];
    all_beams[0] = 0;
    all_beams[1] = start;
    for (int i = 2; i < num_lines; ++i) all_beams[i] = 0;

    long result = iterate(all_beams, all_splitters, 2, 1, num_lines);

    for (int i = 0; i < num_lines; ++i) free(all_splitters[i]);
    return result;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        printf("Usage: %s <input_filename>\n", argv[0]);
        return 1;
    }

    // Read the contents of the input file
    FILE* f = fopen(argv[1], "rb");
    if (!f) {
        printf("Could not open file: %s\n", argv[1]);
        return 1;
    }
    fseek(f, 0, SEEK_END);
    long fsize = ftell(f);
    fseek(f, 0, SEEK_SET);
    char* input_text = (char*)malloc(fsize + 1);
    if (!input_text) {
        printf("Memory allocation failed.\n");
        fclose(f);
        return 1;
    }
    fread(input_text, 1, fsize, f);
    input_text[fsize] = '\0';
    fclose(f);

    // Parse input into lines
    char lines[MAX_LINES][MAX_LINE_LENGTH];
    int num_lines = 0;
    parse_input(input_text, lines, &num_lines);
    printf("Read %d lines from %s\n", num_lines, argv[1]);

    // Call iterate_tachyon_beam and print the result
    unsigned long long result = iterate_tachyon_beam(lines, num_lines);
    printf("\nDay 7 Part 2 result: %llu\n", result);

    free(input_text);
    return 0;
}
