import pandas as pd
import plotly.express as px
import plotly.io as pio
from geopy.geocoders import Nominatim
import numpy as np
import plotly.graph_objects as go
import re
import ast
from collections import defaultdict
import json
import dash_bootstrap_components as dbc
from wordcloud import WordCloud
import numpy

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



def create_job_title_bubble_chart(data, industry_name_orig):
    # Filter data for the selected 'Broader Category'
    industry_data = data[data['Broader Category'] == industry_name_orig]

    # Count the frequency of each job title in the selected industry
    job_title_counts = industry_data['Job Title'].value_counts().reset_index()
    job_title_counts.columns = ['Job Title', 'Job Count']

    # Create a DataFrame for the bubble chart
    job_title_df = pd.DataFrame({
        'Job Title': job_title_counts['Job Title'],
        'Bubble Size': job_title_counts['Job Count'] * 2,  # Increase bubble size proportional to the frequency
        'x': np.random.rand(len(job_title_counts)) * 100,  # Spread out x values more widely
        'y': np.random.rand(len(job_title_counts)) * 100   # Spread out y values more widely
    })
    
    # Create a bubble chart using Plotly
    fig = px.scatter(job_title_df, 
                     x='x', 
                     y='y', 
                     size='Bubble Size',
                     color='Job Title',  
                     text='Job Title',  # Use job titles as bubble labels
                     title=f'Job Titles in {industry_name_orig}', 
                     labels={'x': ' ', 'y': ' '},  # Hide x and y axis labels
                     size_max=80  # Increase the maximum size of the bubbles
                     )
    
    # Customize the hovertemplate to show only the Job Title
    fig.update_traces(
        hovertemplate="<b>%{text}</b><extra></extra>",  # Only display job title on hover
        textposition='middle center'  # Position text inside the bubble
    )

    # Update layout for a clean look and to spread out the bubbles
    fig.update_layout(showlegend=False, 
                      xaxis=dict(showticklabels=False, range=[-10, 110]),  # Spread x axis range
                      yaxis=dict(showticklabels=False, range=[-10, 110]),  # Spread y axis range
                      height=700,  # Adjust the height to give more room for the bubbles
                      margin=dict(l=20, r=20, t=40, b=80),
                      clickmode='event+select')  # Enable click events

    # Return the chart as HTML
    html_code = fig.to_html(full_html=False)
    return html_code


def create_salary_variation_chart(data, industry_name_orig):
    # Filter data for the selected industry
    industry_data = data[data['Broader Category'] == industry_name_orig]

    # Get all unique job titles
    job_titles = industry_data['Job Title'].unique()

    # Create the box plot
    fig = go.Figure()

    # Plot the first 5 job titles and show them by default
    for i, job_title in enumerate(job_titles[:5]):
        job_data = industry_data[industry_data['Job Title'] == job_title]
        fig.add_trace(go.Box(
            y=job_data['Average Salary (K)'],
            name=job_title,
            boxmean=True,
            marker_color=px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)],
            showlegend=True,
            visible=True  # Show the first 5 job titles initially
        ))

    # Plot the rest of the job titles but keep them hidden initially
    for i, job_title in enumerate(job_titles[5:], start=5):
        job_data = industry_data[industry_data['Job Title'] == job_title]
        fig.add_trace(go.Box(
            y=job_data['Average Salary (K)'],
            name=job_title,
            boxmean=True,
            marker_color=px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)],
            showlegend=True,
            visible='legendonly'  # Keep the other job titles hidden initially
        ))

    # Update layout to make the chart larger
    fig.update_layout(
        title=f'Salary Distribution by Job Title in {industry_name_orig}',
        yaxis_title='Average Salary (K)',
        height=800,  # Adjusted height
        clickmode='event+select'
    )

    # Return the box plot as HTML code
    html_code = fig.to_html(full_html=False)
    return html_code

def create_salary_trend_chart(data, industry_name_orig):
    # Filter data for the selected industry
    industry_data = data[data['Broader Category'] == industry_name_orig]

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
        title=f'Average Salary Trends by Job Title in {industry_name_orig} (Quarterly)',
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


def skills_comparison(userSkills, job_type, industry, top_searches=10):
    # Load the JSON data
    with open(f'analysis/job_role_skill_{industry}.json', 'r') as f:
        data = json.load(f)

    # Convert user skills to lowercase for case-insensitive comparison
    userSkillLowerCase = [skill.lower() for skill in userSkills]

    # Extract top skills for the selected job type
    top_skills = data[job_type]
    
    # Sort and get the top N skills
    top_n_skills = sorted(top_skills.items(), key=lambda x: x[1], reverse=True)[:top_searches]
    top_n_skills_lower_case = {skill[0].lower(): skill[1] for skill in top_n_skills}

    # Calculate matched and missing skills
    matched_skills = [skill for skill in userSkillLowerCase if skill in top_n_skills_lower_case]
    missing_skills = [skill for skill in top_n_skills_lower_case if skill not in userSkillLowerCase]

    # Calculate percentages
    matched_percentage = (len(matched_skills) / len(top_n_skills_lower_case)) * 100 if top_n_skills_lower_case else 0
    missing_percentage = (len(missing_skills) / len(top_n_skills_lower_case)) * 100 if top_n_skills_lower_case else 0

    matched_skills_multiline = '<br>'.join(matched_skills)
    missing_skills_multiline = '<br>'.join(missing_skills)

    # Create the donut chart
    fig = go.Figure(data=[go.Pie(values=[matched_percentage, missing_percentage],
                                   labels=["Skills Match", "Skills Missing"],
                                   hole=0.4,
                                   marker=dict(colors=["green", "red"]),
                                   hoverinfo="label+percent",
                                   customdata=[matched_skills_multiline, missing_skills_multiline],
                                   hovertemplate=(
                                       '<b>%{label}</b><br>'
                                       '%{percent:.1%}<br>'
                                       '<b>Skills:</b><br>%{customdata}<extra></extra>'
                                   ))])

    fig.update_layout(
        title="Skills Comparison",
        width=800,
        height=600
    )

    # Return the HTML representation of the chart along with matched and missing skills
    return fig.to_html(), missing_skills, matched_skills


def generate_wordcloud(industry):
    # Load data from JSON file
    with open('analysis/industry_Jobs.json', 'r') as f:
        data = json.load(f)
    
    industryName = industry.replace("_", " ")

    # Check if the industry exists in the data
    if industryName not in data:
        raise ValueError(f"Industry '{industryName}' not found in the data.")
    
    # Get job titles and their counts for the specified industry
    job_titles = data[industryName]
    
    # Create a frequency dictionary for job titles
    word_dict = {job_title: count for job_title, count in job_titles.items()}
    
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

def load_and_geocode_data(industry):
    # Load your CSV data into a pandas DataFrame
    df = pd.read_csv(f"Datasets/(Final)_past_{industry}.csv")

    if 'Location' not in df.columns:
        raise ValueError("CSV must contain a 'Location' column.")
    
    # Group by location, count occurrences
    df_grouped = df.groupby('Location').size().reset_index()
    
    # Rename the columns
    df_grouped.columns = ['Location', 'Value']
    print("Grouped DataFrame:")
    print(df_grouped)

    # Geocode location names to get latitude and longitude
    geolocator = Nominatim(user_agent="geoapi")
    
    # Add new columns for latitude and longitude
    df_grouped['Latitude'] = None
    df_grouped['Longitude'] = None
    
    for index, row in df_grouped.iterrows():
        location = geolocator.geocode(row['Location'])
        if location:
            df_grouped.at[index, 'Latitude'] = location.latitude
            df_grouped.at[index, 'Longitude'] = location.longitude

    return df_grouped

def GeographicalMap(industry):
    # Convert location names to lat/lon
    df = load_and_geocode_data(industry)
    
    # Filter out rows where geocoding failed
    df = df.dropna(subset=['Latitude', 'Longitude'])
    singapore_center = dict(lat=1.3521, lon=103.8198)

    # Create a density heatmap using the converted lat/lon
    fig = px.density_mapbox(df, lat='Latitude', lon='Longitude', z='Value', radius=10,
                            center=singapore_center,
                            mapbox_style="open-street-map", zoom=10)
    
    fig.update_layout(
        title="job locations",
        width=800,  # Adjust width
        height=600  # Adjust height
    )
    # Convert the plotly figure to HTML
    return fig.to_html()


def skill_in_demand():
    # Load the CSV
    with open("Datasets/(Final)_past_Business.csv") as file:
        df = pd.read_csv(file, index_col=False)

    # Filter job roles
    job_role_df = df[df["Job Title"] == "Customer Support Specialist"].copy()

    # Convert date and eval skills
    job_role_df['Job Posting Date'] = pd.to_datetime(job_role_df['Job Posting Date'], format="%Y-%m-%d")
    job_role_df["skills"] = job_role_df["skills"].apply(ast.literal_eval)

    # Sort by Job Posting Date
    job_role_df.sort_values(by="Job Posting Date", inplace=True, ascending=True)

    # Get unique years
    years = job_role_df["Job Posting Date"].dt.to_period("Y").unique()
    df_list = []

    # Prepare data for each year
    for year in years:
        year_df = job_role_df[job_role_df["Job Posting Date"].dt.to_period("Y") == year]
        skill_per_year = year_df["skills"].explode().value_counts()

        total_count = skill_per_year.values.sum()
        skill_per_year = skill_per_year.reset_index()
        skill_per_year.columns = ["skill", "count"]
        skill_per_year["percent"] = np.floor((skill_per_year["count"] / total_count) * 100)
        skill_per_year["year"] = str(year)  # Convert year to string for easier labeling

        leftover = 100 - skill_per_year["percent"].sum()
        # Allocate leftover percentage
        if leftover > 0:
            leftover_row = skill_per_year["percent"].nlargest(int(leftover)).index
            for x in leftover_row:
                skill_per_year.at[x, "percent"] += 1

        df_list.append(skill_per_year)

    # Concatenate all years' data
    job_df = pd.concat(df_list)

    # Create a Plotly pie chart with dropdowns to switch between years
    fig = go.Figure()

    for year in job_df["year"].unique():
        year_df = job_df[job_df["year"] == year]
        fig.add_trace(go.Pie(labels=year_df["skill"], values=year_df["percent"], name=year))

    # Create dropdown buttons to switch between years
    fig.update_layout(
        updatemenus=[
            dict(
                buttons=[
                    dict(label=str(year), method="update", 
                         args=[{"visible": [year == y for y in job_df["year"].unique()]}]) 
                    for year in job_df["year"].unique()
                ],
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.1,
                xanchor="left",
                y=1.1,
                yanchor="top"
            )
        ]
    )

    return fig.to_html()
