import subprocess
import time

try:
    monitoring_sub = subprocess.Popen(["python3", "src/monitoring.py"])
    handlers_sub = subprocess.Popen(["python3", "src/handlers.py"])
    
    while True:
        time.sleep(1)
finally:
    monitoring_sub.kill()
    handlers_sub.kill()
    print(f'\n\nApp`s {monitoring_sub.pid} and {handlers_sub.pid} stopped!\n')
