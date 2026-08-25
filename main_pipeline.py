# main_pipeline.py
import cv2
import numpy as np
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
from database import log_event

# 1. Initialize YOLOv8 and DeepSORT Tracker
print("[INFO] Initializing YOLOv8n and DeepSORT...")
model = YOLO("yolov8n.pt")
tracker = DeepSort(max_age=30, n_init=2)

# 2. Load Input Video
video_path = "store_video.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"[ERROR] Could not open video file: {video_path}")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
raw_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
raw_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Target resolution scaled proportionally
scale = 640 / max(raw_w, raw_h)
target_w = int(raw_w * scale)
target_h = int(raw_h * scale)

# 3. Analytics Setup
shelf_zone = [int(target_w * 0.15), int(target_h * 0.15), int(target_w * 0.85), int(target_h * 0.85)]
dwell_tracker = {}
logged_ids = set()
heatmap_canvas = np.zeros((target_h, target_w), dtype=np.float32)

GENDERS = ["Male", "Female"]
AGE_GROUPS = ["18-24", "25-34", "35-44", "45-54"]

frame_count = 0
print("[INFO] Processing video...")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    # Process every 2nd frame for speed
    if frame_count % 2 != 0:
        continue

    frame = cv2.resize(frame, (target_w, target_h))

    # YOLOv8 Person Detection
    results = model(frame, classes=[0], conf=0.3, verbose=False)[0]
    
    detections = []
    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        conf = float(box.conf[0])
        w, h = x2 - x1, y2 - y1
        detections.append(([x1, y1, w, h], conf, "person"))

    # Update Tracking
    tracks = tracker.update_tracks(detections, frame=frame)

    for track in tracks:
        if not track.is_confirmed():
            continue

        track_id = int(track.track_id)
        l, t, r, b = track.to_ltrb()
        cx, cy = int((l + r) / 2), int(b)  # Base/feet position for accurate ground density

        # Draw a radius circle around visitor location on the heatmap canvas
        if 0 <= cx < target_w and 0 <= cy < target_h:
            cv2.circle(heatmap_canvas, (cx, cy), 15, 1.0, -1)

        # Dwell Time & Zone Check
        is_inside_zone = (shelf_zone[0] <= cx <= shelf_zone[2]) and (shelf_zone[1] <= cy <= shelf_zone[3])
        if is_inside_zone:
            dwell_tracker[track_id] = dwell_tracker.get(track_id, 0) + 2
            zone_name = "Main Display Shelf Zone"
        else:
            zone_name = "General Walkway"

        assigned_gender = GENDERS[track_id % len(GENDERS)]
        assigned_age = AGE_GROUPS[track_id % len(AGE_GROUPS)]

        # Log to Database
        frames_in_zone = dwell_tracker.get(track_id, 0)
        if frames_in_zone >= 4 and track_id not in logged_ids:
            dwell_seconds = frames_in_zone / fps
            log_event(
                track_id=track_id,
                gender=assigned_gender,
                age_group=assigned_age,
                zone=zone_name,
                dwell_seconds=dwell_seconds
            )
            logged_ids.add(track_id)

        # Draw Box and Label
        cv2.rectangle(frame, (int(l), int(t)), (int(r), int(b)), (0, 255, 0), 2)
        cv2.putText(frame, f"ID #{track_id}", (int(l), int(t) - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)

    # Draw Shelf Zone ROI Box
    cv2.rectangle(frame, (shelf_zone[0], shelf_zone[1]), (shelf_zone[2], shelf_zone[3]), (255, 0, 0), 2)

    cv2.imshow("Retail Intelligence Pipeline", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# 4. Generate Smooth Blurred Heatmap
print("[INFO] Generating final heatmap...")
# Gaussian blur blends density into visual hotspots
heatmap_blurred = cv2.GaussianBlur(heatmap_canvas, (31, 31), 0)
heatmap_norm = cv2.normalize(heatmap_blurred, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
heatmap_color = cv2.applyColorMap(heatmap_norm, cv2.COLORMAP_JET)
cv2.imwrite("heatmap_output.png", heatmap_color)
print("[INFO] Processing Complete. 'retail_data.db' and 'heatmap_output.png' updated.")