# -*- coding: utf-8 -*-
"""
scripts/capture_app_screenshots.py
Automated authentic screenshot generator using Selenium and Microsoft Edge.
Captures genuine, high-resolution visual states of the running Streamlit app:
1. Dashboard overview & KPI statistics
2. Search results for '렌터카 (Rental Car)' with 50% threshold
3. Similarity filtering at 70% threshold
4. Lightbox preview modal with chart details and download buttons
"""

import os
import sys
import time
import subprocess
import urllib.request
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_DIR = Path(__file__).resolve().parent.parent
SCREENSHOTS_DIR = BASE_DIR / "docs" / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

PORT = 8503
BASE_URL = f"http://localhost:{PORT}"


def wait_for_server(url: str, timeout: int = 35) -> bool:
    print(f"Waiting for Streamlit server at {url}...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status == 200:
                    print(f"Server is ready! (took {time.time() - start:.1f}s)")
                    return True
        except Exception:
            time.sleep(1)
    return False


def main():
    st_cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(BASE_DIR / "app.py"),
        "--server.port",
        str(PORT),
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false"
    ]
    print("Launching Streamlit server on port", PORT)
    proc = subprocess.Popen(st_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1366,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = None
    try:
        if not wait_for_server(BASE_URL, timeout=40):
            print("Server did not respond in time.")
            return

        print("Initializing Edge WebDriver...")
        driver = webdriver.Edge(options=options)
        driver.set_window_size(1366, 1080)

        # 1. Overview Dashboard
        print("Capturing 1: Dashboard Overview...")
        driver.get(BASE_URL)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "header-container"))
        )
        time.sleep(4)  # Wait for images to load
        path_overview = SCREENSHOTS_DIR / "dashboard_overview.png"
        driver.save_screenshot(str(path_overview))
        print(f"  [OK] Saved {path_overview.name} ({path_overview.stat().st_size:,} bytes)")

        # 2. Search '렌터카' with 50% threshold
        print("Capturing 2: Search '렌터카' @ 50% threshold...")
        driver.get(f"{BASE_URL}/?q=%EB%A0%8C%ED%84%B0%EC%B9%B4&threshold=50")
        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.CLASS_NAME, "stat-metric-card"))
        )
        time.sleep(4)
        path_50 = SCREENSHOTS_DIR / "search_rental_car_50.png"
        driver.save_screenshot(str(path_50))
        print(f"  [OK] Saved {path_50.name} ({path_50.stat().st_size:,} bytes)")

        # 2b. Scroll stAppViewContainer to capture Gallery Cards & Badges in close-up
        driver.execute_script("""
            var el = document.querySelector('[data-testid="stAppViewContainer"]');
            if (el) { el.scrollTop = 580; } else { window.scrollTo(0, 580); }
        """)
        time.sleep(2)
        path_cards = SCREENSHOTS_DIR / "search_cards_detail.png"
        driver.save_screenshot(str(path_cards))
        print(f"  [OK] Saved {path_cards.name} ({path_cards.stat().st_size:,} bytes)")

        # 3. Search '렌터카' with 70% threshold (Filtering demonstration)
        print("Capturing 3: Search '렌터카' @ 70% threshold...")
        driver.get(f"{BASE_URL}/?q=%EB%A0%8C%ED%84%B0%EC%B9%B4&threshold=70")
        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.CLASS_NAME, "stat-metric-card"))
        )
        time.sleep(4)
        path_70 = SCREENSHOTS_DIR / "search_rental_car_70.png"
        driver.save_screenshot(str(path_70))
        print(f"  [OK] Saved {path_70.name} ({path_70.stat().st_size:,} bytes)")

        # 4. Open Modal Dialog
        print("Capturing 4: Lightbox Modal Dialog Preview...")
        # Find detail buttons
        buttons = driver.find_elements(By.TAG_NAME, "button")
        modal_btn = None
        for b in buttons:
            if "크게 보기" in b.text:
                modal_btn = b
                break

        if modal_btn:
            driver.execute_script("arguments[0].click();", modal_btn)
            time.sleep(3)
            path_modal = SCREENSHOTS_DIR / "modal_preview.png"
            driver.save_screenshot(str(path_modal))
            print(f"  [OK] Saved {path_modal.name} ({path_modal.stat().st_size:,} bytes)")
        else:
            print("  [WARN] Detail modal button not found.")

    except Exception as e:
        print(f"Error during capture: {e}")
    finally:
        if driver:
            driver.quit()
        print("Stopping Streamlit server...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("Capture completed.")


if __name__ == "__main__":
    main()
