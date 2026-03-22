import requests
from bs4 import BeautifulSoup

def fetch_html(url):
    response = requests.get(url)
    response.encoding = response.apparent_encoding
    return response.text

def parse_article(html):
    soup = BeautifulSoup(html, 'html.parser')

    articles = []

    for a in soup.find_all("a"):
        title = a.get_text(strip=True)
        link = a.get("href")

        if title and link and "/n/" in link:
            if link.startswith("/"):
                link = "https://note.com" + link

            articles.append({
                "title": title,
                "url": link
            })

    return articles