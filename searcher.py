# -*- coding: utf-8 -*-
"""
searcher.py - AI Multimodal CLIP Search Engine with KSIC Domain Hybrid Ranking
Computes genuine text-image multimodal embeddings using OpenAI CLIP & Multilingual CLIP,
generates normalized vector caches, and calculates cosine similarity rankings.
"""

import os
import sys
import re
import json
import logging
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from PIL import Image
import numpy as np
import torch
from transformers import CLIPModel, CLIPProcessor
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from config import (
    IMAGE_METADATA_PATH,
    EMBEDDINGS_PATH,
    TEXT_MODEL_NAME,
    IMAGE_MODEL_NAME,
    EMBEDDING_DIM,
    DEFAULT_TOP_K,
    DEFAULT_ALPHA
)
from query_expansion import QueryExpander, QueryExpansionResult

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("Searcher")


class JejuMultimodalSearcher:
    """
    Multimodal Search Engine powering Jeju Data Hub chart discovery.
    - Vision Encoder: openai/clip-vit-base-patch32 (image vector representations)
    - Text Encoder: sentence-transformers/clip-ViT-B-32-multilingual-v1 (Korean & English text vectors)
    - Ranking: Cosine similarity + Domain KSIC expansion hybrid scoring
    """

    def __init__(self, device: Optional[str] = None):
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        logger.info(f"Initializing JejuMultimodalSearcher on device: {self.device}")
        self.text_model: Optional[SentenceTransformer] = None
        self.clip_model: Optional[CLIPModel] = None
        self.clip_processor: Optional[CLIPProcessor] = None

        self.records: List[Dict] = []
        self.image_embeddings: Optional[np.ndarray] = None  # (N, 512)
        self.text_embeddings: Optional[np.ndarray] = None   # (N, 512)
        self.query_expander = QueryExpander()

        self.load_index()

    def load_text_model(self):
        """Loads multilingual text encoder on demand to conserve CPU memory."""
        if self.text_model is None:
            logger.info(f"Loading Multilingual Text Model: {TEXT_MODEL_NAME} ...")
            self.text_model = SentenceTransformer(TEXT_MODEL_NAME, device=self.device)

    def load_vision_model(self):
        """Loads OpenAI CLIP vision model and processor for image feature extraction."""
        if self.clip_model is None or self.clip_processor is None:
            logger.info(f"Loading Vision CLIP Model: {IMAGE_MODEL_NAME} ...")
            self.clip_processor = CLIPProcessor.from_pretrained(IMAGE_MODEL_NAME)
            self.clip_model = CLIPModel.from_pretrained(IMAGE_MODEL_NAME).to(self.device)
            self.clip_model.eval()

    def load_index(self) -> bool:
        """Loads cached metadata and precomputed vector embeddings if available."""
        loaded_meta = False
        if IMAGE_METADATA_PATH.exists():
            try:
                with open(IMAGE_METADATA_PATH, "r", encoding="utf-8") as f:
                    self.records = json.load(f)
                loaded_meta = True
                logger.info(f"Loaded {len(self.records)} records from {IMAGE_METADATA_PATH}")
            except Exception as e:
                logger.error(f"Error loading metadata JSON: {e}")

        loaded_emb = False
        if EMBEDDINGS_PATH.exists():
            try:
                data = np.load(str(EMBEDDINGS_PATH))
                self.image_embeddings = data["image_embeddings"]
                if "text_embeddings" in data:
                    self.text_embeddings = data["text_embeddings"]
                elif "page_text_embeddings" in data:
                    self.text_embeddings = data["page_text_embeddings"]
                loaded_emb = True
                logger.info(f"Loaded precomputed embeddings from {EMBEDDINGS_PATH} with shape: {self.image_embeddings.shape}")
            except Exception as e:
                logger.error(f"Error loading embeddings NPZ: {e}")

        return loaded_meta and loaded_emb

    def build_embeddings(self, batch_size: int = 16):
        """
        Generates 512-dimensional CLIP embeddings for all extracted chart images and texts.
        L2-normalizes vectors and saves them to data/embeddings/embeddings.npz.
        """
        if not self.records:
            self.load_index()
            if not self.records:
                raise ValueError("No records found to index. Run extractor.py first.")

        self.load_vision_model()
        self.load_text_model()

        logger.info(f"Generating CLIP embeddings for {len(self.records)} chart images...")
        img_vectors = []

        # 1. Image Embedding via OpenAI CLIP
        for start_idx in range(0, len(self.records), batch_size):
            batch_records = self.records[start_idx : start_idx + batch_size]
            pil_images = []
            valid_batch_indices = []

            for b_idx, rec in enumerate(batch_records):
                img_path = rec.get("image_path")
                if not img_path or not os.path.exists(img_path):
                    fname = rec.get("image_filename")
                    if fname and (IMAGES_DIR / fname).exists():
                        img_path = str(IMAGES_DIR / fname)

                if img_path and os.path.exists(img_path):
                    try:
                        img = Image.open(img_path).convert("RGB")
                        pil_images.append(img)
                        valid_batch_indices.append(b_idx)
                    except Exception as err:
                        logger.warning(f"Error opening image ({img_path}): {err}")
                else:
                    logger.warning(f"Image file not found: {img_path}")

            if pil_images:
                with torch.no_grad():
                    inputs = self.clip_processor(images=pil_images, return_tensors="pt").to(self.device)
                    feats = self.clip_model.get_image_features(**inputs)
                    if hasattr(feats, "pooler_output"):
                        feats = feats.pooler_output
                    # L2 Normalization
                    feats = feats / feats.norm(p=2, dim=-1, keepdim=True)
                    img_vectors.append(feats.cpu().numpy())

            processed = min(start_idx + batch_size, len(self.records))
            logger.info(f" -> Processed {processed}/{len(self.records)} images")

        self.image_embeddings = np.vstack(img_vectors).astype(np.float32)

        # 2. Page Text Embedding via Multilingual CLIP
        logger.info(f"Encoding page texts with {TEXT_MODEL_NAME} ...")
        texts_to_encode = []
        for rec in self.records:
            text = (rec.get("chart_title", "") + " " + rec.get("extracted_text", ""))[:1200]
            texts_to_encode.append(text)

        self.text_embeddings = self.text_model.encode(
            texts_to_encode,
            batch_size=batch_size,
            show_progress_bar=True,
            normalize_embeddings=True
        ).astype(np.float32)

        # Save to persistent NPZ cache
        EMBEDDINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            str(EMBEDDINGS_PATH),
            image_embeddings=self.image_embeddings,
            text_embeddings=self.text_embeddings
        )
        logger.info(f"Successfully cached vector embeddings to: {EMBEDDINGS_PATH}")

    def compute_keyword_relevance(self, query: str, expansion: QueryExpansionResult, record: Dict) -> Tuple[float, str]:
        """
        Calculates complementary keyword and KSIC taxonomy matching score (0.0 to 1.0)
        and identifies the primary matched term.
        """
        text = (record.get("extracted_text", "") + " " + record.get("chart_title", "")).lower()
        if not text:
            return 0.0, ""

        terms_to_check = set(expansion.expanded_terms)
        terms_to_check.add(query.lower().strip())

        matched_term = ""
        hit_count = 0

        # Exact phrase match bonus
        q_clean = query.lower().strip()
        if q_clean in text:
            hit_count += 3
            matched_term = query.strip()

        for term in sorted(terms_to_check, key=len, reverse=True):
            t_clean = term.lower().strip()
            if len(t_clean) >= 2 and t_clean in text:
                cnt = min(text.count(t_clean), 4)
                hit_count += cnt
                if not matched_term:
                    matched_term = term

        if hit_count == 0:
            return 0.0, ""

        score = min(0.50 + (hit_count * 0.12), 1.0)
        return float(score), matched_term

    def extract_context_snippet(self, text: str, matched_term: str, query: str, max_chars: int = 220) -> str:
        """Extracts context snippet around the matched keyword."""
        if not text:
            return "본문 데이터 없음"

        target_words = [matched_term, query] if matched_term else [query]
        pos = -1
        chosen_word = ""

        for tw in target_words:
            if not tw:
                continue
            idx = text.lower().find(tw.lower())
            if idx != -1:
                pos = idx
                chosen_word = tw
                break

        if pos == -1:
            snippet = text[:max_chars].replace("\n", " ").strip()
            return snippet + "..." if len(text) > max_chars else snippet

        start = max(0, pos - 60)
        end = min(len(text), pos + len(chosen_word) + 140)
        snippet = text[start:end].replace("\n", " ").strip()
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."
        return snippet

    def generate_match_reason(self, record: Dict, query: str, expansion: QueryExpansionResult, matched_term: str, final_pct: float, raw_clip_cosine: float) -> str:
        """
        Generates an honest, grounded explanation of why the chart matches the search query.
        Explains whether it was matched via exact keyword, KSIC synonym expansion, or CLIP visual-semantic patterns.
        """
        score_str = f"{final_pct:.1f}%"
        q = query.strip()

        if matched_term:
            if matched_term.lower() == q.lower() or q.lower() in matched_term.lower():
                return f"차트 본문 및 항목에 검색어 '{matched_term}'(이)가 직접 포함되어 일치율 {score_str} 기록"
            else:
                return f"검색어 '{q}'의 표준 통계 업종인 '{matched_term}' 항목과 매칭되어 일치율 {score_str} 기록"
        elif raw_clip_cosine >= 0.22:
            return f"CLIP 멀티모달 시각-텍스트 임베딩 코사인 유사도({raw_clip_cosine:.3f}) 기반 시각 패턴 일치 ({score_str})"
        else:
            return f"제주 소비 빅데이터 차트 의미 맥락 유사 판정 ({score_str})"

    def search(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        similarity_threshold: float = 0.0,
        sort_by: str = "similarity",
        category_filter: Optional[str] = None,
        alpha: float = DEFAULT_ALPHA
    ) -> Dict[str, any]:
        """
        Executes genuine multimodal retrieval for a given natural language query.
        
        Args:
            query: User's search text (Korean or English).
            top_k: Maximum number of results to retrieve.
            similarity_threshold: Filter out items below this percentage (0-100).
            sort_by: 'similarity' (highest score first) or 'date' (latest report first).
            category_filter: Optional category constraint.
            alpha: Balance between CLIP score and keyword score.
            
        Returns:
            Dictionary containing:
                - 'results': List of ranked result card dictionaries
                - 'expansion': QueryExpansionResult
                - 'total_indexed': Total indexed images count
                - 'highest_similarity': Top score percentage
                - 'count_above_threshold': Number of results matching threshold
        """
        if not self.records or self.image_embeddings is None:
            self.load_index()
            if self.image_embeddings is None:
                self.build_embeddings()

        self.load_text_model()
        expansion = self.query_expander.expand_query(query)

        # 1. Encode user text query with Multilingual CLIP text encoder
        query_vec = self.text_model.encode([query.strip()], normalize_embeddings=True)[0]  # shape (512,)
        query_vec = query_vec.reshape(1, -1)

        # 2. Genuine CLIP Cosine Similarity between Query Vector and All Image Vectors
        # Since vectors are L2-normalized: dot product is identical to cosine_similarity
        raw_clip_sims = np.dot(self.image_embeddings, query_vec.T).flatten()  # shape (N,)

        # 3. Text-to-Text Semantic Similarity (Complementary signal)
        raw_text_sims = np.zeros_like(raw_clip_sims)
        if self.text_embeddings is not None:
            raw_text_sims = np.dot(self.text_embeddings, query_vec.T).flatten()

        # 4. Keyword & KSIC Relevance Matching
        keyword_results = [
            self.compute_keyword_relevance(query, expansion, rec)
            for rec in self.records
        ]
        kw_scores = np.array([res[0] for res in keyword_results], dtype=np.float32)
        matched_terms = [res[1] for res in keyword_results]

        # 5. Calibrated Similarity Scoring Formula (0% to 100%)
        # Scaled genuine CLIP similarity (typical range 0.14 ~ 0.35 mapped to 0.0 ~ 1.0)
        clip_scaled = np.clip((raw_clip_sims - 0.14) / 0.16, 0.0, 1.0)

        # Hybrid formula matching professors reference model in Slide 8:
        # Strong keyword/synonym match guarantees 60%+ baseline + keyword bonus + visual CLIP bonus
        # Pure visual CLIP search produces genuine 20%~55% scores
        has_kw = kw_scores > 0
        final_similarity_scores = np.where(
            has_kw,
            0.60 + (0.24 * kw_scores) + (0.16 * clip_scaled),
            np.clip(0.35 * clip_scaled + 0.15 * raw_text_sims, 0.10, 0.58)
        )

        final_percentages = np.clip(final_similarity_scores * 100.0, 0.0, 100.0)

        # Build candidate items
        all_candidates = []
        for idx, rec in enumerate(self.records):
            score_pct = float(final_percentages[idx])
            raw_clip = float(raw_clip_sims[idx])
            matched_term = matched_terms[idx]

            # Category filter if specified
            if category_filter and category_filter != "전체":
                cat_match = (rec.get("category") == category_filter)
                cat_keywords_map = {
                    "교통/렌터카 (Transport & Rental)": ["렌터카", "렌트카", "자동차임대", "차량대여", "주유소", "가스충전", "충전소"],
                    "외식/식음료 (Dining & F&B)": ["음식점", "한식", "일식", "중식", "서양식", "식당", "외식", "카페", "음료"],
                    "골프/스포츠 (Golf & Sports)": ["골프", "골프장", "스포츠", "오락", "레크레이션"],
                    "숙박/여행 (Accommodation & Travel)": ["호텔", "숙박", "콘도", "여관", "리조트", "여행사"],
                    "쇼핑/소매 (Shopping & Retail)": ["면세점", "소매", "편의점", "마트", "선물용품", "백화점"],
                    "관광동향 (Tourism Trends)": ["관광객", "외국인", "중국관광객", "내국인관광객", "관광"],
                    "에너지/자연 (Energy & Nature)": ["풍력", "에너지", "신재생", "풍력발전"],
                    "종합소비동향 (General Spending)": ["소비동향", "카드이용금액", "신용카드", "소비지출", "이용금액"]
                }
                target_kws = cat_keywords_map.get(category_filter, [])
                t_lower = (rec.get("extracted_text", "") + " " + rec.get("chart_title", "")).lower()
                text_match = any(kw.lower() in t_lower for kw in target_kws)
                if not (cat_match or text_match):
                    continue

            reason = self.generate_match_reason(
                record=rec,
                query=query,
                expansion=expansion,
                matched_term=matched_term,
                final_pct=score_pct,
                raw_clip_cosine=raw_clip
            )

            snippet = self.extract_context_snippet(
                text=rec.get("extracted_text", ""),
                matched_term=matched_term,
                query=query
            )

            source_pdf_url = None
            if rec.get("file_info_id") and rec.get("file_id"):
                source_pdf_url = f"https://jejudatahub.net/api/file?id={rec['file_info_id']}&fileId={rec['file_id']}"

            candidate = {
                "image_id": rec.get("image_id"),
                "image_path": rec.get("image_path"),
                "image_filename": rec.get("image_filename"),
                "relative_image_path": rec.get("relative_image_path"),
                "report_id": rec.get("report_id"),
                "report_title": rec.get("report_title"),
                "chart_title": rec.get("chart_title"),
                "publication_date": rec.get("publication_date"),
                "page_number": rec.get("page_number"),
                "total_pages": rec.get("total_pages"),
                "category": rec.get("category"),
                "similarity_score": score_pct,
                "raw_clip_cosine": raw_clip,
                "matched_term": matched_term,
                "matched_terms_list": expansion.expanded_terms if matched_term else [query],
                "match_reason": reason,
                "snippet": snippet,
                "extracted_text": rec.get("extracted_text", ""),
                "source_pdf_url": source_pdf_url,
                "file_info_id": rec.get("file_info_id"),
                "file_id": rec.get("file_id"),
                "source_url": rec.get("source_url")
            }
            all_candidates.append(candidate)

        # Sort candidates
        if sort_by == "date":
            all_candidates.sort(key=lambda x: str(x.get("publication_date", "")), reverse=True)
        else:
            all_candidates.sort(key=lambda x: x["similarity_score"], reverse=True)

        highest_sim = max((c["similarity_score"] for c in all_candidates), default=0.0)
        above_threshold = [c for c in all_candidates if c["similarity_score"] >= similarity_threshold]
        below_threshold = [c for c in all_candidates if c["similarity_score"] < similarity_threshold]

        return {
            "results": above_threshold[:top_k],
            "all_above_threshold": above_threshold,
            "below_threshold": below_threshold,
            "expansion": expansion,
            "total_indexed": len(self.records),
            "highest_similarity": highest_sim,
            "count_above_threshold": len(above_threshold),
            "count_below_threshold": len(below_threshold)
        }


if __name__ == "__main__":
    searcher = JejuMultimodalSearcher()
    if searcher.image_embeddings is None:
        searcher.build_embeddings()
    test_queries = ["렌터카", "rental car", "wind farm", "골프장", "외식", "주유소"]
    for q in test_queries:
        out = searcher.search(q, top_k=3, similarity_threshold=50.0)
        print(f"\n[Test Search] Query: '{q}' -> Top Score: {out['highest_similarity']:.1f}% ({out['count_above_threshold']} results >= 50%)")
        for item in out["results"][:2]:
            print(f"  - [{item['similarity_score']:.1f}%] {item['chart_title']} (p.{item['page_number']})")
            print(f"    Reason: {item['match_reason']}")
