import os
import re
import pandas as pd
from pdfminer.high_level import extract_text

# Path to the folder containing year-wise PDFs
BASE_DIR = "D:/Data Science/Scraped_Data-Using_Python/"
SUCCESS_CSV = "extracted_papers.csv"
FAILED_CSV = "failed_papers.csv"

# Function to extract text from a PDF using PDFMiner
def extract_text_from_pdf(pdf_path):
    try:
        text = extract_text(pdf_path)
        return text.strip() if text else None
    except Exception as e:
        return f"Error: {e}"

# Function to extract title and abstract
def extract_title_and_abstract(text):
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    title = lines[0] if lines else "Title not found"

    abstract_match = re.search(r"Abstract\s*:\s*(.*?)(\n\n|Introduction|$)", text, re.DOTALL)
    abstract = abstract_match.group(1).strip() if abstract_match else "Abstract not found"

    return title, abstract

# Load existing progress
if os.path.exists(SUCCESS_CSV):
    success_df = pd.read_csv(SUCCESS_CSV)
else:
    success_df = pd.DataFrame(columns=["Title", "Abstract", "Year", "File"])

if os.path.exists(FAILED_CSV):
    failed_df = pd.read_csv(FAILED_CSV)
else:
    failed_df = pd.DataFrame(columns=["Year", "File", "Error"])

processed_files = set(success_df["File"]).union(set(failed_df["File"]))

# Counters
success_count = len(success_df)
fail_count = len(failed_df)

# Process PDFs
for year in os.listdir(BASE_DIR):
    year_dir = os.path.join(BASE_DIR, year)
    if os.path.isdir(year_dir):
        for pdf_file in os.listdir(year_dir):
            if pdf_file.endswith(".pdf") and pdf_file not in processed_files:
                pdf_path = os.path.join(year_dir, pdf_file)
                text = extract_text_from_pdf(pdf_path)

                if text and not text.startswith("Error"):
                    title, abstract = extract_title_and_abstract(text)
                    new_entry = pd.DataFrame([{"Title": title, "Abstract": abstract, "Year": year, "File": pdf_file}])
                    success_df = pd.concat([success_df, new_entry], ignore_index=True)
                    success_df.to_csv(SUCCESS_CSV, index=False)  # Save progress
                    success_count += 1
                    print(f"✅ Processed: {pdf_file} ({success_count} successful)")
                else:
                    error_msg = text if text.startswith("Error") else "Unreadable or corrupt PDF"
                    failed_entry = pd.DataFrame([{"Year": year, "File": pdf_file, "Error": error_msg}])
                    failed_df = pd.concat([failed_df, failed_entry], ignore_index=True)
                    failed_df.to_csv(FAILED_CSV, index=False)  # Save progress
                    fail_count += 1
                    print(f"❌ Failed: {pdf_file} ({fail_count} failed)")

# Final summary
print("\n✅ Extraction Complete!")
print(f"Total Success: {success_count}")
print(f"Total Failed: {fail_count}")
print(f"Check '{SUCCESS_CSV}' & '{FAILED_CSV}' for details.")
