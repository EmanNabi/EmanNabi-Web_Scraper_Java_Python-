import os
import re
import pandas as pd
from pdfminer.high_level import extract_text

# Path to the folder containing year-wise PDFs
BASE_DIR = "D:/Data Science/Scraped_Data-Using_Python/"

# Function to extract text from a PDF using PDFMiner
def extract_text_from_pdf(pdf_path):
    try:
        text = extract_text(pdf_path)
        return text.strip() if text else None  # Remove extra spaces
    except Exception as e:
        print(f"Error reading {pdf_path} with PDFMiner: {e}")
        return None

# Function to extract title and abstract from the text
def extract_title_and_abstract(text):
    # Extract title (usually the first non-empty line)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    title = lines[0] if lines else "Title not found"
    
    # Extract abstract (look for the word "Abstract")
    abstract_match = re.search(r"Abstract\s*:\s*(.*?)(\n\n|Introduction|$)", text, re.DOTALL)
    abstract = abstract_match.group(1).strip() if abstract_match else "Abstract not found"
    
    return title, abstract

# Main function to process all PDFs
def process_pdfs():
    papers = []
    for year in os.listdir(BASE_DIR):
        year_dir = os.path.join(BASE_DIR, year)
        if os.path.isdir(year_dir):
            for pdf_file in os.listdir(year_dir):
                if pdf_file.endswith(".pdf"):
                    pdf_path = os.path.join(year_dir, pdf_file)
                    text = extract_text_from_pdf(pdf_path)
                    if text:
                        title, abstract = extract_title_and_abstract(text)
                        papers.append({
                            "Title": title,
                            "Abstract": abstract,
                            "Year": year,
                            "File": pdf_file
                        })
    return papers

# Save the extracted data to a CSV file
if __name__ == "__main__":
    papers = process_pdfs()
    df = pd.DataFrame(papers)
    df.to_csv("extracted_papers.csv", index=False)
    print("Extraction complete! Data saved as 'extracted_papers.csv'.")
