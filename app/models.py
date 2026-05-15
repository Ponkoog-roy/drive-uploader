from sqlalchemy import Column, Integer, String
from app.database import Base


class UploadedVideo(Base):
    __tablename__ = "uploaded_videos"

    id = Column(Integer, primary_key=True, index=True)

    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)

    file_hash = Column(String, unique=True, nullable=True)

    drive_file_id = Column(String, nullable=True)

    status = Column(String, default="pending")