# Global Economic Media Radar

![RSS Update](https://github.com/CFOAndy/Repository-name-imf-rss-feed/actions/workflows/imf.yml/badge.svg)

Automated aggregation of global macro, geopolitics and financial intelligence.

This project collects and consolidates selected media sources into a unified RSS feed, automatically updated via GitHub Actions.

---

## 📡 RSS Feed

Main aggregated feed:

https://CFOAndy.github.io/Repository-name-imf-rss-feed/rss/media.xml

You can subscribe using any RSS reader.

---
## Sources

- Bloomberg
- Financial Times
- Reuters
- CNN
- BBC
- Nikkei
---
## Supported Readers

- NetNewsWire
- Feedly
- Inoreader
- Reeder
---
## 🔄 Update Frequency

The feed is automatically updated:

- Every 30 minutes
- Triggered by GitHub Actions
- Automatically committed and deployed via GitHub Pages

No manual intervention required.

---

## ⚙️ Tech Stack

- Python 3.11
- feedparser
- XML (ElementTree + minidom)
- GitHub Actions (scheduled workflow)
- GitHub Pages (deployment)

---

## 🗂 Project Structure

```
.github/workflows/imf.yml   # Scheduled automation
media_radar.py              # RSS generator
rss/media.xml               # Generated feed output
archive.html                # Historical archive page
media_db.json               # Deduplication database
```

---

## 🛠 System Architecture

```
Media Sources
    ↓
Python Aggregator
    ↓
Deduplication + Sorting
    ↓
RSS Generation
    ↓
Git Commit
    ↓
GitHub Pages Deploy
```

---

## 📜 License

For personal and research use.
