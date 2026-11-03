# -*- coding: utf-8 -*-
"""
run_pipeline.py - One-Click Ingestion, Extraction, and Multimodal CLIP Indexing Pipeline
Orchestrates the entire ETL workflow from Jeju Data Hub to high-resolution PNG rendering,
feature extraction, and vector index caching.
"""

import sys
import time
import logging
from pathlib import Path
import qrcode

from config import (
    DEFAULT_MAX_REPORTS,
    DEFAULT_RENDER_DPI,
    QR_CODE_PATH,
    STREAMLIT_APP_URL,
    REPORTS_META_PATH,
    IMAGE_METADATA_PATH,
    EMBEDDINGS_PATH
)
from collector import fetch_and_download_reports
from extractor import extract_pages_and_render_images
from searcher import JejuMultimodalSearcher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("Pipeline")


def generate_qr_code(target_url: str = STREAMLIT_APP_URL):
    """Generates mobile access QR code for the web application."""
    QR_CODE_PATH.parent.mkdir(parents=True, exist_ok=True)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(target_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1A365D", back_color="white")
    img.save(str(QR_CODE_PATH))
    logger.info(f"Generated mobile access QR code at: {QR_CODE_PATH}")


def run_pipeline(max_reports: int = DEFAULT_MAX_REPORTS, dpi: int = DEFAULT_RENDER_DPI):
    """
    Executes the complete end-to-end pipeline:
    1. Collect recent PDF reports from Jeju Data Hub API.
    2. Extract page text and render 150 DPI chart PNGs.
    3. Generate 512-dim multimodal CLIP embeddings and save cache.
    4. Create mobile access QR code.
    """
    overall_start = time.time()
    print("=" * 70)
    print("  JEJU DATA HUB AI MULTIMODAL IMAGE SEARCH PIPELINE")
    print("=" * 70)

    # Step 1: Collect reports
    t0 = time.time()
    print("\n[Stage 1/3] Collecting periodic reports from Jeju Data Hub...")
    reports = fetch_and_download_reports(max_reports=max_reports)
    print(f" -> Completed Stage 1 in {time.time() - t0:.1f}s ({len(reports)} reports collected)")

    # Step 2: Extract text & render 150 DPI images
    t1 = time.time()
    print(f"\n[Stage 2/3] Extracting text and rendering chart pages ({dpi} DPI PNG)...")
    images = extract_pages_and_render_images(dpi=dpi)
    print(f" -> Completed Stage 2 in {time.time() - t1:.1f}s ({len(images)} pages extracted & rendered)")

    # Step 3: Compute CLIP vector embeddings
    t2 = time.time()
    print("\n[Stage 3/3] Generating Multimodal CLIP embeddings & building index...")
    searcher = JejuMultimodalSearcher()
    searcher.build_embeddings()
    print(f" -> Completed Stage 3 in {time.time() - t2:.1f}s (cached to {EMBEDDINGS_PATH})")

    # Generate QR Code
    generate_qr_code(STREAMLIT_APP_URL)

    total_time = time.time() - overall_start
    print("\n" + "=" * 70)
    print(f"  PIPELINE EXECUTION COMPLETE! Total time: {total_time:.1f} seconds")
    print(f"  - Indexed Reports: {len(reports)}")
    print(f"  - High-Res Charts: {len(images)}")
    print(f"  - Embedding Cache: {EMBEDDINGS_PATH}")
    print("  To launch the Streamlit web application, run:")
    print("    streamlit run app.py")
    print("=" * 70)


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MAX_REPORTS
    run_pipeline(max_reports=count)
