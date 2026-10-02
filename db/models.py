import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, DateTime, UniqueConstraint, LargeBinary
from db.session import Base

class Document(Base):
    __tablename__ = "documents"

    document_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    status = Column(String, nullable=False, default="REGISTERED")
    approved_source = Column(Boolean, default=False)
    original_filename = Column(String, nullable=False)
    file_content = Column(LargeBinary, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    sha256 = Column(String, nullable=False)
    uploaded_by = Column(String, nullable=True) # Optional for now
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    error_message = Column(String, nullable=True)

    __table_args__ = (
        UniqueConstraint('project_id', 'name', 'version', name='uq_project_name_version'),
    )
