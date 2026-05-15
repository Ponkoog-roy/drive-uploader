import os
import time
import hashlib

from app.database import SessionLocal
from app.models import UploadedVideo

from googleapiclient.http import MediaFileUpload
from app.google_drive import authenticate_google_drive


MAX_RETRIES = 3
DRIVE_FOLDER_ID = "1L2DQI0LttBtexKSRwKs7bmKwhaHToo1q"


# =========================
# FILE HASH FUNCTION
# =========================
def get_file_hash(file_path):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            sha256.update(chunk)

    return sha256.hexdigest()


# =========================
# MAIN UPLOAD FUNCTION
# =========================
def upload_video(file_path):

    db = SessionLocal()

    try:
        file_name = os.path.basename(file_path)
        file_hash = get_file_hash(file_path)

        # -------------------------
        # Duplicate check (BY HASH)
        # -------------------------
        existing_video = db.query(UploadedVideo).filter(
            UploadedVideo.file_hash == file_hash
        ).first()

        if existing_video:
            print(f"⚠️ Duplicate skipped: {file_name}")
            return

        # -------------------------
        # Create DB record
        # -------------------------
        new_video = UploadedVideo(
            file_name=file_name,
            file_path=file_path,
            file_hash=file_hash,
            status="pending"
        )

        db.add(new_video)
        db.commit()
        db.refresh(new_video)

        # Set uploading
        new_video.status = "uploading"
        db.commit()

        print(f"⬆️ Uploading: {file_name}")

        # -------------------------
        # Retry loop
        # -------------------------
        for attempt in range(1, MAX_RETRIES + 1):

            try:
                service = authenticate_google_drive()

                file_metadata = {
                    "name": file_name,
                    "parents": [DRIVE_FOLDER_ID]
                }

                media = MediaFileUpload(
                    file_path,
                    resumable=True
                )

                uploaded_file = service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields="id"
                ).execute()

                drive_file_id = uploaded_file.get("id")

                # Success update
                new_video.drive_file_id = drive_file_id
                new_video.status = "uploaded"

                db.commit()

                print(f"✅ Uploaded: {file_name}")
                return

            except Exception as e:

                print(
                    f"❌ Attempt {attempt}/{MAX_RETRIES} failed: {e}"
                )

                if attempt < MAX_RETRIES:
                    print("🔄 Retrying in 5 seconds...")
                    time.sleep(5)

        # Final failure
        new_video.status = "failed"
        db.commit()

        print(f"❌ Final failure: {file_name}")

    except Exception as e:
        db.rollback()
        print(f"❌ System error: {e}")

    finally:
        db.close()


# =========================
# MANUAL RETRY FUNCTION
# =========================
def retry_upload_by_id(file_id):

    db = SessionLocal()

    try:
        file_record = db.query(UploadedVideo).filter(
            UploadedVideo.id == file_id
        ).first()

        if not file_record:
            print("❌ File not found")
            return

        print(f"🔄 Retrying: {file_record.file_name}")

        file_record.status = "uploading"
        db.commit()

        service = authenticate_google_drive()

        file_metadata = {
            "name": file_record.file_name,
            "parents": [DRIVE_FOLDER_ID]
        }

        media = MediaFileUpload(
            file_record.file_path,
            resumable=True
        )

        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()

        file_record.drive_file_id = uploaded_file.get("id")
        file_record.status = "uploaded"

        db.commit()

        print(f"✅ Retry success: {file_record.file_name}")

    except Exception as e:
        file_record.status = "failed"
        db.commit()
        print(f"❌ Retry failed: {e}")

    finally:
        db.close()