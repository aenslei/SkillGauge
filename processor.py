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
#import nltk

# Variables

csv_file = "job_listings.csv"
NewIndustries_csv_file = "job_listingsNewIndustries.csv"
NoDupes_csv_file = "job_listingsNoDupes.csv"

file_path = r'Datasets\\sg_job_data-Cleaned-With Industry1.csv'

industryTranslation = {
    "Information Technology" : "Information Technology",
    "Business" : ["Advertising / Media" , "Customer Service", "Events / Promotions", "Logistics / Supply Chain", "Purchasing / Merchandising", "Risk Management", "Insurance", "Marketing / Public Relations", "Sales / Retail", "Accounting / Auditing / Taxation", "Banking and Finance"],
    "Engineering" : ["Engineering", "Telecommunications"],
    "Legal Services" : "Legal",
    "Healthcare" : ["Environment / Health", "Healthcare / Pharmaceutical", "Medical / Therapy Services"]
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

def industryTranslate(csv_file, output_csv_file, industryTranslation):
    if os.path.exists(csv_file):
        with open(csv_file, 'r', encoding='utf-8') as csvfile:  # Specify encoding
            reader = csv.DictReader(csvfile)
            fieldnames = reader.fieldnames + ['Translated Industries']  # Add new column header
            rows = []
            for row in reader:
                industry = row['Job Industry']  # Replace 'Job Industry' with the actual header name
                translated_industries = tokenize_and_translate(industry, industryTranslation)
                row['Translated Industries'] = ', '.join(translated_industries)  # Join translated industries into a string
                rows.append(row)
        
        # Write the updated rows to a new CSV file
        with open(output_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

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

def SaveDataToNewCSV(outputfile,new_data):
    # Read the existing file or create a new DataFrame if it doesn't exist
    if os.path.isfile(outputfile):
        existing_df = pd.read_csv(outputfile)
    else:
        existing_df = pd.DataFrame()

    # Ensure all columns in new_data_dict exist in the DataFrame
    for column_name in new_data.keys():
        if column_name not in existing_df.columns:
            existing_df[column_name] = None  # Create the column if it doesn't exist

    # Prepare a new DataFrame to hold the new data
    new_rows = pd.DataFrame(new_data)

    # Append new data for each column
    for column_name in new_data.keys():
        # Find the last index of valid data in the column
        last_index = existing_df[column_name].last_valid_index()
        if last_index is None:
            last_index = -1  # If no valid index exists, start from the first row
        
        # Assign new data to the corresponding rows in the existing DataFrame
        for i in range(len(new_rows)):
            existing_df.at[last_index + 1 + i, column_name] = new_rows.iloc[i][column_name]

    # Write the updated DataFrame back to the file without appending the header
    existing_df.to_csv(outputfile, mode='w', index=False)
    print("Data appended successfully.")

def ReformatSalary(input_csv_file,outputfile):
    # Read the input CSV file into a DataFrame
    df = pd.read_csv(input_csv_file, index_col=False)

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

        # Divide the salary by 1000 to get the pay in thousands
        df['Min Salary (K)'] = df['Min Salary'] / 1000
        df['Max Salary (K)'] = df['Max Salary'] / 1000
        # calculate the salary range between maximum and minimum
        df['Salary Range (K)'] = (df['Max Salary'] - df['Min Salary'])/1000
        # Calculate the average salary
        df['Average Salary (K)'] = (df['Min Salary (K)'] + df['Max Salary (K)']) / 2

        # Prepare a new DataFrame with just the columns to append
        new_data = df[['Min Salary (K)', 'Max Salary (K)', 'Average Salary (K)','Salary Range (K)']].copy()  

        SaveDataToNewCSV(outputfile,new_data)

    else:
        print("The 'Job Salary Range' column does not exist in the provided CSV file.")

def ProcessWorkType(input_csv_file,outputfile):
    # Read the input CSV file into a DataFrame
    df = pd.read_csv(input_csv_file, index_col=False)
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

    SaveDataToNewCSV(outputfile,new_data)

def RemoveExtraHeaderRows():
    # Load the CSV file
    df = pd.read_csv(csv_file)

    #2685

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

    # Remove rows that contain any of the specified values
    df_cleaned = df[~df.isin(values_to_remove).any(axis=1)]

    # Save the cleaned DataFrame back to a CSV file
    df_cleaned.to_csv(csv_file, index=False)

def main():
    # industryTranslate(csv_file, NewIndustries_csv_file, industryTranslation)
    # remove_duplicates(NewIndustries_csv_file, NoDupes_csv_file)
    # RemoveExtraHeaderRows()
    ReformatSalary(csv_file,file_path)
    ProcessWorkType(csv_file,file_path)
    

if __name__ == "__main__":
    main()