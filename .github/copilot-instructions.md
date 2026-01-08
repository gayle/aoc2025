# Advent of Code 2025 - AI Agent Instructions

## Project Overview
Collaborative Advent of Code 2025 solutions (Gayle's repo with dstautberg as contributor). Each puzzle has separate solutions for two participants (dean and gayle), with shared test suites.

## File Structure & Naming
- **Solutions**: `dayN_part1.py`, `dayN_part2.py` (N = 1-25)
- **Input files**: `dayN_input_dean.txt`, `dayN_input_gayle.txt`
- **Tests**: `test_dayN_part1.py`, `test_dayN_part2.py`
- **Shared utilities**: `aoc_rectangle_solver.py` (multiprocessing helper for geometry problems)

## Code Patterns

### Solution Structure
Each solution file follows this pattern from [day1_part1.py](day1_part1.py):
- Static class with problem-specific methods
- Main entry point with `if __name__ == "__main__":`
- Accepts input filename as `sys.argv[1]`
- Prints result as `f"Day{N} Part{M} result: {result}"`

### Graceful Input Handling (newer pattern)
Later solutions like [day9_part1.py](day9_part1.py#L24-L36) auto-detect input files when no argument provided:
```python
if len(sys.argv) == 2:
    input_filename = sys.argv[1]
else:
    # Prefer Gayle's input if present, otherwise Dean's
    if os.path.exists("day9_input_gayle.txt"):
        input_filename = "day9_input_gayle.txt"
    elif os.path.exists("day9_input_dean.txt"):
        input_filename = "day9_input_dean.txt"
```
Use this pattern for new solutions.

### Test Conventions
Tests use `pytest` with these patterns:
- Import functions/classes directly: `from dayN_partM import *`
- Use `tempfile.NamedTemporaryFile` for testing file I/O
- Include problem description as comments (see [test_day9_part1.py](test_day9_part1.py#L5-L20))
- Use `textwrap.dedent()` for multi-line test inputs

## Running Code

**Execute solutions** from workspace root:
```bash
python dayN_partM.py dayN_input_dean.txt
```

**Run all tests**:
```bash
pytest
```

## Performance Optimization
For computationally expensive problems:
1. **Python + caching**: See [day7_part2.py](day7_part2.py#L15-L46) recursive approach with cache dict
2. **C reimplementation**: [day7_part2.c](day7_part2.c) shows C conversion pattern (compile with `cl day7_part2.c`)
3. **Multiprocessing**: [aoc_rectangle_solver.py](aoc_rectangle_solver.py) demonstrates batched parallel processing with `multiprocessing.Pool`

## Development Workflow
- Solutions run from workspace root (don't change CWD)
- Test changes with `pytest` before committing
- Debug with `ipdb` (in requirements.txt)
- Both contributors' input files should produce correct results
