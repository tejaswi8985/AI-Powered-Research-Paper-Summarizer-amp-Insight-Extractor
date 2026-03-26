import streamlit as st
st.set_page_config(layout="wide")

import re
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from gemini_file import ask_gemini

from neo4j import GraphDatabase
from pyvis.network import Network
import streamlit.components.v1 as components
import pandas as pd
import io

# -------------------- TITLE --------------------
st.markdown(
    "<h1 style='text-align:center;'>AI-Powered Research Paper Summarizer & Insight Extractor</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center; color:white;'>Ask questions and get AI-powered insights from research papers</p>",
    unsafe_allow_html=True
)

# -------------------- TABS --------------------
tab1, tab2 = st.tabs(['Research Paper QA', "Knowledge Graph Explorer"])

# -------------------- TAB 1 --------------------
with tab1:

    st.markdown("""
    <style>
    .stTextInput input {
        background-color: #F5F5F5;
        color: #000000;
        border-radius: 10px;
        border: 2px solid #00FFFF;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    @st.cache_resource
    def load_vector_db():
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        vector_db = FAISS.load_local(
            "research_papers_faiss",
            embeddings,
            allow_dangerous_deserialization=True
        )
        return vector_db

    vector_db = load_vector_db()

    # Show total papers
    st.write("📚 Vector database loaded with", vector_db.index.ntotal, "papers")

    # Load all papers once for exact match
    all_docs = vector_db.similarity_search("", k=200)
    title_to_doc = {}

    for doc in all_docs:
        title = doc.metadata.get("title", "").strip()
        clean_title = re.sub(r'\s+', ' ', title.lower())
        title_to_doc[clean_title] = doc

    # Dropdown for exact title selection
    titles = [doc.metadata.get("title", "Unknown") for doc in all_docs]
    selected_title = st.selectbox("Or select a paper title", [""] + titles)

    # User input
    user_query = st.text_input("Enter your research question or paper title")

    if selected_title:
        user_query = selected_title

    if st.button("Search"):

        st.subheader("📚 Top Relevant Papers")

        query_clean = re.sub(r'\s+', ' ', user_query.lower().strip())

        # Exact match
        if query_clean in title_to_doc:
            results = [title_to_doc[query_clean]]
            st.info("📄 Showing exact matched paper")
        else:
            results = vector_db.similarity_search(user_query, k=3)
            st.info("📚 Showing top 3 related papers")

        # Remove duplicates
        unique_results = []
        seen_titles = set()

        for doc in results:
            title = doc.metadata.get("title", "Unknown")
            if title not in seen_titles:
                unique_results.append(doc)
                seen_titles.add(title)

        results = unique_results

        content = ""

        for idx, doc in enumerate(results, 1):
            title = doc.metadata.get("title", f"Paper {idx}")
            authors = doc.metadata.get("authors", "Unknown Authors")
            summary = doc.page_content[:400]

            st.write(f"### Paper {idx}")
            st.write("**Title:**", title)
            st.write("**Authors:**", authors)
            st.write("**Summary:**", summary, "...")
            st.divider()

            content += f"""
            Research Paper Title: {title}
            Authors: {authors}
            Content:
            {doc.page_content}
            """

        # Gemini Insights
        with st.spinner("🤖 Generating AI Insights..."):
            response = ask_gemini(content, user_query)

        st.subheader("🤖 AI Generated Insights")
        st.success(response)
        st.info("This summary is generated from multiple research papers using AI.")

# -------------------- TAB 2 --------------------
with tab2:
    st.subheader("Knowledge Graph Explorer")

    @st.cache_resource
    def get_driver():
        return GraphDatabase.driver(
            "bolt://127.0.0.1:7687",
            auth=('neo4j', 'neo4j123')
        )

    driver = get_driver()

    @st.cache_data
    def get_domain():
        query = "MATCH (d:Domain) RETURN d.name as domain"

        with driver.session(database="neo4j") as session:
            result = session.run(query)
            domains = [r["domain"] for r in result]

        return sorted(set(domains))

    def get_graph_data(domain):
        query = """
        MATCH (p:Paper)-[:BELONGS_TO]->(d:Domain)
        WHERE toLower(d.name) = toLower($domain)

        OPTIONAL MATCH (p)<-[:WROTE]-(a:Author)
        OPTIONAL MATCH (p)-[:USES]-(m:Method)

        RETURN p.title AS paper,
               a.name AS author,
               m.name AS method,
               d.name AS domain
        """

        with driver.session(database="neo4j") as session:
            result = session.run(query, domain=domain)
            return [r.data() for r in result]

    def draw_graph(data):
        net = Network(height="650px", width="100%", bgcolor="#0B0F19", font_color="white")

        added_nodes = set()
        data = data[:200]

        for row in data:
            paper = row['paper']
            author = row['author']
            method = row['method']
            domain = row['domain']

            if paper and paper not in added_nodes:
                net.add_node(paper, label=paper[:25], color="#FFA500", shape="box")
                added_nodes.add(paper)

            if author and author not in added_nodes:
                net.add_node(author, label=author, color="#87CEEB")
                added_nodes.add(author)
                net.add_edge(author, paper)

            if method and method not in added_nodes:
                net.add_node(method, label=method, color="#32CD32")
                added_nodes.add(method)
                net.add_edge(paper, method)

            if domain and domain not in added_nodes:
                net.add_node(domain, label=domain, color="#9370DB")
                added_nodes.add(domain)
                net.add_edge(paper, domain)

        net.save_graph("graph.html")

        with open("graph.html", 'r', encoding='utf-8') as f:
            components.html(f.read(), height=650)

    domain = st.selectbox("Select Research Domain", get_domain())

    if domain:
        st.subheader(f"Knowledge Graph for Domain: {domain}")
        data = get_graph_data(domain)

        if len(data) == 0:
            st.warning("No papers found")
        else:
            df = pd.DataFrame(data)

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Papers", df['paper'].nunique())
            col2.metric("Total Authors", df['author'].nunique())
            col3.metric("Total Methods", df['method'].nunique())

            st.divider()
            st.dataframe(df, use_container_width=True)

            st.subheader("Knowledge Graph Visualization")
            draw_graph(data)