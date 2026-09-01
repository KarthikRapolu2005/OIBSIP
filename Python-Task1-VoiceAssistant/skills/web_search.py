"""skills/web_search.py -- Performs a web search by opening the default browser."""

import webbrowser
import urllib.parse


def web_search(query: str) -> str:
    query = (query or "").strip()
    if not query:
        return "I didn't catch what you want me to search for. Please try again."

    url = "https://www.google.com/search?q=" + urllib.parse.quote_plus(query)
    try:
        opened = webbrowser.open(url)
        if opened:
            return f"Here are the search results for {query}, opened in your browser."
        return (
            f"I tried to open a browser to search for '{query}', but no browser "
            "could be launched in this environment. Here is the link: " + url
        )
    except Exception as exc:
        return f"I couldn't open the browser to search ({exc}). You can visit: {url}"
