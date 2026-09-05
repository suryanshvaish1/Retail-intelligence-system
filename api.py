from fastapi import FastAPI, HTTPException
from sqlalchemy import func
import sqlite3
import pandas as pd
from database import Session, VisitorEvent

app = FastAPI(
    title="Retail Intelligence API",
    description="REST API serving store video analytics, visitor tracking data, dwell metrics, and AI recommendations.",
    version="1.0.0"
)

def generate_ai_insights(db_path="retail_data.db"):
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM visitor_events", conn)
        conn.close()
    except Exception:
        return ["Database inaccessible. Run the tracking pipeline first."]

    if df.empty:
        return ["No visitor activity recorded yet. Awaiting video stream processing."]

    insights = []
    total_visitors = df["track_id"].nunique()
    avg_dwell = df["dwell_seconds"].mean()
    
    # Dwell Time & Engagement Analysis
    shelf_events = df[df["zone"].str.contains("Shelf", case=False, na=False)]
    if not shelf_events.empty:
        shelf_avg = shelf_events["dwell_seconds"].mean()
        if shelf_avg > avg_dwell * 1.2:
            insights.append(
                f"High Product Engagement: Visitors spend an average of {shelf_avg:.1f}s near display shelves "
                f"(higher than the store average of {avg_dwell:.1f}s). Suggestion: Deploy sales staff to assist potential buyers."
            )
        elif shelf_avg < 10.0:
            insights.append(
                f"Low Shelf Retention: Visitors browse display shelves for only {shelf_avg:.1f}s on average. "
                f"Suggestion: Optimize shelf layout, visual merchandising, or promotional signage."
            )

    # Demographic Targeting Insight
    gender_counts = df["gender"].value_counts(normalize=True) * 100
    if not gender_counts.empty:
        dominant_gender = gender_counts.idxmax()
        dominant_pct = gender_counts.max()
        if dominant_pct >= 60.0:
            insights.append(
                f"Target Demographic Notice: {dominant_gender} shoppers represent {dominant_pct:.0f}% of total foot traffic. "
                f"Suggestion: Feature {dominant_gender}-targeted campaigns on entrance displays."
            )

    # Queue & Checkout Bottleneck Check
    checkout_events = df[df["zone"].str.contains("Checkout", case=False, na=False)]
    if len(checkout_events) >= 5:
        checkout_dwell = checkout_events["dwell_seconds"].mean()
        if checkout_dwell > 30.0:
            insights.append(
                f"Checkout Congestion Alert: Average checkout dwell time is elevated at {checkout_dwell:.1f}s. "
                f"Suggestion: Open an auxiliary POS register to reduce customer wait times."
            )

    if not insights:
        insights.append(f"Store operations are balanced across {total_visitors} recorded visitors with average dwell of {avg_dwell:.1f}s.")

    return insights

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Retail Intelligence API is running",
        "docs_url": "/docs",
        "summary_endpoint": "/api/summary",
        "events_endpoint": "/api/events",
        "copilot_endpoint": "/api/copilot"
    }

@app.get("/api/summary")
def get_summary():
    session = Session()
    try:
        total_visitors = session.query(VisitorEvent.track_id).distinct().count()
        avg_dwell = session.query(func.avg(VisitorEvent.dwell_seconds)).scalar() or 0.0
        
        gender_query = (
            session.query(VisitorEvent.gender, func.count(VisitorEvent.id))
            .group_by(VisitorEvent.gender)
            .all()
        )
        gender_distribution = {gender: count for gender, count in gender_query}
        
        zone_query = (
            session.query(VisitorEvent.zone, func.count(VisitorEvent.id))
            .group_by(VisitorEvent.zone)
            .all()
        )
        zone_distribution = {zone: count for zone, count in zone_query}

        return {
            "total_visitors": total_visitors,
            "average_dwell_seconds": round(float(avg_dwell), 2),
            "zones_monitored": len(zone_distribution) or 1,
            "gender_distribution": gender_distribution,
            "zone_distribution": zone_distribution
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()

@app.get("/api/events")
def get_events():
    session = Session()
    try:
        events = session.query(VisitorEvent).order_by(VisitorEvent.timestamp.desc()).all()
        return [
            {
                "id": ev.id,
                "track_id": ev.track_id,
                "gender": ev.gender,
                "age_group": ev.age_group,
                "zone": ev.zone,
                "dwell_seconds": ev.dwell_seconds,
                "timestamp": ev.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            for ev in events
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()

@app.get("/api/copilot")
def get_ai_copilot_insights():
    insights = generate_ai_insights()
    return {"status": "success", "recommendations": insights}