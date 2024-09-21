import pandas as pd
import plotly.express as px
import plotly.io as pio
from io import BytesIO
import plotly.graph_objs as go
import random

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


# Function to extract unique job titles by industry
def get_job_titles_by_industry(industry_name, data):
    # Filter jobs for the selected industry and get unique job titles
    industry_jobs = data[data['Industry Name'] == industry_name]
    unique_job_titles = industry_jobs['Job Title'].unique()
    return unique_job_titles


#  Interactive Word Cloud using Plotly
def create_interactive_wordcloud(job_titles):
    # Create a frequency dictionary (here, just assigning a random value for demo purposes)
    title_freq = {title: random.randint(10, 50) for title in job_titles}

    # Create plotly trace for the word cloud
    trace = go.Scatter(
        x=[random.uniform(0, 1) for _ in title_freq],
        y=[random.uniform(0, 1) for _ in title_freq],
        text=list(title_freq.keys()),
        mode='text',
        textfont={'size': [freq * 2 for freq in title_freq.values()]},  # Size of the words
        hoverinfo='text',
        marker={'opacity': 0},
        hoverlabel={'namelength': -1},
    )

    layout = go.Layout(
        xaxis={'showgrid': False, 'showticklabels': False, 'zeroline': False},
        yaxis={'showgrid': False, 'showticklabels': False, 'zeroline': False},
        title="Interactive Job Titles Word Cloud",
        clickmode='event+select',  # Enable click events
    )

    fig = go.Figure(data=[trace], layout=layout)
    
    # Generate the Plotly HTML as a div and return
    wordcloud_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return wordcloud_html