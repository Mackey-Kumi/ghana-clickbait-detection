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
