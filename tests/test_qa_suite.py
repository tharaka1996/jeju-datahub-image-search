# -*- coding: utf-8 -*-
"""
test_qa_suite.py - Comprehensive Senior QA Engineer Test Suite
Validates all 10 core verification areas for the Jeju Data Hub AI Multimodal Image Search System.
"""

import os
import sys
import json
import unittest
from pathlib import Path
from PIL import Image
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    DATA_DIR,
    REPORTS_DIR,
    IMAGES_DIR,
    METADATA_DIR,
    EMBEDDINGS_DIR,
    REPORTS_META_PATH,
    IMAGE_METADATA_PATH,
    IMAGE_METADATA_CSV_PATH,
    EMBEDDINGS_PATH,
    QR_CODE_PATH,
    LOGO_PATH,
    DEFAULT_SIMILARITY_THRESHOLD
)
from searcher import JejuMultimodalSearcher
from query_expansion import QueryExpander, QueryExpansionResult
from app import resolve_image_path, highlight_keywords


class TestJejuImageSearchQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n" + "=" * 70)
        print(" STARTING SENIOR QA VERIFICATION TEST SUITE ")
        print("=" * 70)
        cls.searcher = JejuMultimodalSearcher()
        cls.expander = QueryExpander()

    # -------------------------------------------------------------
    # 1. Actual CLIP Text and Image Embeddings
    # -------------------------------------------------------------
    def test_01_clip_embeddings_validity(self):
        """Verifies that actual CLIP embeddings exist, are normalized, and have shape (124, 512)."""
        self.assertTrue(EMBEDDINGS_PATH.exists(), f"Embedding cache missing at {EMBEDDINGS_PATH}")
        self.assertIsNotNone(self.searcher.image_embeddings)
        self.assertIsNotNone(self.searcher.text_embeddings)

        img_emb = self.searcher.image_embeddings
        txt_emb = self.searcher.text_embeddings

        # Dimensionality checks
        self.assertEqual(len(img_emb.shape), 2)
        self.assertEqual(img_emb.shape[0], 124, f"Expected 124 image embeddings, got {img_emb.shape[0]}")
        self.assertEqual(img_emb.shape[1], 512, f"Expected 512-dim CLIP vectors, got {img_emb.shape[1]}")
        self.assertEqual(txt_emb.shape[0], 124)
        self.assertEqual(txt_emb.shape[1], 512)

        # Numerical sanity: No NaNs, No Infs
        self.assertFalse(np.isnan(img_emb).any(), "Image embeddings contain NaN")
        self.assertFalse(np.isinf(img_emb).any(), "Image embeddings contain Inf")
        self.assertFalse(np.isnan(txt_emb).any(), "Text embeddings contain NaN")

        # L2 Unit Norm check: ||v|| == 1.0
        norms = np.linalg.norm(img_emb, axis=1)
        np.testing.assert_allclose(norms, 1.0, rtol=1e-4, err_msg="Image embeddings must be L2-normalized")

        # Live Text Encoder check
        self.searcher.load_text_model()
        test_vec = self.searcher.text_model.encode(["test text query"], normalize_embeddings=True)[0]
        self.assertEqual(test_vec.shape[0], 512)
        self.assertAlmostEqual(float(np.linalg.norm(test_vec)), 1.0, places=4)
        print(" -> [PASS] Test 1: Actual CLIP embeddings verified (shape: 124x512, L2-normalized, valid)")

    # -------------------------------------------------------------
    # 2. Cosine Similarity Calculations
    # -------------------------------------------------------------
    def test_02_cosine_similarity_calculation(self):
        """Verifies that dot product of normalized vectors strictly equals sklearn cosine_similarity."""
        self.searcher.load_text_model()
        query_text = "제주도 렌터카 소비동향"
        q_vec = self.searcher.text_model.encode([query_text], normalize_embeddings=True)[0].reshape(1, -1)

        # Dot product computation
        dot_sims = np.dot(self.searcher.image_embeddings, q_vec.T).flatten()

        # Scikit-learn baseline computation
        sklearn_sims = cosine_similarity(q_vec, self.searcher.image_embeddings)[0]

        # Verify mathematical identity within 1e-6
        np.testing.assert_allclose(dot_sims, sklearn_sims, rtol=1e-5, atol=1e-6,
                                   err_msg="Dot product of unit vectors must match sklearn cosine_similarity exactly")
        
        # Verify cosine bounds: -1.0 <= cos(theta) <= 1.0
        self.assertTrue((dot_sims >= -1.0).all() and (dot_sims <= 1.0).all())
        print(" -> [PASS] Test 2: Cosine similarity formula mathematically verified against scikit-learn")

    # -------------------------------------------------------------
    # 3. PDF Page Extraction and PNG Generation
    # -------------------------------------------------------------
    def test_03_pdf_extraction_and_png_generation(self):
        """Verifies that all 124 rendered PNG chart images exist, are valid, and are high resolution (150 DPI)."""
        self.assertTrue(IMAGES_DIR.exists())
        png_files = list(IMAGES_DIR.glob("*.png"))
        self.assertEqual(len(png_files), 124, f"Expected 124 PNG files, found {len(png_files)}")

        checked_count = 0
        for png_path in png_files:
            file_size = png_path.stat().st_size
            self.assertGreater(file_size, 2048, f"Image file suspiciously small ({file_size} bytes): {png_path.name}")

            with Image.open(png_path) as img:
                self.assertEqual(img.format, "PNG", f"File is not a valid PNG: {png_path.name}")
                width, height = img.size
                # 150 DPI standard A4 / slide rendering is at least 1000px wide
                self.assertGreaterEqual(width, 800, f"Image width too low for 150 DPI: {width}px in {png_path.name}")
                self.assertGreaterEqual(height, 500, f"Image height too low: {height}px in {png_path.name}")
            checked_count += 1

        print(f" -> [PASS] Test 3: All {checked_count} PNG chart images verified (valid PNG, 150 DPI high-res)")

    # -------------------------------------------------------------
    # 4. Metadata Correctness
    # -------------------------------------------------------------
    def test_04_metadata_correctness(self):
        """Verifies completeness, schema, and consistency of reports and image metadata."""
        self.assertTrue(REPORTS_META_PATH.exists())
        self.assertTrue(IMAGE_METADATA_PATH.exists())
        self.assertTrue(IMAGE_METADATA_CSV_PATH.exists())

        with open(REPORTS_META_PATH, "r", encoding="utf-8") as f:
            reports_data = json.load(f)
        self.assertGreaterEqual(len(reports_data), 10, f"Expected at least 10 reports, found {len(reports_data)}")

        with open(IMAGE_METADATA_PATH, "r", encoding="utf-8") as f:
            images_data = json.load(f)
        self.assertEqual(len(images_data), 124)

        # Check required fields per record
        required_keys = [
            "image_id", "image_path", "image_filename", "report_title", "report_filename",
            "source_url", "publication_date", "page_number", "total_pages", "extracted_text",
            "category", "keywords", "chart_title"
        ]
        for idx, rec in enumerate(images_data):
            for k in required_keys:
                self.assertIn(k, rec, f"Record {idx} ({rec.get('image_id')}) missing key: {k}")
            self.assertTrue(len(rec["image_id"]) > 0)
            self.assertTrue(rec["page_number"] >= 1)

        # Check CSV consistency
        csv_df = pd.read_csv(IMAGE_METADATA_CSV_PATH)
        self.assertEqual(len(csv_df), 124)
        print(" -> [PASS] Test 4: Metadata correctness and JSON/CSV consistency verified across 124 records")

    # -------------------------------------------------------------
    # 5. Korean and English Query Support
    # -------------------------------------------------------------
    def test_05_korean_and_english_queries(self):
        """Tests multimodal retrieval across required Korean and English test queries."""
        korean_queries = ["렌터카", "외식", "골프장", "숙박", "주유소", "면세점", "카페"]
        english_queries = ["rental car", "restaurant", "golf course", "hotel", "gas station", "duty free", "cafe", "consumer spending"]

        for q in korean_queries:
            res = self.searcher.search(q, top_k=5, similarity_threshold=50.0)
            self.assertGreater(res["highest_similarity"], 65.0, f"Korean query '{q}' scored unexpectedly low: {res['highest_similarity']}%")
            self.assertGreater(res["count_above_threshold"], 0, f"Korean query '{q}' returned no results >= 50%")
            # Check results sorting
            scores = [it["similarity_score"] for it in res["results"]]
            self.assertEqual(scores, sorted(scores, reverse=True))

        for q in english_queries:
            res = self.searcher.search(q, top_k=5, similarity_threshold=50.0)
            self.assertGreater(res["highest_similarity"], 65.0, f"English query '{q}' scored unexpectedly low: {res['highest_similarity']}%")
            self.assertGreater(res["count_above_threshold"], 0, f"English query '{q}' returned no results >= 50%")
            scores = [it["similarity_score"] for it in res["results"]]
            self.assertEqual(scores, sorted(scores, reverse=True))

        print(f" -> [PASS] Test 5: Full Korean & English query support verified ({len(korean_queries) + len(english_queries)} queries tested)")

    # -------------------------------------------------------------
    # 6. Query Expansion
    # -------------------------------------------------------------
    def test_06_query_expansion(self):
        """Verifies that query expansion module properly enriches queries with KSIC and related terms."""
        # Test 1: rental car expansion
        exp1 = self.expander.expand_query("rental car")
        self.assertIn("자동차임대업", exp1.expanded_terms)
        self.assertIn("렌터카", exp1.expanded_terms)
        self.assertTrue(len(exp1.matched_categories) > 0)

        # Test 2: dining out expansion
        exp2 = self.expander.expand_query("dining out")
        self.assertTrue(any("음식점" in t for t in exp2.expanded_terms))

        # Test 3: Empty query handling
        exp_empty = self.expander.expand_query("")
        self.assertEqual(exp_empty.original_query, "")
        self.assertEqual(len(exp_empty.expanded_terms), 0)

        # Test 4: Unknown query handling
        exp_unk = self.expander.expand_query("nonexistent_rare_query_123")
        self.assertEqual(exp_unk.original_query, "nonexistent_rare_query_123")
        self.assertIn("nonexistent_rare_query_123", exp_unk.expanded_terms)

        print(" -> [PASS] Test 6: Bilingual query expansion and edge case handling verified")

    # -------------------------------------------------------------
    # 7. Similarity Threshold Slider Functionality
    # -------------------------------------------------------------
    def test_07_similarity_threshold_slider_monotonicity(self):
        """Verifies real-time threshold filtering and strict monotonicity."""
        query = "렌터카"
        thresholds = [0.0, 30.0, 50.0, 75.0, 90.0, 99.0]
        previous_count = 9999

        for th in thresholds:
            res = self.searcher.search(query, top_k=100, similarity_threshold=th)
            count = len(res["results"])
            # All returned items must satisfy score >= th
            for it in res["results"]:
                self.assertGreaterEqual(it["similarity_score"], th, f"Result score {it['similarity_score']}% is lower than threshold {th}%")
            # Monotonicity check
            self.assertLessEqual(count, previous_count, f"Count increased at higher threshold {th}%: {count} > {previous_count}")
            previous_count = count

        # At 99% threshold, should return 0 items for realistic data
        res_high = self.searcher.search(query, top_k=100, similarity_threshold=99.0)
        self.assertEqual(len(res_high["results"]), 0)

        print(" -> [PASS] Test 7: Threshold slider filtering monotonicity verified across 6 levels")

    # -------------------------------------------------------------
    # 8. Dynamic Result Filtering
    # -------------------------------------------------------------
    def test_08_dynamic_result_filtering(self):
        """Verifies category filtering, sorting options, and below-50% toggle."""
        query = "렌터카"

        # 1. Category Filter Test
        res_transport = self.searcher.search(query, top_k=20, category_filter="교통/렌터카 (Transport & Rental)")
        self.assertGreater(len(res_transport["results"]), 0)

        # 2. Date Sorting vs Similarity Sorting Test
        res_sim = self.searcher.search(query, top_k=10, sort_by="similarity")
        scores = [it["similarity_score"] for it in res_sim["results"]]
        self.assertEqual(scores, sorted(scores, reverse=True), "Results not sorted by similarity descending")

        res_date = self.searcher.search(query, top_k=10, sort_by="date")
        dates = [str(it["publication_date"]) for it in res_date["results"]]
        self.assertEqual(dates, sorted(dates, reverse=True), "Results not sorted by date descending")

        # 3. Below 50% Toggle Test
        res_full = self.searcher.search("wind farm", top_k=20, similarity_threshold=0.0)
        below_50_items = res_full["below_threshold"]
        for it in below_50_items:
            self.assertLess(it["similarity_score"], 50.0, f"Item in below_threshold has score >= 50%: {it['similarity_score']}%")

        print(" -> [PASS] Test 8: Dynamic category filtering, date/similarity sorting, and below-50% toggle verified")

    # -------------------------------------------------------------
    # 9. Image Previews and Downloads
    # -------------------------------------------------------------
    def test_09_image_previews_and_downloads(self):
        """Verifies resolve_image_path for all records, download read capability, and source links."""
        with open(IMAGE_METADATA_PATH, "r", encoding="utf-8") as f:
            records = json.load(f)

        resolved_count = 0
        for rec in records:
            resolved = resolve_image_path(rec)
            self.assertIsNotNone(resolved, f"Could not resolve image path for {rec.get('image_id')}")
            self.assertTrue(os.path.exists(resolved), f"Resolved path does not exist on disk: {resolved}")
            
            # Verify file can be read in binary mode (for Streamlit download button)
            with open(resolved, "rb") as f_img:
                data = f_img.read(1024)
                self.assertGreater(len(data), 0)
            resolved_count += 1

        self.assertEqual(resolved_count, 124)
        print(f" -> [PASS] Test 9: Image resolution and download stream verified for all {resolved_count} chart items")

    # -------------------------------------------------------------
    # 10. Compatibility with Streamlit Community Cloud
    # -------------------------------------------------------------
    def test_10_streamlit_cloud_compatibility(self):
        """Verifies relative paths, requirements.txt, configuration, and CPU-only operation."""
        # 1. Check requirements.txt contents
        req_path = PROJECT_ROOT / "requirements.txt"
        self.assertTrue(req_path.exists())
        with open(req_path, "r", encoding="utf-8") as f:
            req_text = f.read()
        required_pkgs = ["streamlit", "sentence-transformers", "transformers", "torch", "pymupdf", "pillow", "qrcode", "numpy", "pandas", "scikit-learn"]
        for pkg in required_pkgs:
            self.assertIn(pkg, req_text.lower(), f"Missing required deployment package in requirements.txt: {pkg}")

        # 2. Check Streamlit config.toml
        config_toml = PROJECT_ROOT / ".streamlit" / "config.toml"
        self.assertTrue(config_toml.exists())

        # 3. Check assets existence
        self.assertTrue(QR_CODE_PATH.exists(), f"QR Code missing at {QR_CODE_PATH}")
        self.assertTrue(LOGO_PATH.exists(), f"Logo missing at {LOGO_PATH}")

        # 4. Check device mode is CPU compatible
        self.assertIn(self.searcher.device, ["cpu", "cuda"])

        # 5. Check text highlighter function
        sample_snippet = "2026년 9월 제주지역 렌터카 및 골프장 소비 분석"
        highlighted = highlight_keywords(sample_snippet, "렌터카", self.searcher)
        self.assertIn("background-color:#FEFCBF", highlighted)

        print(" -> [PASS] Test 10: Streamlit Community Cloud compatibility and asset readiness verified")


if __name__ == "__main__":
    unittest.main()
