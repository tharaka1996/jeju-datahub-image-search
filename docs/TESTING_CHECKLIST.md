# Quality Assurance & Testing Checklist

## Project: AI Multimodal Image Search System for Jeju Data Hub
**Author**: Tharaka (tharaka1996)  
**Institution**: Jeju National University (JNU)  
**Environment**: Python 3.11, Streamlit, PyTorch, Transformers, Sentence-Transformers, PyMuPDF  

---

### Test Summary Matrix

| Test ID | Category | Description | Target Criteria | Status | Verified Result |
|---|---|---|---|---|---|
| **TC-01** | Data Ingestion | Query Jeju Data Hub API & download periodic PDFs | 5–10 recent PDF reports downloaded | **PASS** | 10 reports collected (reports 86 to 95) |
| **TC-02** | ETL & Rendering | Extract text & render chart pages at 150 DPI | Crisp PNGs, no blank pages | **PASS** | 124 high-resolution 150 DPI PNGs rendered |
| **TC-03** | Metadata Export | Store structured metadata in JSON & CSV | `image_metadata.json` & `.csv` generated | **PASS** | 124 structured records with all required fields |
| **TC-04** | Multimodal Vision | Encode chart images via `clip-vit-base-patch32` | 512-dim L2-normalized image vectors | **PASS** | (124, 512) float32 matrix cached |
| **TC-05** | Multimodal Text | Encode Korean/English text via Multilingual CLIP | 512-dim L2-normalized text vectors | **PASS** | `sentence-transformers/clip-ViT-B-32-multilingual-v1` |
| **TC-06** | Vector Caching | Save & load precomputed vectors via NPZ | Rapid app startup without re-encoding | **PASS** | `data/embeddings/embeddings.npz` (124, 512) |
| **TC-07** | Cosine Similarity | Calculate `similarity = dot(text_vec, img_vec)` | Cosine similarity formula implemented | **PASS** | Dot product on unit vectors yields true cosine |
| **TC-08** | Score Calibration | Convert raw scores to 0–100% human-readable % | Realistic similarity percentage scale | **PASS** | Direct matches 85–95%, semantic 20–50% |
| **TC-09** | Query Expansion | Map colloquial & English terms to KSIC | Non-destructive synonym expansion | **PASS** | Korean & English mapping with domain category |
| **TC-10** | Threshold Slider | Filter results in real-time by similarity % | Slider dynamically hides items below % | **PASS** | Verified with 0%–100% slider & <50% checkbox |
| **TC-11** | Match Explanation | Provide grounded reason for each result card | Cites matched term, sector, or CLIP pattern | **PASS** | Direct keyword, KSIC, and CLIP pattern callouts |
| **TC-12** | Lightbox & Download | Modal popup with high-res PNG & PDF link | One-click PNG download & official PDF URL | **PASS** | Streamlit dialog with PNG blob & API link |
| **TC-13** | App Server Startup | Start Streamlit web application | HTTP 200 OK without runtime errors | **PASS** | Uvicorn server started on port 8501 |

---

### Detailed Search Query Validation Logs

#### 1. Query: `rental car` (English) / `렌터카` (Korean)
* **Expanded Terms**: `자동차임대업`, `차량대여`, `렌트카`, `렌터카`, `car rental`
* **Domain Category**: `교통/렌터카 (Transportation & Rental)`
* **Highest Similarity**: **89.7%**
* **Results >= 50%**: 57 charts
* **Top Matched Chart**: `[제주도전체*] 전년 동기 대비 주요 업종별 카드이용금액(BC) 비교`
* **Grounded Reason**: `검색어 'rental car'의 표준 통계 업종인 '자동차임대업' 항목과 매칭되어 일치율 89.7% 기록`

#### 2. Query: `wind farm` (English) / `풍력발전` (Korean)
* **Expanded Terms**: `풍력발전`, `풍력`, `신재생에너지`, `풍력단지`, `wind power`
* **Domain Category**: `신재생에너지 (Renewable Energy)`
* **Highest Similarity**: **26.4%**
* **Results >= 50%**: 0 charts (Correctly reflects absence of wind energy tables in retail card consumption reports)
* **Threshold Behavior**: When slider is set to 20% or "50% 미만 보기" is checked, lowest-distance semantic charts appear with visual pattern explanation.

#### 3. Query: `restaurant` (English) / `외식` (Korean)
* **Expanded Terms**: `한식음식점업`, `일식음식점업`, `중식음식점업`, `서양식음식점업`, `식당`, `외식`
* **Domain Category**: `외식 / 식음료 (Dining & F&B)`
* **Highest Similarity**: **88.1%**
* **Results >= 50%**: 57 charts
* **Grounded Reason**: `검색어 'restaurant'의 표준 통계 업종인 '한식음식점업' 항목과 매칭되어 일치율 88.1% 기록`

#### 4. Query: `golf course` (English) / `골프장` (Korean)
* **Expanded Terms**: `골프장운영업`, `골프장`, `골프`, `golf`
* **Domain Category**: `골프 / 레저 (Sports & Golf)`
* **Highest Similarity**: **89.9%**
* **Results >= 50%**: 57 charts
* **Grounded Reason**: `차트 본문 및 항목에 검색어 '골프장'이 직접 포함되어 일치율 89.9% 기록`

#### 5. Query: `consumer spending` (English) / `소비동향` (Korean)
* **Expanded Terms**: `소비동향`, `카드이용금액`, `신용카드`, `BC카드`, `소비지출`
* **Domain Category**: `소비 지출 / 카드 (Consumer Spending)`
* **Highest Similarity**: **94.7%**
* **Results >= 50%**: 106 charts
* **Grounded Reason**: `차트 본문 및 분석 내용에 '카드이용금액' 키워드가 직접 수록되어 일치율 94.7% 기록`
