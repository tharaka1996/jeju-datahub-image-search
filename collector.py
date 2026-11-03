# -*- coding: utf-8 -*-
"""
collector.py - Official Jeju Data Hub Periodic Statistical Report Collector
Fetches recent periodic reports and downloads source PDFs via official public APIs.
"""

import os
import sys
import json
import logging
from typing import List, Dict, Optional
from pathlib import Path
import urllib3
import requests

from config import (
    REPORTS_DIR,
    METADATA_DIR,
    REPORTS_META_PATH,
    JEJU_DATAHUB_API_URL,
    JEJU_DATAHUB_FILE_URL,
    JEJU_DATAHUB_WEB_URL,
    DEFAULT_MAX_REPORTS
)

# Suppress insecure HTTPS warning for public data access
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("Collector")


def sanitize_filename(filename: str) -> str:
    """Sanitizes filename for cross-platform filesystem safety."""
    invalid_chars = '<>:"/\\|?*\n\r\t'
    for c in invalid_chars:
        filename = filename.replace(c, "_")
    return filename.strip().strip(".")


def fetch_and_download_reports(max_reports: int = DEFAULT_MAX_REPORTS, force_redownload: bool = False) -> List[Dict]:
    """
    Connects to Jeju Data Hub API, collects periodic statistical reports metadata,
    and downloads authentic PDF files into data/reports/.
    
    Args:
        max_reports: Number of recent reports to fetch (5 to 10 recommended).
        force_redownload: If True, re-downloads even if the file exists locally.
        
    Returns:
        List of collected report metadata dictionaries.
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    logger.info(f"Connecting to Jeju Data Hub API: {JEJU_DATAHUB_API_URL}")
    params = {
        "selection": "title + contents",
        "keyword": "",
        "isPaging": "true",
        "start": "0",
        "pageNumber": "1",
        "length": str(max_reports),
        "openYn": "true"
    }

    records = []
    try:
        response = requests.get(
            JEJU_DATAHUB_API_URL,
            params=params,
            verify=False,
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Jeju-DataHub-Search/1.0"}
        )
        response.raise_for_status()
        payload = response.json()
        records = payload.get("data", [])
        logger.info(f"Successfully retrieved {len(records)} report records from Jeju Data Hub.")
    except Exception as exc:
        logger.warning(f"Failed to query Jeju Data Hub API ({exc}). Checking local fallback reports in {REPORTS_DIR}...")
        return fallback_local_reports()

    collected_metadata: List[Dict] = []

    for index, item in enumerate(records, start=1):
        report_id = item.get("id")
        title = item.get("title", f"Report_{report_id}").strip()
        contents_html = item.get("contents", "")
        created_at = item.get("createAt", "")
        file_container = item.get("file") or {}
        file_infos = file_container.get("fileInfos", [])

        # Locate PDF attachment
        pdf_info = None
        for fi in file_infos:
            fname = fi.get("fileName", "").lower()
            if fname.endswith(".pdf"):
                pdf_info = fi
                break
        if not pdf_info and file_infos:
            pdf_info = file_infos[0]

        local_pdf_path = None
        local_filename = None
        download_success = False

        if pdf_info:
            file_id = pdf_info.get("fileId")
            file_info_id = pdf_info.get("id")
            original_fname = pdf_info.get("fileName", f"report_{report_id}.pdf")
            safe_name = sanitize_filename(f"{report_id}_{original_fname}")
            target_path = REPORTS_DIR / safe_name
            local_pdf_path = str(target_path)
            local_filename = safe_name

            download_url = f"{JEJU_DATAHUB_FILE_URL}?id={file_info_id}&fileId={file_id}"

            if not target_path.exists() or target_path.stat().st_size == 0 or force_redownload:
                logger.info(f"[{index}/{len(records)}] Downloading: {safe_name} ...")
                try:
                    dl_resp = requests.get(
                        download_url,
                        verify=False,
                        timeout=35,
                        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                    )
                    if dl_resp.status_code == 200 and len(dl_resp.content) > 1024:
                        with open(target_path, "wb") as f_out:
                            f_out.write(dl_resp.content)
                        download_success = True
                        logger.info(f" -> Saved {len(dl_resp.content):,} bytes to {safe_name}")
                    else:
                        logger.warning(f" -> Download failed with status {dl_resp.status_code}")
                except Exception as dl_err:
                    logger.error(f" -> Download error for {safe_name}: {dl_err}")
            else:
                logger.info(f"[{index}/{len(records)}] Already exists: {safe_name} ({target_path.stat().st_size:,} bytes)")
                download_success = True

        meta_entry = {
            "report_id": report_id,
            "title": title,
            "contents_html": contents_html,
            "created_at": created_at,
            "source_url": f"{JEJU_DATAHUB_WEB_URL}/report/view/{report_id}" if report_id else JEJU_DATAHUB_WEB_URL,
            "pdf_filename": local_filename,
            "pdf_path": local_pdf_path,
            "file_info_id": pdf_info.get("id") if pdf_info else None,
            "file_id": pdf_info.get("fileId") if pdf_info else None,
            "original_filename": pdf_info.get("fileName") if pdf_info else None,
            "file_size": pdf_info.get("fileSize", 0) if pdf_info else 0,
            "download_success": download_success
        }
        collected_metadata.append(meta_entry)

    # Save to JSON
    with open(REPORTS_META_PATH, "w", encoding="utf-8") as f:
        json.dump(collected_metadata, f, ensure_ascii=False, indent=2)

    logger.info(f"Report collection complete. Saved metadata for {len(collected_metadata)} reports to {REPORTS_META_PATH}")
    return collected_metadata


def fallback_local_reports() -> List[Dict]:
    """
    Fallback method: Scans data/reports/ for existing PDFs when remote API is unreachable.
    Guarantees the system functions offline or in disconnected environments.
    """
    existing_pdfs = list(REPORTS_DIR.glob("*.pdf"))
    logger.info(f"Scanning local PDFs: found {len(existing_pdfs)} files in {REPORTS_DIR}")

    if REPORTS_META_PATH.exists():
        try:
            with open(REPORTS_META_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    records = []
    for idx, pdf in enumerate(existing_pdfs, start=1):
        records.append({
            "report_id": f"local_{idx}",
            "title": pdf.stem.replace("_", " "),
            "contents_html": "",
            "created_at": "2026-01-01",
            "source_url": JEJU_DATAHUB_WEB_URL,
            "pdf_filename": pdf.name,
            "pdf_path": str(pdf),
            "file_info_id": None,
            "file_id": None,
            "original_filename": pdf.name,
            "file_size": pdf.stat().st_size,
            "download_success": True
        })

    with open(REPORTS_META_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    return records


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MAX_REPORTS
    fetch_and_download_reports(max_reports=count)
