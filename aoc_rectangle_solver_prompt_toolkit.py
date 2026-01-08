from multiprocessing import Pool, cpu_count, Manager, current_process
import itertools
import time
import threading
import signal
import sys
from prompt_toolkit import Application
from prompt_toolkit.layout import Layout, HSplit, VSplit, Window
from prompt_toolkit.widgets import Frame, Box
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML

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

def generate_progress_display(progress_dict, max_area, title_info="", elapsed_time=0):
    """Generate formatted text display of progress."""
    from prompt_toolkit.formatted_text import FormattedText
    
    lines = []
    
    # Header
    lines.append(('bold underline', 'Rectangle Search Progress'))
    lines.append(('', '\n'))
    if title_info:
        lines.append(('ansicyan', title_info))
        lines.append(('', '\n'))
    # Add elapsed time
    lines.append(('ansiyellow', f"Running Time: {elapsed_time:.1f} seconds"))
    lines.append(('', '\n'))
    
    # Table header
    header = f"{'Worker':<20} {'Activity':<50} {'Progress':>25} {'Status':>55} {'Max Area':>12}"
    lines.append(('bold ansimagenta', header))
    lines.append(('', '\n'))
    lines.append(('', '─' * 165))
    lines.append(('', '\n'))
    
    # Worker rows
    for batch_id in sorted(progress_dict.keys()):
        info = progress_dict[batch_id]
        name = info.get('name', f'Batch-{batch_id}')[:20]
        processed = info.get('processed', 0)
        total = info.get('total', 1)
        max_area_worker = info.get('max_area', 0)
        done = info.get('done', False)
        checking_rect = info.get('checking_rect', '')
        activity = info.get('activity', 'Idle')[:50]
        
        percent = (processed / total) * 100 if total > 0 else 0
        progress_bar = '█' * int(percent // 5) + '░' * (20 - int(percent // 5))
        
        if done:
            status = "✓ Done"
        elif checking_rect:
            status = f"{processed}/{total} [{checking_rect}]"
        else:
            status = f"{processed}/{total}"
        
        row = f"{name:<20} {activity:<50} {progress_bar} {percent:>5.1f}% {status:>55} {max_area_worker:>12}"
        if done:
            lines.append(('ansigreen', row))
        else:
            lines.append(('', row))
        lines.append(('', '\n'))
    
    # Overall best
    lines.append(('', '─' * 165))
    lines.append(('', '\n'))
    overall = f"{'Overall Best':<20} {'':<50} {'':<25} {'':<55} {max_area:>12}"
    lines.append(('bold ansigreen', overall))
    
    return FormattedText(lines)

def find_largest_rectangle(coords, num_processes=None):
    if num_processes is None:
        num_processes = cpu_count()
    
    import os
    main_pid = os.getpid()
    
    # Get command line
    command_line = ' '.join(sys.argv)
    
    # Create a set of coord tuples for O(1) lookup
    coord_set = set(coords)
    
    # Generate all pairs
    pairs = [(i, j) for i in range(len(coords)) for j in range(i + 1, len(coords))]
    total = len(pairs)
    
    # Split pairs into batches for each process
    batch_size = max(1, total // num_processes)  # 1 batch per process
    
    # Create a manager for shared progress tracking and stop flag
    manager = Manager()
    progress_dict = manager.dict()
    stop_flag = manager.Value('i', 0)  # 0 = continue, 1 = stop
    
    batches = []
    for batch_id, i in enumerate(range(0, len(pairs), batch_size)):
        batch = pairs[i:i + batch_size]
        batches.append((batch, coords, coord_set, progress_dict, batch_id, stop_flag))
    
    # Create title info
    title_info = f"Command: {command_line} | Using {num_processes} processes | PID: {main_pid} | kill -9 {main_pid} (mingw64) | taskkill /F /PID {main_pid} (Windows) | Total pairs: {total:,} | Batches: {len(batches)}"
    
    # Track start time
    start_time = time.time()
    
    # Process batches in parallel
    max_area = 0
    max_rect = None
    completed = 0
    
    pool = Pool(processes=num_processes)
    
    # Start the work by creating the iterator
    result_iterator = pool.imap_unordered(check_rectangle_batch, batches)
    
    # Give workers a moment to start
    time.sleep(0.5)
    
    # Set up key bindings
    kb = KeyBindings()
    
    @kb.add('c-c')
    @kb.add('escape')
    def _(event):
        """Exit on Ctrl-C or ESC."""
        stop_flag.value = 1
        event.app.exit()
    
    # Create text control that updates
    text_control = FormattedTextControl(
        text=lambda: generate_progress_display(progress_dict, max_area, title_info, time.time() - start_time)
    )
    
    # Create layout
    root_container = HSplit([
        Window(content=text_control, wrap_lines=False)
    ])
    
    layout = Layout(root_container)
    
    # Create application
    app = Application(
        layout=layout,
        key_bindings=kb,
        full_screen=True,
        mouse_support=False
    )
    
    # Start background thread to process results
    processing_complete = threading.Event()
    
    def process_results():
        nonlocal max_area, max_rect, completed
        try:
            for result in result_iterator:
                if stop_flag.value == 1:
                    break
                area, rect = result
                if area > max_area:
                    max_area = area
                    max_rect = rect
                completed += 1
        except Exception as e:
            pass
        finally:
            processing_complete.set()
            time.sleep(0.5)  # Let final update render
            try:
                if app.is_running:
                    app.exit()
            except:
                pass  # App already exited
    
    # Background thread to refresh display
    def refresh_display():
        while not processing_complete.is_set():
            try:
                if app.is_running:
                    app.invalidate()
            except:
                pass
            time.sleep(5.0)
    
    result_thread = threading.Thread(target=process_results, daemon=True)
    result_thread.start()
    
    refresh_thread = threading.Thread(target=refresh_display, daemon=True)
    refresh_thread.start()
    
    try:
        # Run the application
        app.run()
    except KeyboardInterrupt:
        stop_flag.value = 1
        pool.terminate()
        pool.join()
        print("\nAll processes terminated.")
        sys.exit(1)
    except Exception as e:
        stop_flag.value = 1
        pool.terminate()
        pool.join()
        raise
    else:
        pool.close()
        pool.join()
    
    if stop_flag.value == 1:
        print("\nSearch stopped by user.")
    else:
        print("\n✓ Rectangle search complete!")
    if max_rect:
        print(f"Best rectangle: ({max_rect[0]},{max_rect[1]}) to ({max_rect[2]},{max_rect[3]})")
    return max_area

# Example usage:
if __name__ == "__main__":
    import sys
    import os
    
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        os.system('chcp 65001 >nul 2>&1')
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    
    try:
        with open("day9_input_dean.txt") as f:
            input_text = f.read()
        coords = parse_input(input_text)
        print(f"Number of vertices: {len(coords)}")
        result = find_largest_rectangle(coords)
        print(f"Largest rectangle area: {result}")
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        sys.exit(1)
