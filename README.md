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
1. Ingestion & Perception Layer (Video to Object Tracking)
Video File / Webcam Ingestion

Reads incoming video frames sequentially using OpenCV VideoCapture routines.

Explanation: Captures each individual video frame sequentially from an MP4 file or real-time IP camera/webcam stream using OpenCV's video ingestion tools.

YOLOv8 Person Detection

Each frame is passed into a lightweight YOLOv8 model trained to isolate class 0 (person). It outputs bounding box coordinates (x 
1
​
 ,y 
1
​
 ,x 
2
​
 ,y 
2
​
 ) and detection confidence scores.

Explanation: Every frame passes through the YOLOv8 neural network, filtering specifically for class 0 (person). It detects humans and outputs spatial bounding box coordinates along with detection confidence percentages.

DeepSORT Multi-Object Tracking

Bounding boxes are fed into DeepSORT, which uses Kalman filtering and deep cosine metric learning to assign and preserve a unique track_id across consecutive frames, even during temporary visual occlusions.

Explanation: Takes YOLO's detected bounding boxes and passes them to DeepSORT. DeepSORT uses Kalman filtering (to predict where a person will move next) and deep appearance features to keep assigning the exact same track_id to a person even if they momentarily step behind an object or another shopper.

2. Feature Extraction & Analytics Processing Layer
Spatial ROI & Zone Verification

Checks whether the centroid coordinates (c 
x
​
 ,c 
y
​
 ) of each track_id reside within defined bounding polygons (e.g., Main Display Shelf Zone or Checkout Counter).

Explanation: Calculates the center point (c 
x
​
 ,c 
y
​
 ) of a tracked person's bounding box and tests whether it falls inside user-defined regions of interest (like the shelf area or register line).

Dwell Time Computation

Accumulates frame-level dwell counts for active track_ids within each zone and converts frame numbers into duration in seconds using video FPS.

Explanation: Measures how long a person remains inside a specific zone by incrementing frame counters and dividing by the video's frames-per-second (FPS) rate to calculate exact dwell time in seconds.

Demographic Classification

Crops person bounding boxes to pass through a lightweight demographic classifier (logging estimated age brackets and gender metrics).

Explanation: Crops out the person's bounding box region and runs it through a classifier model to estimate age group and gender for demographic telemetry.

Database Logging

Once a visitor's dwell threshold is reached, event details (track_id, gender, age_group, zone, dwell_seconds, timestamp) are persisted to retail_data.db via SQLAlchemy ORM.

Explanation: When a tracked individual spends enough time in a zone to meet the threshold, their complete session record is written into the SQLite database (retail_data.db) using SQLAlchemy.

3. Spatial Density & Heatmapping Layer
Coordinate Accumulation

Parallel to event logging, bottom-center foot coordinates (c 
x
​
 ,c 
y
​
 ) of all tracked individuals are continuously plotted onto a 2D float NumPy matrix representing the store floor layout.

Explanation: Tracks the bottom-center coordinates of each person's feet and plots those coordinates onto a 2D NumPy numerical grid to map spatial foot traffic across the floor layout.

Gaussian Smoothing & JET Colormap

Applies a 31×31 Gaussian kernel blur to transform point clusters into smooth density gradients, normalized into an 8-bit image and colormapped using OpenCV's COLORMAP_JET before saving as heatmap_output.png.

Explanation: Blurs the raw coordinate points with a Gaussian kernel to turn individual steps into smooth heat gradients, normalizes the intensities, applies a red-to-blue color scale (COLORMAP_JET), and saves the image as heatmap_output.png.

4. Serving & Visual Presentation Layer
FastAPI Backend (api.py)

Asynchronously exposes structured REST endpoints (/api/summary, /api/events, /api/copilot) to query database records without blocking computer vision processing loops.

Explanation: Hosts an asynchronous web server using FastAPI that serves database metrics over REST API endpoints, allowing the dashboard to read data without slowing down the video detection loop.

AI Retail Copilot (ai_copilot.py)

An automated heuristic engine evaluates floor metrics to produce dynamic operational suggestions (e.g., shelf display optimization or auxiliary queue alerts).

Explanation: Runs rule-based analytical checks on recorded store data to generate live operational alerts (e.g., flagging long checkout wait times or underperforming shelves).

Streamlit Dashboard (dashboard.py)

Feeds from the REST API to render real-time KPI cards, interactive Plotly charts (gender distribution pies and dwell time bar graphs), raw database logs, and the spatial movement heatmap.

Explanation: Connects to the FastAPI backend to render an interactive web interface displaying high-level store stats, visual graphs, raw event tables, and the saved movement heatmap image.
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
Quick Start Guide1. Environment SetupClone the repository and set up a Python virtual environment:Bashgit clone [https://github.com/suryanshvaish1/retail-intelligence-system.git](https://github.com/suryanshvaish1/retail-intelligence-system.git)
cd retail-intelligence-system

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# source venv/bin/activate   # Linux/macOS

# Install dependencies
python -m pip install ultralytics deep-sort-realtime opencv-python fastapi uvicorn sqlalchemy streamlit plotly requests reportlab pandas
2. Running the SystemExecute the core modules across three separate terminal windows:Terminal 1: Run Computer Vision PipelineProcesses video input, tracks visitors, writes records to retail_data.db, and outputs heatmap_output.png:Bashpython main_pipeline.py
Terminal 2: Start FastAPI Backend ServiceLaunches the REST API exposing analytics and copilot endpoints at http://127.0.0.1:8000:Bashuvicorn api:app --reload --port 8000
Terminal 3: Launch Streamlit DashboardStarts the interactive analytics dashboard at http://localhost:8501:Bashstreamlit run dashboard.py
3. Generate Executive PDF ReportTo compile an executive audit PDF summary from database records:Bashpython generate_report.py
API ReferenceEndpointMethodDescription/GETHealth check status and endpoint manifest/docsGETInteractive OpenAPI / Swagger UI documentation/api/summaryGETAggregated store KPIs (total visitors, avg dwell, demographics)/api/eventsGETComplete list of recorded visitor events/api/copilotGETAI Copilot operational recommendations and queue alerts
