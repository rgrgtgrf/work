#!/usr/bin/env python3
# scrape_to_md.py

import sys, requests, html2text

def url_to_markdown(url: str) -> str:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    conv = html2text.HTML2Text()
    conv.ignore_images = True
    conv.body_width = 0
    return conv.handle(resp.text)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scrape_to_md.py <URL>")
        sys.exit(1)
    print(url_to_markdown(sys.argv[1]))


