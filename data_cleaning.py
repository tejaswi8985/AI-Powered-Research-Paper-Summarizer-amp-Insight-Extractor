import fitz  # PyMuPDF
import re
import json
import spacy
import os


# ---------------- PDF TEXT EXTRACTION ----------------
def extract_pdf_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


# ---------------- TEXT CLEANING ----------------
def clean_text(text):
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# ---------------- TITLE EXTRACTION ----------------
def extract_title(text):
    lines = text.split("\n")
    for line in lines[:15]:
        if len(line.strip()) > 10:
            return line.strip()
    return "Unknown title"


# ---------------- AUTHOR EXTRACTION ----------------
nlp = spacy.load("en_core_web_sm")

def extract_authors(text):
    # extract text before Abstract
    abstract_match = re.search(r'\nAbstract', text, re.IGNORECASE)
    if not abstract_match:
        return []

    header_text = text[:abstract_match.start()]

    lines = [line.strip() for line in header_text.split("\n") if line.strip()]
    if len(lines) < 2:
        return []

    # remove title line
    lines = lines[1:]

    cleaned_lines = []
    for line in lines:
        if any(word in line.lower() for word in [
            "university", "institute", "department",
            "correspondence", "preprint", "@"
        ]):
            continue
        cleaned_lines.append(line)

    author_block = " ".join(cleaned_lines)

    # remove numbers and symbols
    author_block = re.sub(r'[\*\d]', '', author_block)

    # extract names
    authors = re.findall(
        r'\b[A-Z][a-zA-Z\-\.]+(?:\s[A-Z][a-zA-Z\-\.]+){1,3}\b',
        author_block
    )

    # remove duplicates
    final_authors = []
    seen = set()
    for name in authors:
        if name not in seen:
            seen.add(name)
            final_authors.append(name)

    return final_authors


# ---------------- ABSTRACT EXTRACTION ----------------
def extract_abstract(text):
    text = text.replace('\r', '\n')

    match = re.search(
        r'\bAbstract\b\s*(.*?)(?:\n\s*(?:1\.|I\.)?\s*Introduction|\n\s*Introduction)',
        text,
        re.IGNORECASE | re.DOTALL
    )

    if match:
        abstract = match.group(1).strip()
        abstract = re.sub(r'\n+', ' ', abstract)
        abstract = re.sub(r'\s+', ' ', abstract)
        return abstract

    return "Abstract not found"



# ---------------- MAIN ----------------
if __name__ == "__main__":

    pdf_file = "Data/2004.04906v3.pdf"

    output_dir = "parsed_output"
    os.makedirs(output_dir, exist_ok=True)

    raw_text = extract_pdf_text(pdf_file)

    title = extract_title(raw_text)
    authors = extract_authors(raw_text)
    abstract = extract_abstract(raw_text)

    print("TITLE:\n", title)
    print("\nAUTHORS:\n", authors)
    print("\nABSTRACT:\n", abstract)

    # save output to JSON
    output = {
        "title": title,
        "authors": authors,
        "abstract": abstract
    }

    with open("parsed_output/result.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
