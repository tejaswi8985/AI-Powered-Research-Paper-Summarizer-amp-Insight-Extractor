# =========================
# IMPORTS
# =========================
import os
import json
import uuid
from datetime import datetime
import fitz  # PyMuPDF

# Disable MuPDF error spam
fitz.TOOLS.mupdf_display_errors(False)


# =========================
# EXTRACT PDF CONTENT SAFELY
# =========================
def extract_pdf_content(pdf_path):
    text = ""

    try:
        doc = fitz.open(pdf_path)

        for page in doc:
            try:
                page_text = page.get_text()
                if page_text:
                    text += page_text
            except:
                continue

        doc.close()

    except:
        return ""

    return text.strip()


# =========================
# PROCESS LOCAL PDFs (RECURSIVE)
# =========================
def process_local_pdfs(pdf_dir="data"):

    papers = []
    total_files = 0

    for root, dirs, files in os.walk(pdf_dir):

        for file in files:

            if not file.lower().endswith(".pdf"):
                continue

            total_files += 1
            pdf_path = os.path.join(root, file)

            print(f"📄 Processing: {file}")

            content = extract_pdf_content(pdf_path)

            if len(content) < 50:
                print("⚠️ Skipped (empty content)")
                continue

            paper = {
                "document_id": str(uuid.uuid4()),
                "source": "local_pdf",
                "file_name": file,
                "content": content,
                "collected_at": datetime.utcnow().isoformat()
            }

            papers.append(paper)

    print("\n📊 Total PDFs scanned:", total_files)
    print("📚 Valid documents extracted:", len(papers))

    return papers


# =========================
# SAVE JSON
# =========================
def save_json(data, output_dir="parsed_output"):

    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(
        output_dir,
        "local_pdfs_with_content.json"
    )

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return file_path


# =========================
# MAIN
# =========================
if __name__ == "__main__":

    print("🚀 Starting local PDF extraction...\n")

    papers = process_local_pdfs("Data")

    output_path = save_json(papers)

    print("\n✅ Local PDF extraction completed!")
    print("📁 Saved at:", output_path)