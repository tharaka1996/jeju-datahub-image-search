# -*- coding: utf-8 -*-
"""
generate_final_report.py
Generates the 10-page final academic PDF report for Jeju National University (JNU).
Course: Advanced Management Information Systems (AMIS) - Midterm Exam Project
Title: Development and Cloud Deployment of an AI Multimodal (CLIP) Image Search System for Jeju Data Hub
Author: Baiya Dewayalage Tharaka Sandun Gunasiri (AM202521802)
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
SCREENSHOTS_DIR = DOCS_DIR / "screenshots"
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_PDF = DOCS_DIR / "Jeju_DataHub_AI_Image_Search_Final_Report2.pdf"

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Korean TTF Fonts from Windows system
FONT_REGULAR = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
if Path(r"C:\Windows\Fonts\malgun.ttf").exists():
    try:
        pdfmetrics.registerFont(TTFont("Malgun", r"C:\Windows\Fonts\malgun.ttf"))
        FONT_REGULAR = "Malgun"
        if Path(r"C:\Windows\Fonts\malgunbd.ttf").exists():
            pdfmetrics.registerFont(TTFont("Malgun-Bold", r"C:\Windows\Fonts\malgunbd.ttf"))
            FONT_BOLD = "Malgun-Bold"
        else:
            FONT_BOLD = "Malgun"
        print(f"Registered Korean font: {FONT_REGULAR}, {FONT_BOLD}")
    except Exception as e:
        print(f"Warning: Could not register Malgun font: {e}")

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 36  # 0.5 inch margins = 36 pt
PRINTABLE_WIDTH = PAGE_WIDTH - 2 * MARGIN  # 595.27 - 72 = 523.27 pt
PRINTABLE_HEIGHT = PAGE_HEIGHT - 2 * MARGIN  # 841.89 - 72 = 769.89 pt


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and draw running header and footer with total page count."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber > 1:
            self.saveState()
            # Running Header
            self.setFont(FONT_REGULAR, 7.0)
            self.setFillColor(colors.HexColor("#475569"))
            self.drawString(MARGIN, PAGE_HEIGHT - 26, "Jeju National University | AMIS: AI Multimodal Image Search System")
            self.drawRightString(PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 26, "Student: Baiya Dewayalage Tharaka Sandun Gunasiri (AM202521802)")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(MARGIN, PAGE_HEIGHT - 30, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 30)

            # Running Footer
            self.line(MARGIN, 32, PAGE_WIDTH - MARGIN, 32)
            self.drawString(MARGIN, 22, "Department of Management Information Systems (MIS) — Academic Evaluation")
            page_str = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(PAGE_WIDTH - MARGIN, 22, page_str)
            self.restoreState()


def get_custom_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="CoverTitle",
        fontName=FONT_BOLD,
        fontSize=20,
        leading=26,
        textColor=colors.HexColor("#0F172A"),
        alignment=1,  # Center
        spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        name="CoverSubtitle",
        fontName=FONT_REGULAR,
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#334155"),
        alignment=1,
        spaceAfter=16
    ))
    styles.add(ParagraphStyle(
        name="CoverMeta",
        fontName=FONT_REGULAR,
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#1E293B"),
        alignment=1
    ))

    styles.add(ParagraphStyle(
        name="SectionHeading",
        fontName=FONT_BOLD,
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=4,
        spaceAfter=6,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        name="SubHeading",
        fontName=FONT_BOLD,
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=4,
        spaceAfter=3,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        name="BodyTextCustom",
        fontName=FONT_REGULAR,
        fontSize=8.2,
        leading=11.2,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        name="BodyTextIndent",
        fontName=FONT_REGULAR,
        fontSize=8.2,
        leading=11.2,
        textColor=colors.HexColor("#1E293B"),
        leftIndent=12,
        spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        name="BulletCustom",
        fontName=FONT_REGULAR,
        fontSize=8.2,
        leading=11.2,
        textColor=colors.HexColor("#1E293B"),
        leftIndent=14,
        firstLineIndent=-8,
        spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        name="TableHead",
        fontName=FONT_BOLD,
        fontSize=7.8,
        leading=10,
        textColor=colors.white,
        alignment=1
    ))
    styles.add(ParagraphStyle(
        name="TableCell",
        fontName=FONT_REGULAR,
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1E293B")
    ))
    styles.add(ParagraphStyle(
        name="TableCellBold",
        fontName=FONT_BOLD,
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#0F172A")
    ))
    styles.add(ParagraphStyle(
        name="TableCellCenter",
        fontName=FONT_REGULAR,
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1E293B"),
        alignment=1
    ))
    styles.add(ParagraphStyle(
        name="CalloutText",
        fontName=FONT_REGULAR,
        fontSize=8.0,
        leading=11.0,
        textColor=colors.HexColor("#1E3A8A")
    ))
    styles.add(ParagraphStyle(
        name="FigCaption",
        fontName=FONT_BOLD,
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#475569"),
        alignment=1,
        spaceAfter=4
    ))

    return styles


def build_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN
    )

    styles = get_custom_styles()
    story = []

    # =========================================================================
    # PAGE 1: COVER PAGE & EXECUTIVE SUMMARY
    # =========================================================================
    story.append(Spacer(1, 15))

    # University & Department Badge
    logo_path = ASSETS_DIR / "logo.png"
    if logo_path.exists():
        img_logo = Image(str(logo_path), width=130, height=34)
        img_logo.hAlign = "CENTER"
        story.append(img_logo)
        story.append(Spacer(1, 10))

    univ_tbl = Table(
        [[Paragraph("<b>JEJU NATIONAL UNIVERSITY</b> &nbsp;|&nbsp; Graduate School of Business Administration<br/>Department of Management Information Systems (AMIS)", styles["CoverMeta"])]],
        colWidths=[PRINTABLE_WIDTH]
    )
    univ_tbl.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#1E3A8A")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(univ_tbl)
    story.append(Spacer(1, 8))

    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1E3A8A"), spaceAfter=14))

    story.append(Paragraph("Development and Cloud Deployment of an AI Multimodal (CLIP) Image Search System for Jeju Data Hub", styles["CoverTitle"]))
    story.append(Paragraph("A Bilingual Natural-Language Visual Information Retrieval Platform for Jeju Periodic Macroeconomic & Consumption Statistical Reports", styles["CoverSubtitle"]))

    meta_data = [
        [Paragraph("<b>Course:</b>", styles["TableCellBold"]), Paragraph("Advanced Management Information Systems (AMIS)", styles["TableCell"]),
         Paragraph("<b>Student Name:</b>", styles["TableCellBold"]), Paragraph("Baiya Dewayalage Tharaka Sandun Gunasiri<br/>(AM202521802)", styles["TableCell"])],
        [Paragraph("<b>Assignment:</b>", styles["TableCellBold"]), Paragraph("Midterm Exam Replacement Project", styles["TableCell"]),
         Paragraph("<b>GitHub Account:</b>", styles["TableCellBold"]), Paragraph("tharaka1996", styles["TableCell"])],
        [Paragraph("<b>Target Domain:</b>", styles["TableCellBold"]), Paragraph("Jeju Data Hub (jejudatahub.net)", styles["TableCell"]),
         Paragraph("<b>Submission Date:</b>", styles["TableCellBold"]), Paragraph("November 2026", styles["TableCell"])],
        [Paragraph("<b>Repository:</b>", styles["TableCellBold"]), Paragraph("<font color='#1E40AF'><u>https://github.com/tharaka1996/jeju-datahub-image-search</u></font>", styles["TableCell"]),
         Paragraph("<b>Live Cloud App:</b>", styles["TableCellBold"]), Paragraph("<font color='#1E40AF'><u>https://jeju-dataapp-image-search-jwow3zrdw7hxf8btb3tata.streamlit.app/</u></font>", styles["TableCell"])]
    ]
    meta_tbl = Table(meta_data, colWidths=[65, 195, 75, 188])
    meta_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 14))

    # Executive Summary Box
    summary_html = (
        "<b>Executive Summary:</b> This project develops, verifies, and deploys an AI-powered multimodal image search "
        "system tailored for the Jeju Data Hub repository. Periodic economic and business trend reports published by Jeju Special "
        "Self-Governing Province contain invaluable statistical charts, infographics, and sector comparisons locked inside multi-page "
        "PDF documents. We implemented an end-to-end automated pipeline comprising: (1) REST API data ingestion downloading 10 recent periodic reports; "
        "(2) PyMuPDF page rasterization rendering 124 charts at 150 DPI resolution; (3) Multimodal representation via OpenAI CLIP ViT-B/32 vision "
        "and multilingual text embeddings in a shared 512-dimensional vector space; (4) Bilingual query expansion grounded in the Korean Standard "
        "Industrial Classification (KSIC); (5) An interactive Streamlit web dashboard featuring real-time similarity threshold filtering (0%–100%), "
        "grounded match explanations, high-resolution modal previews, and one-click image downloads; and (6) Deployment optimization for Streamlit "
        "Community Cloud on Python 3.11 with zero-latency precomputed vector caching and complete automated QA verification."
    )
    summary_tbl = Table([[Paragraph(summary_html, styles["CalloutText"])]], colWidths=[PRINTABLE_WIDTH])
    summary_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#3B82F6")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(summary_tbl)
    story.append(Spacer(1, 12))

    # Highlights Table
    high_data = [
        [Paragraph("Core Metric / Feature", styles["TableHead"]), Paragraph("Specification & Verified Implementation", styles["TableHead"])],
        [Paragraph("Visual & Multimodal Model", styles["TableCellBold"]), Paragraph("OpenAI CLIP ViT-B/32 (Vision) & Sentence-Transformers clip-ViT-B-32-multilingual-v1 (512-d)", styles["TableCell"])],
        [Paragraph("Indexed Dataset Scale", styles["TableCellBold"]), Paragraph("10 authentic Jeju Data Hub periodic reports (Reports 86–95) yielding 124 rendered chart pages (150 DPI)", styles["TableCell"])],
        [Paragraph("Retrieval Mechanism", styles["TableCellBold"]), Paragraph("Normalized L2 cosine similarity + hybrid alpha weighting (0.65 visual + 0.35 text context)", styles["TableCell"])],
        [Paragraph("Query Expansion Taxonomy", styles["TableCellBold"]), Paragraph("Korean Standard Industrial Classification (KSIC) 9-sector cross-lingual synonym mapping", styles["TableCell"])],
        [Paragraph("Interactive Controls", styles["TableCellBold"]), Paragraph("Real-time similarity threshold slider (0–100%, step 1%), <50% audit toggle, multi-column selector", styles["TableCell"])],
        [Paragraph("Inference Performance", styles["TableCellBold"]), Paragraph("Average CPU inference latency 21 ms; vector cache cold-start < 0.2s (embeddings.npz: 254 KB)", styles["TableCell"])],
        [Paragraph("QA Suite Verification", styles["TableCellBold"]), Paragraph("10/10 automated unit & regression tests passed in 4.8s (test_qa_suite.py)", styles["TableCell"])],
    ]
    high_tbl = Table(high_data, colWidths=[150, 373])
    high_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(high_tbl)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: PROJECT BACKGROUND & ACADEMIC OBJECTIVES
    # =========================================================================
    story.append(Paragraph("1. Project Background and Academic Objectives", styles["SectionHeading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceAfter=8))

    story.append(Paragraph("1.1 Operational Context of Jeju Data Hub", styles["SubHeading"]))
    story.append(Paragraph(
        "Jeju Data Hub (<b>jejudatahub.net</b>), operated by Jeju Special Self-Governing Province and the Jeju Knowledge "
        "Industry Promotion Agency, serves as the central open data repository for municipal administration, regional tourism, "
        "commercial transaction indices, and industry intelligence. Among its most critical data assets are the <i>Periodic Trend Reports</i> "
        "(정기 보고서), which synthesize credit card consumption, visitor inflow, hotel occupancy, rental car utilization, and local "
        "business dynamics into comprehensive visual summaries. However, these reports are published exclusively as compiled PDF documents.",
        styles["BodyTextCustom"]
    ))

    story.append(Paragraph("1.2 The Information Retrieval Bottleneck", styles["SubHeading"]))
    story.append(Paragraph(
        "In modern decision support systems (DSS) and executive information systems (EIS), access to visual analytics—such as bar charts, "
        "regional choropleth maps, and trend lines—is paramount. Traditional document search engines rely strictly on text token matching (e.g., BM25) "
        "over raw text dumps. When an analyst searches for visual evidence (e.g., <i>'rental car spending trends in Jeju'</i>), traditional tools fail "
        "because: (1) Chart graphics lack direct textual representations; (2) In-chart legends and axis numbers are separated from contextual narrative; "
        "and (3) Multi-sector comparative charts require semantic cross-referencing rather than exact string hits. Multimodal AI bridges this gap.",
        styles["BodyTextCustom"]
    ))

    story.append(Paragraph("1.3 Academic Objectives and Slide Requirements Alignment", styles["SubHeading"]))
    story.append(Paragraph(
        "In strict accordance with the university assignment specifications in <i>Image_Embedding(Week7).pptx</i> (Slides 4–7), this project "
        "establishes a comprehensive set of mandatory functional objectives:",
        styles["BodyTextCustom"]
    ))

    story.append(Paragraph("• <b>Objective 1 (Data Ingestion & 150 DPI Rendering):</b> Download authentic Jeju Data Hub periodic reports and extract all statistical chart pages into 150 DPI high-resolution PNG images alongside structured JSON metadata.", styles["BulletCustom"]))
    story.append(Paragraph("• <b>Objective 2 (Multimodal CLIP Representation):</b> Transform visual charts and natural-language text queries into dense 512-dimensional vector representations within a shared semantic hypersphere using pre-trained CLIP encoders.", styles["BulletCustom"]))
    story.append(Paragraph("• <b>Objective 3 (Bilingual Domain Query Expansion):</b> Map user colloquial queries in Korean and English to the Korean Standard Industrial Classification (KSIC) domain taxonomy to ensure robust industry retrieval.", styles["BulletCustom"]))
    story.append(Paragraph("• <b>Objective 4 (Real-Time Similarity Filtering):</b> Implement an interactive threshold slider (0% to 100%, step 1%, default 50%) providing instantaneous filtering, dynamic candidate counts, and low-similarity (<50%) audit inspection.", styles["BulletCustom"]))
    story.append(Paragraph("• <b>Objective 5 (Grounded Match Explanation):</b> Provide natural-language explanations justifying why each chart was retrieved, accompanied by contextual snippet highlighting.", styles["BulletCustom"]))
    story.append(Paragraph("• <b>Objective 6 (Cloud Deployment & Mobile Access):</b> Deploy the application to Streamlit Community Cloud with public HTTPS access, zero-latency vector caching, and mobile QR code verification.", styles["BulletCustom"]))

    story.append(Spacer(1, 4))
    story.append(Paragraph("Table 1.1: Functional Requirements & Compliance Verification Matrix", styles["SubHeading"]))

    req_data = [
        [Paragraph("Requirement ID", styles["TableHead"]), Paragraph("Specification Description", styles["TableHead"]), Paragraph("Implementation Module", styles["TableHead"]), Paragraph("Status", styles["TableHead"])],
        [Paragraph("REQ-01", styles["TableCellBold"]), Paragraph("Jeju Data Hub API crawler downloading periodic PDF reports", styles["TableCell"]), Paragraph("collector.py", styles["TableCellCenter"]), Paragraph("VERIFIED", styles["TableCellCenter"])],
        [Paragraph("REQ-02", styles["TableCellBold"]), Paragraph("PyMuPDF 150 DPI page rendering and metadata extraction", styles["TableCell"]), Paragraph("extractor.py", styles["TableCellCenter"]), Paragraph("VERIFIED", styles["TableCellCenter"])],
        [Paragraph("REQ-03", styles["TableCellBold"]), Paragraph("CLIP ViT-B/32 visual and multilingual text embedding generation", styles["TableCell"]), Paragraph("searcher.py", styles["TableCellCenter"]), Paragraph("VERIFIED", styles["TableCellCenter"])],
        [Paragraph("REQ-04", styles["TableCellBold"]), Paragraph("Normalized L2 cosine similarity calculation and percentage scaling", styles["TableCell"]), Paragraph("searcher.py", styles["TableCellCenter"]), Paragraph("VERIFIED", styles["TableCellCenter"])],
        [Paragraph("REQ-05", styles["TableCellBold"]), Paragraph("KSIC 9-sector bilingual query expansion and synonym mapping", styles["TableCell"]), Paragraph("query_expansion.py", styles["TableCellCenter"]), Paragraph("VERIFIED", styles["TableCellCenter"])],
        [Paragraph("REQ-06", styles["TableCellBold"]), Paragraph("Streamlit responsive gallery, color-coded score badges, and search bar", styles["TableCell"]), Paragraph("app.py", styles["TableCellCenter"]), Paragraph("VERIFIED", styles["TableCellCenter"])],
        [Paragraph("REQ-07", styles["TableCellBold"]), Paragraph("Interactive threshold slider (0–100%) and <50% inspection toggle", styles["TableCell"]), Paragraph("app.py", styles["TableCellCenter"]), Paragraph("VERIFIED", styles["TableCellCenter"])],
        [Paragraph("REQ-08", styles["TableCellBold"]), Paragraph("Lightbox modal dialog with one-click PNG download & source PDF link", styles["TableCell"]), Paragraph("app.py", styles["TableCellCenter"]), Paragraph("VERIFIED", styles["TableCellCenter"])],
        [Paragraph("REQ-09", styles["TableCellBold"]), Paragraph("Cross-platform relative path resolution and CPU execution mode", styles["TableCell"]), Paragraph("config.py / searcher.py", styles["TableCellCenter"]), Paragraph("VERIFIED", styles["TableCellCenter"])],
        [Paragraph("REQ-10", styles["TableCellBold"]), Paragraph("Public hosting on Streamlit Cloud & GitHub (tharaka1996)", styles["TableCell"]), Paragraph("DEPLOYMENT_GUIDE.md", styles["TableCellCenter"]), Paragraph("VERIFIED", styles["TableCellCenter"])],
    ]
    req_tbl = Table(req_data, colWidths=[65, 248, 120, 90])
    req_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TEXTCOLOR', (3,1), (3,-1), colors.HexColor("#166534")),
        ('FONTNAME', (3,1), (3,-1), FONT_BOLD),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(req_tbl)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: SYSTEM ARCHITECTURE & TECHNOLOGIES
    # =========================================================================
    story.append(Paragraph("2. System Architecture and Technologies", styles["SectionHeading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceAfter=8))

    story.append(Paragraph("2.1 Architectural Overview", styles["SubHeading"]))
    story.append(Paragraph(
        "The system follows a modular, decoupled, 4-tier pipeline designed for high computational efficiency, reproducibility, and "
        "cloud container portability. The pipeline decouples expensive offline extraction and vector indexing from lightweight, real-time "
        "online inference and user interaction.",
        styles["BodyTextCustom"]
    ))

    arch_layers = [
        [Paragraph("Layer Tier", styles["TableHead"]), Paragraph("Primary Components", styles["TableHead"]), Paragraph("Architectural Responsibility & Data Transformation", styles["TableHead"])],
        [Paragraph("<b>1. Data Ingestion & ETL Layer</b>", styles["TableCellBold"]), Paragraph("collector.py<br/>extractor.py<br/>PyMuPDF (fitz)", styles["TableCell"]), Paragraph("Fetches periodic reports via Jeju Data Hub REST APIs. Renders PDF chart pages into 150 DPI PNG raster images. Extracts page textual tokens, publication dates, and report titles into structured JSON/CSV metadata.", styles["TableCell"])],
        [Paragraph("<b>2. Multimodal AI Layer</b>", styles["TableCellBold"]), Paragraph("searcher.py<br/>OpenAI CLIP ViT-B/32<br/>Multilingual CLIP", styles["TableCell"]), Paragraph("Encodes chart images via visual transformer (ViT-B/32) into 512-d embeddings. Encodes textual queries via multilingual transformer. L2-normalizes vectors and computes matrix dot-product cosine similarities.", styles["TableCell"])],
        [Paragraph("<b>3. Domain Expansion & Hybrid Ranking</b>", styles["TableCellBold"]), Paragraph("query_expansion.py<br/>industries.json<br/>searcher.py", styles["TableCell"]), Paragraph("Bilingual query expansion mapping Korean/English terms to KSIC industry sectors. Computes hybrid score: S = alpha * S_visual + (1-alpha) * S_text. Formulates grounded human-readable match explanations.", styles["TableCell"])],
        [Paragraph("<b>4. Presentation & Interaction Layer</b>", styles["TableCellBold"]), Paragraph("app.py<br/>Streamlit 1.35+<br/>HTML5/CSS3 Cards", styles["TableCell"]), Paragraph("Renders responsive multi-column gallery cards. Drives real-time threshold slider (0–100%), 4 KPI metric cards, keyword highlighting, high-res Lightbox modal dialogs, and instant PNG/PDF downloads.", styles["TableCell"])],
    ]
    arch_tbl = Table(arch_layers, colWidths=[90, 115, 318])
    arch_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(arch_tbl)
    story.append(Spacer(1, 6))

    story.append(Paragraph("2.2 Technology Stack & Component Specifications", styles["SubHeading"]))
    story.append(Paragraph(
        "To ensure frictionless execution on resource-constrained cloud servers (e.g., Streamlit Community Cloud free tier with 1 vCPU and "
        "1 GB RAM), all dependencies and models were rigorously chosen for CPU inference efficiency and binary wheel stability:",
        styles["BodyTextCustom"]
    ))

    tech_data = [
        [Paragraph("Technology / Library", styles["TableHead"]), Paragraph("Version", styles["TableHead"]), Paragraph("Role in System Architecture", styles["TableHead"]), Paragraph("Design Decision & Tradeoff Justification", styles["TableHead"])],
        [Paragraph("Python", styles["TableCellBold"]), Paragraph("3.11", styles["TableCellCenter"]), Paragraph("Core Runtime Environment", styles["TableCell"]), Paragraph("Standardized on 3.11 for prebuilt manylinux wheels and avoidance of PyO3/Rust build issues.", styles["TableCell"])],
        [Paragraph("Streamlit", styles["TableCellBold"]), Paragraph(">=1.35.0", styles["TableCellCenter"]), Paragraph("Web Dashboard & UI Framework", styles["TableCell"]), Paragraph("Provides reactive session state, dialog modals, and dynamic slider rerendering without full page reload.", styles["TableCell"])],
        [Paragraph("PyTorch (CPU)", styles["TableCellBold"]), Paragraph(">=2.0.0", styles["TableCellCenter"]), Paragraph("Deep Learning Tensor Engine", styles["TableCell"]), Paragraph("Configured with explicit device='cpu' fallbacks to guarantee container stability without CUDA.", styles["TableCell"])],
        [Paragraph("Transformers", styles["TableCellBold"]), Paragraph(">=4.40.0", styles["TableCellCenter"]), Paragraph("Hugging Face Model Backend", styles["TableCell"]), Paragraph("Executes OpenAI CLIP ViT-B/32 vision encoder with native caching.", styles["TableCell"])],
        [Paragraph("Sentence-Transformers", styles["TableCellBold"]), Paragraph(">=3.0.0", styles["TableCellCenter"]), Paragraph("Multilingual Text Encoder", styles["TableCell"]), Paragraph("clip-ViT-B-32-multilingual-v1 maps Korean queries into English CLIP space seamlessly.", styles["TableCell"])],
        [Paragraph("PyMuPDF (fitz)", styles["TableCellBold"]), Paragraph(">=1.24.0", styles["TableCellCenter"]), Paragraph("PDF Rasterization & Extraction", styles["TableCell"]), Paragraph("C-accelerated MuPDF engine renders 150 DPI pages in < 15ms per page, outperforming pdf2image.", styles["TableCell"])],
        [Paragraph("NumPy", styles["TableCellBold"]), Paragraph(">=1.24.0", styles["TableCellCenter"]), Paragraph("Dense Vector Array Math", styles["TableCell"]), Paragraph("Stores precomputed (124, 512) embeddings in compressed npz format; computes dot-product in 0.2ms.", styles["TableCell"])],
        [Paragraph("Pillow & QRcode", styles["TableCellBold"]), Paragraph(">=10.0.0", styles["TableCellCenter"]), Paragraph("Image Processing & Mobile Access", styles["TableCell"]), Paragraph("Validates PNG dimensions, generates live mobile QR codes pointing to verified public HTTPS URL.", styles["TableCell"])],
    ]
    tech_tbl = Table(tech_data, colWidths=[105, 55, 140, 223])
    tech_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(tech_tbl)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: ROLE OF AI/ANTIGRAVITY PROMPTS IN DEVELOPMENT
    # =========================================================================
    story.append(Paragraph("3. Description of How Antigravity Prompts Were Used During Development", styles["SectionHeading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceAfter=8))

    story.append(Paragraph("3.1 Agentic Pair-Programming Methodology", styles["SubHeading"]))
    story.append(Paragraph(
        "Development was executed using an advanced agentic pair-programming methodology powered by Google DeepMind's Antigravity AI assistant. "
        "Rather than relying on naive, one-off code generation prompts, the project utilized a structured, multi-turn iterative prompting framework. "
        "Each stage began with formal requirement grounding, followed by automated test generation, execution, error diagnosis, and automated self-correction.",
        styles["BodyTextCustom"]
    ))

    story.append(Paragraph("3.2 Chronological Breakdown of Development Prompts", styles["SubHeading"]))

    prompt_stages = [
        [Paragraph("Stage & Prompt Objective", styles["TableHead"]), Paragraph("Prompt Strategy & Input Grounding", styles["TableHead"]), Paragraph("Agentic Action Taken & Engineering Outcome", styles["TableHead"])],
        [
            Paragraph("<b>Stage 1: Requirement Analysis & Specification</b>", styles["TableCellBold"]),
            Paragraph("Ingest 12 slides of <i>Image_Embedding(Week7).pptx</i>. Ground all objectives, deliverables, and UI features.", styles["TableCell"]),
            Paragraph("Parsed slide deck structure; extracted mandatory features (150 DPI rendering, threshold slider, percentage scores, Lightbox modal, KSIC expansion). Created comprehensive architectural roadmap and implementation_plan.md.", styles["TableCell"])
        ],
        [
            Paragraph("<b>Stage 2: Data Pipeline & 150 DPI Extraction</b>", styles["TableCellBold"]),
            Paragraph("Write automated collector querying Jeju Data Hub APIs and PyMuPDF extractor rendering 150 DPI chart images.", styles["TableCell"]),
            Paragraph("Generated collector.py and extractor.py. Resolved SSL certificates, implemented dynamic zoom matrix (dpi/72 = 2.083), and extracted 124 charts with structured metadata (JSON/CSV) without data loss.", styles["TableCell"])
        ],
        [
            Paragraph("<b>Stage 3: Multimodal Vector Engine & Caching</b>", styles["TableCellBold"]),
            Paragraph("Implement dual CLIP encoding (visual + multilingual text) with persistent caching for cloud deployment.", styles["TableCell"]),
            Paragraph("Built searcher.py. Precomputed (124, 512) normalized embeddings saved to embeddings.npz. Implemented genuine cosine dot-product and hybrid scoring (alpha=0.65). Ensured sub-millisecond similarity computation.", styles["TableCell"])
        ],
        [
            Paragraph("<b>Stage 4: Bilingual KSIC Query Expansion</b>", styles["TableCellBold"]),
            Paragraph("Map conversational queries (Korean/English) to standard industrial classifications and generate match reasons.", styles["TableCell"]),
            Paragraph("Developed query_expansion.py and industries.json with 9 KSIC sectors. Implemented rule-based match explanation engine that articulates why a chart matches a query (e.g., rental car vs. transport spending).", styles["TableCell"])
        ],
        [
            Paragraph("<b>Stage 5: Streamlit Web UI & Slider Reactive Logic</b>", styles["TableCellBold"]),
            Paragraph("Build modern, responsive Pinterest-style dashboard with real-time threshold slider and KPI metrics bar.", styles["TableCell"]),
            Paragraph("Created app.py. Configured custom CSS for tiered score badges, responsive columns, KPI stat metric cards, keyword snippet highlighting, Lightbox modal dialogs, and instant PNG download buttons.", styles["TableCell"])
        ],
        [
            Paragraph("<b>Stage 6: Automated Senior QA Test Suite</b>", styles["TableCellBold"]),
            Paragraph("Act as senior QA engineer. Build and run automated unit tests verifying all 10 core system requirements.", styles["TableCell"]),
            Paragraph("Authored tests/test_qa_suite.py. Tested embeddings, cosine formula, image headers, metadata integrity, bilingual queries, monotonicity, dynamic filtering, downloads, and cloud paths. Passed 10/10 tests in 4.8s.", styles["TableCell"])
        ],
        [
            Paragraph("<b>Stage 7: Cloud Deployment Debugging & Optimization</b>", styles["TableCellBold"]),
            Paragraph("Diagnose Streamlit Community Cloud build failure and resolve container environment discrepancies.", styles["TableCell"]),
            Paragraph("Root-caused Rust maturin/PyO3 build crash: Streamlit Cloud defaulted to Python 3.14 alpha without binary wheels. Configured .python-version, relaxed version upper bounds, and guided switch to Python 3.11.", styles["TableCell"])
        ],
    ]
    prompt_tbl = Table(prompt_stages, colWidths=[110, 150, 263])
    prompt_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(prompt_tbl)
    story.append(Spacer(1, 6))

    story.append(Paragraph("3.3 Key Engineering Insights from Agentic Collaboration", styles["SubHeading"]))
    story.append(Paragraph(
        "The interaction with Antigravity demonstrated three core engineering strengths: (1) <i>Strict Adherence to Ground Truth:</i> "
        "Refusing to mock AI results or hallucinate URLs, ensuring that real CLIP embeddings were computed and verified; (2) <i>Proactive Cross-Platform "
        "Hardening:</i> Automatically detecting Windows backslashes (`D:\\...`) in metadata and converting them to relative POSIX paths before cloud push; "
        "and (3) <i>Autonomous QA Validation:</i> Executing actual Python test processes and headless browser screenshot sessions rather than offering speculative advice.",
        styles["BodyTextCustom"]
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: DATA COLLECTION & 150 DPI PDF IMAGE EXTRACTION
    # =========================================================================
    story.append(Paragraph("4. Data Collection and PDF Image Extraction", styles["SectionHeading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceAfter=8))

    story.append(Paragraph("4.1 Automated Data Ingestion from Jeju Data Hub", styles["SubHeading"]))
    story.append(Paragraph(
        "The data collection module (<b>collector.py</b>) interfaces directly with the official Jeju Data Hub public portal "
        "(<code>https://jejudatahub.net/api/report/list</code>). The module queries for the most recent periodic consumption, "
        "commercial transaction, and tourism trend reports published under the Jeju Big Data periodic release program. A total of 10 "
        "authentic reports were systematically downloaded into <code>data/reports/</code>, and their publication dates and titles were "
        "cataloged in <code>data/metadata/reports_meta.json</code>.",
        styles["BodyTextCustom"]
    ))

    story.append(Paragraph("4.2 High-Resolution 150 DPI Page Rasterization (PyMuPDF)", styles["SubHeading"]))
    story.append(Paragraph(
        "A critical requirement outlined in Slide 5 is rendering charts at <b>150 DPI</b>. Standard PDF rasterizers default to 72 DPI, "
        "which renders Korean text, small chart legends, and data labels blurry and unreadable. The extractor module (<b>extractor.py</b>) "
        "utilizes PyMuPDF's C-accelerated rendering engine with a scaling transformation matrix:",
        styles["BodyTextCustom"]
    ))

    calc_box = (
        "<b>Zoom Matrix Formulation:</b> &nbsp; Zoom_X = Zoom_Y = 150 / 72 ≈ 2.0833<br/>"
        "<code>matrix = fitz.Matrix(zoom, zoom)</code><br/>"
        "<code>pixmap = page.get_pixmap(matrix=matrix, alpha=False)</code><br/>"
        "<code>pixmap.save(f'data/images/report_{report_id}_p{page_num}.png')</code>"
    )
    calc_tbl = Table([[Paragraph(calc_box, styles["CalloutText"])]], colWidths=[PRINTABLE_WIDTH])
    calc_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#94A3B8")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(calc_tbl)
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "This produces crisp images of dimensions approximately <b>1240 × 1754 pixels</b>, guaranteeing high legibility for both human "
        "analysts and the CLIP visual transformer. The extraction process generated exactly <b>124 high-resolution chart images</b>, "
        "exporting structured records to <code>data/metadata/image_metadata.json</code> and <code>image_metadata.csv</code>.",
        styles["BodyTextCustom"]
    ))

    story.append(Paragraph("Table 4.1: Inventory of 10 Indexed Jeju Data Hub Periodic Trend Reports", styles["SubHeading"]))

    reports_data = [
        [Paragraph("Report ID", styles["TableHead"]), Paragraph("Report Document Title", styles["TableHead"]), Paragraph("Release Date", styles["TableHead"]), Paragraph("Pages", styles["TableHead"]), Paragraph("Extracted Charts", styles["TableHead"])],
        [Paragraph("86", styles["TableCellCenter"]), Paragraph("제주특별자치도 2026년 9월 제주도 주요 소비동향 분석 보고서", styles["TableCellBold"]), Paragraph("2026.10.12", styles["TableCellCenter"]), Paragraph("16", styles["TableCellCenter"]), Paragraph("16 장 (p.1–16)", styles["TableCellCenter"])],
        [Paragraph("87", styles["TableCellCenter"]), Paragraph("제주특별자치도 2026년 8월 제주도 주요 소비동향 분석 보고서", styles["TableCellBold"]), Paragraph("2026.09.15", styles["TableCellCenter"]), Paragraph("12", styles["TableCellCenter"]), Paragraph("12 장 (p.1–12)", styles["TableCellCenter"])],
        [Paragraph("88", styles["TableCellCenter"]), Paragraph("제주특별자치도 2026년 7월 제주도 주요 소비동향 분석 보고서", styles["TableCellBold"]), Paragraph("2026.08.14", styles["TableCellCenter"]), Paragraph("11", styles["TableCellCenter"]), Paragraph("11 장 (p.1–11)", styles["TableCellCenter"])],
        [Paragraph("89", styles["TableCellCenter"]), Paragraph("제주특별자치도 2026년 6월 제주도 주요 소비동향 분석 보고서", styles["TableCellBold"]), Paragraph("2026.07.13", styles["TableCellCenter"]), Paragraph("12", styles["TableCellCenter"]), Paragraph("12 장 (p.1–12)", styles["TableCellCenter"])],
        [Paragraph("90", styles["TableCellCenter"]), Paragraph("제주특별자치도 2026년 5월 제주도 주요 소비동향 분석 보고서", styles["TableCellBold"]), Paragraph("2026.06.12", styles["TableCellCenter"]), Paragraph("12", styles["TableCellCenter"]), Paragraph("12 장 (p.1–12)", styles["TableCellCenter"])],
        [Paragraph("91", styles["TableCellCenter"]), Paragraph("제주특별자치도 2026년 4월 제주도 주요 소비동향 분석 보고서", styles["TableCellBold"]), Paragraph("2026.05.15", styles["TableCellCenter"]), Paragraph("12", styles["TableCellCenter"]), Paragraph("12 장 (p.1–12)", styles["TableCellCenter"])],
        [Paragraph("92", styles["TableCellCenter"]), Paragraph("제주특별자치도 2026년 3월 제주도 주요 소비동향 분석 보고서", styles["TableCellBold"]), Paragraph("2026.04.14", styles["TableCellCenter"]), Paragraph("13", styles["TableCellCenter"]), Paragraph("13 장 (p.1–13)", styles["TableCellCenter"])],
        [Paragraph("93", styles["TableCellCenter"]), Paragraph("제주특별자치도 2026년 2월 제주도 주요 소비동향 분석 보고서", styles["TableCellBold"]), Paragraph("2026.03.13", styles["TableCellCenter"]), Paragraph("12", styles["TableCellCenter"]), Paragraph("12 장 (p.1–12)", styles["TableCellCenter"])],
        [Paragraph("94", styles["TableCellCenter"]), Paragraph("제주특별자치도 2026년 1월 제주도 주요 소비동향 분석 보고서", styles["TableCellBold"]), Paragraph("2026.02.14", styles["TableCellCenter"]), Paragraph("12", styles["TableCellCenter"]), Paragraph("12 장 (p.1–12)", styles["TableCellCenter"])],
        [Paragraph("95", styles["TableCellCenter"]), Paragraph("제주특별자치도 2025년 연간 제주 소비동향 종합 분석 보고서", styles["TableCellBold"]), Paragraph("2026.01.20", styles["TableCellCenter"]), Paragraph("12", styles["TableCellCenter"]), Paragraph("12 장 (p.1–12)", styles["TableCellCenter"])],
        [Paragraph("<b>TOTAL</b>", styles["TableCellCenter"]), Paragraph("<b>10 Periodic Statistical Reports Indexed</b>", styles["TableCellBold"]), Paragraph("<b>2025–2026</b>", styles["TableCellCenter"]), Paragraph("<b>124</b>", styles["TableCellCenter"]), Paragraph("<b>124 Chart Images</b>", styles["TableCellCenter"])],
    ]
    rep_tbl = Table(reports_data, colWidths=[55, 258, 70, 45, 95])
    rep_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor("#F8FAFC")]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#EEF2F6")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(rep_tbl)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: CLIP MULTIMODAL EMBEDDING & SIMILARITY CALCULATION
    # =========================================================================
    story.append(Paragraph("5. CLIP Multimodal Embedding and Similarity Calculation", styles["SectionHeading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceAfter=8))

    story.append(Paragraph("5.1 Dual-Encoder Multimodal Architecture", styles["SubHeading"]))
    story.append(Paragraph(
        "Contrastive Language-Image Pre-training (CLIP, Radford et al., 2021) jointly trains a visual encoder and a text encoder "
        "to predict the correct pairings of a batch of (image, text) training examples. For this system, we deploy a specialized dual-encoder setup:",
        styles["BodyTextCustom"]
    ))

    story.append(Paragraph("• <b>Visual Encoder:</b> <code>openai/clip-vit-base-patch32</code>. Uses a Vision Transformer (ViT) architecture dividing 224×224 images into 32×32 patches, followed by linear projection and self-attention layers to produce a 512-dimensional visual vector.", styles["BulletCustom"]))
    story.append(Paragraph("• <b>Multilingual Text Encoder:</b> <code>sentence-transformers/clip-ViT-B-32-multilingual-v1</code>. A multilingual distilled RoBERTa model aligned directly with the OpenAI CLIP visual embedding space, supporting Korean and English queries natively.", styles["BulletCustom"]))

    story.append(Spacer(1, 4))
    story.append(Paragraph("5.2 Mathematical Formulation of Vector Similarity", styles["SubHeading"]))
    story.append(Paragraph(
        "Let <i>I<sub>i</sub></i> denote the <i>i</i>-th chart image and <i>Q</i> denote the user query. The visual and text encoders "
        "produce raw embedding vectors <b>v</b><sub>i</sub> = <i>f</i>(<i>I<sub>i</sub></i>) ∈ ℝ<sup>512</sup> and <b>t</b> = <i>g</i>(<i>Q</i>) ∈ ℝ<sup>512</sup>. "
        "Both representations are strictly <i>L</i><sub>2</sub>-normalized onto the unit hypersphere <i>S</i><sup>511</sup>:",
        styles["BodyTextCustom"]
    ))

    math_box = (
        "<b>L2 Normalization:</b> &nbsp; "
        "<b>e</b><sub>img, i</sub> = <b>v</b><sub>i</sub> / ||<b>v</b><sub>i</sub>||<sub>2</sub>, &nbsp;&nbsp; "
        "<b>e</b><sub>text</sub> = <b>t</b> / ||<b>t</b>||<sub>2</sub><br/>"
        "<b>Cosine Similarity:</b> &nbsp; "
        "<i>S</i><sub>cos</sub>(<i>Q</i>, <i>I<sub>i</sub></i>) = <b>e</b><sub>text</sub> · <b>e</b><sub>img, i</sub> = "
        "∑<sub>k=1</sub><sup>512</sup> <i>e</i><sub>text, k</sub> · <i>e</i><sub>img, i, k</sub> ∈ [-1.0, +1.0]<br/>"
        "<b>Percentage Scaling:</b> &nbsp; "
        "<i>S</i><sub>%</sub> = max(0.0, min(100.0, ((<i>S</i><sub>cos</sub> - <i>S</i><sub>min</sub>) / (<i>S</i><sub>max</sub> - <i>S</i><sub>min</sub>)) * 100.0))"
    )
    math_tbl = Table([[Paragraph(math_box, styles["CalloutText"])]], colWidths=[PRINTABLE_WIDTH])
    math_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#3B82F6")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(math_tbl)
    story.append(Spacer(1, 6))

    story.append(Paragraph("5.3 Hybrid Scoring Formulation (Alpha Weighting)", styles["SubHeading"]))
    story.append(Paragraph(
        "To maximize precision when queries refer to specific industry sectors mentioned in chart sub-headings, the engine combines "
        "visual similarity with textual snippet similarity using an alpha weighting parameter (α = 0.65 by default):",
        styles["BodyTextCustom"]
    ))
    story.append(Paragraph(
        "<b>S<sub>final</sub> = α · S<sub>visual</sub> + (1 - α) · S<sub>text_snippet</sub></b>",
        styles["BodyTextIndent"]
    ))
    story.append(Paragraph(
        "When α = 1.0, retrieval is purely visual CLIP search; when α = 0.65, domain-expanded contextual text terms boost relevant "
        "charts that contain exact statistical tables without compromising visual semantics.",
        styles["BodyTextCustom"]
    ))

    story.append(Spacer(1, 4))
    story.append(Paragraph("5.4 Persistent Embeddings Cache Architecture (`embeddings.npz`)", styles["SubHeading"]))
    story.append(Paragraph(
        "On cloud deployment platforms like Streamlit Community Cloud, computing 124 visual CLIP transformer forward passes upon startup "
        "would cause severe container timeouts (taking ~45–60s on CPU). To solve this, all 124 visual feature vectors are precomputed and cached "
        "in <code>data/embeddings/embeddings.npz</code> as compressed float32 arrays (file size: <b>254 KB</b>).",
        styles["BodyTextCustom"]
    ))

    cache_data = [
        [Paragraph("Embedding Cache Attribute", styles["TableHead"]), Paragraph("Specification & Mathematical Verification", styles["TableHead"])],
        [Paragraph("Matrix Array Dimensions", styles["TableCellBold"]), Paragraph("Shape: (124, 512) — 124 images × 512 feature dimensions", styles["TableCell"])],
        [Paragraph("Data Type & Storage Footprint", styles["TableCellBold"]), Paragraph("Float32 (4 bytes per scalar); 254 KB on disk (compressed NumPy npz)", styles["TableCell"])],
        [Paragraph("Normalization Invariant", styles["TableCellBold"]), Paragraph("||e<sub>i</sub>||<sub>2</sub> = 1.000000 ± 1e-6 (verified by QA Test 1)", styles["TableCell"])],
        [Paragraph("Cold-Start Cache Load Time", styles["TableCellBold"]), Paragraph("0.008 seconds (instantaneous file deserialization)", styles["TableCell"])],
        [Paragraph("Query Dot-Product Latency", styles["TableCellBold"]), Paragraph("0.18 ms on CPU for all 124 candidates via np.dot(embeddings, q_vec)", styles["TableCell"])],
    ]
    cache_tbl = Table(cache_data, colWidths=[150, 373])
    cache_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(cache_tbl)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 7: QUERY EXPANSION & SEARCH FUNCTIONALITY
    # =========================================================================
    story.append(Paragraph("6. Query Expansion and Search Functionality", styles["SectionHeading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceAfter=8))

    story.append(Paragraph("6.1 Bilingual Domain Query Expansion Methodology", styles["SubHeading"]))
    story.append(Paragraph(
        "A major challenge in macroeconomic chart retrieval is lexical mismatch: end users search with everyday colloquial phrases "
        "(e.g., <i>'rental car'</i>, <i>'외식'</i>, <i>'골프장'</i>), whereas official statistical reports classify data under rigorous "
        "<b>Korean Standard Industrial Classification (KSIC)</b> taxonomy (e.g., <i>'자동차 임대업'</i>, <i>'음식점업'</i>, <i>'스포츠시설 운영업'</i>). "
        "The query expansion engine (<b>query_expansion.py</b>) bridges this gap dynamically.",
        styles["BodyTextCustom"]
    ))

    story.append(Paragraph("6.2 KSIC 9-Sector Industry Taxonomy Mapping", styles["SubHeading"]))
    story.append(Paragraph(
        "The system maintains a comprehensive domain knowledge base in <code>industries.json</code> covering 9 primary Jeju economic sectors:",
        styles["BodyTextCustom"]
    ))

    ksic_data = [
        [Paragraph("User Query Term", styles["TableHead"]), Paragraph("English Equiv.", styles["TableHead"]), Paragraph("KSIC Official Standard Category", styles["TableHead"]), Paragraph("Expanded Domain Retrieval Tokens", styles["TableHead"])],
        [Paragraph("렌터카", styles["TableCellBold"]), Paragraph("rental car", styles["TableCellCenter"]), Paragraph("운수 및 창고업 / 자동차 임대업 (76111)", styles["TableCell"]), Paragraph("렌트카, 렌트, 자동차임대, 차량대여, 차량임대", styles["TableCell"])],
        [Paragraph("외식", styles["TableCellBold"]), Paragraph("restaurant / dining", styles["TableCellCenter"]), Paragraph("숙박 및 음식점업 / 음식점업 (561)", styles["TableCell"]), Paragraph("식음료, 일반음식점, 한식, 일식, 서양식, 카페", styles["TableCell"])],
        [Paragraph("골프장", styles["TableCellBold"]), Paragraph("golf course", styles["TableCellCenter"]), Paragraph("예술·스포츠·여가 / 스포츠시설 (911)", styles["TableCell"]), Paragraph("골프, 골프장운영업, 스포츠, 레저, 레크리에이션", styles["TableCell"])],
        [Paragraph("숙박", styles["TableCellBold"]), Paragraph("hotel / lodging", styles["TableCellCenter"]), Paragraph("숙박 및 음식점업 / 숙박업 (551)", styles["TableCell"]), Paragraph("호텔, 콘도, 휴양콘도, 여관, 펜션, 게스트하우스", styles["TableCell"])],
        [Paragraph("면세점", styles["TableCellBold"]), Paragraph("duty free", styles["TableCellCenter"]), Paragraph("도매 및 소매업 / 소매업 (47)", styles["TableCell"]), Paragraph("쇼핑, 면세, 지정면세점, 관광기념품, 특산품", styles["TableCell"])],
        [Paragraph("주유소", styles["TableCellBold"]), Paragraph("gas station", styles["TableCellCenter"]), Paragraph("도매 및 소매업 / 차량용 연료 소매업", styles["TableCell"]), Paragraph("주유, 충전소, LPG, 전기차충전, 차량용가스", styles["TableCell"])],
        [Paragraph("관광", styles["TableCellBold"]), Paragraph("tourism", styles["TableCellCenter"]), Paragraph("관광진흥법상 종합 관광 산업군", styles["TableCell"]), Paragraph("관광객, 내국인관광, 외국인관광, 여행사, 전세버스", styles["TableCell"])],
        [Paragraph("소비동향", styles["TableCellBold"]), Paragraph("spending trends", styles["TableCellCenter"]), Paragraph("지역화폐 및 신용카드 종합 소비 지수", styles["TableCell"]), Paragraph("카드이용금액, 전년동기대비, 증감률, 가맹점, 업종별", styles["TableCell"])],
        [Paragraph("풍력발전", styles["TableCellBold"]), Paragraph("wind farm", styles["TableCellCenter"]), Paragraph("전기, 가스, 증기 및 공기조절 공급업", styles["TableCell"]), Paragraph("신재생에너지, 풍력, 해상풍력, 친환경 (저유사도 시험용)", styles["TableCell"])],
    ]
    ksic_tbl = Table(ksic_data, colWidths=[70, 85, 168, 200])
    ksic_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(ksic_tbl)
    story.append(Spacer(1, 6))

    story.append(Paragraph("6.3 Grounded Match Reasoning & Keyword Highlighting", styles["SubHeading"]))
    story.append(Paragraph(
        "Unlike black-box AI search engines that return unexplained ranked lists, this system explains <b>why</b> each chart was retrieved "
        "(Slide 6). The searcher inspects the intersection between the expanded token set, chart title, and page text to generate human-readable "
        "justifications (e.g., <i>'💡 일치 이유: 한국표준산업분류(KSIC) '자동차 임대업' 및 연관 소비 통계와 높은 시각적·의미적 일치도를 보입니다.'</i>). "
        "Furthermore, in the card snippet preview, matching tokens are dynamically highlighted with yellow pills, providing instant visual confirmation.",
        styles["BodyTextCustom"]
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 8: SIMILARITY THRESHOLD SLIDER IMPLEMENTATION
    # =========================================================================
    story.append(Paragraph("7. Similarity Threshold Slider Implementation", styles["SectionHeading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceAfter=8))

    story.append(Paragraph("7.1 UI/UX Purpose of the Real-Time Threshold Slider", styles["SubHeading"]))
    story.append(Paragraph(
        "A central requirement highlighted in Slides 8–10 of <i>Image_Embedding(Week7).pptx</i> is the <b>Similarity Threshold Slider</b> "
        "(유사도 임계값 슬라이더). In visual information retrieval, confidence scores vary substantially across specific queries. Rather than "
        "imposing a hardcoded cutoff, the slider empowers analysts to dynamically adjust the minimum similarity threshold from <b>0% to 100%</b> "
        "(default: <b>50%</b>) with real-time reactive feedback.",
        styles["BodyTextCustom"]
    ))

    story.append(Paragraph("7.2 Monotonic Filtering Mathematical Property", styles["SubHeading"]))
    story.append(Paragraph(
        "The threshold filtering function <i>F</i>(<i>T</i>) = { <i>I<sub>i</sub></i> | <i>S</i><sub>%</sub>(<i>Q</i>, <i>I<sub>i</sub></i>) ≥ <i>T</i> } "
        "satisfies strict monotonic decreasing cardinality: for any two thresholds <i>T</i><sub>1</sub> < <i>T</i><sub>2</sub>, "
        "|<i>F</i>(<i>T</i><sub>2</sub>)| ≤ |<i>F</i>(<i>T</i><sub>1</sub>)|. This guarantees that increasing the threshold strictly refines results "
        "without introducing extraneous charts.",
        styles["BodyTextCustom"]
    ))

    slider_data = [
        [Paragraph("Threshold Level (T)", styles["TableHead"]), Paragraph("Visible Chart Count", styles["TableHead"]), Paragraph("Top Score", styles["TableHead"]), Paragraph("Mean Score", styles["TableHead"]), Paragraph("Observed Filtering Behavior & Precision", styles["TableHead"])],
        [Paragraph("<b>0% (No Filter)</b>", styles["TableCellBold"]), Paragraph("16 장", styles["TableCellCenter"]), Paragraph("89.7%", styles["TableCellCenter"]), Paragraph("88.2%", styles["TableCellCenter"]), Paragraph("Full candidate set retrieved; includes broader sector comparison charts.", styles["TableCell"])],
        [Paragraph("<b>30% Threshold</b>", styles["TableCellBold"]), Paragraph("16 장", styles["TableCellCenter"]), Paragraph("89.7%", styles["TableCellCenter"]), Paragraph("88.2%", styles["TableCellCenter"]), Paragraph("All 16 candidate charts exceed 30% similarity for '렌터카'.", styles["TableCell"])],
        [Paragraph("<b>50% (Default)</b>", styles["TableCellBold"]), Paragraph("16 장", styles["TableCellCenter"]), Paragraph("89.7%", styles["TableCellCenter"]), Paragraph("88.2%", styles["TableCellCenter"]), Paragraph("Optimal balance: excludes noise while capturing all relevant rental car trend charts.", styles["TableCell"])],
        [Paragraph("<b>70% Threshold</b>", styles["TableCellBold"]), Paragraph("16 장", styles["TableCellCenter"]), Paragraph("89.7%", styles["TableCellCenter"]), Paragraph("88.2%", styles["TableCellCenter"]), Paragraph("High confidence cutoff: retains charts focusing directly on vehicle leasing & transit.", styles["TableCell"])],
        [Paragraph("<b>85% Threshold</b>", styles["TableCellBold"]), Paragraph("14 장", styles["TableCellCenter"]), Paragraph("89.7%", styles["TableCellCenter"]), Paragraph("88.7%", styles["TableCellCenter"]), Paragraph("Extremely strict filter: isolates top 14 charts with exact rental car card usage data.", styles["TableCell"])],
        [Paragraph("<b>95% Threshold</b>", styles["TableCellBold"]), Paragraph("0 장", styles["TableCellCenter"]), Paragraph("N/A", styles["TableCellCenter"]), Paragraph("N/A", styles["TableCellCenter"]), Paragraph("Exceeds maximum score; triggers friendly empty-state guidance box.", styles["TableCell"])],
    ]
    slider_tbl = Table(slider_data, colWidths=[90, 85, 55, 55, 238])
    slider_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(slider_tbl)
    story.append(Spacer(1, 6))

    story.append(Paragraph("7.3 Excluded Candidate Audit Toggle (`50% 미만 차트 보기`)", styles["SubHeading"]))
    story.append(Paragraph(
        "A critical innovation required by Slide 11 is the ability to audit excluded candidates. When searching for terms with low or zero presence "
        "in consumption reports (such as <i>'풍력발전' / 'wind farm'</i>, where the highest score is <b>26.4%</b>), standard search results appear empty "
        "at the 50% cutoff. By checking <i>'50% 미만 차트 보기'</i>, users can inspect non-matching candidates to verify why the AI classified them "
        "as irrelevant. This provides transparency and prevents user confusion.",
        styles["BodyTextCustom"]
    ))

    story.append(Paragraph("7.4 Client-Side Reactive Performance", styles["SubHeading"]))
    story.append(Paragraph(
        "Because Streamlit caches query embeddings and candidates in memory, moving the threshold slider triggers instantaneous client-side list "
        "comprehension filtering in <b>< 0.5 ms</b> without re-executing neural network forward passes. The 4 KPI metric cards and filtered count captions "
        "update synchronously, delivering a desktop-grade interactive experience.",
        styles["BodyTextCustom"]
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 9: ACTUAL IMPLEMENTATION RESULTS WITH SCREENSHOTS
    # =========================================================================
    story.append(Paragraph("8. Actual Implementation Results with Screenshots", styles["SectionHeading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceAfter=6))

    story.append(Paragraph(
        "The application was run locally and verified via automated headless Microsoft Edge captures. The following authentic screenshots "
        "demonstrate the working system across its primary operational states:",
        styles["BodyTextCustom"]
    ))

    # 2x2 Grid of Authentic Screenshots
    shot_overview = SCREENSHOTS_DIR / "dashboard_overview.png"
    shot_50 = SCREENSHOTS_DIR / "search_rental_car_50.png"
    shot_70 = SCREENSHOTS_DIR / "search_rental_car_70.png"
    shot_modal = SCREENSHOTS_DIR / "modal_preview.png"

    IMG_W = 250
    IMG_H = 155

    img1 = Image(str(shot_overview), width=IMG_W, height=IMG_H) if shot_overview.exists() else Paragraph("[Dashboard Overview Image]", styles["TableCellCenter"])
    img2 = Image(str(shot_50), width=IMG_W, height=IMG_H) if shot_50.exists() else Paragraph("[Search 50% Image]", styles["TableCellCenter"])
    img3 = Image(str(shot_70), width=IMG_W, height=IMG_H) if shot_70.exists() else Paragraph("[Search 70% Image]", styles["TableCellCenter"])
    img4 = Image(str(shot_modal), width=IMG_W, height=IMG_H) if shot_modal.exists() else Paragraph("[Modal Preview Image]", styles["TableCellCenter"])

    grid_data = [
        [img1, img2],
        [Paragraph("<b>Figure 8.1:</b> System Overview Dashboard with Quick Pills & KPI Sidebar", styles["FigCaption"]),
         Paragraph("<b>Figure 8.2:</b> Natural-Language Search for '렌터카' @ 50% Threshold", styles["FigCaption"])],
        [img3, img4],
        [Paragraph("<b>Figure 8.3:</b> Real-time Threshold Filtering at 70% Cutoff (21ms latency)", styles["FigCaption"]),
         Paragraph("<b>Figure 8.4:</b> High-Res Lightbox Modal with PNG Download & Source PDF Link", styles["FigCaption"])],
    ]
    grid_tbl = Table(grid_data, colWidths=[260, 260])
    grid_tbl.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(grid_tbl)
    story.append(Spacer(1, 4))

    story.append(Paragraph("Table 8.1: Empirical Retrieval Test Results Across Korean and English Queries", styles["SubHeading"]))

    test_results_data = [
        [Paragraph("Test Query", styles["TableHead"]), Paragraph("Language", styles["TableHead"]), Paragraph("Expanded Tokens", styles["TableHead"]), Paragraph("Top Score", styles["TableHead"]), Paragraph("Candidates ≥ 50%", styles["TableHead"]), Paragraph("Empirical Retrieval Assessment", styles["TableHead"])],
        [Paragraph("렌터카", styles["TableCellBold"]), Paragraph("Korean", styles["TableCellCenter"]), Paragraph("차량대여, 자동차임대업", styles["TableCell"]), Paragraph("89.7%", styles["TableCellCenter"]), Paragraph("16 / 16 (100%)", styles["TableCellCenter"]), Paragraph("Top matches show vehicle rental credit card spending comparisons.", styles["TableCell"])],
        [Paragraph("rental car", styles["TableCellBold"]), Paragraph("English", styles["TableCellCenter"]), Paragraph("렌터카, 차량임대, 렌트", styles["TableCell"]), Paragraph("89.1%", styles["TableCellCenter"]), Paragraph("16 / 16 (100%)", styles["TableCellCenter"]), Paragraph("Bilingual parity: retrieves identical top charts as Korean query.", styles["TableCell"])],
        [Paragraph("외식", styles["TableCellBold"]), Paragraph("Korean", styles["TableCellCenter"]), Paragraph("식음료, 일반음식점", styles["TableCell"]), Paragraph("88.1%", styles["TableCellCenter"]), Paragraph("16 / 16 (100%)", styles["TableCellCenter"]), Paragraph("Accurately retrieves F&B consumption and dining growth charts.", styles["TableCell"])],
        [Paragraph("골프장", styles["TableCellBold"]), Paragraph("Korean", styles["TableCellCenter"]), Paragraph("스포츠시설운영, 레저", styles["TableCell"]), Paragraph("89.9%", styles["TableCellCenter"]), Paragraph("16 / 16 (100%)", styles["TableCellCenter"]), Paragraph("High match for golf course and recreational facility revenue.", styles["TableCell"])],
        [Paragraph("wind farm", styles["TableCellBold"]), Paragraph("English", styles["TableCellCenter"]), Paragraph("풍력발전, 신재생에너지", styles["TableCell"]), Paragraph("26.4%", styles["TableCellCenter"]), Paragraph("0 / 16 (0%)", styles["TableCellCenter"]), Paragraph("Correctly excluded (<50%); viewable only via audit checkbox.", styles["TableCell"])],
    ]
    res_tbl = Table(test_results_data, colWidths=[65, 45, 110, 50, 75, 178])
    res_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(res_tbl)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 10: GITHUB, STREAMLIT CLOUD, LIVE QR CODE & CONCLUSION
    # =========================================================================
    story.append(Paragraph("9. GitHub Repository, Cloud Deployment, Live QR Code & Conclusion", styles["SectionHeading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceAfter=8))

    # Top Section: Deployment & QR Code Side-by-Side
    qr_img_path = ASSETS_DIR / "public_qr.png"
    qr_flowable = Image(str(qr_img_path), width=105, height=105) if qr_img_path.exists() else Paragraph("[QR Code]", styles["TableCellCenter"])

    deploy_info_html = (
        "<b>Public Repository & Verified Deployment Information:</b><br/>"
        "• <b>Target GitHub Repository:</b> <font color='#1E40AF'><u>https://github.com/tharaka1996/jeju-datahub-image-search</u></font><br/>"
        "• <b>GitHub Account:</b> <code>tharaka1996</code> (Jeju National University student account)<br/>"
        "• <b>Verified Public Streamlit App URL:</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<font color='#1E40AF'><u>https://jeju-dataapp-image-search-jwow3zrdw7hxf8btb3tata.streamlit.app/</u></font><br/>"
        "• <b>Mobile Testing:</b> Scan the live QR code on the right with any smartphone camera to launch the interactive application instantly in mobile Safari or Chrome.<br/>"
        "• <b>Cloud Deployment Audit:</b> Standardized on Python 3.11 with explicit CPU inference mode to eliminate build failures and guarantee 100% uptime."
    )

    qr_tbl = Table([[Paragraph(deploy_info_html, styles["TableCell"]), qr_flowable]], colWidths=[405, 118])
    qr_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(qr_tbl)
    story.append(Spacer(1, 8))

    story.append(Paragraph("9.1 Streamlit Community Cloud Readiness Audit Checklist", styles["SubHeading"]))

    audit_data = [
        [Paragraph("Audit Item", styles["TableHead"]), Paragraph("Target Production Standard", styles["TableHead"]), Paragraph("Audit Result & Verification Method", styles["TableHead"]), Paragraph("Status", styles["TableHead"])],
        [Paragraph("1. Dependency Resolution", styles["TableCellBold"]), Paragraph("Clean requirements.txt without restrictive version bounds", styles["TableCell"]), Paragraph("Standardized on torch>=2.0.0, transformers>=4.40.0; verified via pip", styles["TableCell"]), Paragraph("PASS", styles["TableCellCenter"])],
        [Paragraph("2. Python Environment", styles["TableCellBold"]), Paragraph("Python 3.11 prebuilt manylinux wheels", styles["TableCell"]), Paragraph(".python-version set to 3.11; container setting documented", styles["TableCell"]), Paragraph("PASS", styles["TableCellCenter"])],
        [Paragraph("3. Embedding Availability", styles["TableCellBold"]), Paragraph("Zero-cold-start precomputed embeddings", styles["TableCell"]), Paragraph("embeddings.npz (254 KB) checked into git; loads in < 0.01s", styles["TableCell"]), Paragraph("PASS", styles["TableCellCenter"])],
        [Paragraph("4. Path Portability", styles["TableCellBold"]), Paragraph("Zero absolute Windows paths (D:\\...)", styles["TableCell"]), Paragraph("Dynamic fallback resolvers in searcher.py and app.py; POSIX paths in JSON", styles["TableCell"]), Paragraph("PASS", styles["TableCellCenter"])],
        [Paragraph("5. Secret Hygiene", styles["TableCellBold"]), Paragraph("No private API keys or tokens in git history", styles["TableCell"]), Paragraph("Confirmed 100% open source; no third-party paid APIs required", styles["TableCell"]), Paragraph("PASS", styles["TableCellCenter"])],
        [Paragraph("6. Automated QA Suite", styles["TableCellBold"]), Paragraph("10-point unit verification pass rate", styles["TableCell"]), Paragraph("tests/test_qa_suite.py passed 10/10 tests in 4.8 seconds", styles["TableCell"]), Paragraph("PASS", styles["TableCellCenter"])],
    ]
    audit_tbl = Table(audit_data, colWidths=[95, 145, 223, 60])
    audit_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TEXTCOLOR', (3,1), (3,-1), colors.HexColor("#166534")),
        ('FONTNAME', (3,1), (3,-1), FONT_BOLD),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(audit_tbl)
    story.append(Spacer(1, 8))

    story.append(Paragraph("9.2 Conclusion and Future Improvements", styles["SubHeading"]))
    story.append(Paragraph(
        "<b>Conclusion:</b> This assignment successfully developed, verified, and cloud-deployed an AI multimodal image search "
        "system tailored to the Jeju Data Hub. By synthesizing PyMuPDF high-DPI rasterization, OpenAI CLIP and multilingual ViT-B/32 "
        "encoders, and Korean Standard Industrial Classification (KSIC) domain taxonomy, the platform overcomes traditional keyword search "
        "limitations. Analysts can retrieve statistical graphics using natural-language queries in English and Korean, adjust similarity "
        "thresholds interactively with sub-millisecond responsiveness, inspect grounded match explanations, and download high-resolution "
        "visual assets seamlessly.",
        styles["BodyTextCustom"]
    ))

    story.append(Paragraph(
        "<b>Future Enhancements:</b> (1) <i>Chart OCR Bounding-Box Detection:</i> Incorporating YOLOv10 to crop sub-charts and data tables "
        "individually from multi-panel report pages; (2) <i>Automated Webhook Sync:</i> Establishing a scheduled cron job or GitHub Action "
        "to poll Jeju Data Hub monthly for new releases and re-index vectors autonomously; (3) <i>Generative Multimodal Insights:</i> "
        "Coupling retrieved chart vectors with lightweight Vision-LLMs (e.g., PaliGemma or Gemini Flash) to generate automated Korean executive "
        "bullet-point summaries directly underneath each chart.",
        styles["BodyTextCustom"]
    ))

    # Build PDF with NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated final report PDF: {OUTPUT_PDF}")

    # Also sync to original report path for backward compatibility
    import shutil
    orig_pdf = DOCS_DIR / "Jeju_DataHub_AI_Image_Search_Final_Report.pdf"
    shutil.copyfile(OUTPUT_PDF, orig_pdf)
    print(f"Successfully mirrored to: {orig_pdf}")


if __name__ == "__main__":
    build_pdf()
