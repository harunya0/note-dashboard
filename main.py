from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os
import requests
import subprocess

# ===== 設定 =====
URL = "https://note.com/metacre/all?sort=latest"
GITHUB_URL = "https://harunya0.github.io/note-dashboard/"
WEBHOOK_URL = "https://discord.com/api/webhooks/1484779516940390490/iPp51c5IpqIv5u1mGA_XpmtuuN_WzLVgyBi70mvGrBBB_0P7RBt1aD2un0ienzJLbGbI"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")
HTML_FILE = os.path.join(BASE_DIR, "index.html")


# ===== Chrome =====
def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    return webdriver.Chrome(options=options)


# ===== データ =====
def load_old_data():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ===== もっとみる =====
def load_more(driver, times=10):
    for _ in range(times):
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//button[.//span[contains(text(),'もっと')]]")
                )
            )

            driver.execute_script("arguments[0].click();", button)
            time.sleep(2)

        except:
            break


# ===== 記事取得 =====
def get_articles(driver):
    articles = []
    seen = set()

    elements = driver.find_elements(By.TAG_NAME, "a")

    for a in elements:
        link = a.get_attribute("href")

        if link and "/n/" in link and link not in seen:
            seen.add(link)

            title = (
                a.get_attribute("aria-label")
                or a.get_attribute("title")
                or a.text.strip()
                or "No Title"
            )

            articles.append({
                "title": title,
                "url": link
            })

    return articles


def get_new_articles(old, new):
    old_urls = {item["url"] for item in old}
    return [item for item in new if item["url"] not in old_urls]


# ===== HTML生成 =====
def generate_html(data):
    html = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>Note Dashboard</title>
<style>
body {font-family:sans-serif;background:#0f172a;color:#e2e8f0;padding:20px;}
.card {background:#1e293b;padding:15px;margin-bottom:10px;border-radius:10px;}
a {color:#38bdf8;text-decoration:none;}
</style>
</head>
<body>
<h1>📄 Note記事一覧</h1>
"""

    for item in data:
        html += f'<div class="card"><a href="{item["url"]}" target="_blank">{item["title"]}</a></div>'

    html += "</body></html>"

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)


# ===== GitHub自動更新 =====
def push_to_github():
    subprocess.run("git add .", shell=True)
    subprocess.run('git commit -m "auto update"', shell=True)
    subprocess.run("git push", shell=True)


# ===== Discord通知 =====
def send_discord(new_articles):
    if not new_articles:
        return

    titles = "\n".join([f"・{a['title']}" for a in new_articles[:10]])

    data = {
        "content": f"📄 新着 {len(new_articles)} 件！\n\n{titles}\n\n🔗 {GITHUB_URL}"
    }

    requests.post(WEBHOOK_URL, json=data)


# ===== main =====
def main():
    driver = create_driver()
    driver.get(URL)

    time.sleep(5)

    load_more(driver, 10)

    articles = get_articles(driver)

    old_data = load_old_data()
    new_articles = get_new_articles(old_data, articles)

    save_data(articles)
    generate_html(articles)

    push_to_github()
    send_discord(new_articles)

    driver.quit()


if __name__ == "__main__":
    main()