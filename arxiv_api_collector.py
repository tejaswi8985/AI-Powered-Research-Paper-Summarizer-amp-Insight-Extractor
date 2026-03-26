# =========================
# IMPORTS
# =========================
import arxiv
import json
import os
from datetime import datetime

# =========================
# SEARCH QUERY
# =========================
query = "machine learning"

# number of papers you want
MAX_RESULTS = 200


# =========================
# FETCH PAPERS FROM ARXIV
# =========================
def collect_arxiv_papers():

    print("🚀 Fetching papers from arXiv...\n")

    search = arxiv.Search(
        query=query,
        max_results=MAX_RESULTS,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    papers = []

    for result in search.results():

        paper = {
            "title": result.title,
            "abstract": result.summary,
            "authors": [a.name for a in result.authors],
            "published": str(result.published),
            "pdf_url": result.pdf_url
        }

        papers.append(paper)

    return papers


# =========================
# SAVE JSON
# =========================
def save_json(data):

    os.makedirs("api_output", exist_ok=True)

    file_name = f"arxiv_with_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    file_path = os.path.join("api_output", file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return file_path


# =========================
# MAIN
# =========================
if __name__ == "__main__":

    papers = collect_arxiv_papers()

    output = save_json(papers)

    print("\n✅ Papers collected:", len(papers))
    print("📁 Saved to:", output)