# Deployment Guide: GitHub & Streamlit Community Cloud

**Project:** AI Multimodal Image Search System for Jeju Data Hub  
**Student:** Tharaka (`tharaka1996`)  
**Repository Target:** `https://github.com/tharaka1996/jeju-datahub-image-search`  
**Deployment Target:** `https://jeju-datahub-image-search.streamlit.app`  

---

## 1. Local Git Initialization & Publishing to GitHub

Follow these steps to push the project to your GitHub account:

### Step 1.1: Initialize Git and Check Status
```powershell
cd "d:\BK21 - Tharaka\Sem 3\AMIS - Midterm exam\jeju-datahub-image-search"
git init
git branch -M main
```

### Step 1.2: Add Files & Commit
```powershell
git add app.py collector.py extractor.py searcher.py run_pipeline.py query_expansion.py config.py industries.json requirements.txt README.md .gitignore .streamlit/ assets/ docs/
git add data/metadata/ data/embeddings/ data/images/
git commit -m "feat: complete multimodal CLIP image search system for Jeju Data Hub"
```

### Step 1.3: Link Remote & Push
Create a public repository named `jeju-datahub-image-search` on GitHub under your account (`tharaka1996`), then run:
```powershell
git remote add origin https://github.com/tharaka1996/jeju-datahub-image-search.git
git push -u origin main
```

---

## 2. Deploying to Streamlit Community Cloud

### Step 2.1: Log into Streamlit Cloud
1. Visit [https://share.streamlit.io/](https://share.streamlit.io/)
2. Sign in using your GitHub account (`tharaka1996`).

### Step 2.2: Create New App
1. Click **"New app"** in the top right corner.
2. Select repository: `tharaka1996/jeju-datahub-image-search`
3. Branch: `main`
4. Main file path: `app.py`
5. App URL: Customize the subdomain if available (e.g., `jeju-datahub-image-search`).

### Step 2.3: Advanced Settings (Python Version)
1. Expand **Advanced settings**.
2. Select **Python 3.11**.
3. No secret keys or environment variables are required because the system does not use paid third-party APIs.

### Step 2.4: Deploy
1. Click **"Deploy!"**.
2. Streamlit Cloud will read `requirements.txt` and load `data/embeddings/embeddings.npz` directly from the repository.
3. Within 1–2 minutes, your web application will be live at:
   `https://<your-subdomain>.streamlit.app`

---

## 3. Verifying Cloud Deployment

Once live:
1. Open the public HTTPS URL in your desktop browser.
2. Open the URL on your mobile smartphone by scanning the QR code in `assets/public_qr.png` or in the application sidebar.
3. Verify that quick-tags (`렌터카`, `외식`, `골프장`) load images with 80%+ similarity.
4. Verify that the threshold slider filters cards smoothly.
5. Capture operational screenshots for the assignment report!
