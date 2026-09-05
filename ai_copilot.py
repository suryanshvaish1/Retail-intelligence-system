import sqlite3
import pandas as pd

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
    
    # 1. Dwell Time & Engagement Analysis
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
                f"Low Shelf Retention: Visitors are browsing display shelves for only {shelf_avg:.1f}s on average. "
                f"Suggestion: Optimize shelf layout, visual merchandising, or promotional signage."
            )

    # 2. Demographic Targeting Insight
    gender_counts = df["gender"].value_counts(normalize=True) * 100
    if not gender_counts.empty:
        dominant_gender = gender_counts.idxmax()
        dominant_pct = gender_counts.max()
        if dominant_pct >= 60.0:
            insights.append(
                f"Target Demographic Notice: {dominant_gender} shoppers represent {dominant_pct:.0f}% of total foot traffic. "
                f"Suggestion: Feature {dominant_gender}-targeted campaigns on entrance displays."
            )

    # 3. Queue & Checkout Bottleneck Check
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

if __name__ == "__main__":
    for item in generate_ai_insights():
        print(f"[AI INSIGHT] {item}")