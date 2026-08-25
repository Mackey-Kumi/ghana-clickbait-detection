import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup


def extract_headlines(html, headline_selector):
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for anchor in soup.select(headline_selector):
        href = anchor.get("href")
        text = anchor.get_text(strip=True)
        if not href or not text:
            continue
        rows.append({"headline_text": text, "url": href})
    return rows


def crawl_outlet(config, fetch_fn):
    collected = {}
    for listing_url in config["listing_urls"]:
        page = 1
        while len(collected) < config["target_count"] and page <= config["max_pages_per_listing"]:
            url = listing_url if page == 1 else urljoin(listing_url, f"page/{page}/")
            html = fetch_fn(url)
            if html is None:
                break
            new_rows = extract_headlines(html, config["headline_selector"])
            added = 0
            for row in new_rows:
                if row["url"] not in collected:
                    collected[row["url"]] = row
                    added += 1
            if added == 0:
                break
            if not config["paginate"]:
                break
            page += 1
        if len(collected) >= config["target_count"]:
            break
    return list(collected.values())[: config["target_count"]]


def extract_sitemap_urls(sitemap_xml, url_filter):
    urls = re.findall(r"<loc>(.*?)</loc>", sitemap_xml)
    return [u for u in urls if url_filter in u]


def extract_single_headline(html, headline_selector):
    soup = BeautifulSoup(html, "html.parser")
    node = soup.select_one(headline_selector)
    if node is None:
        return None
    text = node.get_text(strip=True)
    return text or None


def crawl_sitemap_outlet(config, fetch_fn):
    sitemap_xml = fetch_fn(config["sitemap_url"])
    if sitemap_xml is None:
        return []
    candidate_urls = extract_sitemap_urls(sitemap_xml, config["url_filter"])
    rows = []
    for url in candidate_urls:
        if len(rows) >= config["target_count"]:
            break
        html = fetch_fn(url)
        if html is None:
            continue
        text = extract_single_headline(html, config["headline_selector"])
        if text:
            rows.append({"headline_text": text, "url": url})
    return rows
