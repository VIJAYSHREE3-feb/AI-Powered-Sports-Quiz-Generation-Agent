try:
    from ddgs import DDGS  # current package name (2026+)
except ImportError:
    from duckduckgo_search import DDGS  # legacy fallback


def get_live_news_context(sport_name):
    """
    Searches the live web for recent sport news, matches, or events.
    Returns a unified text summary of search snippets.
    """
    search_query = f"{sport_name} latest tournament results championship winners news 2026"
    retrieved_texts = []

    print(f"Executing web search for: '{search_query}'...")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(search_query, max_results=3))

            if not results:
                return (
                    "No live web results were returned for this query right now "
                    "(DuckDuckGo sometimes rate-limits automated searches). "
                    "The quiz below relies only on the offline historic facts."
                )

            for index, r in enumerate(results, start=1):
                title = r.get("title", "No Title")
                snippet = r.get("body", "No Snippet Content Available")
                retrieved_texts.append(f"Web Source {index}: {title}\nSnippet: {snippet}")

    except Exception as e:
        print(f"Web Search fell back or failed: {e}")
        return "No recent search engine updates available due to system connectivity."

    return "\n\n".join(retrieved_texts)