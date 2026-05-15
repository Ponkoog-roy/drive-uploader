from sqlalchemy import Column, Integer, String
from app.database import Base


class UploadedVideo(Base):
    __tablename__ = "uploaded_videos"

    id = Column(Integer, primary_key=True, index=True)

    file_name = Column(String, unique=True)

    file_path = Column(String)

    drive_file_id = Column(String)