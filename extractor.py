# -*- coding: utf-8 -*-
"""
extractor.py - PDF Text Extraction & 150 DPI Chart/Infographic Rendering Module
Extracts page-level text, detects visual chart elements, renders high-resolution PNGs,
and generates structured JSON and CSV metadata.
"""

import os
import sys
import re
import json
import logging
from typing import List, Dict, Optional
from pathlib import Path
import pymupdf  # PyMuPDF
import pandas as pd

from config import (
    REPORTS_DIR,
    IMAGES_DIR,
    METADATA_DIR,
    REPORTS_META_PATH,
    IMAGE_METADATA_PATH,
    IMAGE_METADATA_CSV_PATH,
    DEFAULT_RENDER_DPI,
    JEJU_DATAHUB_WEB_URL
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("Extractor")


def extract_chart_title_from_text(page_text: str, fallback_title: str) -> str:
    """
    Identifies specific chart/graph titles inside statistical report pages.
    E.g.: '[국내관광객] 전년 동기 대비 주요 업종별 카드이용금액(BC) 비교'
    """
    lines = [line.strip() for line in page_text.split("\n") if line.strip()]
    for line in lines:
        if "[" in line and "]" in line and len(line) >= 6 and not line.startswith("※"):
            return line
    for line in lines:
        if any(keyword in line for keyword in ["비교", "동향", "추이", "매출", "이용금액", "점유율", "증감률"]):
            if len(line) >= 6 and not line.startswith("※"):
                return line
    return fallback_title


def determine_chart_category(text: str) -> str:
    """Classifies chart page into standard thematic categories based on extracted text."""
    t_lower = text.lower()
    if any(k in t_lower for k in ["골프", "스포츠", "레저"]):
        return "골프/스포츠 (Golf & Sports)"
    elif any(k in t_lower for k in ["음식점", "외식", "한식", "일식", "중식", "서양식", "식당", "카페", "음료"]):
        return "외식/식음료 (Dining & F&B)"
    elif any(k in t_lower for k in ["렌터카", "렌트카", "자동차임대", "주유소", "충전"]):
        return "교통/렌터카 (Transport & Rental)"
    elif any(k in t_lower for k in ["호텔", "숙박", "콘도", "여관", "리조트"]):
        return "숙박/여행 (Accommodation & Travel)"
    elif any(k in t_lower for k in ["면세점", "쇼핑", "소매", "편의점", "마트"]):
        return "쇼핑/소매 (Shopping & Retail)"
    elif any(k in t_lower for k in ["관광객", "외국인", "중국관광객", "내국인관광객"]):
        return "관광동향 (Tourism Trends)"
    elif any(k in t_lower for k in ["풍력", "에너지", "신재생"]):
        return "에너지/자연 (Energy & Nature)"
    else:
        return "종합소비동향 (General Spending)"


def extract_keywords_from_text(text: str) -> List[str]:
    """Extracts high-value statistical keywords from the page text."""
    target_terms = [
        "렌터카", "자동차임대", "외식", "음식점", "한식", "일식", "중식", "서양식",
        "골프장", "숙박", "호텔", "콘도", "면세점", "소매", "편의점", "주유소",
        "카페", "비알콜음료", "관광객", "외국인", "내국인", "소비동향", "카드이용금액",
        "BC카드", "이용금액", "증가", "감소", "풍력발전", "신재생에너지"
    ]
    found = []
    text_clean = text.replace(" ", "")
    for term in target_terms:
        if term in text_clean:
            found.append(term)
    return found[:8]


def is_meaningful_page(page: pymupdf.Page, text: str) -> bool:
    """
    Filters out empty or blank pages while preserving chart and table pages.
    """
    clean_text = text.strip()
    if len(clean_text) > 25:
        return True
    # If text is brief, check if page contains vector graphics or images
    drawings = page.get_drawings()
    images = page.get_images()
    return len(drawings) > 5 or len(images) > 0


def extract_pages_and_render_images(dpi: int = DEFAULT_RENDER_DPI) -> List[Dict]:
    """
    Processes all downloaded PDF reports:
    1. Extracts text from each page.
    2. Renders high-resolution 150 DPI PNG images for all chart pages.
    3. Generates structured JSON and CSV metadata matching assignment specifications.
    
    Returns:
        List of processed image metadata records.
    """
    if not REPORTS_META_PATH.exists():
        raise FileNotFoundError(f"Missing reports metadata: {REPORTS_META_PATH}. Run collector.py first.")

    with open(REPORTS_META_PATH, "r", encoding="utf-8") as f:
        reports_meta = json.load(f)

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    zoom = dpi / 72.0
    render_matrix = pymupdf.Matrix(zoom, zoom)

    all_image_records: List[Dict] = []
    logger.info(f"Starting PDF page extraction and {dpi} DPI rendering...")

    for r_idx, report in enumerate(reports_meta, start=1):
        pdf_path_str = report.get("pdf_path")
        report_id = report.get("report_id")
        title = report.get("title", f"Report_{report_id}")
        created_at = report.get("created_at", "")
        source_url = report.get("source_url", JEJU_DATAHUB_WEB_URL)
        pdf_filename = report.get("pdf_filename", "")

        if not pdf_path_str or not os.path.exists(pdf_path_str):
            logger.warning(f"[{r_idx}/{len(reports_meta)}] PDF missing for: {title}")
            continue

        try:
            doc = pymupdf.open(pdf_path_str)
            total_pages = len(doc)
            logger.info(f"[{r_idx}/{len(reports_meta)}] Processing '{title}' ({total_pages} pages)")

            rendered_in_report = 0
            for page_idx in range(total_pages):
                page_num = page_idx + 1
                page = doc[page_idx]
                page_text = page.get_text("text").strip()

                if not is_meaningful_page(page, page_text):
                    continue

                image_id = f"report_{report_id}_p{page_num}"
                image_filename = f"{image_id}.png"
                image_path = IMAGES_DIR / image_filename
                rel_image_path = f"data/images/{image_filename}"

                # Render 150 DPI PNG if not already existing
                if not image_path.exists() or image_path.stat().st_size == 0:
                    pix = page.get_pixmap(matrix=render_matrix, alpha=False)
                    pix.save(str(image_path))

                chart_title = extract_chart_title_from_text(page_text, fallback_title=f"{title} (p.{page_num})")
                category = determine_chart_category(page_text)
                keywords = extract_keywords_from_text(page_text)

                record = {
                    "image_id": image_id,
                    "image_path": str(image_path),
                    "image_filename": image_filename,
                    "relative_image_path": rel_image_path,
                    "report_id": report_id,
                    "report_title": title,
                    "chart_title": chart_title,
                    "report_filename": pdf_filename,
                    "source_url": source_url,
                    "publication_date": created_at,
                    "page_number": page_num,
                    "total_pages": total_pages,
                    "extracted_text": page_text,
                    "category": category,
                    "keywords": keywords,
                    "file_info_id": report.get("file_info_id"),
                    "file_id": report.get("file_id")
                }
                all_image_records.append(record)
                rendered_in_report += 1

            doc.close()
            logger.info(f" -> Rendered {rendered_in_report} chart pages from {title}")
        except Exception as exc:
            logger.error(f"Failed processing PDF ({title}): {exc}")

    # Save to primary JSON
    with open(IMAGE_METADATA_PATH, "w", encoding="utf-8") as f_json:
        json.dump(all_image_records, f_json, ensure_ascii=False, indent=2)

    # Save pages_index.json (for slide 10 function call graph compatibility)
    legacy_index_path = METADATA_DIR.parent / "pages_index.json"
    with open(legacy_index_path, "w", encoding="utf-8") as f_leg:
        json.dump(all_image_records, f_leg, ensure_ascii=False, indent=2)

    # Export to CSV via Pandas (as specified in Section 4 & Technology Stack)
    df = pd.DataFrame(all_image_records)
    # Simplify text column for clean CSV storage
    if not df.empty:
        df["text_preview"] = df["extracted_text"].apply(lambda t: t[:150].replace("\n", " ") if isinstance(t, str) else "")
        csv_df = df.drop(columns=["extracted_text"])
        csv_df.to_csv(IMAGE_METADATA_CSV_PATH, index=False, encoding="utf-8-sig")
        logger.info(f"Saved metadata CSV to: {IMAGE_METADATA_CSV_PATH}")

    logger.info(f"Extraction completed. Total {len(all_image_records)} chart images extracted and indexed.")
    return all_image_records


if __name__ == "__main__":
    extract_pages_and_render_images(DEFAULT_RENDER_DPI)
