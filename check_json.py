import os
import fitz  # PyMuPDF
import json

data_folder = "Data"
output_file = "parsed_output/local_pdfs_with_content.json"

papers = []
failed = []

for file in os.listdir(data_folder):
    if file.endswith(".pdf"):
        path = os.path.join(data_folder, file)
        print("Processing:", file)

        text = ""

        try:
            doc = fitz.open(path)

            for page in doc:
                try:
                    text += page.get_text()
                except:
                    continue

            if len(text.strip()) < 100:
                print("Too little text, skipping:", file)
                failed.append(file)
                continue

            papers.append({
                "file_name": file,
                "content": text
            })

        except Exception as e:
            print("Failed:", file)
            failed.append(file)

# Save JSON
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(papers, f, indent=2)

print("\nTotal PDFs:", len(os.listdir(data_folder)))
print("Successfully processed:", len(papers))
print("Failed PDFs:", len(failed))

with open("parsed_output/failed_pdfs.txt", "w") as f:
    for item in failed:
        f.write(item + "\n")

print("JSON saved:", output_file)