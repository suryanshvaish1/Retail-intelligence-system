# database.py
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
engine = create_engine("sqlite:///retail_data.db", connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)

class VisitorEvent(Base):
    __tablename__ = "visitor_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    track_id = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    age_group = Column(String, nullable=False)
    zone = Column(String, nullable=False)
    dwell_seconds = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(engine)

def log_event(track_id: int, gender: str, age_group: str, zone: str, dwell_seconds: float):
    session = Session()
    event = VisitorEvent(
        track_id=track_id,
        gender=gender,
        age_group=age_group,
        zone=zone,
        dwell_seconds=round(dwell_seconds, 2)
    )
    session.add(event)
    session.commit()
    session.close()
    print(f"[DB LOG] Saved Track #{track_id} | {gender} | {age_group} | {zone} | {round(dwell_seconds, 2)}s")