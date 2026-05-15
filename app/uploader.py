import os
from app.database import SessionLocal
from app.models import UploadedVideo

from googleapiclient.http import MediaFileUpload
from app.google_drive import authenticate_google_drive


def upload_video(file_path):
    db = SessionLocal()

    try:
        file_name = os.path.basename(file_path)

        # Check duplicate
        existing_video = db.query(UploadedVideo).filter(
            UploadedVideo.file_name == file_name
        ).first()

        if existing_video:
            print(f"⚠️ Already uploaded: {file_name}")
            return

        # Authenticate Google Drive
        service = authenticate_google_drive()

        file_metadata = {
            "name": file_name,
            "parents": ["1L2DQI0LttBtexKSRwKs7bmKwhaHToo1q"]
        }

        media = MediaFileUpload(file_path, resumable=True)

        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()

        drive_file_id = uploaded_file.get("id")

        # Save to DB
        new_video = UploadedVideo(
            file_name=file_name,
            file_path=file_path,
            drive_file_id=drive_file_id
        )

        db.add(new_video)
        db.commit()

        print(f"✅ Uploaded: {file_name}")

    except Exception as e:
        db.rollback()
        print(f"❌ Upload failed: {e}")

    finally:
        db.close()