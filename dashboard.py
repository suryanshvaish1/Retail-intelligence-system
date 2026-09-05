import os
import requests
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Autonomous Retail Intelligence System", layout="wide")

API_BASE_URL = "http://127.0.0.1:8000"

st.title("Autonomous Retail Intelligence System")
st.caption("Store Video Analytics, Customer Behavior & AI Insights")

# Fetch Backend Data
try:
    summary_res = requests.get(f"{API_BASE_URL}/api/summary", timeout=3)
    events_res = requests.get(f"{API_BASE_URL}/api/events", timeout=3)
    copilot_res = requests.get(f"{API_BASE_URL}/api/copilot", timeout=3)

    summary_data = summary_res.json() if summary_res.status_code == 200 else None
    events_data = events_res.json() if events_res.status_code == 200 else []
    copilot_data = copilot_res.json().get("recommendations", []) if copilot_res.status_code == 200 else []
except requests.exceptions.RequestException:
    st.error("Cannot reach analytics backend. Please make sure FastAPI (`api.py`) is running on port 8000.")
    st.stop()

# Metric KPI Cards
m1, m2, m3 = st.columns(3)
if summary_data and summary_data.get("total_visitors", 0) > 0:
    m1.metric("Total Visitors Tracked", summary_data.get("total_visitors", 0))
    m2.metric("Average Dwell Time", f"{summary_data.get('average_dwell_seconds', 0.0)} s")
    m3.metric("Monitored Zones", summary_data.get("zones_monitored", 1))
else:
    m1.metric("Total Visitors Tracked", 0)
    m2.metric("Average Dwell Time", "0.0 s")
    m3.metric("Monitored Zones", 1)
    st.info("No visitor data found. Run the video pipeline (`main_pipeline.py`) to analyze footage.")

st.divider()

# AI Copilot Recommendations
st.subheader("AI Retail Copilot & Actionable Insights")
if copilot_data:
    for rec in copilot_data:
        st.info(f"**AI Recommendation:** {rec}")
else:
    st.write("No operational insights available at this time.")

st.divider()

# Heatmap Section
st.subheader("Store Movement Heatmap")
if os.path.exists("heatmap_output.png"):
    st.image("heatmap_output.png", caption="Aggregated Customer Movement Density", use_container_width=True)
else:
    st.warning("Heatmap not yet generated. Run `main_pipeline.py` to produce 'heatmap_output.png'.")

st.divider()

# Demographic and Dwell Charts
if events_data:
    df = pd.DataFrame(events_data)
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Visitors by Gender")
        pie_fig = px.pie(df, names="gender", title="Gender Distribution", hole=0.35,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(pie_fig, use_container_width=True)

    with col2:
        st.subheader("Dwell Time per Visitor")
        bar_fig = px.bar(df, x="track_id", y="dwell_seconds", color="zone",
                         title="Dwell Duration by Track ID (Seconds)",
                         labels={"track_id": "Visitor Track ID", "dwell_seconds": "Dwell Time (s)"})
        st.plotly_chart(bar_fig, use_container_width=True)

    # Raw Event Log Table & CSV Export
    st.subheader("Raw Visitor Events Log")
    st.dataframe(df[["id", "track_id", "gender", "age_group", "zone", "dwell_seconds", "timestamp"]],
                 use_container_width=True)

    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button("Export CSV Report", data=csv_data, file_name="retail_visitor_report.csv", mime="text/csv")