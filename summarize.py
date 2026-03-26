from transformers import pipeline
import fitz  # PyMuPDF
import re

# ---------- PDF TEXT EXTRACTION ----------
def extract_pdf_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# ---------- ABSTRACT EXTRACTION ----------
def extract_abstract(text):
    match = re.search(
        r'abstract[:\s]*(.*?)(introduction|methods|materials)',
        text,
        re.IGNORECASE | re.DOTALL
    )
    if match:
        return match.group(1).strip()
    return ""

# ---------- LOAD SUMMARIZER ----------
summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn"
)

# ---------- YOUR PDF PATH ----------
pdf_path = "Data/1912.13318v5.pdf"

# ---------- PIPELINE ----------
raw_text = extract_pdf_text(pdf_path)
abstract = extract_abstract(raw_text)

if not abstract:
    print("❌ Abstract not found in PDF")
else:
    summary = summarizer(
        abstract,
        max_length=120,
        min_length=40,
        do_sample=False
    )

    print("\n📄 ABSTRACT:\n")
    print(abstract)

    print("\n📝 SUMMARY:\n")
    print(summary[0]["summary_text"])