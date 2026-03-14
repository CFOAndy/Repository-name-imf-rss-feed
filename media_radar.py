import feedparser
import os
import json
import re
import hashlib
import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from xml.etree.ElementTree import Element, SubElement, ElementTree
from datetime import datetime
from email.utils import parsedate_to_datetime
from newspaper import Article


# ==============================
# RSS SOURCES
# ==============================

RSS_FEEDS = {

    "Bloomberg": "https://feeds.bloomberg.com/markets/news.rss",

    "FT": "https://www.ft.com/rss/home",

    "Reuters": "https://www.reuters.com/world/rss",

    "CNN": "https://rss.cnn.com/rss/edition_world.rss",

    "BBC": "https://feeds.bbci.co.uk/news/world/rss.xml",

    "Nikkei": "https://asia.nikkei.com/rss/feed/nar",

    "Caixin": "https://www.caixinglobal.com/rss/",
}

MAX_ITEMS_PER_SOURCE = 5

SIMILARITY_THRESHOLD = 0.92

OUTPUT_DIR = "rss"

DB_FILE = "media_db.json"


# ==============================
# ECONOMIC TOPICS
# ==============================

TOPIC_KEYWORDS = {

    "Energy": ["oil", "gas", "energy", "opec", "crude", "lng"],

    "Geopolitics": ["war", "iran", "russia", "military", "sanction"],

    "Rates": ["interest rate", "fed", "ecb", "central bank", "inflation"],

    "China": ["china", "beijing", "xi", "renminbi", "yuan"],

    "AI": [" artificial intelligence", " openai", " deepseek"],

    "Markets": ["stocks", "equity", "bond", "market", "trading"],

    "Companies": ["earnings", "company", "ceo", "merger", "acquisition"]
}


# ==============================
# UTILS
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

        dt = parsedate_to_datetime(date_str)

        if dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)

        return dt

    except:

        return datetime.utcnow()


def generate_guid(link):

    return hashlib.md5(link.encode()).hexdigest()


# ==============================
# FULL TEXT EXTRACTION
# ==============================

def fetch_full_text(url):

    try:

        article = Article(url)

        article.download()

        article.parse()

        text = article.text.strip()

        if len(text) > 200:
            return text

    except:
        pass

    try:

        headers = {"User-Agent": "Mozilla/5.0"}

        r = requests.get(url, headers=headers, timeout=10)

        soup = BeautifulSoup(r.text, "html.parser")

        paragraphs = soup.find_all("p")

        text = " ".join([p.get_text() for p in paragraphs])

        if len(text) > 200:
            return text

    except:
        pass

    return ""


# ==============================
# FETCH RSS
# ==============================

def fetch_rss(source_name, url):

    entries = []

    try:

        feed = feedparser.parse(url)

    except:

        print(f"RSS error: {source_name}")

        return entries

    for entry in feed.entries[:MAX_ITEMS_PER_SOURCE]:

        title = clean_html(entry.get("title", ""))

        summary = clean_html(entry.get("summary", ""))

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
# SAVE DB
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
# GENERATE RSS
# ==============================

def generate_rss(entries):

    rss = Element("rss", version="2.0")

    channel = SubElement(rss, "channel")

    SubElement(channel, "title").text = "Global Economic Media Radar"

    SubElement(channel, "link").text = "https://cfoandy.github.io/Repository-name-imf-rss-feed/"

    SubElement(channel, "description").text = "Global economic news feed"

    for entry in entries:

        item = SubElement(channel, "item")

        SubElement(item, "title").text = entry["title"]

        SubElement(item, "pubDate").text = entry["published"]

        SubElement(item, "source").text = entry["source"]

        SubElement(item, "link").text = entry["link"]

        SubElement(item, "guid").text = entry["guid"]

        desc = SubElement(item, "description")

        desc.text = entry["content"]

    tree = ElementTree(rss)

    tree.write(

        os.path.join(OUTPUT_DIR, "media.xml"),

        encoding="utf-8",

        xml_declaration=True

    )


# ==============================
# PIPELINE
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

                content = fetch_full_text(entry["link"])

                if not content:
                    content = entry.get("summary", "")

                topic = classify_topic(title)

                processed = {

                    "source": entry["source"],

                    "title": f"[{entry['source']}][{topic}] {title}",

                    "published": entry["published"],

                    "link": entry["link"],

                    "guid": generate_guid(entry["link"]),

                    "content": content

                }

                all_entries.append(processed)

                existing_titles.append(title)

    all_entries.sort(

        key=lambda x: parse_date(x["published"]),

        reverse=True

    )

    save_to_db(all_entries)

    generate_rss(all_entries)

    print("media.xml generated successfully.")


# ==============================

if __name__ == "__main__":

    run_pipeline()