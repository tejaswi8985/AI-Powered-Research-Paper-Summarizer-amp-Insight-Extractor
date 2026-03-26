from neo4j import GraphDatabase
import json
import re

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "neo4j123")
)

# -------- Extract Authors --------
def extract_authors(text):
    lines = text.split("\n")[:10]
    author_line = " ".join(lines)

    # Find names like: John Smith
    authors = re.findall(r"[A-Z][a-z]+ [A-Z][a-z]+", author_line)

    # Remove duplicates
    return list(set(authors))


# -------- Detect Domain --------
def detect_domain(text):
    text = text.lower()

    if "vision" in text or "image" in text or "object detection" in text:
        return "Computer Vision"
    elif "nlp" in text or "language" in text or "transformer" in text:
        return "Natural Language Processing"
    elif "robot" in text or "robotics" in text:
        return "Robotics"
    elif "reinforcement learning" in text:
        return "Reinforcement Learning"
    elif "medical" in text or "health" in text:
        return "Healthcare AI"
    else:
        return "Machine Learning"


# -------- Create Graph --------
def create_graph(tx, paper):
    title = paper.get("file_name", "Unknown Paper").replace(".pdf", "")
    content = paper.get("content", "")

    domain = detect_domain(content)
    authors = extract_authors(content)

    # Method detection
    methods = []
    keywords = ["CNN", "RNN", "Transformer", "Reinforcement Learning",
                "GAN", "BERT", "Diffusion", "LSTM", "Neural Network",
                "RLHF", "Attention", "LLM", "FAISS", "BM25"]

    for k in keywords:
        if k.lower() in content.lower():
            methods.append(k)

    # Paper node
    tx.run("MERGE (p:Paper {title:$title})", title=title)

    # Domain
    tx.run("""
        MERGE (d:Domain {name:$domain})
        MERGE (p:Paper {title:$title})
        MERGE (p)-[:BELONGS_TO]->(d)
    """, domain=domain, title=title)

    # Authors
    for author in authors:
        tx.run("""
            MERGE (a:Author {name:$author})
            MERGE (p:Paper {title:$title})
            MERGE (a)-[:WROTE]->(p)
        """, author=author, title=title)

    # Methods
    for method in methods:
        tx.run("""
            MERGE (m:Method {name:$method})
            MERGE (p:Paper {title:$title})
            MERGE (p)-[:USES]->(m)
        """, method=method, title=title)


# -------- Load Papers --------
def load_all_papers():
    with open("api_output/arxiv_with_content_20260326_211126.json", "r", encoding="utf-8") as f:
            papers = json.load(f)

    count = 0
    with driver.session(database="neo4j") as session:
        for paper in papers:
            session.execute_write(create_graph, paper)
            print("Inserted:", paper.get("title"))
            count += 1

    print("Total papers inserted:", count)


load_all_papers()
driver.close()
print("Knowledge Graph Created with Authors, Methods, Domain!")