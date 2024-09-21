import pandas as pd
import plotly.express as px
import plotly.io as pio

# gets dataset from app.py
def load_data(file_path):
    data = pd.read_csv(file_path)

    # Convert 'Min Salary' and 'Max Salary' to numeric in case they are not
    data['Min Salary (K)'] = pd.to_numeric(data['Min Salary (K)'], errors='coerce')
    data['Max Salary (K)'] = pd.to_numeric(data['Max Salary (K)'], errors='coerce')

    # Create 'Average Salary (K)' if not present
    if 'Average Salary (K)' not in data.columns:
        data['Average Salary (K)'] = (data['Min Salary (K)'] + data['Max Salary (K)']) / 2

    return data

def analyse_industry_distribution(data):
    # Group the data by industry to get job distribution
    industry_distribution = data['Industry Name'].value_counts()
    industry_distribution_dict = industry_distribution.to_dict()
    total_jobs = len(data)
    
    return industry_distribution, total_jobs