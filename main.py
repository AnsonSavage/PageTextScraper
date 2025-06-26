"""Simple paragraph scraper and highlighter.

This script can scrape multiple URLs and search for multiple words in the
retrieved paragraphs. The results for each URL/word pair are saved to a JSON
file and can optionally be rendered to a Markdown document.
"""

import argparse
import json
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def _scrape_url(url: str, words: list[str]) -> dict[str, list[str]]:
    """Return paragraphs from *url* containing any of *words*.

    The returned mapping has each searched word as the key and a list of
    paragraphs containing that word as the value. Words are returned in
    uppercase for emphasis.
    """
    response = requests.get(url)
    response.raise_for_status()

    # Some sites misreport their encoding. Using apparent_encoding helps avoid
    # mojibake characters in the scraped text.
    response.encoding = response.apparent_encoding or "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = [p.get_text() for p in soup.find_all("p")]

    results: dict[str, list[str]] = {}
    for word in words:
        # Use word boundaries to avoid matching substrings inside other words.
        pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
        matches = []
        for text in paragraphs:
            if pattern.search(text):
                matches.append(pattern.sub(lambda m: m.group(0).upper(), text))
        if matches:
            results[word] = matches
    return results


def _write_markdown(results: dict[str, dict[str, list[str]]], path: Path) -> None:
    """Write *results* to *path* formatted as Markdown."""
    lines = []
    for url, word_map in results.items():
        lines.append(f"## {url}")
        for word, paragraphs in word_map.items():
            lines.append(f"### {word}")
            for para in paragraphs:
                lines.append(f"- {para}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    """Retrieve pages and save paragraphs matching given words."""
    parser = argparse.ArgumentParser(
        description="Find paragraphs containing the specified words",
    )
    parser.add_argument(
        "--urls",
        nargs="+",
        required=True,
        help="One or more URLs of pages to scrape",
    )
    parser.add_argument(
        "--words",
        nargs="+",
        required=True,
        help="Words to search for in the pages",
    )
    parser.add_argument(
        "--json-output",
        default="results.json",
        help="Path of the JSON file to write results to",
    )
    parser.add_argument(
        "--markdown-output",
        help="Optional path of a Markdown file to write formatted results",
    )
    args = parser.parse_args()

    all_results: dict[str, dict[str, list[str]]] = {}
    for url in args.urls:
        all_results[url] = _scrape_url(url, args.words)

    json_path = Path(args.json_output)
    json_path.write_text(
        json.dumps(all_results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    if args.markdown_output:
        _write_markdown(all_results, Path(args.markdown_output))


if __name__ == "__main__":
    main()
