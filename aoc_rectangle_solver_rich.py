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

def parse_input(input_text):
    coords = []
    for line in input_text.splitlines():
        line = line.strip()
        if not line:
            continue
        x, y = map(int, line.split(','))
        coords.append((x, y))
    return coords

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

def is_green_tile(x, y, coords, cache=None):
    """Check if a tile is green (on edge or inside polygon)."""
    if cache is not None and (x, y) in cache:
        return cache[(x, y)]
    
    result = is_on_polygon_edge(x, y, coords) or is_inside_polygon(x, y, coords)
    
    if cache is not None:
        cache[(x, y)] = result
    
    return result

def check_rectangle_batch(args):
    """Check a batch of rectangle pairs."""
    pairs, coords, coord_set, progress_dict, batch_id, stop_flag = args
    max_area = 0
    max_rect = None
    
    # Progress tracking for this worker
    total_pairs = len(pairs)
    processed = 0
    last_update_time = time.time()
    process_name = current_process().name
    
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
        
        # Update progress every second
        current_time = time.time()
        if current_time - last_update_time >= 1.0:
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
        
        area = (max_rx - min_rx + 1) * (max_ry - min_ry + 1)
        
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
        
        # Check the other two corners first (fast rejection)
        if (min_rx, max_ry) not in coord_set and not is_green_tile(min_rx, max_ry, coords):
            continue
        if (max_rx, min_ry) not in coord_set and not is_green_tile(max_rx, min_ry, coords):
            continue
        
        # Check all points in rectangle
        total_points = (max_rx - min_rx + 1) * (max_ry - min_ry + 1)
        points_checked = 0
        valid = True
        
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
                        progress_dict[batch_id] = {
                            'processed': processed,
                            'total': total_pairs,
                            'max_area': max_area,
                            'name': process_name,
                            'checking_rect': f"{area:,} area, {rect_progress:.0f}% checked",
                            'activity': f'Validating: {area:,} area'
                        }
                        last_update_time = current_time
                
                if (x, y) not in coord_set and not is_green_tile(x, y, coords):
                    valid = False
                    break
            if not valid:
                break
        
        if valid:
            if area > max_area:
                max_area = area
                max_rect = (min_rx, min_ry, max_rx, max_ry)
    
    # Final progress update
    progress_dict[batch_id] = {
        'processed': total_pairs,
        'total': total_pairs,
        'max_area': max_area,
        'name': process_name,
        'done': True,
        'activity': 'Completed'
    }
    return max_area, max_rect

def generate_progress_table(progress_dict, max_area, title_info="", elapsed_time=0):
    """Generate a rich table showing progress of all workers."""
    time_str = f"\n[yellow]Running Time: {elapsed_time:.1f} seconds[/yellow]"
    table_title = f"Rectangle Search Progress\n{title_info}{time_str}" if title_info else f"Rectangle Search Progress{time_str}"
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

def find_largest_rectangle(coords, num_processes=None):
    if num_processes is None:
        num_processes = cpu_count()
    
    console = Console()
    import os
    main_pid = os.getpid()
    
    # Get command line
    command_line = ' '.join(sys.argv)
    
    console.print(f"[bold]Command: {command_line}[/bold]")
    console.print(f"[bold green]Using {num_processes} processes[/bold green]")
    console.print(f"[bold cyan]Main Process PID: {main_pid}[/bold cyan]")
    console.print(f"[bold cyan]To kill (mingw64): kill -9 {main_pid}[/bold cyan]")
    console.print(f"[bold cyan]Or (Windows): taskkill /F /PID {main_pid}[/bold cyan]")
    console.print(f"[bold yellow]Press Ctrl-C or ESC to stop[/bold yellow]\n")
    
    # Create a set of coord tuples for O(1) lookup
    coord_set = set(coords)
    
    # Generate all pairs
    pairs = [(i, j) for i in range(len(coords)) for j in range(i + 1, len(coords))]
    total = len(pairs)
    console.print(f"[bold]Total rectangle pairs to check: {total:,}[/bold]")
    
    # Split pairs into batches for each process
    batch_size = max(1, total // num_processes)  # 1 batch per process
    
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
        batches.append((batch, coords, coord_set, progress_dict, batch_id, stop_flag))
    
    console.print(f"[bold]Split into {len(batches)} batches[/bold]\n")
    
    # Create title info for table
    title_info = f"Command: {command_line} | PID: {main_pid} | kill -9 {main_pid} (mingw64) | taskkill /F /PID {main_pid} (Windows) | Ctrl-C/ESC to stop"
    
    # Track start time
    start_time = time.time()
    
    # Process batches in parallel
    max_area = 0
    max_rect = None
    completed = 0
    
    pool = Pool(processes=num_processes)
    
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
    
    try:
        with open("day9_input_dean.txt") as f:
            input_text = f.read()
        coords = parse_input(input_text)
        console = Console()
        console.print(f"[bold]Number of vertices: {len(coords)}[/bold]")
        result = find_largest_rectangle(coords)
        console.print(f"[bold green]Largest rectangle area: {result}[/bold green]")
    except KeyboardInterrupt:
        console = Console()
        console.print("\n[bold red]Interrupted by user.[/bold red]")
        sys.exit(1)

