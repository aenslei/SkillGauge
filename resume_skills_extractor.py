import os
import json
import spacy
import re
from pdfminer.high_level import extract_text
from pdfminer.layout import LTFigure, LTTextBox
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter

# Load the spaCy model for English
nlp = spacy.load("en_core_web_sm")

# Define the list of industry JSON files
industry_files = [
    "engineering_skills.json",
    "healthcare_skills.json",
    "legal_service_skills.json",
    "finance_skills.json",
    "tech_skills.json"
]

# Define the general skills JSON file
general_skills_file = "general_skills.json"
file_path = os.path.join('uploads', 'results.txt')

#extract text from pdf and output as txt file
def extract_text_from_pdf(pdf_file, output_file=file_path):
    try:
        with open(pdf_file, 'rb') as f:
            text = extract_text(f)
            text = text.lower()
            text = re.sub(r'[^\w\s]', ' ', text)
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            with open(output_file, 'w', encoding='utf-8') as output:
                output.write(text)
    except Exception as e:
        print(f"Error extracting text: {e}")

# Define the function to extract skills from a text file
def extract_skills_from_text(text, industry_file, general_skills_file):
    with open(industry_file, "r") as f:
        industry_skills = json.load(f)

    with open(general_skills_file, "r") as f:
        general_skills = json.load(f)

    combined_skills = {**industry_skills, **general_skills}

    words = re.findall(r'\b\w+\b', text.lower())

    extracted_skills = set()
    for word in words:
        for skill, aliases in combined_skills.items():
            if word in [skill.lower()] + [alias.lower() for alias in aliases]:
                extracted_skills.add(skill)
                break

    return list(extracted_skills)

def outputSkillsExtracted(industry_choice):
    # Define the text file path
    text_file = file_path

    if not os.path.exists(text_file):
        print("Text file not found. Please check the file path and try again.")
    else:
        with open(text_file, "r") as f:
            text = f.read()

        industry_file = industry_files[industry_choice - 1 ]

        extracted_skills = extract_skills_from_text(text, industry_file, general_skills_file)

        industry_skills = []
        general_skills = []

        for skill in extracted_skills:
            if skill in json.load(open(industry_file, "r")):
                industry_skills.append(skill)
            else:
                general_skills.append(skill)

    final_skills = [skills.lower() for skills in industry_skills + general_skills]

    return final_skills