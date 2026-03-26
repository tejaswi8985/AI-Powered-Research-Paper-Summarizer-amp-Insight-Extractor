import streamlit as st
import re
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from gemini_file import ask_gemini

st.title("📚 AI Research Paper Assistant")

# Load embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Load vector database
vector_db = FAISS.load_local(
    "research_papers_faiss",
    embeddings,
    allow_dangerous_deserialization=True
)

st.write(f"📚 Vector database loaded with {vector_db.index.ntotal} papers")

# Load all documents once
all_docs = vector_db.similarity_search("", k=200)

# Create title → doc dictionary
title_to_doc = {}
titles = []

for doc in all_docs:
    title = doc.metadata.get("title", "").strip()
    clean_title = re.sub(r'\s+', ' ', title.lower())
    title_to_doc[clean_title] = doc
    titles.append(title)

# Dropdown
selected_title = st.selectbox("Or select a paper title", [""] + titles)

# User input
query = st.text_input("Enter your research question or paper title")

# If dropdown selected → use that
if selected_title:
    query = selected_title

if query:
    query_clean = re.sub(r'\s+', ' ', query.lower().strip())

    # Exact match
    if query_clean in title_to_doc:
        results = [title_to_doc[query_clean]]
        st.info("📄 Showing exact matched paper")
    else:
        results = vector_db.similarity_search(query, k=3)
        st.info("📚 Showing top 3 related papers")

    context = ""
    relevant_docs = []

    for doc in results:
        title = doc.metadata.get("title", "Unknown Title")
        authors = doc.metadata.get("authors", "Unknown Authors")
        abstract = doc.page_content

        relevant_docs.append(doc)

        context += f"""
Title: {title}
Authors: {authors}
Abstract: {abstract}

"""

    # Ask Gemini
    response = ask_gemini(context, query)

    if "Not found in the retrieved papers" in response:
        st.warning("❌ No relevant research papers found.")
    else:
        st.subheader("📄 Relevant Papers")

        for i, doc in enumerate(relevant_docs, 1):
            title = doc.metadata.get("title", "Unknown Title")
            authors = doc.metadata.get("authors", "Unknown Authors")
            abstract = doc.page_content

            st.write(f"### Paper {i}")
            st.write("**Title:**", title)
            st.write("**Authors:**", authors)
            st.write("**Abstract:**", abstract[:300])

        st.subheader("🤖 AI Generated Insights")
        st.success(response)