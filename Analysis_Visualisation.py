'''
This file contains the visualisation and analysis codes

'''

import pandas as pd
import plotly.express as px
import plotly.io as pio
from geopy.geocoders import Nominatim           
import numpy as np
import plotly.graph_objects as go
import re
import ast
from collections import defaultdict
from sklearn.linear_model import LinearRegression
import json
import dash_bootstrap_components as dbc
from wordcloud import WordCloud
from scipy import stats
import warnings

#  Cleaning salary column
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
                # Extracting just the numeric part
                val = re.sub(r'\D', '', val)  # Remove non-numeric characters
                return float(val) if val else None
        return val

    # Apply the cleaning function to the column
    return salary_column.apply(clean_salary_value)

def load_data(file_path):
    data = pd.read_csv(file_path) #load file 
    data['Min Salary (K)'] = pd.to_numeric(data['Min Salary (K)'], errors='coerce') # coerce to convert the specifed columns into the same data type
    data['Max Salary (K)'] = pd.to_numeric(data['Max Salary (K)'], errors='coerce')
    data['Job Posting Date'] = pd.to_datetime(data['Job Posting Date'], errors='coerce')
    data['Year-Quarter'] = data['Job Posting Date'].dt.to_period('Q').astype(str)

    # Calculate Average Salary for each jon title
    data['Average Salary (K)'] = (data['Min Salary (K)'] + data['Max Salary (K)']) / 2

    return data

def analyse_industry_distribution(data):
    # Group the data by 'Broader Category' to get job distribution
    industry_distribution = data['Broader Category'].value_counts()
    # industry_distribution_dict = industry_distribution.to_dict()
    total_jobs = len(data)
    
    return industry_distribution, total_jobs

# ----------------------Start of Bubble Chart ------------------------------
'''
    Author: Sabihah Amirudeen
    This is a bubble chart showing the various job titles'distributions as well as to find the counts of the job titles.
    Bigger the bubble size, higher the count of the job title.
    Data columns such as Broader Catergory, Job title were being used
'''
def create_job_title_bubble_chart(data, industry_name_orig, json_file="analysis/job_title_bubble_chart.json"):

    # -- ANALYSIS -- 
    # Filter data for the selected 'Broader Category'
    industry_data = data[data['Broader Category'] == industry_name_orig]

    # Count the frequency of each job title in the selected industry
    job_title_counts = industry_data['Job Title'].value_counts().reset_index()
    job_title_counts.columns = ['Job Title', 'Job Count']

    job_title_counts = job_title_counts[job_title_counts['Job Count'] > 10]

    # Create a DataFrame for the bubble chart
    job_title_df = pd.DataFrame({
        'Job Title': job_title_counts['Job Title'],
        'Bubble Size': job_title_counts['Job Count'] * 2,  # Increase bubble size proportional to the frequency
        'x': np.random.rand(len(job_title_counts)) * 100,  # Spread out x values more widely
        'y': np.random.rand(len(job_title_counts)) * 100   # Spread out y values more widely
    })
    
    # -- VISUALISATION -- Create a bubble chart 
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
                      height=700,  # Adjusting the height to give more room for the bubbles
                      margin=dict(l=20, r=20, t=40, b=80),
                      clickmode='event+select')  # Enable click events

    # Convert the chart to HTML
    html_code = fig.to_html(full_html=False)

    # Save the chart to a JSON file
    json_dict = {}
    json_dict[industry_name_orig] = html_code

    with open(json_file, "w") as file:
        json.dump(json_dict, file)

    return html_code

#  ------------ Start of Salary Variation Boxplot  -------------------
''' 
Author: Sabihah Amirudeen
Salary variation chart is a box plot that show the median, mean salaries of jobs using 
data columns such as Broader Catergory, Job title, Average Salary (K).

'''

def create_salary_variation_chart(data, industry_name_orig):

    #  -- ANALYSIS --
    # Filter data for the selected industry
    industry_data = data[data['Broader Category'] == industry_name_orig]

    # Get all unique job titles
    job_titles = industry_data['Job Title'].unique()

    # -- VISUALISAITON -- Create the box plot
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

#  ------------ Start of Salary Trend Line Graph  -------------------
'''
Author: Sabihah Amirudeen
Salary trend graph is a line chart that shows the avergae salary of the all the instrances of a unique job title over the quarter years
Data columns used are Broader Category, Job Title, Year-Quarter and Average Salary (K)
'''

def create_salary_trend_chart(data, industry_name_orig):
      # -- ANALYSIS --
    # Filter data for the selected industry
    industry_data = data[data['Broader Category'] == industry_name_orig]

    # Group by Job Title and Year-Quarter, then calculate average salary
    salary_trend = industry_data.groupby(['Job Title', 'Year-Quarter'])['Average Salary (K)'].mean().reset_index()

    # Separate 'Year-Quarter' into 'Year' and 'Quarter' for proper sorting
    salary_trend['Year'] = salary_trend['Year-Quarter'].str[:4].astype(int)
    salary_trend['Quarter'] = salary_trend['Year-Quarter'].str[-1].astype(int)

    # Sort the data by 'Year' and 'Quarter'
    salary_trend = salary_trend.sort_values(by=['Year', 'Quarter'])

    # -- VISUALISATION --
    fig = go.Figure()

    job_titles = salary_trend['Job Title'].unique()
    colors = px.colors.qualitative.Plotly

    for i, job_title in enumerate(job_titles):
        job_data = salary_trend[salary_trend['Job Title'] == job_title]
        color = colors[i % len(colors)]  # Use a consistent color for both lines

        # Add actual salary line
        fig.add_trace(go.Scattergl(
            x=job_data['Year-Quarter'],
            y=job_data['Average Salary (K)'],
            mode='lines+markers',
            name=f'{job_title} Salary',
            line=dict(color=color, width=2),
            showlegend=True,
            visible='legendonly'
        ))

        # Calculate and add the trendline
        numeric_quarter = job_data['Year'] * 10 + job_data['Quarter']

        # Suppress the RankWarning
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=np.RankWarning)  # Ignore RankWarnings
            z = np.polyfit(numeric_quarter, job_data['Average Salary (K)'], 1)
            p = np.poly1d(z)

        fig.add_trace(go.Scattergl(
            x=job_data['Year-Quarter'],
            y=p(numeric_quarter),
            mode='lines',
            name=f'{job_title} Trendline',
            line=dict(dash='dash', color=color, width=2),  # Same color but dashed for the trendline
            showlegend=True,
            visible='legendonly'  # Initially hidden
        ))

    # Sort 'Year-Quarter' for fixed and evenly spaced x-axis
    sorted_quarters = salary_trend['Year-Quarter'].unique()

    # Update layout
    fig.update_layout(
        title=f'Average Salary Trends by Job Title in {industry_name_orig} (Quarterly)',
        xaxis_title='Quarter Year',
        yaxis_title='Average Salary (K)',
        height=600,
        margin=dict(l=20, r=20, t=40, b=80),
        xaxis=dict(
            tickmode='array',
            tickvals=sorted_quarters,
            ticktext=sorted_quarters,
            type='category',
            dtick=1,
            tickangle=45,
            range=[-0.5, len(sorted_quarters) + 0.5],
        ),
        yaxis=dict(showgrid=True),
        template='plotly_white',
        plot_bgcolor='rgba(223, 232, 243, 1)',
        paper_bgcolor='rgba(223, 232, 243, 1)',
        legend=dict(
            bgcolor='rgba(255, 255, 255, 0.5)',
            x=1.2,
            y=1,
            xanchor='left',
            yanchor='top',
            orientation="v",
            font=dict(size=10),
            itemclick='toggle',
            itemdoubleclick='toggleothers',
            itemwidth=30,
            title_text='Legend',
            traceorder="normal"
        )
    )

    # Convert the figure to HTML
    html_code = fig.to_html(full_html=False)
    return html_code

#  ------------ Start of Salary Growth Line Graph  -------------------
'''
Author: Sabihah Amirudeen
Salary Growth Graph shows the prediction trend of the job title's salary for the next 5 years.
Data columns used are Braoder Category, Job title, Job Minimum Experience and Average Salary (K).
'''

def create_salary_growth_chart(data, industry_name_orig):

    # -- ANALYSIS --
    # Filter data for the selected industry
    industry_data = data[data['Broader Category'] == industry_name_orig]

    # Group data by both Job Title and Job Minimum Experience and calculate the average salary
    experience_salary = industry_data.groupby(['Job Title', 'Job Minimum Experience'])['Average Salary (K)'].mean().reset_index()

    # Filter out job titles that have only one entry
    job_title_counts = experience_salary.groupby('Job Title').size().reset_index(name='counts')
    job_titles_with_more_than_one = job_title_counts[job_title_counts['counts'] > 1]['Job Title']

    # Filter the data to include only those job titles
    experience_salary_filtered = experience_salary[experience_salary['Job Title'].isin(job_titles_with_more_than_one)]

    # Add anomaly detection using Z-score
    def remove_anomalies(df):
        df['z_score'] = stats.zscore(df['Average Salary (K)'])
        # Filter out anomalies (Z-score greater than 3)
        filtered_df = df[df['z_score'].abs() <= 2]
        return filtered_df
    
    experience_salary_filtered = experience_salary_filtered.groupby('Job Title').apply(remove_anomalies).reset_index(drop=True)

    # Sort job titles by maximum salary and include all job titles that meet the criteria
    job_titles_sorted = experience_salary_filtered.groupby('Job Title')['Average Salary (K)'].max().sort_values(ascending=False).index

    # -- VISUALISATION -- Create a line chart for Salary Growth by Experience for each job title
    fig = go.Figure()

    # Define some colors for consistency
    colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A']

    for i, job_title in enumerate(job_titles_sorted):
        job_data = experience_salary_filtered[experience_salary_filtered['Job Title'] == job_title]
        color = colors[i % len(colors)]  # Color for both growth and prediction lines

        # Add the actual salary line for the job title
        fig.add_trace(go.Scattergl(
            x=job_data['Job Minimum Experience'],
            y=job_data['Average Salary (K)'],
            mode='lines+markers',
            name=f'{job_title} Salary Growth',
            line=dict(color=color, width=2),
            showlegend=True,
            visible=True if i < 5 else 'legendonly'  # Show the first 5 job titles, hide the rest in the legend
        ))

        # Salary prediction for the next 5 years
        X = np.array(job_data['Job Minimum Experience']).reshape(-1, 1)
        y = job_data['Average Salary (K)']

        # Train the model and make predictions
        model = LinearRegression().fit(X, y)
        max_experience = job_data['Job Minimum Experience'].max()
        future_experience = np.array(range(int(max_experience), int(max_experience) + 6)).reshape(-1, 1)
        predicted_salaries = model.predict(future_experience)

        # Add the predicted salary line (dashed) for the next 5 years
        fig.add_trace(go.Scattergl(
            x=future_experience.flatten(),
            y=predicted_salaries,
            mode='lines',
            name=f'{job_title} Salary Prediction (Next 5 Years)',
            line=dict(dash='dash', color=color, width=2),
            showlegend=True,
            visible=True if i < 5 else 'legendonly'  # Show the first 5 job titles, hide the rest in the legend
        ))

    # Determine the min and max experience for the x-axis range
    min_experience = experience_salary_filtered['Job Minimum Experience'].min()
    max_experience += 5  # Extend by 5 years to cover predictions

    # Update layout with fixed range
    fig.update_layout(
        title='Salary Growth by Experience and Prediction (Next 5 Years)',
        xaxis_title='Years of Experience',
        yaxis_title='Average Salary (K)',
        height=600,
        margin=dict(l=20, r=20, t=40, b=80),
        xaxis=dict(
            range=[min_experience, max_experience],  # Use min and max experience for x-axis range
            tickmode='linear',
            dtick=1  # Interval between ticks set to 1 year
        ),
        yaxis=dict(showgrid=True),
        template='plotly_white',
        plot_bgcolor='rgba(223, 232, 243, 1)',  # Light blue background for plot area
        paper_bgcolor='rgba(223, 232, 243, 1)',  # White background for surrounding area to create the border
        legend=dict(
            bgcolor='rgba(255, 255, 255, 0.5)',  # Transparent white legend background
            xanchor="left",  # Position the legend to the right
            x=1.02,  # Shift the legend horizontally to the right outside the plot
            y=1,  # Position the legend at the top
        )
    )

    # Convert the figure to HTML and return
    html_code = fig.to_html(full_html=False)
    return html_code
# ---------------------------------------------------------------------------



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

def skill_in_demand(job_role_df):
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

    # Add traces for each year, only the first one will be visible initially
    for i, year in enumerate(job_df["year"].unique()):
        year_df = job_df[job_df["year"] == year]
        fig.add_trace(go.Pie(
            labels=year_df["skill"], 
            values=year_df["percent"], 
            name=year, 
            visible=(i == 0),
            textinfo='label+percent',  # Show skill label and percentage in the pie sections
            textposition='inside',  # Position text inside
            insidetextorientation='horizontal',  # Align text horizontally
            textfont_size=10  # Adjust font size as needed
        ))

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
        ],
        width=1000,  # Adjust width
        height=800  # Adjust height
    )
    return fig.to_html()
