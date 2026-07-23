from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm

from dotenv import load_dotenv


from datetime import datetime, timedelta

import os

load_dotenv()
import urllib.parse
import feedparser



def get_company_news(company_name: str) -> dict:
    """
    Retrieve latest news for a company from Google News RSS.
    """

    try:

        query = f'"{company_name}"'

        rss_url = (
            "https://news.google.com/rss/search?"
            f"q={urllib.parse.quote(query)}+when:14d"
            "&hl=en-US&gl=US&ceid=US:en"
        )

        feed = feedparser.parse(rss_url)

        if feed.bozo:
            return {
                "agent": "NewsAgent",
                "status": "failed",
                "error": str(feed.bozo_exception)
            }

        entries = feed.entries

        if not entries:
            return {
                "agent": "NewsAgent",
                "status": "failed",
                "error": f"No news found for {company_name}"
            }

        articles = []

        seen = set()

        for entry in entries:

            title = entry.get("title", "").strip()

            if title.lower() in seen:
                continue

            seen.add(title.lower())

            source = "Google News"

            if " - " in title:
                title, source = title.rsplit(" - ", 1)

            articles.append({

                "title": title,

                "summary": entry.get("summary", ""),

                "published_at": entry.get("published", ""),

                "source": source,

                "url": entry.get("link", "")

            })

            if len(articles) == 10:
                break

        return {

            "agent": "NewsAgent",

            "status": "success",

            "company": company_name,

            "time_window": "Last 14 Days",

            "article_count": len(articles),

            "articles": articles,

            "retrieved_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),

            "source": "Google News RSS"

        }

    except Exception as e:

        return {

            "agent": "NewsAgent",

            "status": "failed",

            "error": str(e)

        }



