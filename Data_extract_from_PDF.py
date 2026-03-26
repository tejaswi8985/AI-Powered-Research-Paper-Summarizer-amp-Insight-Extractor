import fitz  
import re
import spacy
import json
import os
import uuid

def extract_pdf_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def clean_text(text):
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_title(text):
    lines = text.split("\n")
    for line in lines[:15]:
        if len(line.strip()) > 10:
            return line.strip()
    return "Unknown title"


nlp = spacy.load("en_core_web_sm")


def extract_authors(text):
    doc = nlp(text[:2000])
    authors = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    return list(set(authors))

def extract_pdf_content(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

if __name__ == "__main__":

    pdf_file = "Data/2004.04906v3.pdf"
    os.makedirs("parsed_output", exist_ok=True)

    raw_text = extract_pdf_text(pdf_file)

    title = extract_title(raw_text)
    authors = extract_authors(raw_text)
    content = extract_pdf_content(pdf_file)

    print("Title:")
    print(title)

    print("\nAuthors:")
    print(authors)

    paper = {
        "document_id": str(uuid.uuid4()),
        "title": title,
        "authors": authors,
        "content": content
    }

    with open("parsed_output/result.json", "w", encoding="utf-8") as f:
        json.dump(paper, f, indent=4, ensure_ascii=False)

    print("\n✅ Saved to parsed_output/result.json")


