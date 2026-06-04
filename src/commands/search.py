from ddgs import DDGS

def web_search(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if not results:
                return None, "No results found."
            
            output = f"Here's what I found for '{query}':\n\n"
            raw = ""
            for i, r in enumerate(results, 1):
                output += f"{i}. {r['title']}\n"
                output += f"   {r['body']}\n"
                output += f"   {r['href']}\n\n"
                raw += f"{r['title']}: {r['body']}\n"
            
            return raw, output
    except Exception as e:
        return None, f"Search failed: {e}"