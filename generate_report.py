import os
import sqlite3
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_report(output_pdf="Retail_Executive_Report.pdf"):
    # 1. Fetch DB Stats
    if not os.path.exists("retail_data.db"):
        print("[ERROR] retail_data.db not found.")
        return

    conn = sqlite3.connect("retail_data.db")
    df = pd.read_sql_query("SELECT * FROM visitor_events", conn)
    conn.close()

    total_visitors = df["track_id"].nunique() if not df.empty else 0
    avg_dwell = df["dwell_seconds"].mean() if not df.empty else 0.0

    # 2. Build PDF Document
    doc = SimpleDocTemplate(output_pdf, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=20, leading=24, textColor=colors.HexColor('#1E293B'))
    story.append(Paragraph("Autonomous Retail Intelligence System - Store Audit", title_style))
    story.append(Paragraph(f"Generated on: <b>{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</b>", styles['Normal']))
    story.append(Spacer(1, 15))

    # 3. Metric KPI Table
    kpi_data = [
        ["Total Visitors Tracked", "Average Dwell Time", "Top Monitored Zone"],
        [f"{total_visitors}", f"{avg_dwell:.2f} s", "Main Display Shelf Zone"]
    ]
    kpi_table = Table(kpi_data, colWidths=[175, 175, 175])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#F1F5F9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1'))
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 20))

    # 4. Insert Heatmap Image
    story.append(Paragraph("<b>Store Foot-Traffic Density Map</b>", styles['Heading2']))
    if os.path.exists("heatmap_output.png"):
        story.append(Image("heatmap_output.png", width=480, height=270))
    else:
        story.append(Paragraph("<i>Heatmap file not found.</i>", styles['Normal']))
    story.append(Spacer(1, 15))

    # 5. Recent Visitor Events Table
    story.append(Paragraph("<b>Recent Visitor Events Log</b>", styles['Heading2']))
    table_rows = [["Track ID", "Gender", "Age Group", "Zone", "Dwell (s)"]]
    for _, row in df.tail(8).iterrows():
        table_rows.append([str(row['track_id']), str(row['gender']), str(row['age_group']), str(row['zone']), f"{row['dwell_seconds']:.2f}"])

    events_table = Table(table_rows, colWidths=[70, 90, 90, 180, 70])
    events_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#475569')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(events_table)

    doc.build(story)
    print(f"[INFO] Successfully generated PDF report: {output_pdf}")

if __name__ == "__main__":
    generate_pdf_report()