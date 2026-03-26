import arxiv
import os

DOWNLOAD_FOLDER = "Data"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

query = "machine learning OR artificial intelligence OR deep learning OR natural language processing"

search = arxiv.Search(
    query=query,
    max_results=200,
    sort_by=arxiv.SortCriterion.SubmittedDate
)

for i, result in enumerate(search.results()):
    print(f"Downloading {i+1}: {result.title}")

    try:
        result.download_pdf(
            dirpath=DOWNLOAD_FOLDER,
            filename=f"{result.title[:50].replace('/', '_')}.pdf"
        )
    except Exception as e:
        print("Failed:", result.title)

print("Download complete! PDFs saved in Data folder.")