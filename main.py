"""Simple paragraph scraper and highlighter."""

import argparse
import re
import requests
from bs4 import BeautifulSoup


def main() -> None:
    """Retrieve a page and print paragraphs matching given words."""
    parser = argparse.ArgumentParser(
        description="Find paragraphs containing the specified words"
    )
    parser.add_argument("url", help="URL of the page to scrape")
    parser.add_argument(
        "words",
        nargs="+",
        help="One or more words to search for in the page",
    )
    args = parser.parse_args()

    response = requests.get(args.url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = soup.find_all("p")

    # Build regex for any of the search terms (case-insensitive)
    pattern = re.compile(
        r"(" + "|".join(re.escape(w) for w in args.words) + r")",
        re.IGNORECASE,
    )

    for p in paragraphs:
        text = p.get_text()
        if pattern.search(text):
            highlighted = pattern.sub(lambda m: m.group(0).upper(), text)
            print(highlighted)


if __name__ == "__main__":
    main()

