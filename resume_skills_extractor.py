import spacy
import json
import re
import pdfplumber

# Load SpaCy English model
nlp = spacy.load('en_core_web_sm')

# Load skill synonyms from external JSON file
def load_skill_synonyms(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

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

# Pattern matching for additional skills (scalable to industries not in predefined list)
def extract_skills_with_patterns(text, skill_patterns):
    identified_skills = set()
    for pattern in skill_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            identified_skills.add(match.lower())
    return list(identified_skills)

# Allow users to manage (add, modify, remove) the extracted skills
def manage_skills(skills_list):
    while True:
        # Display skills with index numbers
        print("\nCurrent Skills:")
        for idx, skill in enumerate(skills_list):
            print(f"{idx + 1}. {skill}")

# Extract text from a PDF file
def extract_text_from_pdf(file_path):
    text = ''
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Detect industry based on keywords (optional)
def detect_industry(text):
    if re.search(r"\b(hospital|patient care|nursing)\b", text, re.IGNORECASE):
        return "healthcare"
    elif re.search(r"\b(programming|coding|development)\b", text, re.IGNORECASE):
        return "tech"
    elif re.search(r"\b(accounting|finance|bookkeeping)\b", text, re.IGNORECASE):
        return "finance"
    else:
        return "general"

def GatherSkills(pdfPath):
    # Ask user to upload the resume file (PDF)
    file_path = pdfPath
    
    # Extract text from the uploaded resume
    resume_text = extract_text_from_pdf(file_path)

    # Detect industry and load appropriate skill set
    industry = detect_industry(resume_text)

    print(f"\nResume text extracted successfully! industry: {industry}")

    if industry == "tech":
        skill_synonyms = load_skill_synonyms("tech_skills.json")
    elif industry == "healthcare":
        skill_synonyms = load_skill_synonyms("healthcare_skills.json")
    elif industry == "finance":
        skill_synonyms = load_skill_synonyms("finance_skills.json")
    else:
        skill_synonyms = load_skill_synonyms("general_skills.json")

    # Create reverse skill map for synonym matching
    reverse_skill_map = create_reverse_skill_map(skill_synonyms)

    # Extract skills using synonyms
    skills_from_synonyms = extract_skills_with_synonyms(resume_text, reverse_skill_map)

    # Additional pattern matching for other skill sets
    skill_patterns = [
        r"\b(accounting|financial reporting|bookkeeping)\b",  # Finance skills
        r"\b(nursing|patient care|medical assistance)\b",     # Healthcare skills
        r"\b(project management|PM|managing projects)\b"      # General skills
    ]
    
    skills_from_patterns = extract_skills_with_patterns(resume_text, skill_patterns)

    # Combine both sets of skills
    combined_skills = set(skills_from_synonyms + skills_from_patterns)
    print("Skills recognized from resume extractor:", list(combined_skills))

    # Convert the set to a list for managing skills
    all_skills = list(combined_skills)
    
    print("Final Skills:", all_skills)

    return all_skills