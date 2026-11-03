# -*- coding: utf-8 -*-
"""
app.py - Jeju Data Hub AI Multimodal Image Search Web Application
Built with Streamlit, Multilingual CLIP, and PyTorch for Jeju National University (JNU).
Features:
- Real multimodal image-text retrieval (OpenAI CLIP & Multilingual CLIP)
- Korean & English query expansion (KSIC domain taxonomy)
- Real-time similarity threshold slider (0% to 100%)
- Pinterest & Google Images-style responsive gallery card feed
- High-resolution modal preview, image download, and source PDF links
"""

import os
import sys
import html
import json
import re
from pathlib import Path
from typing import List, Dict, Optional
import streamlit as st
from PIL import Image

# Ensure local imports resolve across platforms
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from config import (
    IMAGES_DIR,
    METADATA_DIR,
    REPORTS_META_PATH,
    IMAGE_METADATA_PATH,
    EMBEDDINGS_PATH,
    QR_CODE_PATH,
    LOGO_PATH,
    DEFAULT_SIMILARITY_THRESHOLD,
    DEFAULT_TOP_K,
    DEFAULT_ALPHA,
    GITHUB_REPO_URL,
    STREAMLIT_APP_URL,
    JEJU_DATAHUB_WEB_URL
)
from searcher import JejuMultimodalSearcher
from query_expansion import QueryExpansionResult
from collector import fetch_and_download_reports
from extractor import extract_pages_and_render_images

# Streamlit Page Configuration
st.set_page_config(
    page_title="Jeju Data Hub – AI Multimodal Image Search",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Pinterest / Google Images Modern UI)
st.markdown("""
<style>
    /* Layout & Spacing */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }
    
    /* Header Styles */
    .header-container {
        text-align: center;
        margin-bottom: 1.6rem;
        padding: 1.2rem 1rem;
        background: linear-gradient(135deg, #F0F4F8 0%, #E2E8F0 100%);
        border-radius: 16px;
        border: 1px solid #CBD5E1;
    }
    .header-title {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(120deg, #1A365D, #2B6CB0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
        letter-spacing: -0.5px;
    }
    .header-subtitle {
        color: #4A5568;
        font-size: 1.1rem;
        font-weight: 500;
    }
    
    /* Card Styles */
    .image-card {
        background: #ffffff;
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid #E2E8F0;
        box-shadow: 0 3px 10px rgba(0,0,0,0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        margin-bottom: 18px;
    }
    .image-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(43, 108, 176, 0.12);
        border-color: #3182CE;
    }
    .card-meta {
        padding: 12px 14px 14px 14px;
        background: #ffffff;
    }
    .card-title {
        font-size: 0.92rem;
        font-weight: 700;
        color: #1A202C;
        line-height: 1.35;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        min-height: 2.5em;
    }
    .card-report {
        font-size: 0.77rem;
        color: #718096;
        margin-top: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .card-sub {
        font-size: 0.76rem;
        color: #A0AEC0;
        margin-top: 6px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .score-badge {
        background-color: #EBF8FF;
        color: #2B6CB0;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.78rem;
        border: 1px solid #BEE3F8;
    }
    .reason-box {
        font-size: 0.78rem;
        color: #2B6CB0;
        background: #EBF8FF;
        border-left: 3px solid #3182CE;
        border-radius: 4px;
        padding: 6px 9px;
        margin-top: 8px;
        line-height: 1.4;
    }
    .snippet-box {
        font-size: 0.76rem;
        color: #4A5568;
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 4px;
        padding: 6px 8px;
        margin-top: 6px;
        line-height: 1.38;
    }
    
    /* Query Expansion Banner */
    .expansion-banner {
        background: #F0FFF4;
        border: 1px solid #C6F6D5;
        border-left: 4px solid #38A169;
        border-radius: 8px;
        padding: 8px 14px;
        margin-bottom: 12px;
        font-size: 0.85rem;
        color: #22543D;
    }
    .term-pill {
        display: inline-block;
        background: #C6F6D5;
        color: #22543D;
        font-weight: 600;
        padding: 2px 7px;
        border-radius: 4px;
        margin-right: 5px;
        font-size: 0.78rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="Initializing AI Multimodal CLIP Engine...")
def get_searcher() -> JejuMultimodalSearcher:
    """Instantiates singleton Multimodal Searcher."""
    return JejuMultimodalSearcher()


def resolve_image_path(record: dict) -> Optional[str]:
    """Resolves local absolute image path across Windows and Linux environments."""
    img_filename = record.get("image_filename")
    if not img_filename and record.get("image_path"):
        img_filename = Path(record["image_path"]).name

    if img_filename:
        # Check standard data/images directory
        target = IMAGES_DIR / img_filename
        if target.exists():
            return str(target)
        # Check relative to current script
        alt_target = CURRENT_DIR / "data" / "images" / img_filename
        if alt_target.exists():
            return str(alt_target)

    raw_path = record.get("image_path")
    if raw_path and os.path.exists(raw_path):
        return raw_path

    return None


def highlight_keywords(snippet: str, query: str, searcher: JejuMultimodalSearcher) -> str:
    """Safely escapes HTML and highlights query tokens & expanded terms in snippet."""
    if not snippet:
        return ""
    escaped = html.escape(snippet)
    terms_to_highlight = set()

    for word in query.strip().split():
        if len(word) >= 2:
            terms_to_highlight.add(word)

    try:
        expansion = searcher.query_expander.expand_query(query)
        for term in expansion.expanded_terms:
            if len(term) >= 2:
                terms_to_highlight.add(term)
    except Exception:
        pass

    for t in sorted(terms_to_highlight, key=len, reverse=True):
        esc_t = html.escape(t)
        pattern = re.compile(re.escape(esc_t), re.IGNORECASE)
        escaped = pattern.sub(
            f'<span style="background-color:#FEFCBF; color:#744210; font-weight:bold; padding:1px 3px; border-radius:3px;">{esc_t}</span>',
            escaped
        )
    return escaped


@st.dialog("📊 차트 상세 정보 (Chart Preview & Details)", width="large")
def show_image_modal(item: dict):
    """Interactive Lightbox modal displaying high-res chart, metadata, and download buttons."""
    img_path = resolve_image_path(item)
    if img_path and os.path.exists(img_path):
        st.image(img_path, use_container_width=True)
    else:
        st.warning("⚠️ 고해상도 이미지 파일을 찾을 수 없습니다.")

    st.markdown(f"### {item.get('chart_title', item.get('report_title'))}")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**📑 원본 리포트:** {item.get('report_title', 'N/A')}")
        st.markdown(f"**📅 발간 일자:** {item.get('publication_date', 'N/A')}")
        st.markdown(f"**📄 리포트 페이지:** `{item.get('page_number', 1)} / {item.get('total_pages', 1)}쪽`")
    with col2:
        if "similarity_score" in item:
            st.metric("🎯 CLIP 종합 일치율", f"{item['similarity_score']:.1f}%")
        if "raw_clip_cosine" in item:
            st.caption(f"Visual CLIP 코사인 유사도: `{item['raw_clip_cosine']:.4f}`")

    if item.get("snippet"):
        st.info(f"**📝 해당 페이지 텍스트 발췌 요약:**\n\n{item['snippet']}")

    st.markdown("---")
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if img_path and os.path.exists(img_path):
            with open(img_path, "rb") as f_img:
                st.download_button(
                    label="💾 고해상도 차트 이미지 다운로드 (PNG)",
                    data=f_img,
                    file_name=item.get("image_filename", "jeju_chart.png"),
                    mime="image/png",
                    use_container_width=True
                )
    with btn_col2:
        source_url = item.get("source_pdf_url")
        if source_url:
            st.link_button("📥 제주데이터허브 원본 PDF 받기", source_url, use_container_width=True)
        else:
            st.link_button("🌐 제주데이터허브 리포트 목록 방문", JEJU_DATAHUB_WEB_URL, use_container_width=True)


def main():
    # Session state for query and history
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""
    if "search_history" not in st.session_state:
        st.session_state.search_history = []

    # Application Header
    st.markdown("""
    <div class="header-container">
        <div class="header-title">🌴 Jeju Data Hub – AI Multimodal Image Search</div>
        <div class="header-subtitle">Discover relevant charts, statistics and infographics using AI-powered semantic search.</div>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar Navigation & Settings
    with st.sidebar:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), use_container_width=True)
        else:
            st.title("🌴 Jeju Data Hub")

        st.markdown("### ⚙️ 시스템 설정 및 필터")

        # System Metrics
        report_count = 0
        chart_count = 0
        if REPORTS_META_PATH.exists():
            try:
                with open(REPORTS_META_PATH, "r", encoding="utf-8") as f:
                    report_count = len(json.load(f))
            except Exception:
                pass
        if IMAGE_METADATA_PATH.exists():
            try:
                with open(IMAGE_METADATA_PATH, "r", encoding="utf-8") as f:
                    chart_count = len(json.load(f))
            except Exception:
                pass

        m1, m2 = st.columns(2)
        m1.metric("색인 리포트", f"{report_count} 편")
        m2.metric("보유 차트", f"{chart_count} 장")

        st.markdown("---")
        st.subheader("🔍 검색 및 정렬 옵션")

        # Category Filter
        categories = [
            "전체",
            "교통/렌터카 (Transport & Rental)",
            "외식/식음료 (Dining & F&B)",
            "골프/스포츠 (Golf & Sports)",
            "숙박/여행 (Accommodation & Travel)",
            "쇼핑/소매 (Shopping & Retail)",
            "관광동향 (Tourism Trends)",
            "에너지/자연 (Energy & Nature)",
            "종합소비동향 (General Spending)"
        ]
        selected_category = st.selectbox("업종 카테고리 필터", categories, index=0)

        sort_by_choice = st.radio(
            "결과 정렬 기준",
            ["유사도 순 (Highest Similarity)", "최신 발간일 순 (Newest Date)"],
            index=0
        )
        sort_by = "similarity" if "유사도" in sort_by_choice else "date"

        grid_columns = st.radio("갤러리 열 수 (Columns)", [3, 4], index=1, horizontal=True)
        top_k = st.slider("출력할 최대 차트 수", min_value=6, max_value=36, value=DEFAULT_TOP_K, step=2)

        # Mobile Access QR Code
        if QR_CODE_PATH.exists():
            st.markdown("---")
            st.subheader("📱 모바일 접속 QR 코드")
            st.image(str(QR_CODE_PATH), caption="카메라로 스캔하여 스마트폰에서 바로 테스트하세요", width=180)
            st.caption(f"[배포 URL 바로가기]({STREAMLIT_APP_URL})")

        # Re-Index Button
        st.markdown("---")
        if st.button("🔄 최신 데이터 수집 및 인덱싱 재실행", use_container_width=True):
            with st.spinner("제주데이터허브에서 최신 보고서를 수집하고 멀티모달 벡터를 생성하는 중..."):
                fetch_and_download_reports(max_reports=10)
                extract_pages_and_render_images(dpi=150)
                s = get_searcher()
                s.build_embeddings()
                st.cache_resource.clear()
            st.success("데이터 갱신 완료!")
            st.rerun()

        # Search History
        if st.session_state.search_history:
            st.markdown("---")
            st.subheader("🕒 최근 검색 기록")
            for h_item in reversed(st.session_state.search_history[-5:]):
                if st.button(f"🔍 {h_item}", key=f"hist_{h_item}", use_container_width=True):
                    st.session_state.search_query = h_item
                    st.rerun()

    # Verify Vector Cache Availability
    if not EMBEDDINGS_PATH.exists() or not IMAGE_METADATA_PATH.exists():
        st.warning("⚠️ 색인 데이터 또는 임베딩 캐시가 없습니다. 사이드바에서 [최신 데이터 수집 및 인덱싱 재실행] 버튼을 눌러주세요.")
        return

    searcher = get_searcher()

    # Recommended Quick Keyword Pills
    quick_tags = [
        ("전체보기", ""),
        ("렌터카 (Rental Car)", "렌터카"),
        ("외식 (Restaurant)", "외식"),
        ("골프장 (Golf)", "골프장"),
        ("숙박 (Hotel)", "숙박"),
        ("카페·음료 (Cafe)", "카페"),
        ("면세점 (Duty Free)", "면세점"),
        ("주유소 (Gas Station)", "주유소"),
        ("풍력발전 (Wind Farm)", "wind farm")
    ]

    st.markdown("##### 💡 추천 인기 검색 키워드 (Quick Filter)")
    cols_tags = st.columns(len(quick_tags))
    for idx, (label, val) in enumerate(quick_tags):
        if cols_tags[idx].button(label, key=f"qtag_{idx}", use_container_width=True):
            st.session_state.search_query = val
            st.rerun()

    # Search Bar
    input_col1, input_col2 = st.columns([5, 1])
    with input_col1:
        user_query = st.text_input(
            "검색어 입력",
            value=st.session_state.search_query,
            placeholder="자연어 검색어를 입력하세요 (예: rental car, 외식, 골프장, wind farm, 호텔, 관광객 소비동향...)",
            label_visibility="collapsed"
        )
    with input_col2:
        search_clicked = st.button("🔍 검색", use_container_width=True)

    st.caption("⌨️ 검색어를 입력하고 **Enter**를 누르거나 **검색** 버튼을 클릭하면 AI 멀티모달 분석 결과가 즉시 표시됩니다.")

    active_query = user_query.strip()

    # Record search history
    if active_query and (not st.session_state.search_history or st.session_state.search_history[-1] != active_query):
        st.session_state.search_history.append(active_query)

    # Search Execution or Default Feed
    if active_query:
        # Perform Multimodal Search
        with st.spinner(f"AI가 '{active_query}' 관련 시각화 차트를 분석 및 랭킹하는 중..."):
            cat_filter = None if selected_category == "전체" else selected_category
            search_res = searcher.search(
                query=active_query,
                top_k=top_k,
                similarity_threshold=0.0,  # retrieve full candidate pool for interactive slider
                sort_by=sort_by,
                category_filter=cat_filter,
                alpha=DEFAULT_ALPHA
            )

        expansion: QueryExpansionResult = search_res["expansion"]
        raw_items = search_res["results"]
        top_score = search_res["highest_similarity"]

        # Display Query Expansion Banner
        if expansion.expanded_terms and len(expansion.expanded_terms) > 1:
            pills_html = "".join([f"<span class='term-pill'>{html.escape(t)}</span>" for t in expansion.expanded_terms[:8]])
            st.markdown(
                f"""
                <div class="expansion-banner">
                    <b>🔗 연관 도메인 확장 (Query Expansion):</b> {pills_html}
                    <div style="font-size:0.78rem; margin-top:4px; color:#2F855A;">{html.escape(expansion.domain_explanation)}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # 🎛️ Interactive Similarity Threshold Slider & Metrics Bar
        above_50_count = sum(1 for it in raw_items if it.get("similarity_score", 0.0) >= 50.0)
        below_50_count = len(raw_items) - above_50_count

        bar_col1, bar_col2, bar_col3 = st.columns([1.6, 1.4, 0.8])
        with bar_col1:
            st.markdown(f"#### 🔍 **'{active_query}'** 검색 결과")
            st.caption(f"최고 일치율: **{top_score:.1f}%** | 50% 이상: **{above_50_count}장** | 50% 미만: **{below_50_count}장**")
        with bar_col2:
            min_threshold = st.slider(
                "최소 일치율 필터 (%)",
                min_value=0,
                max_value=100,
                value=50,
                step=1,
                help="슬라이더를 좌우로 움직이면 설정한 일치율 이상의 차트만 실시간으로 필터링됩니다."
            )
        with bar_col3:
            st.write("")
            show_below_50 = st.checkbox("50% 미만 보기", value=False, help="체크 시 50% 미만의 저유사도 차트들을 확인합니다.")

        # Apply Threshold Filtering
        if show_below_50:
            display_items = [it for it in raw_items if it.get("similarity_score", 0.0) < 50.0]
            st.info(f"📋 일치율 50% 미만 차트 목록입니다 ({len(display_items)}장).")
        else:
            display_items = [it for it in raw_items if it.get("similarity_score", 0.0) >= min_threshold]

        if not display_items:
            st.warning(f"🔍 현재 설정한 일치율 기준(**{min_threshold}% 이상**)에 해당하는 차트 이미지가 없습니다.", icon="⚠️")
            st.info("💡 위의 슬라이더 핸들을 왼쪽으로 내려 기준을 낮추거나, '50% 미만 보기'를 체크해 보세요.")
            return

    else:
        # Default View: Show Latest Feed
        st.markdown(f"#### 📌 최신 제주 소비 빅데이터 차트 피드 ({min(top_k, len(searcher.records))}장)")
        display_items = searcher.records[:top_k]

    if not display_items:
        st.info("표시할 이미지가 없습니다.")
        return

    # Responsive Pinterest / Google Images Style Grid
    cols = st.columns(grid_columns)
    for idx, item in enumerate(display_items):
        col = cols[idx % grid_columns]
        with col:
            img_path = resolve_image_path(item)
            if img_path and os.path.exists(img_path):
                st.image(img_path, use_container_width=True)

            score_html = ""
            if "similarity_score" in item:
                score_html = f"<span class='score-badge'>일치율 {item['similarity_score']:.1f}%</span>"

            chart_title = item.get("chart_title", item.get("report_title", "차트"))
            report_title = item.get("report_title", "")
            pub_date = item.get("publication_date", "")
            page_num = item.get("page_number", 1)
            reason_text = item.get("match_reason", "최신 정기 보고서 주요 통계 차트")
            snippet_text = item.get("snippet", "")
            if len(snippet_text) > 80:
                snippet_text = snippet_text[:80] + "..."

            highlighted_snippet = highlight_keywords(snippet_text, active_query, searcher)

            st.markdown(
                f"""
                <div class="card-meta">
                    <div class="card-title" title="{html.escape(chart_title)}">{html.escape(chart_title)}</div>
                    <div class="card-report" title="{html.escape(report_title)}">출처: {html.escape(report_title)}</div>
                    <div class="card-sub">
                        <span>{pub_date} (p.{page_num})</span>
                        {score_html}
                    </div>
                    <div class="reason-box">
                        💡 <b>일치 이유:</b> {html.escape(reason_text)}
                    </div>
                    <div class="snippet-box">
                        📝 <b>본문 언급:</b> {highlighted_snippet}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Action Buttons
            action_c1, action_c2 = st.columns([1.4, 1])
            with action_c1:
                if st.button("🔍 크게 보기 & 상세", key=f"btn_modal_{idx}_{item.get('image_id', idx)}", use_container_width=True):
                    show_image_modal(item)
            with action_c2:
                if img_path and os.path.exists(img_path):
                    with open(img_path, "rb") as f_dl:
                        st.download_button(
                            label="💾 PNG",
                            data=f_dl,
                            file_name=item.get("image_filename", "chart.png"),
                            mime="image/png",
                            key=f"btn_dl_{idx}_{item.get('image_id', idx)}",
                            use_container_width=True
                        )


if __name__ == "__main__":
    main()
