import arxiv
import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document

DB_PATH = "research_papers_faiss"

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)

documents = []

query = "machine learning OR artificial intelligence OR deep learning OR NLP"

search = arxiv.Search(
    query=query,
    max_results=200,
    sort_by=arxiv.SortCriterion.SubmittedDate
)

print("Fetching arXiv papers...")

for i, result in enumerate(search.results()):
    print(f"Processing {i+1}: {result.title}")

    text = f"""
    Title: {result.title}
    Authors: {", ".join([a.name for a in result.authors])}
    Abstract: {result.summary}
    Category: {result.primary_category}
    Published: {result.published}
    PDF Link: {result.pdf_url}
    """

    doc = Document(
        page_content=text,
        metadata={
            "title": result.title,
            "authors": ", ".join([a.name for a in result.authors]),
            "pdf_link": result.pdf_url
        }
    )

    documents.append(doc)

print("Creating FAISS index...")
vector_db = FAISS.from_documents(documents, embeddings)
vector_db.save_local(DB_PATH)

print("FAISS index created successfully!")