'''
Author: Ainsley Cabading

Develop a data processor to clean and process data through the following processes:

1. Do industry name translation using a dictionary of Industry Name key --> MCF industry value
For example:

industryTranslation = {
    "Technology" : "information-technology",
    "Business" : ["Advertising / Media" , "Customer Service", "Events / Promotions", "Logistics / Supply Chain", "Purchasing / Merchandising"],
    "Engineering" : "xx",
    "Legal Services" : "xx",
    "Healthcare" : "xx"
}

2. For Skills column, for every row, change the delimiter between skills from \n to ,

3. For jobs with multiple industries assigned to them in MCF, workflow will be as follows:
    a. Translate industry names first
    b. For every value under the industry column in the job row, make duplicates to fit the number
    c. Split the industry names into each row. Can store the industry names somewhere first, then
    do a for name in range len(var)

4. General data cleaning functions
--> remove rows that have illegible characters

'''

#Library and File Imports

import pandas as pd
import csv
import os
import re

# Variables

csv_file = "job_listings_scraped.csv"
new_csv_file = "job_listingsNEW.csv"

file_path = r'Datasets\\sg_job_data-Cleaned-With Industry1.csv'

industryTranslation = {
    "Information Technology" : "Information Technology",
    "Business" : ["Advertising / Media" , "Customer Service", "Events / Promotions", "Logistics / Supply Chain", "Purchasing / Merchandising", "Risk Management", "Insurance", "Marketing / Public Relations", "Sales / Retail", "Accounting / Auditing / Taxation", "Banking and Finance"],
    "Engineering" : ["Engineering", "Telecommunications"],
    "Legal Services" : "Legal",
    "Healthcare" : ["Environment / Health", "Healthcare / Pharmaceutical", "Medical / Therapy Services"]
}

monthTranslation = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
    "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
    "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}

quarterTranslation = {
    "Jan": "Q1", "Feb": "Q1", "Mar": "Q1", "Apr": "Q2",
    "May": "Q2", "Jun": "Q2", "Jul": "Q3", "Aug": "Q3",
    "Sep": "Q3", "Oct": "Q4", "Nov": "Q4", "Dec": "Q4"
}

# Functions

def tokenize_and_translate(industry, industryTranslation):
    # Tokenize the industry string based on the delimiter ','
    tokens = [token.strip() for token in industry.split(',')]
    
    # Map the tokenized words to the industryTranslation dictionary
    translated_tokens = []
    for token in tokens:
        for key, values in industryTranslation.items():
            if isinstance(values, list):
                if token in values:
                    translated_tokens.append(key)
            elif token == values:
                translated_tokens.append(key)
    
    # Remove duplicates and return the translated tokens
    return list(set(translated_tokens))

def DuplicateRowsByCategory(df):
    # Read the input CSV file into a DataFrame
    print(df)

    # Check if 'Broader Category' column exists
    if 'Broader Category' not in df.columns:
        print("Error: 'Broader Category' column not found in the input CSV file.")
        return

    # Create a list to hold the new rows
    new_rows = []

    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        # Split the Broader Category column by comma
        categories = row['Broader Category'].split(', ') if pd.notna(row['Broader Category']) else []
        
        # If there are multiple categories, create duplicates of the row
        if len(categories) > 1:
            for i, category in enumerate(categories):
                new_row = row.copy()
                new_row['Broader Category'] = category
                new_row['Job Id'] = f"{row['Job Id']}-{i+1}"
                new_rows.append(new_row)
        else:
            new_rows.append(row)

    # Create a new DataFrame from the new rows
    new_data = pd.DataFrame(new_rows)

    return new_data

def remove_duplicates(input_csv_file, output_csv_file):
    if os.path.exists(input_csv_file):
        with open(input_csv_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            fieldnames = reader.fieldnames
            seen = set()
            unique_rows = []
            for row in reader:
                row_tuple = tuple(row.items())  # Convert row to a tuple of items
                if row_tuple not in seen:
                    seen.add(row_tuple)
                    unique_rows.append(row)
        
        # Write the unique rows to a new CSV file
        with open(output_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(unique_rows)

def SaveDataToNewCSV(outputfile, new_data):
    # Read the existing file or create a new DataFrame if it doesn't exist
    if os.path.isfile(outputfile):
        existing_df = pd.read_csv(outputfile)
    else:
        existing_df = pd.DataFrame()

    # Ensure all columns in new_data exist in the DataFrame
    for column_name in new_data.keys():
        if column_name not in existing_df.columns:
            existing_df[column_name] = None  # Create the column if it doesn't exist

    # Prepare a new DataFrame to hold the new data
    new_rows = pd.DataFrame(new_data)

    # Find the last row index (max) across all columns
    last_row_index = existing_df.index.max() if not existing_df.empty else -1

    # Append new rows starting from the last row index + 1
    for i in range(len(new_rows)):
        for column_name in new_data.keys():
            # Ensure new data gets appended after the last row
            existing_df.at[last_row_index + 1 + i, column_name] = new_rows.iloc[i][column_name]

    # Write the updated DataFrame back to the file, overwriting the previous one
    existing_df.to_csv(outputfile, mode='w', index=False)
    
def ReformatSalary(input_csv_file):
    # Read the input CSV file into a DataFrame
    df = pd.read_csv(input_csv_file, index_col=False, on_bad_lines='skip')

    # Ensure the 'Job Salary Range' column exists
    if 'Job Salary Range' in df.columns:
        # Remove '$' and ',' and split the salary range into two columns
        df[['Min Salary', 'Max Salary']] = df['Job Salary Range'].str.replace('[\$,]', '', regex=True).str.split('to', expand=True)

        # Convert the new columns to numeric, coercing errors
        df['Min Salary'] = pd.to_numeric(df['Min Salary'], errors='coerce')
        df['Max Salary'] = pd.to_numeric(df['Max Salary'], errors='coerce')

        # Check for NaN values after conversion
        if df['Min Salary'].isnull().any() or df['Max Salary'].isnull().any():
            print("There are NaN values in 'Min Salary' or 'Max Salary' after conversion.")
            print(df[df['Min Salary'].isnull() | df['Max Salary'].isnull()])  # Print problematic rows

        # Convert monthly salaries to annual salaries in thousands
        df['Min Salary (K)'] = ((df['Min Salary'] / 1000) * 12)   # Annual Min Salary in K
        df['Max Salary (K)'] = ((df['Max Salary'] / 1000) * 12)   # Annual Max Salary in K
        

        # Calculate the salary range between maximum and minimum
        df['Salary Range (K)'] = (df['Max Salary (K)'] - df['Min Salary (K)']) # Annual Salary Range in K

        # Calculate the average salary in thousands
        df['Average Salary (K)'] = (df['Min Salary (K)'] + df['Max Salary (K)']) / 2 

        # Prepare a new DataFrame with just the columns to append
        new_data = df[['Min Salary (K)', 'Max Salary (K)', 'Average Salary (K)','Salary Range (K)']].copy()  

        #SaveDataToNewCSV(outputfile,new_data)
        return new_data

    else:
        print("The 'Job Salary Range' column does not exist in the provided CSV file.")

def ProcessWorkType(input_csv_file):
    # Read the input CSV file into a DataFrame
    df = pd.read_csv(input_csv_file, index_col=False, on_bad_lines='skip')
    df.rename(columns={'Job Employment Type': 'Work Type'}, inplace=True)
    df['Work Type'] = df['Work Type'].str.split(',').str[0].str.split('/').str[0]
    replacements = {
        'Full Time': 'Full-Time',
        'Part Time': 'Part-Time'
    }

    # Replace spaces with dashes for specific values
    for key, value in replacements.items():
        df['Work Type'] = df['Work Type'].str.replace(key, value, regex=False)

    new_data = df[['Work Type']].copy()     

    #SaveDataToNewCSV(outputfile,new_data)
    return new_data

def RemoveExtraHeaderRows(csv_file):
    # Load the CSV file
    df = pd.read_csv(csv_file)

    # Define the list of values to remove rows if any cell contains these values
    values_to_remove = [   
        "Job URL", 
        "Job Title", 
        "Job Location", 
        "Job Employment Type", 
        "Job Seniority", 
        "Job Minimum Experience", 
        "Job Industry", 
        "Job Salary Range", 
        "Job Description", 
        "Job Skills Needed",
        ">>>>>>> Stashed changes",
        "<<<<<<< Updated upstream",
        "======="
    ]

    # Column to check for duplicate id
    id_column = 'Job Id'

    # Remove duplicate rows based on the ID column
    df_cleaned = df.drop_duplicates(subset=id_column, keep='first')

    # Remove header rows
    df_cleaned = df_cleaned[~df_cleaned.isin(values_to_remove).any(axis=1)]

    # Save the cleaned DataFrame back to the CSV file
    df_cleaned.to_csv(csv_file, index=False)


def ProcessPostingDate(input_csv_file):

    # Load the CSV file
    df = pd.read_csv(input_csv_file)

    # Extract the entire posting date column and fill NaN values with an empty string
    posting_dates = df['Job Posting Date'].fillna('')

    # Create a new column for processed posting dates
    processed_dates = []

    # Iterate through each row in posting dates
    for date in posting_dates:
        try:
            # Remove the "Posted " prefix if it exists
            if date.startswith("Posted "):
                date = date.replace("Posted ", "")
            # Split the date into day, month, and year
            day, month_str, year = date.split()
            # Translate the month to its numerical value
            month = monthTranslation[month_str]
            # Reformat the date to the desired format
            processed_date = f"{year}-{month}-{day}"
        except Exception as e:
            # If any error occurs, keep the original date string
            processed_date = date
        processed_dates.append(processed_date)

    # Add the new column to the DataFrame
    df['Job Posting Date'] = processed_dates

    # Return the updated DataFrame
    return df[['Job Posting Date']].copy()


def ProcessQuarter(input_csv_file):
    # Load the CSV file
    df = pd.read_csv(input_csv_file, on_bad_lines='skip')

    # Extract the entire Job Posting Date column
    posting_dates = df['Job Posting Date'].fillna('')

    # Create a new column for Year-Quarter
    year_quarter = []

    # Iterate through each row in Job Posting Date
    for date in posting_dates:
        # Extract the posting date and split it into components
        date_parts = date.split(' ')
        if len(date_parts) == 4:
            day = int(date_parts[1])
            month = date_parts[2]
            year = int(date_parts[3])

            # Determine the quarter
            quarter = quarterTranslation[month]

            # Format the Year-Quarter
            year_quarter.append(f"{year}{quarter}")
        else:
            year_quarter.append(None)  # Handle unexpected date format

    # Add the new column to the DataFrame
    df['Year-Quarter'] = year_quarter

    # Return the updated DataFrame
    return df[['Year-Quarter']].copy()

def TransformByIndustry(input_csv_file, industryTranslation):
    if os.path.exists(input_csv_file):
        # Load the CSV file into a DataFrame
        df = pd.read_csv(input_csv_file, on_bad_lines='skip')
        # Translate industries and add a new column
        df['Broader Category'] = df['Job Industry'].apply(lambda x: ', '.join(tokenize_and_translate(x, industryTranslation)) if pd.notna(x) else '')
        print(df['Broader Category'])

        return df[['Broader Category']].copy()

def ProcessMinExp(input_csv_file):
    # Load the CSV file
    df = pd.read_csv(input_csv_file, on_bad_lines='skip')

    # Extract the entire Job Minimum Experience column
    min_exp = df['Job Minimum Experience']

    # Create a new column for processed minimum experience
    processed_min_exp = []

    # Iterate through each row in Job Minimum Experience
    for exp in min_exp:
        # Extract numeric value from the experience string
        exp_value = ''.join(filter(str.isdigit, str(exp)))
        if exp_value:
            processed_min_exp.append(int(exp_value))
        else:
            processed_min_exp.append(0)

    # Add the new column to the DataFrame
    df['Job Minimum Experience'] = processed_min_exp

    # Return the updated DataFrame
    return df[['Job Minimum Experience']].copy()

def ProcessSkills(input_csv_file):
    # Load the CSV file
    df = pd.read_csv(input_csv_file, on_bad_lines='skip')

    # Extract the entire skills column
    skills = df['skills'].fillna('')

    # Create a new column for processed skills
    processed_skills = []

    # Iterate through each row in skills
    for skill in skills:
        # Split the skills by newline characters
        skill_list = skill.split('\n')
        # Encapsulate each skill with single quotes and join them with commas
        processed_skill = "[" + ", ".join(f"'{s}'" for s in skill_list) + "]"
        processed_skills.append(processed_skill)

    # Add the new column to the DataFrame
    df['skills'] = processed_skills
    print("SKILLS DONE")

    # Return the updated DataFrame
    return df[['skills']].copy()

def TransformCompany(input_csv_file):
    # Load the CSV file
    df = pd.read_csv(input_csv_file, on_bad_lines='skip')

    # Extract the entire Company column
    companies = df['Company'].fillna('')

    # Create a new column for transformed company names
    transformed_companies = []

    # Iterate through each row in Company
    for company in companies:
        # Convert the company name to title case (camel case)
        transformed_company = company.title()
        transformed_companies.append(transformed_company)

    # Add the new column to the DataFrame
    df['Company'] = transformed_companies

    # Return the updated DataFrame
    return df[['Company']].copy()

def PruneNullIndustryRows(new_data):
    # Remove rows where the 'Broader Category' column is empty
    pruned_data = new_data[new_data['Broader Category'].notna() & (new_data['Broader Category'] != '')]
    return pruned_data

def FillMaxExp(input_csv_file):
    # Load the CSV file
    df = pd.read_csv(input_csv_file, on_bad_lines='skip')

    # Set the 'Job Maximum Experience' column to 0 for every row
    df['Job Maximum Experience'] = 0

    # Return the updated DataFrame
    return df[['Job Maximum Experience']].copy()

def PruneExtraCols(csv_file):
    # Check if the output CSV file exists
    if os.path.isfile(csv_file):
        output_df = pd.read_csv(csv_file)
        # Check if the DataFrame has more than 18 columns
        if len(output_df.columns) > 18:
            output_df = output_df.iloc[:, :18]
            output_df.to_csv(csv_file, index=False)

def CleanJobTitle(input_csv_file):
    df = pd.read_csv(input_csv_file, on_bad_lines='skip')
    # Clean the 'Job Title' column using regex
    df['Job Title'] = df['Job Title'].apply(lambda text: re.sub(
        r'[\(\[\{].*?[\)\]\}]|\*\*.*?\*\*|//.*?//|\\.*?\\|\|\|.*?\|\|[^\x00-\x7F]+', 
        '', 
        text) if isinstance(text, str) else text
    )

    # Return the cleaned DataFrame with the 'Job Title' column
    return df[['Job Title']].copy()
    



def main(input_csv_file, output_csv_file):
    try:
        if os.path.exists(input_csv_file):
            # Load the CSV file into a DataFrame

            #PruneExtraCols(input_csv_file)
            df = pd.read_csv(input_csv_file, on_bad_lines='skip')

            RemoveExtraHeaderRows(input_csv_file)

            # Fill NaN values in relevant columns
            df['Job Industry'] = df['Job Industry'].fillna('')

            #Process the worktype, postdate, and salary columns
            worktype = ProcessWorkType(input_csv_file)
            postdate = ProcessPostingDate(input_csv_file)
            salary = ReformatSalary(input_csv_file)
            yearquarter = ProcessQuarter(input_csv_file)
            broaderCat = TransformByIndustry(input_csv_file, industryTranslation)
            minExp = ProcessMinExp(input_csv_file)
            skills = ProcessSkills(input_csv_file)
            company = TransformCompany(input_csv_file)
            maxExp = FillMaxExp(input_csv_file)
            jobTitle = CleanJobTitle(input_csv_file)

            # Merge the processed columns back into the main DataFrame
            df['Work Type'] = worktype['Work Type']
            df['Job Posting Date'] = postdate['Job Posting Date']
            df['Min Salary (K)'] = salary['Min Salary (K)']
            df['Max Salary (K)'] = salary['Max Salary (K)']
            df['Average Salary (K)'] = salary['Average Salary (K)']
            df['Salary Range (K)'] = salary['Salary Range (K)']
            df['Year-Quarter'] = yearquarter['Year-Quarter']
            df['Broader Category'] = broaderCat['Broader Category']
            df['Job Minimum Experience'] = minExp['Job Minimum Experience']
            df['skills'] = skills['skills']
            df['Company'] = company['Company']
            df['Job Maximum Experience'] = maxExp['Job Maximum Experience']
            df['Job Title'] = jobTitle['Job Title'] 

            # Transform the Broader Category column
            new_data = DuplicateRowsByCategory(df)

            # Prune rows with null Broader Category
            pruned_data = PruneNullIndustryRows(new_data)

            # Save the updated DataFrame to a new CSV file
            SaveDataToNewCSV(output_csv_file, pruned_data)

            # Remove extra colummns at the end.
            PruneExtraCols(output_csv_file)

            #remove duplicate rows
            RemoveExtraHeaderRows(output_csv_file)
            
            print("Extra Data Columns Pruned. Data successfully appended. EXITING...")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main(csv_file, file_path)