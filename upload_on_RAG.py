import json
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.document import Document

documents = []

# ---------- Load Arxiv JSON ----------
arxiv_file = "api_output/arxiv_with_content_20260316_112020.json"

with open(arxiv_file, "r", encoding="utf-8") as f:
    arxiv_data = json.load(f)

# ---------- Process Arxiv Papers ----------
for paper in arxiv_data:

    if isinstance(paper, dict):

        title = paper.get("title", "")
        authors = ", ".join(paper.get("authors", []))
        abstract = paper.get("abstract", "")

        summary = " ".join(abstract.split()[:100])

        documents.append(
            Document(
                page_content=summary,
                metadata={
                    "title": title,
                    "authors": authors
                }
            )
        )

print("Total documents loaded:", len(documents))

# ---------- Create Embeddings ----------
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ---------- Create FAISS DB ----------
vector_db = FAISS.from_documents(documents, embeddings)

# ---------- Save FAISS ----------
vector_db.save_local("research_papers_faiss")

print("✅ FAISS database created successfully!")