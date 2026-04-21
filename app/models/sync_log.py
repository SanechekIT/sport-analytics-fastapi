from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class SyncLog(Base):
    __tablename__ = "sync_logs"
    
    id = Column(Integer, primary_key=True)
    task_name = Column(String)
    status = Column(String)
    records_synced = Column(Integer)
    error_message = Column(String, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
