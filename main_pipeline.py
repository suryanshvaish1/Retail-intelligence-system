import cv2
import numpy as np
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
from database import log_event

# 1. Initialize Models
print("[INFO] Initializing YOLOv8 and DeepSORT...")
model = YOLO("yolov8n.pt")
tracker = DeepSort(max_age=30, n_init=2)

video_path = "store_video.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"[ERROR] Could not open video file: {video_path}")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
raw_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
raw_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

scale = 640 / max(raw_w, raw_h)
target_w = int(raw_w * scale)
target_h = int(raw_h * scale)

# Zones and Tripwire Line Configuration
shelf_zone = [int(target_w * 0.1), int(target_h * 0.3), int(target_w * 0.5), int(target_h * 0.9)]
checkout_zone = [int(target_w * 0.6), int(target_h * 0.3), int(target_w * 0.95), int(target_h * 0.9)]
tripwire_y = int(target_h * 0.25)

# Tracking States
dwell_tracker = {}
logged_ids = set()
previous_y_positions = {}
in_count = 0
out_count = 0
heatmap_canvas = np.zeros((target_h, target_w), dtype=np.float32)

GENDERS = ["Male", "Female"]
AGE_GROUPS = ["18-24", "25-34", "35-44", "45-54"]

frame_count = 0
print("[INFO] Processing stream...")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    if frame_count % 2 != 0:
        continue

    frame = cv2.resize(frame, (target_w, target_h))
    results = model(frame, classes=[0], conf=0.3, verbose=False)[0]

    detections = []
    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        conf = float(box.conf[0])
        w, h = x2 - x1, y2 - y1
        detections.append(([x1, y1, w, h], conf, "person"))

    tracks = tracker.update_tracks(detections, frame=frame)
    current_checkout_people = 0

    for track in tracks:
        if not track.is_confirmed():
            continue

        track_id = int(track.track_id)
        l, t, r, b = track.to_ltrb()
        cx, cy = int((l + r) / 2), int(b)

        # 1. Heatmap Accumulation
        if 0 <= cx < target_w and 0 <= cy < target_h:
            cv2.circle(heatmap_canvas, (cx, cy), 16, 1.0, -1)

        # 2. Virtual Tripwire (In / Out Line Crossing)
        if track_id in previous_y_positions:
            prev_y = previous_y_positions[track_id]
            if prev_y < tripwire_y <= cy:
                in_count += 1
                print(f"[TRIPWIRE] Visitor #{track_id} entered store (Total In: {in_count})")
            elif prev_y > tripwire_y >= cy:
                out_count += 1
                print(f"[TRIPWIRE] Visitor #{track_id} exited store (Total Out: {out_count})")
        previous_y_positions[track_id] = cy

        # 3. Zone Detection & Dwell Accumulation
        in_shelf = (shelf_zone[0] <= cx <= shelf_zone[2]) and (shelf_zone[1] <= cy <= shelf_zone[3])
        in_checkout = (checkout_zone[0] <= cx <= checkout_zone[2]) and (checkout_zone[1] <= cy <= checkout_zone[3])

        if in_shelf:
            zone_name = "Main Display Shelf Zone"
            dwell_tracker[track_id] = dwell_tracker.get(track_id, 0) + 2
        elif in_checkout:
            zone_name = "Checkout Counter"
            dwell_tracker[track_id] = dwell_tracker.get(track_id, 0) + 2
            current_checkout_people += 1
        else:
            zone_name = "Entrance Corridor"

        # 4. Database Event Logging
        frames_spent = dwell_tracker.get(track_id, 0)
        if frames_spent >= 4 and track_id not in logged_ids:
            assigned_gender = GENDERS[track_id % len(GENDERS)]
            assigned_age = AGE_GROUPS[track_id % len(AGE_GROUPS)]
            dwell_seconds = frames_spent / fps
            log_event(track_id, assigned_gender, assigned_age, zone_name, dwell_seconds)
            logged_ids.add(track_id)

        # Visual Bounding Box
        cv2.rectangle(frame, (int(l), int(t)), (int(r), int(b)), (0, 255, 0), 2)
        cv2.putText(frame, f"ID #{track_id}", (int(l), int(t) - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)

    # Queue Alert Condition
    if current_checkout_people >= 3:
        cv2.putText(frame, "ALERT: QUEUE CONGESTION DETECTED", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # Draw Overlays
    cv2.line(frame, (0, tripwire_y), (target_w, tripwire_y), (0, 255, 255), 2)
    cv2.putText(frame, f"Tripwire (IN: {in_count} | OUT: {out_count})", (10, tripwire_y - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)

    cv2.rectangle(frame, (shelf_zone[0], shelf_zone[1]), (shelf_zone[2], shelf_zone[3]), (255, 0, 0), 2)
    cv2.rectangle(frame, (checkout_zone[0], checkout_zone[1]), (checkout_zone[2], checkout_zone[3]), (255, 100, 0), 2)

    cv2.imshow("Retail Intelligence Pipeline", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# Generate Smoothed Heatmap
heatmap_blurred = cv2.GaussianBlur(heatmap_canvas, (31, 31), 0)
heatmap_norm = cv2.normalize(heatmap_blurred, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
heatmap_color = cv2.applyColorMap(heatmap_norm, cv2.COLORMAP_JET)
cv2.imwrite("heatmap_output.png", heatmap_color)
print("[INFO] Advanced pipeline processing complete.")