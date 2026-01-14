from multiprocessing import Pool, cpu_count, Manager, current_process
import itertools
import time
import threading
import signal
import sys
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

DEFAULT_MIN_AREA_THRESHOLD = 1_190_747_376  # Max area from previous runs that was not the right answer.
MIN_AREA_THRESHOLD = DEFAULT_MIN_AREA_THRESHOLD  # Will be set from command line
SAMPLE_INTERVAL = 50_000  # Check every 50_000th point

def parse_input(input_text):
    coords = []
    for line in input_text.splitlines():
        line = line.strip()
        if not line:
            continue
        x, y = map(int, line.split(','))
        coords.append((x, y))
    return coords

def compute_edge_set(coords):
    """Pre-compute all points on polygon edges for O(1) lookup."""
    edge_points = set()
    n = len(coords)
    for i in range(n):
        x1, y1 = coords[i]
        x2, y2 = coords[(i + 1) % n]
        if x1 == x2:  # Vertical line
            for y in range(min(y1, y2), max(y1, y2) + 1):
                edge_points.add((x1, y))
        elif y1 == y2:  # Horizontal line
            for x in range(min(x1, x2), max(x1, x2) + 1):
                edge_points.add((x, y1))
    return edge_points

def is_on_polygon_edge(x, y, coords):
    """Check if point (x, y) is on the polygon edge."""
    n = len(coords)
    for i in range(n):
        x1, y1 = coords[i]
        x2, y2 = coords[(i + 1) % n]
        # Check if point is on line segment
        if x1 == x2:  # Vertical line
            if x == x1 and min(y1, y2) <= y <= max(y1, y2):
                return True
        elif y1 == y2:  # Horizontal line
            if y == y1 and min(x1, x2) <= x <= max(x1, x2):
                return True
    return False

def is_inside_polygon(x, y, coords):
    """Check if point (x, y) is inside polygon using ray casting."""
    n = len(coords)
    inside = False
    for i in range(n):
        x1, y1 = coords[i]
        x2, y2 = coords[(i + 1) % n]
        if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
            inside = not inside
    return inside

def is_green_tile(x, y, coords, edge_set=None, cache=None):
    """Check if a tile is green (on edge or inside polygon)."""
    if cache is not None and (x, y) in cache:
        return cache[(x, y)]
    
    # Use edge_set for O(1) lookup if available, otherwise fall back to O(n) check
    if edge_set is not None:
        result = (x, y) in edge_set or is_inside_polygon(x, y, coords)
    else:
        result = is_on_polygon_edge(x, y, coords) or is_inside_polygon(x, y, coords)
    
    if cache is not None:
        cache[(x, y)] = result
    
    return result

def check_rectangle_batch(args):
    """Check a batch of rectangle pairs."""
    pairs, coords, coord_set, bbox, progress_dict, batch_id, stop_flag = args
    min_x, max_x, min_y, max_y = bbox
    max_area = 0
    max_rect = None
    
    # Compute edge set locally to avoid copying large data on Windows
    edge_set = compute_edge_set(coords)
    
    # Create local cache for this worker - use size-limited cache to avoid memory issues
    # For very large rectangles, we'll disable caching to prevent OOM
    tile_cache = {}
    CACHE_SIZE_LIMIT = 10_000_000  # Max 10M cached points (~160MB with 16 bytes per entry)
    
    # Progress tracking for this worker
    import os
    worker_pid = os.getpid()
    total_pairs = len(pairs)
    processed = 0
    last_update_time = time.time()
    process_name = f"{current_process().name}-PID{worker_pid}"
    
    # Initial progress update - show worker immediately
    progress_dict[batch_id] = {
        'processed': 0,
        'total': total_pairs,
        'max_area': 0,
        'name': process_name,
        'activity': 'Starting...'
    }
    
    for i, j in pairs:
        # Check if we should stop
        if stop_flag.value == 1:
            progress_dict[batch_id] = {
                'processed': processed,
                'total': total_pairs,
                'max_area': max_area,
                'name': process_name,
                'stopped': True,
                'activity': 'Stopped by user'
            }
            return max_area, max_rect
        
        processed += 1
        
        # Update progress every 10 seconds to minimize Manager overhead (major bottleneck)
        current_time = time.time()
        if current_time - last_update_time >= 10.0:
            progress_dict[batch_id] = {
                'processed': processed,
                'total': total_pairs,
                'max_area': max_area,
                'name': process_name,
                'activity': 'Checking pairs'
            }
            last_update_time = current_time
        x1, y1 = coords[i]
        x2, y2 = coords[j]
        
        # Skip if corners don't form a proper rectangle
        if x1 == x2 or y1 == y2:
            continue
        
        min_rx, max_rx = min(x1, x2), max(x1, x2)
        min_ry, max_ry = min(y1, y2), max(y1, y2)
        
        # Skip if rectangle extends outside polygon bounding box
        if min_rx < min_x or max_rx > max_x or min_ry < min_y or max_ry > max_y:
            continue
        
        area = (max_rx - min_rx + 1) * (max_ry - min_ry + 1)
      
        if area < MIN_AREA_THRESHOLD:
            continue
        
        # Skip if this rectangle is smaller than current max
        if area <= max_area:
            continue
        
        # Update: checking corners
        progress_dict[batch_id] = {
            'processed': processed,
            'total': total_pairs,
            'max_area': max_area,
            'name': process_name,
            'activity': f'Checking corners: {area:,} area'
        }
        
        # Batch check both corners (fast rejection)
        corners_to_check = [(min_rx, max_ry), (max_rx, min_ry)]
        valid_corners = True
        for cx, cy in corners_to_check:
            if (cx, cy) not in coord_set and not is_green_tile(cx, cy, coords, edge_set, tile_cache):
                valid_corners = False
                break
        
        if not valid_corners:
            continue
        
        # Check all points in rectangle
        total_points = (max_rx - min_rx + 1) * (max_ry - min_ry + 1)
        points_checked = 0
        valid = True
        rect_start_time = time.time()  # Track how long this rectangle takes
        rect_timeout = 300  # 5 minutes max per rectangle
        
        # For very large rectangles, disable caching and do sparse sampling first
        use_cache = total_points < 10_000_000  # Only cache for rectangles < 10M points
        if not use_cache and len(tile_cache) > 0:
            tile_cache.clear()  # Free memory from previous cached rectangle
        
        # Sparse sampling for huge rectangles (check every Nth point first)
        if total_points > 50_000_000:  # 50M+ points
            sample_step = max(2, int((total_points ** 0.5) / 10))  # Adaptive sampling (larger steps = faster)
            progress_dict[batch_id] = {
                'processed': processed,
                'total': total_pairs,
                'max_area': max_area,
                'name': process_name,
                'activity': f'Sampling: {area:,} area (step={sample_step})'
            }
            for x in range(min_rx, max_rx + 1, sample_step):
                for y in range(min_ry, max_ry + 1, sample_step):
                    if (x, y) == (x1, y1) or (x, y) == (x2, y2):
                        continue
                    if (x, y) not in coord_set and not is_green_tile(x, y, coords, edge_set, None):
                        valid = False
                        break
                if not valid:
                    break
            if not valid:
                progress_dict[batch_id] = {
                    'processed': processed,
                    'total': total_pairs,
                    'max_area': max_area,
                    'name': process_name,
                    'activity': f'❌ Failed sampling: {area:,} area'
                }
                continue  # Skip exhaustive check
        
        for x in range(min_rx, max_rx + 1):
            # Check stop flag at the start of each row
            if stop_flag.value == 1:
                progress_dict[batch_id] = {
                    'processed': processed,
                    'total': total_pairs,
                    'max_area': max_area,
                    'name': process_name,
                    'stopped': True,
                    'activity': 'Stopped by user'
                }
                return max_area, max_rect
            
            for y in range(min_ry, max_ry + 1):
                # Skip the corners we're using
                if (x, y) == (x1, y1) or (x, y) == (x2, y2):
                    continue
                
                points_checked += 1
                
                # Update progress for large rectangles (every 100 points or every 0.5s)
                if total_points > 1000:
                    current_time = time.time()
                    if points_checked % 100 == 0 or current_time - last_update_time >= 0.5:
                        rect_progress = (points_checked / total_points) * 100
                        rect_elapsed = current_time - rect_start_time
                        progress_dict[batch_id] = {
                            'processed': processed,
                            'total': total_pairs,
                            'max_area': max_area,
                            'name': process_name,
                            'checking_rect': f"{area:,} area, {rect_progress:.0f}% checked, {rect_elapsed:.1f}s",
                            'activity': f'Validating: ({min_rx},{min_ry})-({max_rx},{max_ry})'
                        }
                        last_update_time = current_time
                
                # Use cache only for smaller rectangles to avoid OOM
                cache_to_use = tile_cache if use_cache else None
                if (x, y) not in coord_set and not is_green_tile(x, y, coords, edge_set, cache_to_use):
                    valid = False
                    break
            if not valid:
                break
        
        # Prevent cache from growing unbounded - clear if it exceeds limit
        if use_cache and len(tile_cache) > CACHE_SIZE_LIMIT:
            tile_cache.clear()
            progress_dict[batch_id] = {
                'processed': processed,
                'total': total_pairs,
                'max_area': max_area,
                'name': process_name,
                'activity': f'🧹 Cleared cache ({CACHE_SIZE_LIMIT:,} limit)'
            }
        
        if valid:
            rect_elapsed = time.time() - rect_start_time
            if area > max_area:
                max_area = area
                max_rect = (min_rx, min_ry, max_rx, max_ry)
                # Log when we find a new best (only for large rectangles)
                if total_points > 1000:
                    progress_dict[batch_id] = {
                        'processed': processed,
                        'total': total_pairs,
                        'max_area': max_area,
                        'name': process_name,
                        'activity': f'✓ New best! {area:,} in {rect_elapsed:.1f}s'
                    }
    
    # Final progress update
    progress_dict[batch_id] = {
        'processed': total_pairs,
        'total': total_pairs,
        'max_area': max_area,
        'name': process_name,
        'done': True,
        'activity': f"Completed at {time.strftime('%m/%d/%Y %H:%M:%S')}"
    }
    return max_area, max_rect

def generate_progress_table(progress_dict, max_area, title_info="", elapsed_time=0):
    """Generate a rich table showing progress of all workers."""
    import psutil
    from datetime import datetime, timedelta
    
    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = int(elapsed_time % 60)
    time_str = f"\n[yellow]Running Time: {hours:02d}:{minutes:02d}:{seconds:02d}[/yellow]"
    
    # Calculate overall progress
    total_processed = sum(info.get('processed', 0) for info in progress_dict.values())
    total_work = sum(info.get('total', 0) for info in progress_dict.values())
    overall_percent = (total_processed / total_work) * 100 if total_work > 0 else 0
    
    # Calculate rate
    rate = total_processed / elapsed_time if elapsed_time > 0 else 0
    
    # Get memory info
    mem = psutil.virtual_memory()
    mem_avail_gb = mem.available / (1024**3)
    
    # Calculate ETA
    remaining = total_work - total_processed
    eta_seconds = remaining / rate if rate > 0 else 0
    if eta_seconds > 0 and eta_seconds < 86400 * 7:  # Less than a week
        end_time = datetime.now() + timedelta(seconds=eta_seconds)
        eta_str = end_time.strftime("%m/%d/%Y %H:%M:%S")
    else:
        eta_str = "?"
    
    # Overall status line
    overall_status = f"\n[bold cyan]Overall: {overall_percent:.1f}% | Processed: {total_processed:,}/{total_work:,} | Rate: {rate:,.0f} pairs/s | Free RAM: {mem_avail_gb:.1f}GB | ETA: {eta_str}[/bold cyan]"
    
    optimizations = "\n[green]Optimizations: Per-worker edge cache | Tile cache | 4x batches | Sorted by area | Bounding box[/green]"
    table_title = f"Rectangle Search Progress{time_str}{overall_status}{optimizations}" if title_info else f"Rectangle Search Progress{time_str}{overall_status}{optimizations}"
    table = Table(title=table_title, show_header=True, header_style="bold magenta")
    table.add_column("Worker", style="cyan", width=20)
    table.add_column("Activity", style="white", width=50)
    table.add_column("Progress", justify="right", style="green")
    table.add_column("Status", justify="right", width=55)
    table.add_column("Max Area", justify="right", style="yellow")
    
    for batch_id in sorted(progress_dict.keys()):
        info = progress_dict[batch_id]
        name = info.get('name', f'Batch-{batch_id}')
        processed = info.get('processed', 0)
        total = info.get('total', 1)
        max_area_worker = info.get('max_area', 0)
        done = info.get('done', False)
        checking_rect = info.get('checking_rect', '')
        activity = info.get('activity', 'Idle')
        
        percent = (processed / total) * 100 if total > 0 else 0
        progress_bar = '█' * int(percent // 5) + '░' * (20 - int(percent // 5))
        
        if done:
            status = "✓ Done"
        elif checking_rect:
            status = f"{processed}/{total} [{checking_rect}]"
        else:
            status = f"{processed}/{total}"
        
        table.add_row(
            name,
            activity,
            f"{progress_bar} {percent:.1f}%",
            status,
            str(max_area_worker)
        )
    
    table.add_row(
        "[bold]Overall Best[/bold]",
        "",
        "",
        "",
        f"[bold]{max_area}[/bold]",
        style="bold green"
    )
    
    return table

def find_largest_rectangle(coords, num_processes=None, output_file="day9_part2_progress.txt"):
    if num_processes is None:
        num_processes = min(40, cpu_count())  # Limit to 40 workers max to avoid resource exhaustion
    
    console = Console()
    import os
    main_pid = os.getpid()
    
    # Get command line
    command_line = ' '.join(sys.argv)
    
    # Get Python implementation info
    python_impl = sys.implementation.name
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    # Get start time
    from datetime import datetime
    start_datetime = datetime.now()
    start_datetime_str = start_datetime.strftime("%m/%d/%Y %H:%M:%S")
    
    console.print(f"[bold]Command: {command_line}[/bold]")
    console.print(f"[bold magenta]Python: {python_impl} {python_version}[/bold magenta]")
    console.print(f"[bold yellow]Started: {start_datetime_str}[/bold yellow]")
    console.print(f"[bold green]Using {num_processes} processes[/bold green]")
    console.print(f"[bold cyan]Main Process PID: {main_pid}[/bold cyan]")
    console.print(f"[bold cyan]To kill (mingw64): kill -9 {main_pid}[/bold cyan]")
    console.print(f"[bold cyan]Or (Windows): taskkill /F /PID {main_pid}[/bold cyan]")
    console.print(f"[bold yellow]Press Ctrl-C or ESC to stop[/bold yellow]")
    console.print(f"[bold yellow]Progress log: {output_file}[/bold yellow]\n")
    
    # Open output file and write header
    with open(output_file, 'w') as f:
        f.write(f"Day 9 Part 2 - Largest Rectangle Search Progress\n")
        f.write(f"Started: {start_datetime_str}\n")
        f.write(f"Command: {command_line}\n")
        f.write(f"Python: {python_impl} {python_version}\n")
        f.write(f"Processes: {num_processes}\n")
        f.write(f"{'='*80}\n\n")
    
    # Pre-compute polygon bounding box for early rejection
    min_x = min(x for x, y in coords)
    max_x = max(x for x, y in coords)
    min_y = min(y for x, y in coords)
    max_y = max(y for x, y in coords)
    bbox = (min_x, max_x, min_y, max_y)
    console.print(f"[bold]Polygon bounds: x=[{min_x}, {max_x}], y=[{min_y}, {max_y}][/bold]")
    
    # Create a set of coord tuples for O(1) lookup
    coord_set = set(coords)
    
    # Note: Edge set will be computed per-worker to avoid copying large data on Windows
    
    # Generate all pairs
    pairs = [(i, j) for i in range(len(coords)) for j in range(i + 1, len(coords))]
    
    # Sort pairs by potential area (descending) - check largest rectangles first
    console.print(f"[bold yellow]Sorting {len(pairs):,} pairs by potential area...[/bold yellow]")
    def pair_area(pair):
        i, j = pair
        x1, y1 = coords[i]
        x2, y2 = coords[j]
        return abs(x2 - x1 + 1) * abs(y2 - y1 + 1)
    
    pairs.sort(key=pair_area, reverse=True)
    total = len(pairs)
    console.print(f"[bold]Total rectangle pairs to check: {total:,}[/bold]")
    
    # Split pairs into batches - create 4x more batches than processes for better load balancing
    num_batches = num_processes * 2
    batch_size = max(1, total // num_batches)
    
    # Create a manager for shared progress tracking and stop flag
    manager = Manager()
    progress_dict = manager.dict()
    stop_flag = manager.Value('i', 0)  # 0 = continue, 1 = stop
    
    # Set up ESC key listener in a background thread
    def key_listener():
        import msvcrt
        while stop_flag.value == 0:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'\x1b':  # ESC key
                    console.print("\n[bold red]ESC pressed - stopping all workers...[/bold red]")
                    stop_flag.value = 1
                    break
            time.sleep(0.1)
    
    listener_thread = threading.Thread(target=key_listener, daemon=True)
    listener_thread.start()
    
    batches = []
    for batch_id, i in enumerate(range(0, len(pairs), batch_size)):
        batch = pairs[i:i + batch_size]
        batches.append((batch, coords, coord_set, bbox, progress_dict, batch_id, stop_flag))
    
    console.print(f"[bold]Split into {len(batches)} batches[/bold]\n")
    
    # Create title info for table
    title_info = f"Command: {command_line} | PID: {main_pid} | kill -9 {main_pid} (mingw64) | taskkill /F /PID {main_pid} (Windows) | Ctrl-C/ESC to stop"
    
    # Track start time
    start_time = time.time()
    
    # Process batches in parallel
    max_area = 0
    max_rect = None
    completed = 0
    
    # Use maxtasksperchild=1 to ensure each batch gets a fresh process
    pool = Pool(processes=num_processes, maxtasksperchild=1)
    
    # Start the work by creating the iterator (this starts workers processing)
    result_iterator = pool.imap_unordered(check_rectangle_batch, batches)
    
    # Give workers a moment to start and update their status
    time.sleep(0.5)
    
    try:
        with Live(console=console, refresh_per_second=4, screen=False) as live:
            # Start background thread to continuously update display
            display_running = threading.Event()
            display_running.set()
            
            def update_display_loop():
                while display_running.is_set():
                    live.update(generate_progress_table(progress_dict, max_area, title_info, time.time() - start_time))
                    time.sleep(0.25)
            
            display_thread = threading.Thread(target=update_display_loop, daemon=True)
            display_thread.start()
            
            # Process results as they come in
            for result in result_iterator:
                if stop_flag.value == 1:
                    break
                area, rect = result
                if area > max_area:
                    max_area = area
                    max_rect = rect
                    # Write progress to file
                    elapsed = time.time() - start_time
                    hours = int(elapsed // 3600)
                    minutes = int((elapsed % 3600) // 60)
                    seconds = int(elapsed % 60)
                    timestamp = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                    with open(output_file, 'a') as f:
                        f.write(f"[{timestamp}] Elapsed: {hours:02d}:{minutes:02d}:{seconds:02d} | New max area: {max_area:,}\n")
                        if max_rect:
                            f.write(f"  Rectangle: ({max_rect[0]},{max_rect[1]}) to ({max_rect[2]},{max_rect[3]})\n")
                        f.flush()
                completed += 1
            
            # Stop display thread
            display_running.clear()
            display_thread.join(timeout=1)
    except KeyboardInterrupt:
        console.print("\n[bold red]Ctrl-C detected. Stopping all worker processes...[/bold red]")
        stop_flag.value = 1
        time.sleep(0.5)  # Give workers a moment to see the stop flag
        pool.terminate()
        pool.join()
        console.print("[bold red]All processes terminated.[/bold red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Error occurred: {e}[/bold red]")
        stop_flag.value = 1
        pool.terminate()
        pool.join()
        raise
    else:
        pool.close()
        pool.join()
    
    if stop_flag.value == 1:
        console.print("\n[bold yellow]Search stopped by user.[/bold yellow]")
    else:
        console.print("\n[bold green]✓ Rectangle search complete![/bold green]")
    if max_rect:
        console.print(f"[bold yellow]Best rectangle: ({max_rect[0]},{max_rect[1]}) to ({max_rect[2]},{max_rect[3]})[/bold yellow]")
    
    # Write final result to file
    end_datetime = datetime.now()
    end_datetime_str = end_datetime.strftime("%m/%d/%Y %H:%M:%S")
    total_elapsed = time.time() - start_time
    hours = int(total_elapsed // 3600)
    minutes = int((total_elapsed % 3600) // 60)
    seconds = int(total_elapsed % 60)
    with open(output_file, 'a') as f:
        f.write(f"\n{'='*80}\n")
        f.write(f"Finished: {end_datetime_str}\n")
        f.write(f"Total time: {hours:02d}:{minutes:02d}:{seconds:02d}\n")
        f.write(f"Final max area: {max_area:,}\n")
        if max_rect:
            f.write(f"Final rectangle: ({max_rect[0]},{max_rect[1]}) to ({max_rect[2]},{max_rect[3]})\n")
    
    return max_area

# Example usage:
if __name__ == "__main__":
    import sys
    import os
    
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        os.system('chcp 65001 >nul 2>&1')  # Set console code page to UTF-8
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    
    # If no filename is provided, try common input filenames before failing.
    if len(sys.argv) == 2:
        input_filename = sys.argv[1]
    else:
        # Prefer Gayle's input if present, otherwise Dean's input
        if os.path.exists("day9_input_gayle.txt"):
            input_filename = "day9_input_gayle.txt"
        elif os.path.exists("day9_input_dean.txt"):
            input_filename = "day9_input_dean.txt"
        else:
            print(f"Usage: python {sys.argv[0]} <input_filename>")
            sys.exit(1)
    
    try:
        with open(input_filename) as f:
            input_text = f.read()
        coords = parse_input(input_text)
        console = Console()
        console.print(f"[bold]Number of vertices: {len(coords)}[/bold]")
        result = find_largest_rectangle(coords)
        console.print(f"[bold green]Day 9 Part 2 result: {result}[/bold green]")
    except KeyboardInterrupt:
        console = Console()
        console.print("\n[bold red]Interrupted by user.[/bold red]")
        sys.exit(1)
