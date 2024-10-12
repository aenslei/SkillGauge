'''
Author: Devin 
Extracts the skills from the resume that the user upload
'''

import os
import json
import re
from pdfminer.high_level import extract_text

# Define the list of industry JSON files
industry_files = [
    "Skills/engineering_skills.json",
    "Skills/healthcare_skills.json",
    "Skills/legal_service_skills.json",
    "Skills/finance_skills.json",
    "Skills/tech_skills.json"
]

# Define the general skills JSON file
general_skills_file = "Skills/general_skills.json"
file_path = os.path.join('uploads', 'results.txt')

# Extract text from PDF and output as TXT file
def extract_text_from_pdf(pdf_file, output_file=file_path):
    try:
        # Open the PDF file in read-binary mode
        with open(pdf_file, 'rb') as f:
            # Extract text from the PDF using a library function
            text = extract_text(f)
            
            # Convert the extracted text to lowercase for uniformity
            text = text.lower()
            
            # Remove punctuation and non-word characters using regex
            text = re.sub(r'[^\w\s]', ' ', text)
            
            # Replace multiple spaces with a single space and strip leading/trailing whitespace
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            # Open the output TXT file in write mode with UTF-8 encoding
            with open(output_file, 'w', encoding='utf-8') as output:
                # Write the cleaned text to the output file
                output.write(text)
    except Exception as e:
        # Print an error message if an exception occurs during the extraction process
        print(f"Error extracting text: {e}")

# Define the function to extract skills from a text file
def extract_skills_from_text(text, industry_file, general_skills_file):
    with open(industry_file, "r") as f:
        industry_skills = json.load(f)

    with open(general_skills_file, "r") as f:
        general_skills = json.load(f)

    # Combine industry-specific and general skills into a single dictionary
    combined_skills = {**industry_skills, **general_skills}

    # Find all words in the input text, converting to lowercase
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Create a set to store unique extracted skills
    extracted_skills = set()

    for word in words:
        # Check each skill and its aliases in the combined skills dictionary
        for skill, aliases in combined_skills.items():
            # If the word matches the skill or any of its aliases, add it to the extracted skills set
            if word in [skill.lower()] + [alias.lower() for alias in aliases]:
                extracted_skills.add(skill) 
                break

    # Return the extracted skills as a list
    return list(extracted_skills)

def outputSkillsExtracted(industry_choice):
    text_file = file_path

    if not os.path.exists(text_file):
        print("Text file not found. Please check the file path and try again.")
    else:
        with open(text_file, "r") as f:
            text = f.read()

        # Extract skills from the text using the selected industry and general skills files
        industry_file = industry_files[industry_choice - 1]
        extracted_skills = extract_skills_from_text(text, industry_file, general_skills_file)

        industry_skills = []
        general_skills = []

        # Append skills into different list
        for skill in extracted_skills:
            if skill in json.load(open(industry_file, "r")):
                industry_skills.append(skill)
            else:
                general_skills.append(skill)

    # Combine industry and general skills, converting them to lowercase
    final_skills = [skills.lower() for skills in industry_skills + general_skills]
    return final_skills
