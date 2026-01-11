import time

def multibeep(n=3):
    for _ in range(n):
        print('\a', end='', flush=True)
        time.sleep(0.2)
    