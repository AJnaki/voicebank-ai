import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from app.services.adapters.base import Transaction


def generate_statement_pdf(
    user_name: str,
    account_number: str,
    bank_name: str,
    transactions: list[Transaction],
    month_label: str,
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75 * inch)
    styles = getSampleStyleSheet()
    elements = []

    # Header
    header_style = ParagraphStyle("header", fontSize=18, spaceAfter=4, textColor=colors.HexColor("#1a237e"))
    elements.append(Paragraph(bank_name, header_style))
    elements.append(Paragraph("Account Statement", styles["Heading2"]))
    elements.append(Spacer(1, 0.1 * inch))

    # Account info
    info_data = [
        ["Account Holder:", user_name],
        ["Account Number:", account_number],
        ["Statement Period:", month_label],
        ["Generated:", datetime.now().strftime("%d %b %Y, %H:%M")],
    ]
    info_table = Table(info_data, colWidths=[2 * inch, 4 * inch])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.2 * inch))

    # Transactions table
    elements.append(Paragraph("Transactions", styles["Heading3"]))
    elements.append(Spacer(1, 0.05 * inch))

    tx_data = [["Date", "Description", "Category", "Amount"]]
    running = 0.0
    for t in transactions:
        running += t.amount
        sign = "" if t.amount >= 0 else "-"
        tx_data.append([
            t.date,
            t.description,
            t.category,
            f"{sign}${abs(t.amount):.2f}",
        ])
    tx_data.append(["", "", "Closing Balance", f"${running:.2f}"])

    tx_table = Table(tx_data, colWidths=[1.2 * inch, 3 * inch, 1.4 * inch, 1.2 * inch])
    tx_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a237e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f5f5f5")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e8eaf6")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ALIGN", (3, 0), (3, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(tx_table)
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(
        "This is a system-generated statement. For queries, contact your nearest branch.",
        styles["Italic"],
    ))

    doc.build(elements)
    return buffer.getvalue()
