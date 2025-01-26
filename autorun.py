from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import sys
import subprocess
import time

class ReloadHandler(FileSystemEventHandler):
    def __init__(self, script_name):
        self.script_name = script_name
        self.process = self.start_script()

    def start_script(self):
        return subprocess.Popen([sys.executable, self.script_name])

    def restart_script(self):
        print("Changes detected. Restarting script...")
        self.process.terminate()
        self.process = self.start_script()

    def on_modified(self, event):
        if event.src_path.endswith("AiCore.py"): 
            self.restart_script()

if __name__ == "__main__":
    script_name = "AiCore.py"  
    event_handler = ReloadHandler(script_name)
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        event_handler.process.terminate()

    observer.join()
