import requests
import re
from urllib.parse import unquote

def debug_scrape(query):
    print(f"--- Debugging query: {query} ---")
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }
    resp = requests.post("https://html.duckduckgo.com/html/", data={"q": query}, headers=headers)
    html = resp.text
    print(f"HTML size: {len(html)} bytes")
    
    # 1. Test generic regex
    links = re.findall(r'<a class="result__a" href="([^"]+)">(.*?)</a>', html)
    snippets = re.findall(r'<a class="result__snippet" href="[^"]+">(.*?)</a>', html)
    
    print(f"Regex 1 (result__a) matches: {len(links)}")
    print(f"Regex 2 (result__snippet) matches: {len(snippets)}")
    
    for i in range(min(3, len(links))):
        print(f"Match {i}: {links[i][1]} -> {snippets[i] if i < len(snippets) else 'NO SNIPPET'}")

    # 2. Test alternative regex (if layout changed)
    # Sometimes DDG uses result__body or result__snippet inside a div/span
    
    if not links:
        print("TRYING ALTERNATIVES...")
        # Dump part of HTML to see structure
        print(html[:1000])

if __name__ == "__main__":
    debug_scrape("cotacao dolar hoje")
    debug_scrape("weather tokyo")
