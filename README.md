# PageTextScraper

This tool fetches web pages and searches their paragraphs for given words.
Multiple URLs and words may be supplied. Results are written to a JSON file and
can optionally be exported as a Markdown document.

## Usage

```bash
python main.py --urls URL1 URL2 --words word1 word2 \
    --json-output results.json --markdown-output results.md
```

The generated JSON maps each URL to the words that were found and the matching
paragraphs.
