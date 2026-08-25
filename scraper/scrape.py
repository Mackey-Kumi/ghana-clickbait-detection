import argparse
import csv
import os
import re
import time
from datetime import date
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from scraper.outlets import OUTLETS
from scraper.utils import USER_AGENT, REQUEST_DELAY_SECONDS, fetch_with_retry, dedupe_rows

CSV_FIELDS = ["outlet", "source_style", "headline_text", "url", "scraped_date"]


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


def write_csv(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def run(dry_run=False):
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    def fetch(url):
        html = fetch_with_retry(session, url)
        time.sleep(REQUEST_DELAY_SECONDS)
        return html

    today = date.today().isoformat()
    all_rows = []
    summary = []

    for outlet in OUTLETS:
        config = dict(outlet)
        if dry_run:
            config["target_count"] = 10
            if config["mode"] == "listing":
                config["max_pages_per_listing"] = 1

        if config["mode"] == "sitemap":
            rows = crawl_sitemap_outlet(config, fetch)
        else:
            rows = crawl_outlet(config, fetch)

        for row in rows:
            row["outlet"] = outlet["name"]
            row["source_style"] = outlet["source_style"]
            row["scraped_date"] = today

        rows = dedupe_rows(rows)
        write_csv(rows, f"data/raw/{outlet['name']}.csv")
        all_rows.extend(rows)
        summary.append((outlet["name"], len(rows), config["target_count"]))

    write_csv(all_rows, "data/raw/headlines_combined.csv")

    print(f"{'Outlet':<15}{'Collected':<12}{'Target':<10}")
    for name, collected, target in summary:
        flag = "" if collected >= target else "  <-- short of target"
        print(f"{name:<15}{collected:<12}{target:<10}{flag}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Fetch ~10 headlines/outlet only, for selector sanity-checking")
    args = parser.parse_args()
    run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
