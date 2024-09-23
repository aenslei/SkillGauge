import pandas as pd
import plotly.express as px
import plotly.io as pio
import numpy as np
import plotly.graph_objects as go
import re

def clean_salary_column(salary_column):
    # Handle strings with hyphens (ranges) or other non-numeric values
    def clean_salary_value(val):
        if pd.isna(val):  # If the value is NaN, return it as is
            return val
        if isinstance(val, str):
            # Check if it's a range (e.g., "65-9960"), and take the average of the range
            if '-' in val:
                try:
                    parts = [float(p) for p in val.split('-') if p.isdigit()]
                    return sum(parts) / len(parts) if parts else None
                except:
                    return None
            else:
                # Try to extract just the numeric part
                val = re.sub(r'\D', '', val)  # Remove non-numeric characters
                return float(val) if val else None
        return val

    # Apply the cleaning function to the column
    return salary_column.apply(clean_salary_value)

def load_data(file_path):
    data = pd.read_csv(file_path)
    print("Columns in dataset:", data.columns)
    print("First few rows of Min and Max Salary columns:")
    print(data[['Min Salary (K)', 'Max Salary (K)']].head())

    data['Min Salary (K)'] = pd.to_numeric(data['Min Salary (K)'], errors='coerce')
    data['Max Salary (K)'] = pd.to_numeric(data['Max Salary (K)'], errors='coerce')
    data['Job Posting Date'] = pd.to_datetime(data['Job Posting Date'], errors='coerce')
    data['Year-Quarter'] = data['Job Posting Date'].dt.to_period('Q').astype(str)

    # Calculate Average Salary
    data['Average Salary (K)'] = (data['Min Salary (K)'] + data['Max Salary (K)']) / 2

    return data



def analyse_industry_distribution(data):
    # Group the data by 'Broader Category' to get job distribution
    industry_distribution = data['Broader Category'].value_counts()
    industry_distribution_dict = industry_distribution.to_dict()
    total_jobs = len(data)
    
    return industry_distribution, total_jobs


def create_job_title_bubble_chart(data, industry_name, output_file):
    # Filter data for the selected 'Broader Category'
    industry_data = data[data['Broader Category'] == industry_name]

    # Get unique job titles for the selected industry
    job_titles = industry_data['Job Title'].unique()

    # Create a DataFrame for the bubble chart
    job_title_df = pd.DataFrame({
        'Job Title': job_titles,
        'Bubble Size': [10] * len(job_titles),  # Set all bubble sizes equally
        'x': np.random.rand(len(job_titles)),   # Generate random x values
        'y': np.random.rand(len(job_titles))    # Generate random y values
    })
    
    # Create a bubble chart using Plotly
    fig = px.scatter(job_title_df, 
                     x='x', 
                     y='y', 
                     size='Bubble Size',
                     color='Job Title',  
                     text='Job Title',  # Use job titles as bubble labels
                     title=f'Job Titles in {industry_name}', 
                     labels={'x': ' ', 'y': ' '},  # Hide x and y axis labels
                     size_max=40  # Control the maximum size of the bubbles
                     )
    
    # Customize the hovertemplate to show only the Job Title
    # fig.update_traces(
    #     hovertemplate="<b>%{text}</b><extra></extra>",  # Only display job title, remove other values
    #     textposition='middle center'
    # )

    # Update layout for a clean look
    fig.update_traces(textposition='middle center')
    fig.update_layout(showlegend=False, 
                      xaxis=dict(showticklabels=False), 
                      yaxis=dict(showticklabels=False),
                      height=800,
                      margin=dict(l=20, r=20, t=40, b=80),
                      clickmode='event+select')  # Enable click events

    # Add a custom click event handler to highlight the corresponding bar
    fig.update_layout(
        clickmode='event+select'
    )

    # Save the bubble chart as an HTML file
    pio.write_html(fig, file=output_file, auto_open=False)


def create_salary_variation_chart(data, industry_name, output_file):
    # Filter data for the selected industry
    industry_data = data[data['Broader Category'] == industry_name]

    # Group by Job Title and calculate average salary range
    salary_range_by_job_title = industry_data.groupby('Job Title').agg(
        avg_salary_range=('Salary Range (K)', 'mean'),
        min_salary=('Min Salary (K)', 'mean'),
        max_salary=('Max Salary (K)', 'mean')
    ).reset_index()

    # Sort by average salary range
    salary_range_by_job_title = salary_range_by_job_title.sort_values(by='avg_salary_range', ascending=False)

    # Create a bar chart to visualize the variation in salary range across job titles
    fig = px.bar(salary_range_by_job_title,
                 x='Job Title',
                 y='avg_salary_range',
                 title=f'Average Salary Range by Job Title in {industry_name}',
                 labels={'avg_salary_range': 'Average Salary Range (K)', 'Job Title': 'Job Title'},
                 color='Job Title',
                 height=600)

    fig.update_layout(
        clickmode='event+select'
    )

    # Save the figure to the specified output file
    pio.write_html(fig, file=output_file, auto_open=False)

def create_salary_trend_chart(data, industry_name, output_file):
# Filter data for the selected industry
    industry_data = data[data['Broader Category'] == industry_name]

    # Group by Job Title and Year-Quarter, then calculate average salary
    salary_trend = industry_data.groupby(['Job Title', 'Year-Quarter'])['Average Salary (K)'].mean().reset_index()

    # Create a line chart for salary trends by job title
    fig = go.Figure()

    job_titles = salary_trend['Job Title'].unique()
    colors = px.colors.qualitative.Plotly  # Use a pre-defined color palette

    for i, job_title in enumerate(job_titles):
        job_data = salary_trend[salary_trend['Job Title'] == job_title]

        # Add the actual salary line
        fig.add_trace(go.Scatter(
            x=job_data['Year-Quarter'],
            y=job_data['Average Salary (K)'],
            mode='lines+markers',
            name=f'{job_title} Salary',
            line=dict(color=colors[i % len(colors)], width=2),
            showlegend=True
        ))

        # Add the trendline (linear regression)
        z = np.polyfit(pd.to_numeric(job_data['Year-Quarter'].str.replace('Q','')), job_data['Average Salary (K)'], 1)
        p = np.poly1d(z)
        fig.add_trace(go.Scatter(
            x=job_data['Year-Quarter'],
            y=p(pd.to_numeric(job_data['Year-Quarter'].str.replace('Q',''))),
            mode='lines',
            name=f'{job_title} Trendline',
            line=dict(dash='dash', color=colors[i % len(colors)], width=2),
            showlegend=True
        ))

    # Update layout
    fig.update_layout(
        title=f'Average Salary Trends by Job Title in {industry_name} (Quarterly)',
        xaxis_title='Quarter Year',
        yaxis_title='Average Salary (K)',
        height=600,
        margin=dict(l=20, r=20, t=40, b=80)
    )

    # Save the figure to the specified output file
    pio.write_html(fig, file=output_file, auto_open=False)
