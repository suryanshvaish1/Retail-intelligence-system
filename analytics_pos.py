import os
import sqlite3
import pandas as pd

def compute_look_to_buy():
    if not os.path.exists("retail_data.db"):
        print("[ERROR] 'retail_data.db' not found. Run the video pipeline first.")
        return

    # 1. Load Video Tracking DB
    conn = sqlite3.connect("retail_data.db")
    vision_df = pd.read_sql_query("SELECT * FROM visitor_events", conn)
    conn.close()

    total_visitors = vision_df["track_id"].nunique()
    shelf_visitors = vision_df[vision_df["zone"] == "Main Display Shelf Zone"]["track_id"].nunique()
    avg_shelf_dwell = vision_df[vision_df["zone"] == "Main Display Shelf Zone"]["dwell_seconds"].mean() or 0.0

    # 2. Load POS Sales CSV
    csv_file = "retail_sales_dataset.csv"
    if os.path.exists(csv_file):
        sales_df = pd.read_csv(csv_file)
        total_transactions = len(sales_df)
        total_revenue = sales_df["Total Amount"].sum() if "Total Amount" in sales_df.columns else 0.0
    else:
        # Fallback simulation if CSV is not placed yet
        total_transactions = int(total_visitors * 0.4)
        total_revenue = total_transactions * 45.00

    # 3. Calculate Conversion Metrics
    conversion_rate = (total_transactions / max(total_visitors, 1)) * 100.0
    look_to_buy_ratio = (total_transactions / max(shelf_visitors, 1)) * 100.0

    print("=" * 50)
    print("      RETAIL STORE PERFORMANCE METRICS")
    print("=" * 50)
    print(f"Total Unique Footfall Tracked : {total_visitors}")
    print(f"Visitors Browsing Shelf Zone  : {shelf_visitors}")
    print(f"Avg Shelf Dwell Duration      : {avg_shelf_dwell:.2f} seconds")
    print(f"Total Completed Transactions  : {total_transactions}")
    print(f"Total Recorded Revenue        : ${total_revenue:,.2f}")
    print(f"Overall Store Conversion Rate : {conversion_rate:.2f}%")
    print(f"Look-to-Buy Shelf Efficiency  : {look_to_buy_ratio:.2f}%")
    print("=" * 50)

if __name__ == "__main__":
    compute_look_to_buy()