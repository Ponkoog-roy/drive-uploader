from fastapi import FastAPI
import threading

from app.watcher import start_watching
from app.database import engine
from app.models import Base

app = FastAPI()

WATCH_FOLDER = r"C:\Users\Mr. Nobody\Desktop\drive"

# Create DB tables
Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"message": "Video Auto Upload API Running"}


def run_watcher():
    try:
        print("📁 Watcher started...")
        start_watching(WATCH_FOLDER)
    except Exception as e:
        print(f"❌ Watcher error: {e}")


@app.on_event("startup")
def startup_event():
    watcher_thread = threading.Thread(
        target=run_watcher,
        daemon=True
    )
    watcher_thread.start()