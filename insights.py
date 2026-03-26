from transformers import pipeline
import fitz
import re
import spacy
import json
import os

# ---------------- LOAD MODELS ----------------
nlp = spacy.load("en_core_web_sm")

summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn"
)

# ---------------- PDF TEXT ----------------
def extract_pdf_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def extract_title(text):
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    for line in lines[:15]:
        if len(line.split()) > 4:
            return line
    return "Title not found"
# ---------------- ABSTRACT ----------------
def extract_abstract(text):
    match = re.search(
        r'abstract[:\s]*(.*?)(introduction|methods|materials)',
        text,
        re.IGNORECASE | re.DOTALL
    )
    return match.group(1).strip() if match else ""

# ---------------- INSIGHTS ----------------
def extract_insights(text):
    doc = nlp(text)

    # Extract keywords
    keywords = [
        token.text.lower()
        for token in doc
        if token.pos_ in ["NOUN", "PROPN"]
        and token.is_alpha
        and len(token.text) > 4
    ]

    # Extract key findings
    key_findings = [
        sent.text.strip()
        for sent in doc.sents
        if "propose" in sent.text.lower()
        or "introduce" in sent.text.lower()
        or "present" in sent.text.lower()
    ][:3]

    method = "Transformer-based models"

    return {
        "task": "Understanding research paper",
        "method": method,
        "key_findings": key_findings,
        "keywords": list(dict.fromkeys(keywords))[:10]
    }

# ---------------- MAIN ----------------
if __name__ == "__main__":

    pdf_path = "Data/2511.04683v1.pdf"   # YOUR PDF
    output_dir = "parsed_output"
    os.makedirs(output_dir, exist_ok=True)

    raw_text = extract_pdf_text(pdf_path)
    abstract = extract_abstract(raw_text)

    if not abstract:
        print("❌ Abstract not found")
        exit()

    # -------- SUMMARY --------
    summary = summarizer(
        abstract,
        max_length=120,
        min_length=40,
        do_sample=False
    )[0]["summary_text"]

    # -------- INSIGHTS --------
    insights = extract_insights(abstract)

    final_output = {
        "summary": summary,
        "insights": insights
    }

    with open(f"{output_dir}/summary_insights.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=4, ensure_ascii=False)

    print("✅ SUMMARY + INSIGHTS SAVED")