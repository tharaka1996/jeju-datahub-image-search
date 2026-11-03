# University Assignment Report Guide (1–2 Pages, PDF)

**Course:** Advanced Management Information Systems (AMIS)  
**Assignment:** Midterm Exam Replacement Assignment – AI Multimodal Image Search System for Jeju Data Hub  
**Student Name:** Tharaka  
**GitHub:** [https://github.com/tharaka1996](https://github.com/tharaka1996)  
**Submission Deadline:** Sunday, November 15, 2026 (JNUClass)  

---

## Required Report Sections (Slide 7 Mapping)

### 1. Project Overview & Public URLs
* **Project Title:** AI-Powered Multimodal (CLIP) Image Search System for Jeju Data Hub
* **Streamlit Community Cloud URL:** `https://jeju-datahub-image-search.streamlit.app`
* **GitHub Repository URL:** `https://github.com/tharaka1996/jeju-datahub-image-search`
* **Mobile QR Code:** Embed image from `assets/public_qr.png`

### 2. Antigravity Prompting Methodology & Development Decisions
Describe how Google DeepMind Antigravity was utilized across stages:
* **Stage 1 (Architecture & Research):** Used Antigravity to analyze `Image_Embedding(Week7).pptx`, extract slides, and construct the system call graph.
* **Stage 2 (ETL Pipeline):** Designed `collector.py` for automated REST API batch collection of 10 periodic reports and `extractor.py` for 150 DPI chart image rendering.
* **Stage 3 (AI Multimodal Engine):** Implemented dual-encoder CLIP architecture with `openai/clip-vit-base-patch32` (vision) and `sentence-transformers/clip-ViT-B-32-multilingual-v1` (text), coupled with KSIC domain synonym expansion.
* **Stage 4 (Streamlit Cloud Optimization):** Precomputed 512-dimensional vector embeddings into `data/embeddings/embeddings.npz` to ensure CPU-friendly, instant cloud deployment.

### 3. Key Screenshots (Required Evidence)
Include high-quality screenshots captured from your working Streamlit application:
1. **Screenshot 1: Main Header & Quick Filters**
   - Displays header: `Jeju Data Hub – AI Multimodal Image Search`
   - Category tags: `렌터카`, `외식`, `골프장`, `숙박`, `카페·음료`, `면세점`, `주유소`, `풍력발전`
2. **Screenshot 2: Search Results for "렌터카" (Rental Car)**
   - Shows similarity score (`89.7%`), matched chart thumbnail, grounded match reason, and context snippet.
3. **Screenshot 3: Similarity Threshold Slider in Action**
   - Demonstrates default `50%` threshold vs. adjusted higher threshold showing fewer, more precise results.
4. **Screenshot 4: Large View Modal & Download**
   - Shows the dialog popup with the high-resolution chart, one-click PNG download button, and source PDF reference.
5. **Screenshot 5: Search for "wind farm"**
   - Demonstrates query expansion and threshold behavior when a term has low similarity in consumption reports.

### 4. System Value & Future Expansion
* **Impact:** Replaces cumbersome manual PDF browsing on Jeju Data Hub with instant, visual semantic search.
* **Extensions:** Automatic indexing of real-time incoming reports, integration with local Jeju tourism APIs, and multi-language support (English, Japanese, Chinese).
