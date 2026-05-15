from fastapi import FastAPI
import threading

from app.watcher import start_watching
from app.database import engine, SessionLocal
from app.models import Base, UploadedVideo
from app.queue import start_worker

from app.uploader import retry_upload_by_id

app = FastAPI()

WATCH_FOLDER = r"C:\Users\Mr. Nobody\Desktop\drive"

# Create DB tables
Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {
        "message": "Video Auto Upload API Running"
    }


# -------------------------------
# GET ALL FILES
# -------------------------------
@app.get("/files")
def get_files():

    db = SessionLocal()

    files = db.query(
        UploadedVideo
    ).all()

    result = []

    for file in files:
        result.append({
            "id": file.id,
            "file_name": file.file_name,
            "status": file.status,
            "drive_file_id": file.drive_file_id
        })

    db.close()

    return result


# -------------------------------
# GET UPLOADED FILES
# -------------------------------
@app.get("/uploaded")
def uploaded_files():

    db = SessionLocal()

    files = db.query(
        UploadedVideo
    ).filter(
        UploadedVideo.status == "uploaded"
    ).all()

    db.close()

    return files


# -------------------------------
# GET FAILED FILES
# -------------------------------
@app.get("/failed")
def failed_files():

    db = SessionLocal()

    files = db.query(
        UploadedVideo
    ).filter(
        UploadedVideo.status == "failed"
    ).all()

    db.close()

    return files


# -------------------------------
# GET PENDING FILES
# -------------------------------
@app.get("/pending")
def pending_files():

    db = SessionLocal()

    files = db.query(
        UploadedVideo
    ).filter(
        UploadedVideo.status == "pending"
    ).all()

    db.close()

    return files


def run_watcher():
    try:
        print("📁 Watcher started...")
        start_watching(WATCH_FOLDER)

    except Exception as e:
        print(
            f"❌ Watcher error: {e}"
        )

from app.uploader import retry_upload_by_id


@app.post("/retry/{file_id}")
def retry(file_id: int):

    retry_upload_by_id(file_id)

    return {
        "message": f"Retry triggered for file {file_id}"
    }
@app.on_event("startup")
def startup_event():

    print("🚀 Starting queue worker...")
    start_worker()   # 🔥 THIS IS REQUIRED

    watcher_thread = threading.Thread(
        target=run_watcher,
        daemon=True
    )

    watcher_thread.start()