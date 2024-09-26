import pandas as pd
import plotly.express as px
import plotly.io as pio

import numpy as np
import plotly.graph_objects as go
import re
import ast
from collections import defaultdict

import dash_bootstrap_components as dbc
from wordcloud import WordCloud


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



def create_job_title_bubble_chart(data, industry_name):
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
    fig.update_traces(
        hovertemplate="<b>%{text}</b><extra></extra>",  # Only display job title, remove other values
        textposition='middle center'
    )

    # Update layout for a clean look
    fig.update_layout(showlegend=False, 
                      xaxis=dict(showticklabels=False), 
                      yaxis=dict(showticklabels=False),
                      height=600,
                      margin=dict(l=20, r=20, t=40, b=80),
                      clickmode='event+select')  # Enable click events

    # Return the chart as HTML
    html_code = fig.to_html(full_html=False)
    return html_code



def create_salary_variation_chart(data, industry_name):
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

    # Return the bubble chart as HTML code
    html_code = fig.to_html(full_html=False)
    return html_code


def create_salary_trend_chart(data, industry_name):
    # Filter data for the selected industry
    industry_data = data[data['Broader Category'] == industry_name]

    # Group by Job Title and Year-Quarter, then calculate average salary
    salary_trend = industry_data.groupby(['Job Title', 'Year-Quarter'])['Average Salary (K)'].mean().reset_index()

    # Ensure Year-Quarter is sorted and convert to string
    salary_trend['Year-Quarter'] = pd.Categorical(salary_trend['Year-Quarter'], 
                                                  categories=sorted(salary_trend['Year-Quarter'].unique()),
                                                  ordered=True)

    # Create a line chart for salary trends by job title
    fig = go.Figure()

    job_titles = salary_trend['Job Title'].unique()

    # Use a color palette for consistency
    colors = px.colors.qualitative.Plotly

    for i, job_title in enumerate(job_titles):
        job_data = salary_trend[salary_trend['Job Title'] == job_title]

        # Add the actual salary line, initially hidden, using Scattergl for performance
        fig.add_trace(go.Scattergl(
            x=job_data['Year-Quarter'],
            y=job_data['Average Salary (K)'],
            mode='lines+markers',
            name=f'{job_title} Salary',
            line=dict(color=colors[i % len(colors)], width=2),  # Set color from palette
            showlegend=True,
            visible='legendonly'  # Initially hidden
        ))

        # Add the trendline with the same color but dashed, initially hidden
        z = np.polyfit(pd.to_numeric(job_data['Year-Quarter'].str.replace('Q', '')), job_data['Average Salary (K)'], 1)
        p = np.poly1d(z)

        fig.add_trace(go.Scattergl(
            x=job_data['Year-Quarter'],
            y=p(pd.to_numeric(job_data['Year-Quarter'].str.replace('Q', ''))),
            mode='lines',
            name=f'{job_title} Trendline',
            line=dict(dash='dash', color=colors[i % len(colors)], width=2),  # Same color but dashed
            showlegend=True,
            visible='legendonly'  # Initially hidden
        ))

    # Update layout with fixed x-axis
    fig.update_layout(
        title=f'Average Salary Trends by Job Title in {industry_name} (Quarterly)',
        xaxis_title='Quarter Year',
        yaxis_title='Average Salary (K)',
        height=600,
        margin=dict(l=20, r=20, t=40, b=80),
        xaxis=dict(
            tickmode='array',
            tickvals=sorted(salary_trend['Year-Quarter'].unique()),  # Fixed, evenly spaced x-axis
            ticktext=sorted(salary_trend['Year-Quarter'].unique()),   # Ensure all quarters are displayed
            type='category'  # Keep the order of the quarters as categories
        )
    )

    # Convert the figure to HTML
    html_code = fig.to_html(full_html=False)
    return html_code

def merge_sort(word_freq_list):
    if len(word_freq_list) <= 1:
        return word_freq_list
    
    mid = len(word_freq_list) // 2
    left_half = merge_sort(word_freq_list[:mid])
    right_half = merge_sort(word_freq_list[mid:])
    
    sorted_list = []
    i = j = 0
    
    while i < len(left_half) and j < len(right_half):
        if left_half[i][1] >= right_half[j][1]:  # Sort in descending order
            sorted_list.append(left_half[i])
            i += 1
        else:
            sorted_list.append(right_half[j])
            j += 1
            
    sorted_list.extend(left_half[i:])
    sorted_list.extend(right_half[j:])
    
    return sorted_list

def CountWords(jobTitles,topNumOfItem):

    word_list=[]

    for jobs in jobTitles:
        try:
            # Convert string representation of list to actual list
            evaluated_jobs = ast.literal_eval(jobs)
            # Extend the final list with the skills
            word_list.extend([job.strip() for job in evaluated_jobs])
        except (ValueError, SyntaxError):
            # If the string isn't a list, split it by commas and process it
            clean_data = jobs.replace("'", "").split(',')
            word_list.extend([job.strip() for job in clean_data])


    if not isinstance(word_list, list) or len(word_list) == 0:
        print("Your input is invalid!")
        return []

    try:
        # Initialize a regular dictionary for word counts
        word_counts = {}

        # Count the frequency of each word
        for word in word_list:
            if word in word_counts:
                word_counts[word] += 1
            else:
                word_counts[word] = 1

        # Convert the dictionary to a list of tuples (word, frequency)
        word_freq_list = list(word_counts.items())

        # Sort the list of tuples using merge sort
        sorted_word_freq = merge_sort(word_freq_list)

        # Get the top 5 words
        top_words = [word for word, freq in sorted_word_freq[:topNumOfItem]]

        print(f"{sorted_word_freq} {top_words} {type(sorted_word_freq)}")

        # Return the top 5 words as a list
        return top_words,sorted_word_freq

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def skills_comparison(Industry,job_role,user_skills):    
    industry_path = pd.read_csv(f"Datasets/(Final)_past_{Industry}.csv")

    # get all skills from a particular job title
    skills = industry_path[industry_path['Job Title'] == job_role]['skills'].tolist()

    top10Skills,sortedWords = CountWords(skills,10)


    userSkillLowerCase, top10SkillsLowerCase = ([item.lower() for item in lst] for lst in (user_skills, top10Skills))

    # Calculate matched and missing skills
    matched_skills = [skill for skill in userSkillLowerCase if skill in top10SkillsLowerCase]
    missing_skills = [skill for skill in top10SkillsLowerCase if skill not in userSkillLowerCase]

    # Calculate percentages
    matched_percentage = (len(matched_skills) / len(top10SkillsLowerCase)) * 100
    missing_percentage = (len(missing_skills) / len(top10SkillsLowerCase)) * 100

    # Create the donut chart
    fig = go.Figure(data=[go.Pie(values=[matched_percentage, missing_percentage],
                                    labels=["Skills Match", "Skills Missing"],
                                    hole=0.4,
                                    marker=dict(colors=["green", "red"]),
                                    hoverinfo="label+percent",  # This controls what is shown when hovering
                                    # Add custom data for hover information
                                    customdata=[matched_skills, missing_skills],
                                    
                                    # Configure hover template to show skills
                                    hovertemplate=(
                                        '<b>%{label}</b><br>'  # Display label ("Skills Match" or "Skills Missing")
                                        '%{percent:.1%}<br>'  # Display percentage
                                        '<b>Skills:</b> %{customdata}<extra></extra>'  # Show the list of skills
                                    )
                                    )])

    # Add annotations for the percentages
    # fig.add_annotation(text=f"{matched_percentage}%", x=0.2, y=0.5, showarrow=False)
    # fig.add_annotation(text=f"{missing_percentage}%", x=0.8, y=0.5, showarrow=False)

    # Add text for matched and missing skills
    # fig.add_annotation(text="Skills Match", x=0.15, y=0.2, showarrow=False)
    # fig.add_annotation(text="Skills Missing", x=0.85, y=0.2, showarrow=False)

    # Add text for specific skills
    # for i, skill in enumerate(skills):
    #     if skill in matched_skills:
    #         fig.add_annotation(text=skill, x=0, y=0.6 - 0.05 * i, showarrow=False)
    #     else:
    #         fig.add_annotation(text=skill, x=1.0, y=0.6 - 0.05 * i, showarrow=False)

    fig.update_layout(
            title="Skills Comparison",
            width=800,  # Adjust width
            height=600  # Adjust height
        )
    # Return the HTML representation of the chart
    return fig.to_html(),missing_skills

def generate_wordcloud(Industry):
    industry_path = pd.read_csv(f"Datasets/(Final)_past_{Industry}.csv")

    # get all skills from a particular job title
    jobTitles = industry_path['Job Title'].apply(lambda x: x.split()[0])

    top10Jobs,sortedJobTitles = CountWords(jobTitles,10)

    # Create a dictionary from the word data
    word_dict = dict(sortedJobTitles)
    
    # Generate the word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_dict)
    
    # Create a Plotly figure
    fig = go.Figure()
    fig.add_trace(go.Image(z=wordcloud.to_array()))
    
    # Update layout for better display
    fig.update_layout(
        height=400,
        xaxis={"visible": False},
        yaxis={"visible": False},
        margin={"t": 0, "b": 0, "l": 0, "r": 0},
        hovermode=False,
        paper_bgcolor="white",
        plot_bgcolor="white"
    )
    
    return pio.to_html(fig, full_html=False)