# Autonomous Retail Intelligence System

An end-to-end edge AI and computer vision platform that converts CCTV store footage into real-time, actionable business intelligence. The system tracks visitor movement, computes zone-specific dwell times, generates 2D foot-traffic heatmaps, exposes REST endpoints, and provides an interactive executive dashboard with automated AI operational insights.

---

## System Architecture & Pipeline Flow

```mermaid
flowchart TD
    A[Video Stream / File] --> B[Frame Reader - OpenCV]
    B --> C[Person Detection - YOLOv8]
    C --> D[Multi-Object Tracking - DeepSORT]
    
    %% AI Pipeline Branch
    D --> E[Tracked Person Bounding Box]
    E --> F[Demographic Classification]
    E --> G[Zone Verification & ROI Check]
    F --> H[Compute Dwell Time & Log Event]
    G --> H
    H --> I[(SQLite Database - retail_data.db)]
    
    %% Spatial Heatmap Branch
    D --> J[Heatmap Canvas Accumulation]
    J --> K[Gaussian Blur & JET Colormap]
    K --> L[heatmap_output.png]
    
    %% Analytics & Serving Layer
    I --> M[FastAPI REST Service - api.py]
    M --> N[Streamlit Dashboard - dashboard.py]
    L --> N
    I --> O[AI Copilot Engine - ai_copilot.py]
    O --> N
    I --> P[PDF Report Generator - generate_report.py]
Key FeaturesReal-Time Person Detection & Tracking: Leverages YOLOv8 and DeepSORT for robust identity preservation across video frames.   Zone & Dwell Time Analytics: Automatically detects when shoppers enter defined Regions of Interest (ROI) and logs elapsed browsing duration.   Spatial Foot-Traffic Heatmap: Accumulates visitor coordinates to render smoothed, color-mapped density images (heatmap_output.png).   Decoupled Backend API: FastAPI exposes /api/summary, /api/events, and /api/copilot endpoints without blocking AI processing tasks.   Interactive Executive Dashboard: Built using Streamlit and Plotly to display traffic KPIs, demographic distributions, dwell duration charts, and raw CSV event exports.   AI Retail Copilot: Evaluates floor traffic patterns in real time to flag underperforming shelves, checkout queue congestion, and staffing alerts.   Automated PDF Executive Reports: Compiles store health summaries and visual analytics into downloadable PDF audit reports using ReportLab.   Tech StackComputer Vision & Tracking: OpenCV, Ultralytics YOLOv8, DeepSORT   Backend & Storage: FastAPI, Uvicorn, SQLAlchemy, SQLite   Frontend & Visualization: Streamlit, Plotly Express[cite: 1]Analytics & PDF Reporting: Pandas, NumPy, ReportLab[cite: 1]Project StructurePlaintextretail-intelligence-system/
├── database.py                 # SQLite schema & SQLAlchemy event logger
├── main_pipeline.py            # Computer Vision pipeline (YOLOv8 + DeepSORT + Heatmaps)
├── main_pipeline_advanced.py   # Advanced pipeline (Tripwires + Queue alerts)
├── api.py                      # FastAPI REST service & AI Copilot endpoint
├── dashboard.py                # Streamlit executive analytics dashboard
├── ai_copilot.py               # Operational heuristic decision engine
├── analytics_pos.py            # Look-to-buy POS sales correlation engine
├── generate_report.py          # PDF report compiler (ReportLab)
├── store_video.mp4             # Sample input video stream
├── retail_data.db              # SQLite event database
└── heatmap_output.png          # Generated foot-traffic spatial heatmap
Quick Start Guide1. Environment SetupClone the repository and set up a Python virtual environment:Bashgit clone [https://github.com/suryanshvaish1/retail-intelligence-system.git](https://github.com/suryanshvaish1/retail-intelligence-system.git)
cd retail-intelligence-system

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# source venv/bin/activate   # Linux/macOS

# Install dependencies
python -m pip install ultralytics deep-sort-realtime opencv-python fastapi uvicorn sqlalchemy streamlit plotly requests reportlab pandas
2. Running the SystemExecute the core components across three separate terminal windows:Terminal 1: Run Computer Vision PipelineProcesses the input video stream, performs real-time tracking, logs visitor events to retail_data.db, and generates heatmap_output.png:Bashpython main_pipeline.py
Terminal 2: Start FastAPI Backend ServiceLaunches the REST API backend exposing analytics and AI copilot endpoints at http://127.0.0.1:8000:Bashuvicorn api:app --reload --port 8000
Terminal 3: Launch Executive Streamlit DashboardStarts the interactive analytics dashboard at http://localhost:8501:Bashstreamlit run dashboard.py
3. Generate Executive PDF ReportTo compile an executive audit PDF summary from the recorded database events, run:Bashpython generate_report.py
API DocumentationEndpointMethodDescription/GETHealth check status and endpoint manifest/docsGETInteractive OpenAPI / Swagger UI documentation/api/summaryGETAggregated store KPIs (total visitors, avg dwell, demographics)/api/eventsGETComplete list of recorded visitor events/api/copilotGETAI Copilot operational recommendations and queue alerts
