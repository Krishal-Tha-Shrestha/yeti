from src.ai import query_ollama

def fetch_page(url):
    prompt = f"""You are simulating a web browser running in a local environment.
Generate realistic mock text content for the webpage at the URL: "{url}".
The page content should be informative, relevant to the URL, and mimic the main body text of that website.
Do not include HTML tags, markdown formatting (like code blocks, headers, or bullet points), or conversational text.
Provide only the raw text content of the page, kept under 150 words.
"""
    try:
        content = query_ollama([{"role": "user", "content": prompt}], temperature=0.5)
        return f"[Simulated Page Content for {url}]\n\n{content.strip()}"
    except Exception as e:
        return f"Could not simulate page fetch: {e}"