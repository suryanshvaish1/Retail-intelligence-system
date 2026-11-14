# 🛒 Autonomous Retail Intelligence System

An end-to-end **Edge AI and Computer Vision platform** that converts CCTV/store footage into real-time, actionable retail intelligence.

The system detects and tracks visitors, calculates zone-specific dwell times, analyzes estimated demographics, generates 2D foot-traffic heatmaps, exposes analytics through REST APIs, and provides an interactive executive dashboard with automated operational insights.

🎥 **[Watch Live System Demo](https://1drv.ms/v/c/8db0741b659a15e5/IQBv2A0uQMopRphrxK-tGT2NAcsuJP_YEkLUymK3AzJpt6I?e=eYqY8s)**

---

## 📌 Overview

The **Autonomous Retail Intelligence System** combines computer vision, multi-object tracking, spatial analytics, backend APIs, and business intelligence into a single platform.

It transforms raw CCTV footage into useful retail metrics, including:

- 👥 Visitor count and movement
- 🎯 Person detection and tracking
- 📍 Zone-specific visitor activity
- ⏱️ Customer dwell time
- 🧑‍🤝‍🧑 Estimated age-group and gender distribution
- 🗺️ Foot-traffic heatmaps
- 📊 Store performance analytics
- 🤖 Automated operational recommendations
- 📄 Executive PDF reports

---

## 🏗️ System Architecture

![System Architecture Flowchart](docs/flowchart.png)

```mermaid
flowchart TD
    A[Video File / Webcam / IP Camera] --> B[Frame Reader - OpenCV]
    B --> C[Person Detection - YOLOv8]
    C --> D[Tracking - DeepSORT]

    D --> E[Crop Tracked Person]
    E --> F[Age & Gender Classification]
    E --> G[Zone / ROI Detection]

    F --> H[Analytics Processing]
    G --> H
    H --> I[(SQLite Database)]

    D --> J[Track Position]
    J --> K[Heatmap Accumulation]
    K --> L[Heatmap Image]

    I --> M[FastAPI Backend]
    M --> N[REST API]
    N --> O[Streamlit Dashboard]
    L --> O

    M --> P[AI Retail Copilot]
    P --> O
```

## 🔍 Architecture & Processing Pipeline

The system is organized into four major layers.

### 1. 🎥 Ingestion & Perception Layer

#### Video Ingestion

The system supports:

- Pre-recorded MP4 video
- USB webcam
- RTSP/IP camera streams

Frames are captured sequentially using OpenCV's `VideoCapture`.

#### Person Detection — YOLOv8

Each frame is processed using a pretrained YOLOv8 object-detection model.

The pipeline:

1. Processes the current video frame.
2. Detects objects in the frame.
3. Filters detections to the person class.
4. Extracts bounding boxes and confidence scores.

#### Multi-Object Tracking — DeepSORT

Detected people are passed to DeepSORT.

DeepSORT assigns a unique `track_id` to each tracked person and attempts to maintain that identity across consecutive frames.

For example, the person detected in frame 500 can be associated with the same person in frame 501.

Tracking can also help maintain identity during temporary occlusion.

### 2. 🧠 Feature Extraction & Analytics Layer

#### Spatial ROI / Zone Detection

The system calculates a representative point for each tracked person's bounding box, such as its bottom-center point.

This coordinate is checked against predefined Regions of Interest (ROIs).

Example store zones:

```text
+---------------------------------------+
|                                       |
|              SHELF AREA               |
|                                       |
|        [ Zone 1 / Products ]          |
|                                       |
|                                       |
|------------- CUSTOMER AREA -----------|
|                                       |
|               CHECKOUT                |
+---------------------------------------+
```

This allows the system to determine whether a visitor is currently inside a configured store zone.

#### ⏱️ Dwell-Time Calculation

The system tracks how long each visitor remains inside a particular zone.

A basic frame-based calculation is:

```text
Dwell Time = Frames Spent in Zone / Video FPS

Example:
FPS = 30
Frames in Zone = 300

Dwell Time = 300 / 30
            = 10 seconds
```

When the configured threshold is reached, the visitor session can be persisted to the database.

Example event:

```text
Track ID     : 42
Zone         : Shelf Area
Gender       : Male (estimated)
Age Group    : Adult (estimated)
Dwell Time   : 18.5 seconds
Timestamp    : 2026-10-08 10:30:21
```

#### 🧑 Demographic Classification

The system crops the tracked person's bounding box and passes it through a pretrained classification model.

The model estimates:

- Gender
- Age group

These predictions are stored as telemetry associated with the visitor's tracking session.

**Note:** Demographic predictions are model estimates, not verified personal attributes. Their accuracy can vary with camera placement, lighting, occlusion, and model limitations.

#### 🗄️ Database Logging

Processed events are persisted using:

- SQLite
- SQLAlchemy ORM

Example event fields:

| Field | Description |
|---|---|
| `track_id` | Unique tracked visitor ID |
| `gender` | Estimated gender classification |
| `age_group` | Estimated age group |
| `zone` | Store zone |
| `dwell_seconds` | Time spent in the zone |
| `timestamp` | Event timestamp |

Database file: `retail_data.db`

### 3. 🗺️ Spatial Density & Heatmap Layer

The system continuously records the movement coordinates of tracked visitors.

For every tracked person, the pipeline captures an approximate bottom-center point of the bounding box, representing the visitor's floor position.

These coordinates are accumulated into a 2D NumPy grid.

#### Heatmap Processing

```text
Visitor Coordinates
        ↓
2D NumPy Grid
        ↓
Gaussian Smoothing
        ↓
Intensity Normalization
        ↓
OpenCV JET Colormap
        ↓
heatmap_output.png
```

The resulting heatmap helps identify:

- High-traffic areas
- Low-traffic areas
- Product-browsing zones
- Potential customer bottlenecks
- Checkout congestion
- Underutilized store space

Typical JET colormap interpretation:

```text
Low traffic  → Blue
              Green
              Yellow
High traffic → Red
```

### 4. 🌐 Serving & Presentation Layer

#### FastAPI Backend

The FastAPI service provides a decoupled REST interface for accessing analytics.

Main endpoints:

```text
GET /
GET /api/summary
GET /api/events
GET /api/copilot
```

This separation means the dashboard does not need to interact directly with the computer-vision processing loop.

#### 🤖 AI Retail Copilot

The AI Retail Copilot analyzes recorded store data and generates operational recommendations.

Example:

```text
⚠ High checkout dwell time detected.

Recommendation:
Consider opening an additional checkout counter
during peak traffic periods.
```

Other possible insights include:

- High visitor dwell time
- Underperforming zones
- High-traffic areas
- Checkout congestion
- Low customer engagement
- Potential staffing requirements

The current implementation uses **rule-based analytical logic** to convert store telemetry into actionable recommendations. It is not currently an LLM-based system.

#### 📊 Streamlit Executive Dashboard

The Streamlit dashboard provides an interactive interface for viewing store analytics.

The dashboard includes:

**Store Overview**
- Total visitors
- Average dwell time
- Zone activity
- Estimated demographic distribution

**Analytics Charts**
- Visitor distribution
- Dwell times
- Zone activity
- Demographic estimates

**Heatmap**
- Displays `heatmap_output.png` for spatial movement analysis.

**Event Logs**
- Displays individual visitor events in a detailed table.

**CSV Export**
- Allows processed event data to be exported for further analysis.

---

## 📊 Dashboard Features

### 1. Store Analytics Overview

Provides an executive-level summary of store activity.

Key metrics include:

- Total visitors
- Average dwell time
- Zone activity
- Estimated gender distribution
- Estimated age distribution

### 2. AI Retail Copilot

Identifies potential operational issues and provides recommendations.

Example:

```text
🚨 Checkout congestion detected

Average checkout dwell time:
42 seconds

Suggested action:
Increase checkout capacity during peak hours.
```

### 3. Spatial Foot-Traffic Heatmap

Visualizes visitor movement throughout the store.

This can help identify:

- Customer hotspots
- Low-traffic areas
- Congested areas
- Product-placement opportunities
- Store-layout optimization opportunities

### 4. Demographic & Dwell Analysis

Provides analytics based on visitor sessions.

Example:

```text
Estimated Gender Distribution
-----------------------------
Male       52%
Female     48%

Average Dwell Time
------------------
Shelf Area       21.4 sec
Checkout         34.7 sec
```

These demographic values are estimates produced by the classification model.

### 5. Raw Event Logs

Provides access to individual tracking events.

| Track ID | Zone | Gender (estimated) | Age group (estimated) | Dwell |
|---:|---|---|---|---:|
| 1 | Shelf | Male | Adult | 18.2s |
| 2 | Checkout | Female | Adult | 35.4s |
| 3 | Shelf | Male | Young Adult | 12.7s |

The data can also be exported as CSV for additional analysis.

---

## ✨ Key Features

- 🎯 Real-time person detection using YOLOv8
- 🧭 Multi-object tracking using DeepSORT
- 📍 Zone / ROI detection
- ⏱️ Visitor dwell-time analytics
- 🧑 Estimated demographic classification
- 🗺️ 2D foot-traffic heatmaps
- 🗄️ SQLite event storage
- ⚡ FastAPI REST backend
- 📊 Interactive Streamlit dashboard
- 🤖 Rule-based AI Retail Copilot
- 📄 Automated PDF reporting
- 📥 CSV event export
- 🔌 Decoupled computer-vision and dashboard architecture

---

## 🛠️ Technology Stack

| Category | Technology |
|---|---|
| Programming Language | Python |
| Computer Vision | OpenCV |
| Object Detection | Ultralytics YOLOv8 |
| Object Tracking | DeepSORT |
| Numerical Processing | NumPy |
| Data Analysis | Pandas |
| Backend | FastAPI |
| API Server | Uvicorn |
| ORM | SQLAlchemy |
| Database | SQLite |
| Dashboard | Streamlit |
| Visualization | Plotly Express |
| Reporting | ReportLab |
| Environment | Python Virtual Environment |

---

## 💻 Hardware Requirements & Edge Setup

Because the system runs YOLOv8 object detection, DeepSORT tracking, and demographic classification, hardware selection can directly affect inference frame rate (FPS) and real-time responsiveness.

### 1. Compute Specifications

| Component | Minimum (Offline/Demo Mode) | Recommended (Real-Time/Multi-Stream) |
|---|---|---|
| CPU | 4-Core Intel Core i5 / AMD Ryzen 5 | 8-Core+ Intel Core i7/i9 / AMD Ryzen 7/9 |
| GPU | Integrated Graphics (CPU Inference) | NVIDIA GPU with CUDA support, such as RTX 3060 with 6GB+ VRAM |
| RAM | 8 GB | 16–32 GB |
| Storage | 10 GB free, SSD recommended | 50 GB+ NVMe SSD |
| OS | Windows 10/11, Ubuntu 20.04+, macOS | Ubuntu 22.04 LTS or Windows 11 for supported CUDA setups |

Actual requirements depend on video resolution, number of camera streams, model sizes, and target FPS.

### 2. Camera & Sensor Hardware

For live in-store deployment:

- **IP/CCTV Cameras:** 1080p Full HD at approximately 30 FPS, supporting RTSP or ONVIF-compatible streaming.
- **USB Webcams:** Standard 720p/1080p UVC-compliant cameras for local testing.
- **Mounting and Placement:** An overhead or elevated angled mount can reduce shopper occlusion and improve floor-position estimates used for ROI and heatmap mapping.

A suggested starting point is 2.5–3.5 metres high with a 30°–45° downward angle. The final setup should be calibrated to the store layout.

### 3. Edge AI Deployment Targets

The lightweight architecture (for example, YOLOv8n/YOLOv8s with SQLite) can be adapted to run on compact edge-compute nodes inside a retail store.

Potential deployment targets:

- **NVIDIA Jetson Orin Nano / Jetson Xavier NX:** Potential options for edge inference, depending on model size, stream count, and optimization.
- **Industrial Mini PCs:** Systems such as Intel NUC-class devices or mini PCs with a suitable NVIDIA GPU can host the CV pipeline, FastAPI, and dashboard.
- **Network Infrastructure:** Gigabit Ethernet and a PoE switch are useful for IP-camera deployments requiring reliable, low-latency RTSP ingestion.

---

## 📁 Project Structure

```text
retail-intelligence-system/
│
├── docs/
│   ├── flowchart.png
│   ├── dashboard_top.png
│   ├── dashboard_middle.png
│   └── dashboard_bottom.png
│
├── database.py
├── main_pipeline.py
├── api.py
├── dashboard.py
├── ai_copilot.py
├── generate_report.py
│
├── store_video.mp4
├── retail_data.db
└── heatmap_output.png
```

### File Responsibilities

| File | Responsibility |
|---|---|
| `main_pipeline.py` | Video processing, YOLOv8 detection, DeepSORT tracking, analytics, and heatmap generation |
| `database.py` | SQLite database schema and SQLAlchemy event logging |
| `api.py` | FastAPI application and REST endpoints |
| `ai_copilot.py` | Retail operational analysis and recommendations |
| `dashboard.py` | Streamlit executive dashboard |
| `generate_report.py` | Generates executive PDF reports |
| `store_video.mp4` | Input video source |
| `retail_data.db` | Generated event database |
| `heatmap_output.png` | Generated visitor-movement heatmap |

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/suryanshvaish1/retail-intelligence-system.git

cd retail-intelligence-system
```

### 2. Create a Virtual Environment

**Windows PowerShell**

```powershell
python -m venv venv

.\venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
python3 -m venv venv

source venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install ultralytics deep-sort-realtime opencv-python fastapi uvicorn sqlalchemy streamlit plotly requests reportlab pandas
```

For NVIDIA GPU acceleration, install a CUDA-enabled PyTorch build compatible with your CUDA environment and the installed Ultralytics version.

---

## ▶️ Running the System

The system uses three primary processes.

Open three separate terminals and activate the virtual environment in each one.

### Terminal 1 — Computer Vision Pipeline

Run the AI processing pipeline:

```bash
python main_pipeline.py
```

This process:

1. Reads the input video.
2. Detects people using YOLOv8.
3. Tracks people using DeepSORT.
4. Calculates zone activity.
5. Computes dwell times.
6. Performs demographic classification.
7. Stores events in SQLite.
8. Generates the movement heatmap.

Generated files:

```text
retail_data.db
heatmap_output.png
```

### Terminal 2 — FastAPI Backend

Start the REST API:

```bash
uvicorn api:app --reload --port 8000
```

The API will be available at:

- Base API: `http://127.0.0.1:8000`
- Interactive Swagger Documentation: `http://127.0.0.1:8000/docs`

### Terminal 3 — Streamlit Dashboard

Start the dashboard:

```bash
streamlit run dashboard.py
```

The dashboard will normally be available at:

`http://localhost:8501`

---

## 📄 Generate Executive PDF Report

After processing the video and generating database records, run:

```bash
python generate_report.py
```

This generates an executive-style PDF report containing summarized retail analytics.

---

## 📡 REST API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | API health check and endpoint information |
| `/docs` | GET | Interactive Swagger/OpenAPI documentation |
| `/api/summary` | GET | Aggregated store KPIs |
| `/api/events` | GET | Recorded visitor events |
| `/api/copilot` | GET | Operational recommendations |

### `GET /api/summary`

Returns aggregated store analytics.

Example response:

```json
{
  "total_visitors": 42,
  "average_dwell_seconds": 24.7,
  "male_percentage": 52,
  "female_percentage": 48
}
```

### `GET /api/events`

Returns individual visitor event records.

Example response:

```json
[
  {
    "track_id": 1,
    "zone": "Shelf Area",
    "gender": "Male",
    "age_group": "Adult",
    "dwell_seconds": 18.4
  }
]
```

### `GET /api/copilot`

Returns operational recommendations generated from store analytics.

Example response:

```json
{
  "alerts": [
    "High checkout dwell time detected",
    "Shelf Area has unusually high visitor activity"
  ]
}
```

---

## 🔄 End-to-End Data Flow

```text
                  CCTV / Video
                       │
                       ▼
               OpenCV Frame Reader
                       │
                       ▼
                 YOLOv8 Detection
                       │
                       ▼
                    DeepSORT
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
      Visitor Analytics     Movement Data
             │                   │
       ┌─────┼─────┐             ▼
       ▼     ▼     ▼       Heatmap Engine
      Zone  Dwell  Demographic  │
       │     │     │             ▼
       └─────┴─────┘      heatmap_output.png
             │
             ▼
          SQLite DB
             │
             ▼
         FastAPI API
             │
             ▼
      Streamlit Dashboard
             │
             ▼
       Executive Insights
```

---

## 🎯 Business Use Cases

### Store Layout Optimization

Identify areas receiving high or low customer traffic and use those patterns to inform product placement and store-layout decisions.

### Customer Engagement

Measure how long visitors spend in specific product areas.

### Checkout Monitoring

Identify long dwell times around checkout areas and detect potential congestion.

### Staffing Optimization

Use traffic patterns to understand when additional employees may be required.

### Product Placement Analysis

Compare visitor activity around different store zones.

### Customer Journey Analysis

Analyze movement between different store areas using tracked visitor trajectories.

### Executive Reporting

Generate summarized analytics and reports for store managers and business stakeholders.

---

## 🔐 Privacy & Responsible AI

This project is intended as a technical retail-analytics prototype.

The demographic classification component produces model-based estimates and should not be considered verified personal information.

For production deployments, additional considerations should be implemented:

- Appropriate customer consent and notification
- Compliance with applicable privacy regulations
- Secure data storage and transmission
- Data-retention and deletion policies
- Role-based access control
- Model-accuracy evaluation
- Bias and fairness evaluation
- Appropriate handling of CCTV footage
- Clear policies for access to and use of analytics

Where possible, production deployments should minimize the retention of identifiable video and use aggregated analytics for reporting.

---

## 📈 Future Improvements

Potential improvements include:

- 🔴 Live CCTV/IP camera streaming
- 🧠 More advanced customer-behavior analysis
- 📦 Product detection and shelf monitoring
- 🛍️ Product-level interaction tracking
- 🚨 Real-time anomaly detection
- 📱 Mobile analytics dashboard
- ☁️ Cloud-based deployment
- 🔔 Real-time alerts through Slack/email
- 🧠 LLM-powered retail analytics
- 📊 Historical trend analysis
- 👥 Customer-journey visualization
- ⚡ TensorRT / ONNX edge-GPU optimization
- 🔄 Real-time streaming analytics
- 🏬 Multi-store analytics

---

## 🧪 Example Analytics Pipeline

A typical visitor session can look like this:

```text
Visitor enters store
        ↓
YOLO detects person
        ↓
DeepSORT assigns Track ID = 17
        ↓
Visitor enters Shelf Zone
        ↓
System starts dwell timer
        ↓
Visitor remains for 22.6 seconds
        ↓
Demographic model estimates attributes
        ↓
Event stored in SQLite
        ↓
Movement coordinates added to heatmap
        ↓
FastAPI exposes analytics
        ↓
Streamlit displays metrics
        ↓
Retail Copilot generates operational insight
```

---

## 📊 Project Output

After successfully running the pipeline, the system produces:

```text
retail_data.db
    │
    ├── Visitor Events
    ├── Zone Analytics
    ├── Dwell Times
    └── Demographic Telemetry

heatmap_output.png
    │
    └── Visitor Foot-Traffic Visualization
```

The dashboard combines these outputs into an executive retail-intelligence interface.

---

## 📜 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Suryansh Vaish**

- GitHub: [suryanshvaish1](https://github.com/suryanshvaish1)
- Repository: [retail-intelligence-system](https://github.com/suryanshvaish1/retail-intelligence-system)
- Demo Video: [Watch on OneDrive](https://1drv.ms/v/c/8db0741b659a15e5/IQBv2A0uQMopRphrxK-tGT2NAcsuJP_YEkLUymK3AzJpt6I?e=eYqY8s)

---

## ⭐ If You Find This Project Useful

Consider giving the repository a ⭐ on GitHub.
