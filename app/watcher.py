import os
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.queue import add_to_queue

from .uploader import upload_video


def wait_for_file_complete(file_path):
    """
    Wait until file copy is complete.
    Checks if file size stops changing.
    """

    previous_size = -1

    while True:
        try:
            current_size = os.path.getsize(file_path)

            if current_size == previous_size:
                print(f"✅ File ready: {os.path.basename(file_path)}")
                return True

            previous_size = current_size

            print(
                f"⏳ Waiting for file copy to finish: "
                f"{os.path.basename(file_path)}"
            )

            time.sleep(3)

        except FileNotFoundError:
            print("❌ File disappeared.")
            return False


class VideoHandler(FileSystemEventHandler):

    def on_created(self, event):

        if event.is_directory:
            return

        file_path = event.src_path

        print(
            f"📂 New file detected: "
            f"{os.path.basename(file_path)}"
        )

        # Wait for file copy to complete
        ready = wait_for_file_complete(file_path)

        if ready:
            add_to_queue(file_path)


def start_watching(folder_path):

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