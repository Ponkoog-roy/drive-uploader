from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .uploader import upload_video
import time
import os


class VideoHandler(FileSystemEventHandler):
  
   # Detect new files
   

    def on_created(self, event):

        # Ignore folders
        if event.is_directory:
            return

        file_path = event.src_path
        file_name = os.path.basename(file_path)

        print(f"New file detected: {file_name}")

        try:
            upload_video(file_path)
            print(f"Uploaded: {file_name}")

        except Exception as e:
            print(f"Upload failed: {e}")


def start_watching(folder_path):
   
    #Start monitoring folder
    

    event_handler = VideoHandler()

    observer = Observer()

    observer.schedule(
        event_handler,
        folder_path,
        recursive=False
    )

    observer.start()

    print(f"Watching folder: {folder_path}")

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()

    observer.join()