# -*- coding: utf-8 -*-
"""
config.py - Configuration management for Jeju Data Hub Multimodal Image Search System
Centralizes directories, file paths, model configurations, and runtime settings.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = DATA_DIR / "reports"
IMAGES_DIR = DATA_DIR / "images"
METADATA_DIR = DATA_DIR / "metadata"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"
ASSETS_DIR = BASE_DIR / "assets"
DOCS_DIR = BASE_DIR / "docs"

# Ensure runtime directories exist
for directory in [DATA_DIR, REPORTS_DIR, IMAGES_DIR, METADATA_DIR, EMBEDDINGS_DIR, ASSETS_DIR, DOCS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# File Paths
REPORTS_META_PATH = METADATA_DIR / "reports_meta.json"
IMAGE_METADATA_PATH = METADATA_DIR / "image_metadata.json"
IMAGE_METADATA_CSV_PATH = METADATA_DIR / "image_metadata.csv"
EMBEDDINGS_PATH = EMBEDDINGS_DIR / "embeddings.npz"
INDUSTRIES_PATH = BASE_DIR / "industries.json"
QR_CODE_PATH = ASSETS_DIR / "public_qr.png"
LOGO_PATH = ASSETS_DIR / "logo.png"

# Remote API Endpoints (Official Jeju Data Hub)
JEJU_DATAHUB_API_URL = "https://jejudatahub.net/api/report/list"
JEJU_DATAHUB_FILE_URL = "https://jejudatahub.net/api/file"
JEJU_DATAHUB_WEB_URL = "https://jejudatahub.net"

# Multimodal CLIP Model Settings
TEXT_MODEL_NAME = "sentence-transformers/clip-ViT-B-32-multilingual-v1"
IMAGE_MODEL_NAME = "openai/clip-vit-base-patch32"
EMBEDDING_DIM = 512

# Processing & UI Parameters
DEFAULT_MAX_REPORTS = 10
DEFAULT_RENDER_DPI = 150
DEFAULT_SIMILARITY_THRESHOLD = 50.0  # percentage
DEFAULT_TOP_K = 16
DEFAULT_ALPHA = 0.65  # Weight between visual/semantic CLIP score and keyword score

# Public Deployment Info
GITHUB_REPO_URL = "https://github.com/tharaka1996/jeju-datahub-image-search"
STREAMLIT_APP_URL = "https://jeju-datahub-image-search.streamlit.app"
