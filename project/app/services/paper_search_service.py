import requests

CROSSREF_URL = "https://api.crossref.org/works"

def search_research_papers(query, limit=5):
    params = {
        "query": query,
        "rows": limit
    }

    response = requests.get(CROSSREF_URL, params=params, timeout=10)
    response.raise_for_status()

    items = response.json().get("message", {}).get("items", [])

    papers = []

    for item in items:
        papers.append({
            "title": item.get("title", ["No title"])[0],
            "authors": ", ".join(
                [a.get("given", "") + " " + a.get("family", "") 
                 for a in item.get("author", [])]
            ),
            "year": item.get("issued", {}).get("date-parts", [[None]])[0][0],
            "url": item.get("URL"),
            "abstract": item.get("abstract", "Abstract not available")
        })

    return papers