from sqlalchemy import Column, String, Float, Integer, Boolean
from app.database import Base


class EventDB(Base):
    __tablename__ = "events"

    event_id = Column(String, primary_key=True, index=True)

    store_id = Column(String)
    camera_id = Column(String)

    visitor_id = Column(String)

    event_type = Column(String)

    timestamp = Column(String)

    zone_id = Column(String, nullable=True)

    dwell_ms = Column(Integer, default=0)

    is_staff = Column(Boolean, default=False)

    confidence = Column(Float)

    
