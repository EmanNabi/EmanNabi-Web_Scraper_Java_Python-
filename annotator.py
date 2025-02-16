import os
import pandas as pd
import google.generativeai as genai
import requests

# API Keys
GEMINI_API_KEY = "your_Gemini_API" # Gemini API
OPENROUTER_API_KEY = "your_OpenRouter_API" # OpenRouter API

# Define categories (flexible matching)
LABELS = ["Deep Learning", "Computer Vision", "Reinforcement Learning", "Natural Language Processing", "Optimization"]
LABELS_SET = {label.lower(): label for label in LABELS}

# Load extracted dataset
INPUT_CSV = "extracted_papers1.csv"
OUTPUT_CSV = "annotated_papers.csv"

# Load existing annotations if available
if os.path.exists(OUTPUT_CSV):
    df = pd.read_csv(OUTPUT_CSV)
else:
    df = pd.read_csv(INPUT_CSV)

# Ensure the "Category" column exists
if "Category" not in df.columns:
    df["Category"] = None

# Initialize Gemini model
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-pro")

# Function to classify a paper using Gemini API
def classify_with_gemini(title, abstract):
    prompt = f"""
    Classify the following research paper into one of these categories: {", ".join(LABELS)}.
    Title: {title}
    Abstract: {abstract}
    Return only the category name.
    """
    try:
        response = gemini_model.generate_content(prompt)
        category = response.text.strip().lower()
        return LABELS_SET.get(category, "Unknown")
    except Exception as e:
        print(f"⚠️ Gemini API Error: {e}")
        return None  

# Function to classify a paper using OpenRouter (GPT-4 Turbo)
def classify_with_openrouter(title, abstract):
    prompt = f"""
    Classify the following research paper into one of these categories: {", ".join(LABELS)}.
    Title: {title}
    Abstract: {abstract}
    Return only the category name.
    """
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            json={"model": "openai/gpt-4-turbo", "messages": [{"role": "user", "content": prompt}]}
        )
        result = response.json()
        
        # Validate response format
        if "choices" in result and result["choices"]:
            category = result["choices"][0]["message"]["content"].strip().lower()
            return LABELS_SET.get(category, "Unknown")
        else:
            print(f"⚠️ OpenRouter API Error: Unexpected response format: {result}")
            return "Unknown"

    except Exception as e:
        print(f"⚠️ OpenRouter API Error: {e}")
        return "Unknown"

# Annotate each paper (skipping already labeled ones)
total_papers = len(df)
for index, row in df.iterrows():
    if pd.notna(row["Category"]): 
        continue

    title, abstract = row["Title"], row["Abstract"]
    print(f"📄 Processing {index + 1}/{total_papers}: {title}")

    # Try Gemini first
    category = classify_with_gemini(title, abstract)

    # If Gemini fails (returns None), switch to OpenRouter
    if category is None:
        print("⚠️ Switching to OpenRouter AI due to Gemini failure...")
        category = classify_with_openrouter(title, abstract)

    df.at[index, "Category"] = category 
    df.to_csv(OUTPUT_CSV, index=False)

print("\n✅ Annotation complete! Results saved in 'annotated_papers.csv'.")
