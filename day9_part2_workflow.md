# The current workflow is

## Preprocessing (run each once)

    ./pypy day9_fill_green_tiles.py day9_input_dean.txt 
    → creates indexed tiles file
    
    ./pypy day9_fill_green_tiles_build_index.py day9_green_tiles_dean_filled_indexed.txt
     → creates .idx file

    ./pypy day9_extract_corners.py day9_green_tiles_dean_filled_indexed.txt
     → creates .corners file

## Rectangle search (can rerun with different parameters)

    ./pypy day9_find_rectangle_from_tiles.py day9_green_tiles_dean_filled_indexed.txt
    
    Single-process, PyPy optimized.

Note: There is a multiprocess version, but it runs out of memory. According to copilot: The multiprocessing version won't work with your dataset - it requires loading all corners into memory before processing can begin. With your massive corner file, you'll always hit the memory limit during the loading phase.

    python day9_find_rectangle_from_tiles_mp.py day9_green_tiles_dean_filled_indexed.txt

    The multiprocessing version uses CPython since it handles multiprocessing better than PyPy.
