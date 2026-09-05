Markdown
# Autonomous Retail Intelligence System

An end-to-end edge AI and computer vision platform that converts CCTV store footage into actionable business intelligence. The system tracks visitor movement, computes zone-specific dwell times, generates 2D foot-traffic heatmaps, exposes REST endpoints, and provides an interactive executive dashboard with automated AI operational insights.

---

## System Architecture & Pipeline Flow

```mermaid
flowchart TD
    A[Video File / CCTV Stream] --> B[Frame Reader - OpenCV]
    B --> C[Person Detection - YOLOv8]
    C --> D[Multi-Object Tracking - DeepSORT]
    
    %% Branch A
    D --> E[Tracked Person Bounding Box]
    E --> F[Demographic Classification]
    E --> G[Zone Check & ROI Verification]
    F --> H[Compute Dwell Time & Log Event]
    G --> H
    H --> I[(SQLite Database - retail_data.db)]
    
    %% Branch B
    D --> J[Heatmap Canvas Accumulation]
    J --> K[Gaussian Blur & JET Colormap]
    K --> L[heatmap_output.png]
    
    %% Serving Layer
    I --> M[FastAPI Backend - api.py]
    M --> N[Streamlit Dashboard - dashboard.py]
    L --> N
Key Features
Real-Time Person Detection & Tracking: Leverages YOLOv8 and DeepSORT for robust identity preservation across frames.  
PDF

Zone & Dwell Time Analytics: Automatically detects when shoppers enter defined Regions of Interest (ROI) and logs elapsed browsing duration.

Spatial Foot-Traffic Heatmap: Accumulates visitor coordinates to render smoothed, color-mapped density images (heatmap_output.png).

Decoupled Backend API: FastAPI exposes /api/summary, /api/events, and /api/copilot endpoints without running blocking AI tasks.

Executive Streamlit UI: Visualizes traffic KPIs, Plotly demographic breakdown charts, dwell time distributions, and raw CSV event exports[cite: 1].

AI Retail Copilot: Evaluates floor traffic patterns and flags underperforming shelves or checkout congestion bottlenecks[cite: 1].

Tech Stack
Computer Vision: OpenCV, Ultralytics YOLOv8, DeepSORT

Backend: FastAPI, Uvicorn, SQLAlchemy, SQLite

Frontend / Visualization: Streamlit, Plotly Express

Analytics & Reporting: Pandas, NumPy, ReportLab

Directory Structure
Plaintext
retail-intelligence-system/
├── database.py                 # SQLite schema & SQLAlchemy event logger
├── main_pipeline.py            # AI Pipeline (YOLOv8 + DeepSORT + Heatmap)
├── api.py                      # FastAPI REST service & AI Copilot logic
├── dashboard.py                # Streamlit analytics dashboard
├── generate_report.py          # Automated executive PDF report compiler
├── store_video.mp4             # Input video footage
├── retail_data.db              # Generated event database
└── heatmap_output.png          # Generated foot-traffic heatmap
Quick Start Guide
1. Environment Setup
Clone the repository and install required packages:

Bash
git clone [https://github.com/](https://github.com/)<YOUR_USERNAME>/<YOUR_REPO_NAME>.git
cd retail-intelligence-system

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # On Windows PowerShell
# source venv/bin/activate   # On Linux/macOS

# Install dependencies
pip install -r requirements.txt
(If you don't have a requirements.txt, install manually: pip install ultralytics deep-sort-realtime opencv-python fastapi uvicorn sqlalchemy streamlit plotly requests reportlab pandas)

2. Running the System
Execute the modules across three separate terminal instances:

Terminal 1: Run AI Video Analytics
Processes the input video, performs tracking, and writes records to retail_data.db and heatmap_output.png:

Bash
python main_pipeline.py
Terminal 2: Start FastAPI Backend
Hosts the REST API endpoints and AI copilot services at http://127.0.0.1:8000:

Bash
uvicorn api:app --reload --port 8000
Terminal 3: Launch Streamlit Dashboard
Starts the interactive analytics dashboard at http://localhost:8501:

Bash
streamlit run dashboard.py
API Reference
Endpoint	Method	Description
/	GET	API health check and route manifest
/docs	GET	Interactive Swagger API documentation
/api/summary	GET	Aggregated store KPIs (total visitors, avg dwell, demographics)
/api/events	GET	Tabular array of all visitor logging events
/api/copilot	GET	Dynamic operational recommendations and alerts
License
This project is licensed under the MIT License.
