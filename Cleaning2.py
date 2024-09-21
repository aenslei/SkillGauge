import re
import pandas as pd


# Define a mapping between the 30 clusters and the new categories
cluster_mapping = {
    0: "Human Resources & Customer Support",
    1: "Supply Chain & Operations",
    2: "IT Infrastructure & Security",
    3: "Marketing & Content Creation",
    4: "Engineering & Architecture",
    5: "Design & Front-End Development",
    6: "Data Science & Analytics",
    7: "Digital Marketing",
    8: "Quality Assurance & Testing",
    9: "Legal & Social Services",
    10: "Finance & Investment",
    11: "Healthcare & Medicine",
    12: "Finance & Tax Services",
    13: "Sales & Business Development",
    14: "Administration & Office Support",
    15: "Legal Advisory & Consulting",
    16: "Software Development & Engineering",
    17: "Customer Success & Account Management",
    18: "Consulting & Business Strategy",
    19: "Education & Training",
    20: "Marketing Strategy & Advertising",
    21: "Executive Leadership & Management",
    22: "Manufacturing & Production",
    23: "Legal Research & Documentation",
    24: "Healthcare Support & Nursing",
    25: "IT Support & Maintenance",
    26: "Sales Operations & Management",
    27: "Business Intelligence & Reporting",
    28: "Product Management & Development",
    29: "Construction & Civil Engineering"
}

# Define the broader categories
broader_categories_mapping = {
    "Human Resources & Customer Support": "Business",
    "Supply Chain & Operations": "Business",
    "IT Infrastructure & Security": "Information Technology",
    "Marketing & Content Creation": "Business",
    "Engineering & Architecture": "Engineering",
    "Design & Front-End Development": "Information Technology",
    "Data Science & Analytics": "Information Technology",
    "Digital Marketing": "Business",
    "Quality Assurance & Testing": "Information Technology",
    "Legal & Social Services": "Legal Services",
    "Finance & Investment": "Business",
    "Healthcare & Medicine": "Healthcare",
    "Finance & Tax Services": "Business",
    "Sales & Business Development": "Business",
    "Administration & Office Support": "Business",
    "Legal Advisory & Consulting": "Business",
    "Software Development & Engineering": "Information Technology",
    "Customer Success & Account Management": "Business",
    "Consulting & Business Strategy": "Business",
    "Education & Training": "Business",
    "Marketing Strategy & Advertising": "Business",
    "Executive Leadership & Management": "Business",
    "Manufacturing & Production": "Engineering",
    "Legal Research & Documentation": "Information Technology",
    "Healthcare Support & Nursing": "Healthcare",
    "IT Support & Maintenance": "Information Technology",
    "Sales Operations & Management": "Business",
    "Business Intelligence & Reporting": "Information Technology",
    "Product Management & Development": "Business",
    "Construction & Civil Engineering": "Engineering"
}




# Load your dataset (assuming the dataset contains a 'Cluster' column)
data = pd.read_csv('Datasets/sg_job_data-Cleaned-With Industry1.csv')

# Apply the cluster mapping
data['Cluster Name'] = data['Predicted Industry'].map(cluster_mapping)

# Apply the broader category mapping
data['Broader Category'] = data['Cluster Name'].map(broader_categories_mapping)

# Save the new dataset with the cluster names and broader categories
data.to_csv('Datasets/sg_job_data-Cleaned-With Industry1.csv', index=False)

print("Cluster names and broader categories added and saved successfully!")

# Load the CSV file
csv_file_path = 'Datasets/sg_job_data-Cleaned-With Industry1.csv'
data = pd.read_csv(csv_file_path)

# Jobs to remove from Cluster 24
remove_from_cluster_24 = ["Art Teacher", "Art Director", "Teacher"]
# Job to move from Cluster 24 to Cluster 11
move_to_cluster_11 = "Public Relations Specialist","Substance Abuse Counselor"


data.loc[(data['Job Title'] == 'SEO Specialist') & (data['Predicted Industry'] == 3), 'Predicted Industry'] = 2

# Move legal-related job titles from Predicted Industry 14 to 9
legal_jobs = ['Legal Advisor', 'Paralegal', 'Legal Secretary', 'Legal Counsel', 'Legal Assistant', 'Litigation Attorney']
data.loc[(data['Job Title'].isin(legal_jobs)) & (data['Predicted Industry'] == 14), 'Predicted Industry'] = 9

# Move the specified job titles to cluster 2 based on their current clusters
move_to_cluster_2 = {
    'Data Entry Clerk': 0,
    'IT Manager': 20,
    'IT Support Specialist': 19,
    'Systems Administrator': 19,
    'Systems Analyst': 26,
    'SEO Specialist': 3,
    'SEO Analyst': 28
}
for job, industry in move_to_cluster_2.items():
    data.loc[(data['Job Title'] == job) & (data['Predicted Industry'] == industry), 'Predicted Industry'] = 2

# Move the specified engineering-related job titles to cluster 4
move_to_cluster_4 = {
    'Electrical Engineering': 26,
    'Process Engineer': 26,
    'Technical Writer': [3, 19],  # Technical Writer is in two clusters, so we handle both
    'Chemical Engineer': 26,
    'Mechanical Engineer': 26
}
for job, industry in move_to_cluster_4.items():
    if isinstance(industry, list):
        data.loc[(data['Job Title'] == job) & (data['Predicted Industry'].isin(industry)), 'Predicted Industry'] = 4
    else:
        data.loc[(data['Job Title'] == job) & (data['Predicted Industry'] == industry), 'Predicted Industry'] = 4


data.loc[(data['Job Title'] == 'Architect') & (data['Predicted Industry'] == 15), 'Predicted Industry'] = 4


# Move "Substance Abuse Counselor" from cluster 19 to cluster 11
data.loc[(data['Job Title'] == 'Substance Abuse Counselor') & (data['Predicted Industry'] == 19), 'Predicted Industry'] = 11

# Move the specified job titles to cluster 2 based on their current clusters
move_to_cluster_2 = {
    'Network Administrator': 22,
    'Systems Administrator': 22,
    'IT Support Specialist': 22,
    'Systems Engineer': 4,
    'IT Manager': 22,
    'Software Architect': 4
}
for job, industry in move_to_cluster_2.items():
    data.loc[(data['Job Title'] == job) & (data['Predicted Industry'] == industry), 'Predicted Industry'] = 2

# Move specified job titles to cluster 13 based on their current clusters
move_to_cluster_13 = {
    'Research Analyst': 29,
    'Marketing Manager': 29,
    'Research Scientist': 29,
    'Market Research Analyst': 29,
    'Market Analyst': 29
}
for job, industry in move_to_cluster_13.items():
    data.loc[(data['Job Title'] == job) & (data['Predicted Industry'] == industry), 'Predicted Industry'] = 13

# Move "Psychologist" from cluster 29 to cluster 11
data.loc[(data['Job Title'] == 'Psychologist') & (data['Predicted Industry'] == 29), 'Predicted Industry'] = 11


# Move the specified job titles to cluster 13 based on their current clusters
move_to_cluster_13 = {
    'Marketing Analyst': 6,
    'Business Analyst': 6,
    'Personal Assistant': 6
}
for job, industry in move_to_cluster_13.items():
    data.loc[(data['Job Title'] == job) & (data['Predicted Industry'] == industry), 'Predicted Industry'] = 13

# Move the specified job titles to cluster 4 based on their current clusters
move_to_cluster_4 = {
    'Landscape Architect': 25,
    'Technical Writer': 25,
    'Architect': 25,
    'Urban Planner': 25,
    'QA Engineer': 8,
    'Environmental Engineer': 25,
    'Architectural Designer': 25,
    'Mechanical Designer': 5,
    'Technical Writer': 25
}
for job, industry in move_to_cluster_4.items():
    data.loc[(data['Job Title'] == job) & (data['Predicted Industry'] == industry), 'Predicted Industry'] = 4

move_to_cluster_6 = {
    'Interior Designer': 25,
    'Executive Assistant': 27,
    'Personal Assistant': 27
}
for job, industry in move_to_cluster_6.items():
    data.loc[(data['Job Title'] == job) & (data['Predicted Industry'] == industry), 'Predicted Industry'] = 6

# Move the specified job titles to cluster 4 based on their current clusters
move_to_cluster_4 = {
    'Environmental Consultant': 25,
    'Electrical Designer': 25,
    'Product Designer': 25
}
for job, industry in move_to_cluster_4.items():
    data.loc[(data['Job Title'] == job) & (data['Predicted Industry'] == industry), 'Predicted Industry'] = 4

# Move "Business Analyst" from cluster 11 to cluster 6
data.loc[(data['Job Title'] == 'Business Analyst') & (data['Predicted Industry'] == 11), 'Predicted Industry'] = 6
data.loc[(data['Job Title'] == 'Personal Assistant') & (data['Predicted Industry'] == 25), 'Predicted Industry'] = 6
data.loc[(data['Job Title'] == 'Executive Assistant') & (data['Predicted Industry'] == 27), 'Predicted Industry'] = 6
data.loc[(data['Job Title'] == 'Interior Designer') & (data['Predicted Industry'] == 25), 'Predicted Industry'] = 4
data.loc[(data['Job Title'] == 'Product Designer') & (data['Predicted Industry'] == 25), 'Predicted Industry'] = 4


# Delete all rows where the Job Title is "Teacher" and Predicted Industry is 11
data = data[~((data['Job Title'] == 'Teacher') & (data['Predicted Industry'] == 11))]

# Save the updated CSV file
output_file_path = 'path_to_save_updated_file.csv'  # Replace with your desired output file path
data.to_csv(output_file_path, index=False)

# Update Cluster 24 by removing specified job titles
data = data[~((data['Predicted Industry'] == 24) & (data['Job Title'].isin(remove_from_cluster_24)))]

# Move "Public Relations Specialist" from Cluster 24 to Cluster 11
data.loc[(data['Predicted Industry'] == 24) & (data['Job Title'] == move_to_cluster_11), 'Predicted Industry'] = 11

# DELETE CLUSTER 24
data = data[data['Predicted Industry'] != 24]


# Check if the column "Predicted Industry.1" exists and remove it
if 'Predicted Industry.1' in data.columns:
    data = data.drop(columns=['Predicted Industry.1'])
    
else:
    print("'Predicted Industry.1' column does not exist.")

    cluster_mapping = {
    0: "Human Resources & Customer Support",
    1: "Supply Chain & Operations",
    2: "IT Infrastructure & Security",
    3: "Marketing & Content Creation",
    4: "Engineering & Architecture",
    5: "Design & Front-End Development",
    6: "Data Science & Analytics",
    7: "Digital Marketing",
    8: "Quality Assurance & Testing",
    9: "Legal & Social Services",
    10: "Finance & Investment",
    11: "Healthcare & Medicine",
    12: "Finance & Tax Services",
    13: "Sales & Business Development",
    14: "Administration & Office Support",
    15: "Legal Advisory & Consulting",
    16: "Software Development & Engineering",
    17: "Customer Success & Account Management",
    18: "Consulting & Business Strategy",
    19: "Education & Training",
    20: "Marketing Strategy & Advertising",
    21: "Executive Leadership & Management",
    22: "Manufacturing & Production",
    23: "Legal Research & Documentation",
    24: "Healthcare Support & Nursing",
    25: "IT Support & Maintenance",
    26: "Sales Operations & Management",
    27: "Business Intelligence & Reporting",
    28: "Product Management & Development",
    29: "Construction & Civil Engineering"
}

# Define the broader categories
broader_categories_mapping = {
    "Human Resources & Customer Support": "Business",
    "Supply Chain & Operations": "Business",
    "IT Infrastructure & Security": "Information Technology",
    "Marketing & Content Creation": "Business",
    "Engineering & Architecture": "Engineering",
    "Design & Front-End Development": "Information Technology",
    "Data Science & Analytics": "Information Technology",
    "Digital Marketing": "Business",
    "Quality Assurance & Testing": "Information Technology",
    "Legal & Social Services": "Legal Services",
    "Finance & Investment": "Business",
    "Healthcare & Medicine": "Healthcare",
    "Finance & Tax Services": "Business",
    "Sales & Business Development": "Business",
    "Administration & Office Support": "Business",
    "Legal Advisory & Consulting": "Business",
    "Software Development & Engineering": "Information Technology",
    "Customer Success & Account Management": "Business",
    "Consulting & Business Strategy": "Business",
    "Education & Training": "Business",
    "Marketing Strategy & Advertising": "Business",
    "Executive Leadership & Management": "Business",
    "Manufacturing & Production": "Engineering",
    "Legal Research & Documentation": "Information Technology",
    "Healthcare Support & Nursing": "Healthcare",
    "IT Support & Maintenance": "Information Technology",
    "Sales Operations & Management": "Business",
    "Business Intelligence & Reporting": "Information Technology",
    "Product Management & Development": "Business",
    "Construction & Civil Engineering": "Engineering"
}


# Apply the cluster mapping
data['Cluster Name'] = data['Predicted Industry'].map(cluster_mapping)

# Apply the broader category mapping
data['Broader Category'] = data['Cluster Name'].map(broader_categories_mapping)



# Step 1: Load abbreviations from the text file
with open('unique_abbreviations.txt', 'r') as f:
    abbreviations = [line.strip() for line in f.readlines()]

# Add the list of abbreviations that should be kept together
preserve_abbreviations = ['XML', 'LEED', 'HTML', 'CSS', 'AJAX', 'UI UX', 'CI,', 'ETL', 'GIS', 'ROI', 'ISO9001' 'CD', 'CAD Software', 'SQL', 'API', 'SEO', 'SEM', 'QC', 'OS', 'CAD', 'CAM']

# Step 2: List of skills you want to token together (including multi-word abbreviations)
skills_to_token_together = [
    ['Java', 'Script'],
    ['Mongo', 'D B'],
    ['S Q', 'L', 'Server'],
    ['My', 'S Q', 'L Oracle'],
    ['S E', 'O'],
    ['S E', 'M'],
    ['U X design', '3', 'D modeling'],
    ['I S', 'O 9001'],
    ['L E', 'E D certification'],
    ['Auto', 'C A', 'D Aerodynamics'],
    ['Power', 'B I'],
    ['Metrics and', 'K P', 'Is'],
    ['A P', 'I knowledge'],
    ['X M', 'L sitemaps'],
    ['I E', 'Ps'],
    ['C A', 'D software'],
    ['Auto', 'C A', 'D Aerodynamics']
]

# Convert the list to a dictionary to map the tokens to their merged version
skills_dict = {" ".join(key): " ".join(key) for key in skills_to_token_together}


# Step 3: Define the tokenization function with abbreviations and merging logic
def tokenize_and_find_combined_skills(skills_str):
    if pd.isna(skills_str):  # Handle missing skills
        return []
    
    # Replace different delimiters (commas, semicolons) with a uniform delimiter (comma)
    skills_str = skills_str.replace(';', ',').replace('/', ',')
    
    # Split the string by commas
    tokens = skills_str.split(',')

    # Preserve abbreviations and multi-word combinations
    refined_tokens = []
    for token in tokens:
        token = token.strip()
        
        # Check if the token is in the list of abbreviations to preserve
        if token in preserve_abbreviations or token in abbreviations:
            refined_tokens.append(token)
        else:
            # Split by capital letters and rejoin with spaces for phrases like 'ArchitecturalDesign'
            refined_tokens.extend(re.findall(r'[A-Z][^A-Z]*', token))
    
    # Handle cases where single letters need to be merged with the next token
    merged_tokens = []
    i = 0
    while i < len(refined_tokens):
        # Check for combinations of two or three tokens in the dictionary
        token_combination_two = " ".join(refined_tokens[i:i + 2])
        token_combination_three = " ".join(refined_tokens[i:i + 3])
        
        if token_combination_three in skills_dict:
            merged_tokens.append(skills_dict[token_combination_three])
            i += 3  # Skip the next two tokens as they are already merged
        elif token_combination_two in skills_dict:
            merged_tokens.append(skills_dict[token_combination_two])
            i += 2  # Skip the next token as it is already merged
        else:
            merged_tokens.append(refined_tokens[i])
            i += 1  # Move to the next token

    # Strip extra spaces and return the final list of skills
    return [skill.strip() for skill in merged_tokens if skill.strip()]




# Apply the tokenization to each row of the "skills" column
data['Tokenized Skills'] = data['skills'].apply(tokenize_and_find_combined_skills)

# Collect all the tokenized skills into a single list
all_skills = [skill for skills_list in data['Tokenized Skills'] for skill in skills_list]

# Save the skills to a text file
skills_text_file_path = 'all_skills.txt'  # Update this to your desired output path
with open(skills_text_file_path, 'w') as f:
    for skill in all_skills:
        f.write(f"{skill}\n")

# Check the output of tokenized skills
print(data['Tokenized Skills'].head())

# Step 4: Drop the 'Abbreviations' column
if 'Abbreviations' in data.columns:
    data.drop(columns=['Abbreviations'], inplace=True)
    
if 'Tokenized Skills' in data.columns:
    data['skills'] = data['Tokenized Skills']
    data.drop(columns=['Tokenized Skills'], inplace=True)


# Step 5: Save the changes back to the same file
data.to_csv(csv_file_path, index=False)
# Save the changes back to the same file





