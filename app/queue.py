from collections import deque
import threading
import time

from app.uploader import upload_video

file_queue = deque()


def add_to_queue(file_path):
    print(f"📥 Added to queue: {file_path}")
    file_queue.append(file_path)


def worker():
    print("🚀 Queue worker started")

    while True:

        if file_queue:
            file_path = file_queue.popleft()
            print(f"📦 Processing: {file_path}")

            upload_video(file_path)

        time.sleep(1)


def start_worker():
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()