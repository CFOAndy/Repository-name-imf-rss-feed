import feedparser
import os
import json
import re
from difflib import SequenceMatcher
from xml.etree.ElementTree import Element, SubElement, ElementTree
from datetime import datetime

# ==============================
# 配置
# ==============================

RSS_FEEDS = {
    "Bloomberg": "https://feeds.bloomberg.com/markets/news.rss",
    "FT": "https://www.ft.com/rss/home",
    "Caixin": "https://www.caixinglobal.com/rss/",
}

MAX_ITEMS_PER_SOURCE = 10
SIMILARITY_THRESHOLD = 0.8
OUTPUT_DIR = "output"
DB_FILE = "media_db.json"


# ==============================
# 工具函数
# ==============================

def ensure_dirs():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)


def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def is_duplicate(title, existing_titles):
    for t in existing_titles:
        if similarity(title, t) > SIMILARITY_THRESHOLD:
            return True
    return False

def clean_text(text):
    if not text:
        return ""

   
    # 去常见噪音提示
    noise_keywords = [
        "Subscribe to read",
        "Client Challenge",
        "Please enable JavaScript",
        "Accessibility help"
    ]

    for word in noise_keywords:
        text = text.replace(word, "")

    return text.strip()

def fetch_rss(source_name, url):
    feed = feedparser.parse(url)
    entries = []

    for entry in feed.entries[:MAX_ITEMS_PER_SOURCE]:
        entries.append({
            "source": source_name,
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
            "summary": entry.get("summary", "")
        })

    return entries


def save_to_db(entries):
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    data.extend(entries)

    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_rss(entries):
    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")

    SubElement(channel, "title").text = "PCOS Media Radar"
    SubElement(channel, "link").text = "https://yourgithubpage"
    SubElement(channel, "description").text = "Daily Media Feed"

    for entry in entries:
        item = SubElement(channel, "item")

        SubElement(item, "title").text = entry["title"]
        SubElement(item, "pubDate").text = entry["published"] or datetime.utcnow().isoformat()
        SubElement(item, "source").text = entry["source"]
        SubElement(item, "link").text = entry.get("link", "")
        
        description = SubElement(item, "description")
        description.text = entry["content"]

    tree = ElementTree(rss)
    tree.write(os.path.join(OUTPUT_DIR, "media.xml"),
               encoding="utf-8",
               xml_declaration=True)


# ==============================
# 主流程
# ==============================

def run_pipeline():
    ensure_dirs()

    all_entries = []
    existing_titles = []

    for source_name, url in RSS_FEEDS.items():
        print(f"Fetching: {source_name}")

        entries = fetch_rss(source_name, url)

        for entry in entries:
            title = entry["title"]

            if not is_duplicate(title, existing_titles):
                content = entry["summary"]
                
                content = clean_text(content)
                
                processed_entry = {
                    "source": entry["source"],
                    "title": title,
                    "published": entry["published"],
                    "link": entry.get("link", ""),                    
                    "content": content
                }

                all_entries.append(processed_entry)
                existing_titles.append(title)

    save_to_db(all_entries)
    generate_rss(all_entries)

    print("media.xml generated successfully.")


if __name__ == "__main__":
    run_pipeline()