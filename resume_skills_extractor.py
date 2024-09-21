import spacy
import json
import pdfplumber

# Load SpaCy English model
nlp = spacy.load('en_core_web_sm')

# Load skill synonyms from external JSON file
def load_skill_synonyms(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return {}

# Flatten synonym dictionary for reverse lookup
def create_reverse_skill_map(skill_synonyms):
    reverse_skill_map = {}
    for skill, synonyms in skill_synonyms.items():
        for synonym in synonyms:
            reverse_skill_map[synonym.lower()] = skill
        reverse_skill_map[skill.lower()] = skill  # Add canonical name itself
    return reverse_skill_map

# Extract skills using SpaCy and synonym mapping
def extract_skills_with_synonyms(text, reverse_skill_map):
    doc = nlp(text)
    
    identified_skills = set()

    # Tokenize text and map skills back to their canonical form using the synonym dictionary
    for token in doc:
        skill_key = token.text.lower()
        if skill_key in reverse_skill_map:
            identified_skills.add(reverse_skill_map[skill_key])

    return list(identified_skills)

# Allow users to manage (add, modify, remove) the extracted skills, separating industry and general skills
def manage_skills(industry_skills, general_skills):
    total_skills = industry_skills + general_skills
    return total_skills
        
# Extract text from a PDF file
def extract_text_from_pdf(file_path):
    text = ''
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Prompt user for industry and load corresponding JSON file
def choose_industry(industry): 
    # Define possible industries and corresponding JSON files
    industry_to_file = {
        "tech": "tech_skills.json",
        "healthcare": "healthcare_skills.json",
        "finance": "finance_skills.json",
        "other": "general_skills.json"  # For unspecified industries, default to general
    }
    
    # Load the appropriate JSON file or default to general skills
    file_path = industry_to_file.get(industry, "general_skills.json")
    return file_path

# Split the skills into general and industry-specific categories
def split_skills(all_skills, general_skills):
    industry_specific_skills = [skill for skill in all_skills if skill not in general_skills]
    general_specific_skills = [skill for skill in all_skills if skill in general_skills]
    return industry_specific_skills, general_specific_skills

def GatherSkills(pdfPath, industry):
    # Ask user to upload the resume file (PDF)
    file_path = pdfPath
    
    # Extract text from the uploaded resume
    resume_text = extract_text_from_pdf(file_path)

    # Always load general skills
    general_skill_file = "general_skills.json"
    general_skill_synonyms = load_skill_synonyms(general_skill_file)
    general_reverse_skill_map = create_reverse_skill_map(general_skill_synonyms)

    # Ask user for the industry they want to use for additional skill extraction
    industry_skill_file = choose_industry(industry)
    industry_skill_synonyms = load_skill_synonyms(industry_skill_file)
    industry_reverse_skill_map = create_reverse_skill_map(industry_skill_synonyms)

    # Extract industry-specific skills
    industry_skills_from_synonyms = extract_skills_with_synonyms(resume_text, industry_reverse_skill_map)

    # Extract general skills
    general_skills_from_synonyms = extract_skills_with_synonyms(resume_text, general_reverse_skill_map)

    # Split current skills into industry-specific and general skills
    current_skills = industry_skills_from_synonyms + general_skills_from_synonyms
    current_industry_skills, current_general_skills = split_skills(current_skills, general_skills_from_synonyms)

    # Manage current skills, allowing user to modify them
    finalskills = manage_skills(current_industry_skills, current_general_skills)

    return finalskills
