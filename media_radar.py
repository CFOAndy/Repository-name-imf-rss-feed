import feedparser
import os
import json
import re
from difflib import SequenceMatcher
from xml.etree.ElementTree import Element, SubElement, ElementTree
from datetime import datetime
from email.utils import parsedate_to_datetime


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
OUTPUT_DIR = "rss"
DB_FILE = "media_db.json"


# ==============================
# 宏观主题关键词
# ==============================

TOPIC_KEYWORDS = {
    "Energy": ["oil", "gas", "energy", "opec", "crude", "lng"],
    "Geopolitics": ["war", "iran", "china", "russia", "military", "sanction"],
    "Rates": ["interest rate", "fed", "ecb", "central bank", "inflation"],
    "China": ["china", "beijing", "xi", "renminbi"],
    "AI": ["ai", "artificial intelligence", "deepseek", "openai"],
    "Markets": ["stocks", "equity", "bond", "market"],
}


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


def clean_html(text):
    return re.sub(r"<.*?>", "", text or "")


def classify_topic(title):
    title_lower = title.lower()

    for topic, keywords in TOPIC_KEYWORDS.items():
        for keyword in keywords:
            if keyword in title_lower:
                return topic

    return "General"


def parse_date(date_str):
    try:
        return parsedate_to_datetime(date_str)
    except:
        return datetime.utcnow()


# ==============================
# RSS抓取
# ==============================

def fetch_rss(source_name, url):

    entries = []

    try:
        feed = feedparser.parse(url)
    except Exception as e:
        print(f"RSS error: {source_name}")
        return entries

    for entry in feed.entries[:MAX_ITEMS_PER_SOURCE]:

        title = clean_html(entry.get("title", ""))
        summary = entry.get("summary", "")
        link = entry.get("link", "")
        published = entry.get("published", "")

        entries.append({
            "source": source_name,
            "title": title,
            "link": link,
            "published": published,
            "summary": summary
        })

    return entries


# ==============================
# DB保存
# ==============================

def save_to_db(entries):

    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    data.extend(entries)

    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ==============================
# 生成RSS
# ==============================

def generate_rss(entries):

    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")

    SubElement(channel, "title").text = "Global Macro Media Radar"
    SubElement(channel, "link").text = "https://cfoandy.github.io/Repository-name-imf-rss-feed/"
    SubElement(channel, "description").text = "Automated global macro news feed"

    for entry in entries:

        item = SubElement(channel, "item")

        SubElement(item, "title").text = entry["title"]

        pub = entry["published"] or datetime.utcnow().isoformat()
        SubElement(item, "pubDate").text = pub

        SubElement(item, "source").text = entry["source"]
        SubElement(item, "link").text = entry["link"]

        description = SubElement(item, "description")
        description.text = entry["content"]

    tree = ElementTree(rss)

    tree.write(
        os.path.join(OUTPUT_DIR, "media.xml"),
        encoding="utf-8",
        xml_declaration=True
    )


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

            title = entry["title"].strip()

            if not is_duplicate(title, existing_titles):

                content = entry.get("summary", "").strip()

                if not content:
                    link = entry.get("link", "")
                    content = f"<p>Full article: <a href='{link}'>{link}</a></p>"

                topic = classify_topic(title)

                processed_entry = {

                    "source": entry["source"],

                    "title": f"[{entry['source']}][{topic}] {title}",

                    "published": entry["published"],

                    "link": entry.get("link", ""),

                    "content": content

                }

                all_entries.append(processed_entry)
                existing_titles.append(title)

    # 排序（最新新闻优先）

    all_entries.sort(
        key=lambda x: parse_date(x["published"]),
        reverse=True
    )

    save_to_db(all_entries)

    generate_rss(all_entries)

    print("media.xml generated successfully.")


# ==============================
# 入口
# ==============================

if __name__ == "__main__":
    run_pipeline()
