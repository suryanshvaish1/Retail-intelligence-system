# Autonomous Retail Intelligence System

An end-to-end edge AI and computer vision platform that converts CCTV store footage into real-time, actionable business intelligence. The system tracks visitor movement, computes zone-specific dwell times, generates 2D foot-traffic heatmaps, exposes REST endpoints, and provides an interactive executive dashboard with automated AI operational insights.

---

## System Architecture & Pipeline Flow

![System Architecture Flowchart](docs/flowchart.png)

```mermaid
flowchart TD
    A[Video File / Webcam] --> B[Frame Reader - OpenCV]
    B --> C[Person Detection - YOLOv8 pretrained]
    C --> D[Tracking - DeepSORT assigns track_id]
    
    %% AI Pipeline Branch
    D --> E[Crop each tracked person]
    E --> F[Age & Gender Classification pretrained model]
    E --> G[Zone Check Inside shelf area?]
    F --> H[Compute Dwell Time & Log Event]
    G --> H
    H --> I[(SQLite Database)]
    
    %% Spatial Heatmap Branch
    D --> J[Heatmap Accumulation mark position each frame]
    J --> K[Save Heatmap Image]
    
    %% Analytics & Serving Layer
    I --> L[FastAPI Backend /api/summary, /api/events]
    L --> M[Streamlit Dashboard Charts + Metrics + Table]
    K --> M
Detailed Architecture & Flowchart Explanation
The system architecture is structured into four core layers to ensure real-time performance and complete decoupling between computer vision processing and the web frontend:   
PDF

1. Ingestion & Perception Layer (Video to Object Tracking)
Video File / Webcam Ingestion: Captures each individual video frame sequentially from an MP4 file or real-time IP camera/webcam stream using OpenCV VideoCapture routines.

YOLOv8 Person Detection: Every frame passes through the YOLOv8 neural network, filtering specifically for class 0 (person) to isolate humans and output spatial bounding box coordinates along with detection confidence percentages.

DeepSORT Multi-Object Tracking: Takes YOLO's detected bounding boxes and passes them to DeepSORT, which uses Kalman filtering and deep appearance features to preserve a unique track_id across consecutive frames, even during temporary visual occlusions.   
PDF

2. Feature Extraction & Analytics Processing Layer
Spatial ROI & Zone Verification: Calculates the center point (c 
x
​
 ,c 
y
​
 ) of a tracked person's bounding box and tests whether it falls inside user-defined regions of interest (like the shelf area or register line).   
PDF

Dwell Time Computation: Measures how long a person remains inside a specific zone by incrementing frame counters and dividing by the video's frames-per-second (FPS) rate to calculate exact dwell time in seconds.

Demographic Classification: Crops out the person's bounding box region and runs it through a classifier model to estimate age group and gender for demographic telemetry.

Database Logging: Once a tracked individual spends enough time in a zone to meet the threshold, their complete session record (track_id, gender, age_group, zone, dwell_seconds, timestamp) is persisted to retail_data.db via SQLAlchemy ORM.   
PDF

3. Spatial Density & Heatmapping Layer
Coordinate Accumulation: Tracks the bottom-center coordinates of each person's feet and plots those coordinates onto a 2D NumPy numerical grid to map spatial foot traffic across the floor layout.

Gaussian Smoothing & JET Colormap: Blurs raw coordinate points with a Gaussian kernel to turn individual steps into smooth heat gradients, normalizes intensities, applies a red-to-blue color scale (COLORMAP_JET), and saves the image as heatmap_output.png.   
PDF

4. Serving & Visual Presentation Layer
FastAPI Backend (api.py): Hosts an asynchronous web server using FastAPI that serves database metrics over REST API endpoints (/api/summary, /api/events, /api/copilot), allowing the dashboard to read data without slowing down the video detection loop.   
PDF

AI Retail Copilot (ai_copilot.py): Runs rule-based analytical checks on recorded store data to generate live operational alerts (e.g., flagging long checkout wait times or underperforming shelves).   
PDF

Streamlit Dashboard (dashboard.py): Connects to the FastAPI backend to render an interactive web interface displaying high-level store stats, visual graphs, raw event tables, and the saved movement heatmap image.   
PDF

Dashboard Results & Visualizations
1. Store Analytics Overview & AI Retail Copilot
Displays real-time KPIs, zone statistics, and automated operational recommendations.   
PDF

2. Spatial Foot-Traffic Heatmap Result
Visualizes customer movement density and high-traffic friction areas within the store layout.   
PDF

3. Demographic & Dwell Analysis
Provides breakdown charts for visitor gender distributions and individual dwell times per tracking ID.   
PDF

4. Raw Event Logs & Export
Allows real-time inspection of database records and direct CSV report downloads.   
PDF

Key Features
Real-Time Person Detection & Tracking: Leverages YOLOv8 and DeepSORT for identity preservation across video frames.   
PDF

Zone & Dwell Time Analytics: Automatically detects when shoppers enter defined Regions of Interest (ROI) and logs browsing duration.   
PDF

Spatial Movement Heatmapping: Accumulates visitor coordinates to render color-mapped density images (heatmap_output.png).   
PDF

Decoupled Backend API: FastAPI exposes /api/summary, /api/events, and /api/copilot endpoints asynchronously.   
PDF

Interactive Executive Dashboard: Built using Streamlit and Plotly Express to visualize store KPIs and event telemetry.   
PDF

AI Retail Copilot: Evaluates floor traffic patterns in real time to generate actionable floor management advice.   
PDF

Tech Stack
Computer Vision & Tracking: OpenCV, Ultralytics YOLOv8, DeepSORT   
PDF

Backend & Storage: FastAPI, Uvicorn, SQLAlchemy, SQLite   
PDF

Frontend & Visualization: Streamlit, Plotly Express[cite: 1]

Analytics & Reporting: Pandas, NumPy, ReportLab[cite: 1]

Project Structure
Plaintext
retail-intelligence-system/
├── docs/
│   ├── flowchart.png           # Pipeline architecture diagram
│   ├── dashboard_top.png       # Executive metrics screenshot
│   ├── dashboard_middle.png    # Analytics charts screenshot
│   └── dashboard_bottom.png    # Event log table screenshot
├── database.py                 # SQLite schema & SQLAlchemy event logger
├── main_pipeline.py            # AI Video Pipeline (YOLOv8 + DeepSORT + Heatmaps)
├── api.py                      # FastAPI REST service & AI Copilot logic
├── dashboard.py                # Streamlit analytics dashboard
├── ai_copilot.py               # Operational heuristic decision engine
├── generate_report.py          # PDF report compiler (ReportLab)
├── store_video.mp4             # Input video stream
├── retail_data.db              # Generated SQLite event database
└── heatmap_output.png          # Generated foot-traffic spatial heatmap
Quick Start Guide
1. Environment Setup
Clone the repository and set up a Python virtual environment:

Bash
git clone https://github.com/suryanshvaish1/retail-intelligence-system.git
cd retail-intelligence-system

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# source venv/bin/activate   # Linux/macOS

# Install dependencies
python -m pip install ultralytics deep-sort-realtime opencv-python fastapi uvicorn sqlalchemy streamlit plotly requests reportlab pandas
2. Running the System
Execute the core modules across three separate terminal windows:

Terminal 1: Run Computer Vision Pipeline
Processes video input, tracks visitors, writes records to retail_data.db, and outputs heatmap_output.png:

Bash
python main_pipeline.py
Terminal 2: Start FastAPI Backend Service
Launches the REST API exposing analytics and copilot endpoints at [http://127.0.0.1:8000](http://127.0.0.1:8000):

Bash
uvicorn api:app --reload --port 8000
Terminal 3: Launch Streamlit Dashboard
Starts the interactive analytics dashboard at http://localhost:8501:

Bash
streamlit run dashboard.py
3. Generate Executive PDF Report
To compile an executive audit PDF summary from database records:

Bash
python generate_report.py
API Reference
Endpoint	Method	Description
/	GET	Health check status and endpoint manifest
/docs	GET	Interactive OpenAPI / Swagger UI documentation
/api/summary	GET	Aggregated store KPIs (total visitors, avg dwell, demographics)
/api/events	GET	Complete list of recorded visitor events
/api/copilot	GET	AI Copilot operational recommendations and queue alerts
License
This project is licensed under the MIT License.
