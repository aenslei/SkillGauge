import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go

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

def skills_comparison(user_skills):
    # Define the fixed skills list
    skills = ["Python", "SQL", "PHP", "Graph QL", "AWS", "Jira"]

    # Calculate matched and missing skills
    matched_skills = [skill for skill in user_skills if skill in skills]
    missing_skills = [skill for skill in skills if skill not in user_skills]

    # Calculate percentages
    matched_percentage = (len(matched_skills) / len(skills)) * 100
    missing_percentage = (len(missing_skills) / len(skills)) * 100

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
    return fig.to_html()