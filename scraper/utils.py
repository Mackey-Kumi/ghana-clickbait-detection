import time

import requests

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
REQUEST_DELAY_SECONDS = 1.5


def fetch_with_retry(session, url, retries=2, timeout=15, backoff_seconds=2):
    for attempt in range(retries + 1):
        try:
            response = session.get(url, timeout=timeout)
            if response.status_code == 200:
                return response.text
        except requests.RequestException:
            pass
        if attempt < retries:
            time.sleep(backoff_seconds)
    return None


def dedupe_rows(rows):
    seen = set()
    result = []
    for row in rows:
        if row["url"] in seen:
            continue
        seen.add(row["url"])
        result.append(row)
    return result
