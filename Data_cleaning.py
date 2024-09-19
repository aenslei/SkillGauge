import re
import pandas as pd

# Load your CSV file into a pandas DataFrame
data = pd.read_csv('Datasets\sg_job_data-Raw.csv')

column_names = data.columns.tolist()

# Remove brackets {}, quotation marks ", and single quotes ' from the Benefits column
data['Benefits'] = data['Benefits'].str.replace(r'[{}"\']', '', regex=True)



# Define a function to split the text by capitalized words and list them vertically
def split_by_capital_words(text):
    # Use regular expression to split the string at every capitalized word
    return '\n'.join(re.findall(r'[A-Z][a-zA-Z\s]+', text))


# Define a function to split the text by words or phrases, keeping them together
def split_phrases_with_commas(text):
    if pd.isna(text):
        return text  # Handle missing values
    
    # Use regex to split by a space following a lowercase word and a capitalized word
    return ', '.join(re.findall(r'[\w\s]+(?:\s[\w\s]+)?', text))

# Apply the updated function to the "skills" column
data['skills'] = data['skills'].apply(split_phrases_with_commas)


# Remove any unwanted characters (e.g., currency symbols, commas, etc.)
data['Salary Range'] = data['Salary Range'].str.replace(r'[^\d-]', '', regex=True)

# Split the 'Salary Range' column into 'Min Salary' and 'Max Salary'
data[['Min Salary', 'Max Salary']] = data['Salary Range'].str.split('-', expand=True)

# Convert the min and max salary columns to numeric
data['Min Salary'] = pd.to_numeric(data['Min Salary'], errors='coerce')
data['Max Salary'] = pd.to_numeric(data['Max Salary'], errors='coerce')

# Rename Coulm Name
data.rename(columns={'Salary Range': 'Salary Range (K)'}, inplace=True)

# Insert 'Min Salary' after the Salary Range column (index 5), which is between E and F
data.insert(5, 'Min Salary (K)', data.pop('Min Salary'))

# Insert 'Max Salary' after 'Min Salary' (index 6)
data.insert(6, 'Max Salary (K)', data.pop('Max Salary'))


# Save the cleaned and formatted DataFrame to a new CSV file
data.to_csv('Datasets\sg_job_data-Cleaned.csv', index=False)

