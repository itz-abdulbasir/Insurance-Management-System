import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def get_export_dir() -> str:
    """
    Returns the path to the 'IMS_Reports' folder in the user's Downloads directory.
    Creates the folder if it doesn't exist.
    """
    try:
        downloads_path = str(Path.home() / "Downloads")
        export_dir = os.path.join(downloads_path, "IMS_Reports")
        os.makedirs(export_dir, exist_ok=True)
        return export_dir
    except Exception:
        # Fallback to current directory if Downloads is inaccessible
        return os.getcwd()

def open_file(filepath: str):
    """
    Opens the specified file using the system's default application.
    """
    if sys.platform == "win32":
        os.startfile(filepath)
    elif sys.platform == "darwin":
        subprocess.call(["open", filepath])
    else:
        subprocess.call(["xdg-open", filepath])

def generate_table_report(title: str, headers: list, data: list, filename_prefix: str = "report", auto_open: bool = True) -> str:
    """
    Generates a PDF report containing a data table and saves it to the Downloads/IMS_Reports folder.
    :param title: The title of the report.
    :param headers: A list of column header strings.
    :param data: A list of rows (each row is a list of cell strings).
    :param filename_prefix: Prefix for the generated PDF filename.
    :param auto_open: Whether to automatically open the file after generation.
    :return: The absolute path to the generated PDF.
    """
    export_dir = get_export_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.pdf"
    filepath = os.path.join(export_dir, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontSize=18,
        spaceAfter=14,
        textColor=colors.HexColor("#1B4F72")
    )
    
    # Title & Timestamp
    elements.append(Paragraph(title, title_style))
    elements.append(Paragraph(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
    elements.append(Spacer(1, 20))
    
    # Table Data
    table_data = [headers] + data
    
    # Ensure all items in data are strings
    str_table_data = [[str(cell) if cell is not None else "" for cell in row] for row in table_data]
    
    t = Table(str_table_data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EBF5FB")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1B4F72")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#D5D8DC")),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    
    elements.append(t)
    
    # Build PDF
    doc.build(elements)
    
    if auto_open:
        open_file(filepath)
        
    return filepath

def generate_detailed_report(report_title: str, policy_data: dict, payment_data: list, request_data: dict, filename_prefix: str = "receipt") -> str:
    """
    Generates a multi-section PDF report for a specific claim or surrender.
    """
    export_dir = get_export_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.pdf"
    filepath = os.path.join(export_dir, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle("Title", parent=styles["Heading1"], fontSize=22, spaceAfter=20, textColor=colors.HexColor("#1B4F72"), alignment=1)
    section_style = ParagraphStyle("Section", parent=styles["Heading2"], fontSize=14, spaceBefore=15, spaceAfter=10, textColor=colors.HexColor("#2E86C1"), borderPadding=5)
    normal_style = styles["Normal"]
    
    # ── Header ──────────────────────────────────────────────────
    elements.append(Paragraph(report_title, title_style))
    elements.append(Paragraph(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ParagraphStyle("TS", parent=normal_style, alignment=1)))
    elements.append(Spacer(1, 30))
    
    # ── Section 1: Policy Information ───────────────────────────
    elements.append(Paragraph("1. Policy Information", section_style))
    policy_table_data = [
        ["Policy ID:", str(policy_data.get("policy_id")), "Plan Name:", str(policy_data.get("plan_name"))],
        ["Start Date:", str(policy_data.get("start_date")), "Status:", str(policy_data.get("status", "")).capitalize()],
        ["Total Installments:", str(policy_data.get("total_installments")), "Paid:", str(policy_data.get("paid_installments"))],
        ["Remaining:", str(int(policy_data.get("total_installments", 0)) - int(policy_data.get("paid_installments", 0))), "Coverage:", str(policy_data.get("coverage_amount"))]
    ]
    pt = Table(policy_table_data, colWidths=[110, 140, 110, 140])
    pt.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(pt)
    
    # ── Section 2: Payment History ──────────────────────────────
    elements.append(Paragraph("2. Payment History", section_style))
    if payment_data:
        headers = ["Date & Time", "Amount Paid", "Status"]
        hist_data = [[p.get("paid_date", "—"), p.get("amount", "0.00"), "Paid"] for p in payment_data]
        ht = Table([headers] + hist_data, colWidths=[200, 150, 150])
        ht.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EBF5FB")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1B4F72")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(ht)
    else:
        elements.append(Paragraph("No payment history found.", normal_style))
        
    # ── Section 3: Request/Settlement Details ───────────────────
    elements.append(Paragraph(f"3. {request_data.get('type')} Details", section_style))
    req_table_data = []
    if request_data.get("type") == "Claim":
        req_table_data = [
            ["Claim ID:", str(request_data.get("id"))],
            ["Requested At:", str(request_data.get("requested_at"))],
            ["Resolved At:", str(request_data.get("resolved_at", "Pending"))],
            ["Amount Requested:", str(request_data.get("amount"))],
            ["Reason:", str(request_data.get("reason"))],
            ["Status:", str(request_data.get("status", "")).capitalize()]
        ]
    else: # Surrender
        req_table_data = [
            ["Surrender ID:", str(request_data.get("id"))],
            ["Surrendered Date:", str(request_data.get("requested_at"))],
            ["Surrender Value:", str(request_data.get("amount"))],
            ["Reason:", str(request_data.get("reason"))],
            ["Status:", "Immediate Settlement"]
        ]
        
    rt = Table(req_table_data, colWidths=[150, 350])
    rt.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(rt)
    
    # Build
    doc.build(elements)
    open_file(filepath)
    return filepath

