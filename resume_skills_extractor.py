import PyPDF2
import re

# Step 1: Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in range(len(reader.pages)):
            text += reader.pages[page].extract_text()
    return text

# Step 2: Preprocess the resume text (lowercase, remove punctuation, etc.)
def preprocess_text(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
    text = text.strip()  # Remove leading and trailing spaces
    return text

# Step 3: Extract relevant sections based on common headings
def extract_skills_section(text):
    # Detect where "Skills" section starts
    skills_pattern = re.search(r'\bskills\b', text, re.IGNORECASE)
    if not skills_pattern:
        return ""
    
    # Extract text starting from the "Skills" section
    start_idx = skills_pattern.end()
    remaining_text = text[start_idx:]
    
    # Define where the "Skills" section might end based on common headings
    end_patterns = [r'\bkey experiences\b', r'\bexperience\b', r'\beducation\b', r'\bsummary\b', r'\bprojects\b', r'\bachievements\b']
    end_idx = len(remaining_text)  # Default to end of text if no other sections are found
    
    for pattern in end_patterns:
        match = re.search(pattern, remaining_text, re.IGNORECASE)
        if match:
            end_idx = match.start()
            break
    
    # Extract the content of the "Skills" section only
    skills_section = remaining_text[:end_idx]
    
    return skills_section.strip()

# Step 4: Clean up unnecessary characters from skill entries
def clean_skill(skill):
    # Remove brackets and dashes
    skill = re.sub(r'[\[\](){}-]', '', skill)  # Remove brackets and dashes
    skill = re.sub(r'\s+', ' ', skill)  # Normalize spaces
    skill = skill.strip()  # Remove leading and trailing spaces
    return skill

# Step 5: Extract skills as individual entries
def extract_skills(text):
    skills_section = extract_skills_section(text)
    if not skills_section:
        return []

    # Splitting the skills based on common delimiters
    skills_list = re.split(r'[•\n,;\r]+', skills_section)  # Handles bullets, newlines, commas, and semicolons
    skills_list = [clean_skill(skill) for skill in skills_list if skill.strip()]

    # Further split based on spaces if needed to handle compound skills
    individual_skills = []
    for skill in skills_list:
        # Split by common skill delimiters
        parts = re.split(r'\s{2,}', skill)  # Split by two or more spaces
        individual_skills.extend([clean_skill(part) for part in parts if part.strip()])
    
    return individual_skills

# Step 6: Display skills as a numbered list
def display_skills(skills_list):
    print("\nCurrent Skills List:")
    for index, skill in enumerate(skills_list, 1):
        print(f"{index}. {skill}")

# Step 7: Manage skills interactively
def manage_skills(skills_list):
    while True:
        display_skills(skills_list)
        print("\nOptions:")
        print("1. Add a new skill")
        print("2. Remove a skill")
        print("3. Modify a skill")
        print("4. Exit")
        
        choice = input("Choose an option: ").strip()
        
        if choice == '1':
            new_skill = input("Enter the new skill: ").strip()
            if new_skill:
                skills_list.append(clean_skill(new_skill))
        
        elif choice == '2':
            try:
                index = int(input("Enter the number of the skill to remove: ").strip())
                if 1 <= index <= len(skills_list):
                    removed_skill = skills_list.pop(index - 1)
                    print(f"Removed skill: {removed_skill}")
                else:
                    print("Invalid number.")
            except ValueError:
                print("Please enter a valid number.")
        
        elif choice == '3':
            try:
                index = int(input("Enter the number of the skill to modify: ").strip())
                if 1 <= index <= len(skills_list):
                    new_skill = input("Enter the new skill: ").strip()
                    if new_skill:
                        old_skill = skills_list[index - 1]
                        skills_list[index - 1] = clean_skill(new_skill)
                        print(f"Modified skill from '{old_skill}' to '{new_skill}'")
                else:
                    print("Invalid number.")
            except ValueError:
                print("Please enter a valid number.")
        
        elif choice == '4':
            break
        
        else:
            print("Invalid choice. Please choose again.")



def main():
    print("Welcome to the SkillGauge!")
    print("1. Extract skills from a resume PDF")
    print("2. Enter skills manually")

    choice = input("Choose an option: ").strip()

    skills_list = []

    if choice == '1':
        # Path to the resume PDF
        pdf_path = r'C:\Users\Devin\Desktop\Y1T1\FOP\resume.pdf'
        
        # Extract text from the resume PDF
        resume_text = extract_text_from_pdf(pdf_path)

        # Preprocess the text (optional, depends on how clean the extraction is)
        processed_text = preprocess_text(resume_text)

        # Extract skills from the resume
        skills_list = extract_skills(processed_text)
    
    elif choice == '2':
        print("Enter your skills separated by commas or new lines:")
        manual_input = input().strip()
        skills_list = [clean_skill(skill) for skill in re.split(r'[,\n]+', manual_input) if skill.strip()]

    else:
        print("Invalid choice. Exiting program.")
        return

    # Manage skills interactively
    manage_skills(skills_list)

    # Print the final skills list
    print("\nFinal Skills List:")
    for skill in skills_list:
        print(skill)

def RunTest(pathName):
    # Path to the resume PDF
    pdf_path = pathName
    
    # Extract text from the resume PDF
    resume_text = extract_text_from_pdf(pdf_path)

    # Preprocess the text (optional, depends on how clean the extraction is)
    processed_text = preprocess_text(resume_text)

    # Extract skills from the resume
    skills_list = extract_skills(processed_text)
    
    return skills_list

if __name__ == "__main__":
    main()
