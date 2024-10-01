import struct

import pandas as pd
import plotly.graph_objects as go
import ast
import plotly.express as px


# ========================================    Industry Section      ========================================================

def industry_job_trend(df):

    # change date to pd datetime format
    df['Job Posting Date'] = pd.to_datetime(df['Job Posting Date'], format="%Y-%m-%d")

    # find top 5 job
    top_5_job = df["Job Title"].value_counts()

    top_5_jobs = top_5_job.head(5).index.tolist()
    # filter out top 5 job to display
    df = df[df['Job Title'].isin(top_5_jobs)]

    # set date to period and sort by quarter
    df["Quarter"] = df["Job Posting Date"].dt.to_period("Q")


    df3 = df.groupby(["Job Title", "Quarter"]).size().to_frame("Count of job per quarter").reset_index()
    df3 = df3.sort_values(by="Quarter")


    df3 = df3.pivot_table(index="Quarter", columns="Job Title", values="Count of job per quarter", fill_value=0)
    df3.reset_index(inplace=True)

    # add a line for every job role
    fig = go.Figure()
    for job in df3.columns[1:]:
        fig.add_trace(go.Scatter(
            x=df3['Quarter'].astype(str),
            y=df3[job],
            mode='lines+markers',
            name=job
        ))


    fig.update_layout(
        title = "Industry Job Trends",
        xaxis_title="Period",
        yaxis_title="No. of Job",


    )


    html_code = fig.to_html(full_html=False)
    #fig.write_html("fig.html", full_html= False, auto_open=True)
    return html_code





def filter_skills(skills_list):

    skills_list = list(skills_list)
    new_skill_list = []
    for skill in skills_list:
        if len(skill) > 1:
            new_skill_list.append(skill)

    return new_skill_list


def industry_general_skills(df, selection , industry_name):

    # apply cause input value to be str ast literal eval to change it to list type before apply again to clean out single letter skills
    df["skills"] = df["skills"].apply(ast.literal_eval)
    df["skills"] = df["skills"].apply(filter_skills)


    all_skills = df['skills'].explode()
    total_skill_count = all_skills.value_counts()


    if selection == 1:

        with open("skill_count.txt", "w") as file:
            file.write(str(total_skill_count))

    if selection == 2:
        path = "analysis/industry_skills.json"

        #print(total_skill_count)
        top20_skill_json = total_skill_count.head(20)
        result = {
            'title': industry_name,
            'data': top20_skill_json.to_dict()

        }
        pd.Series(result).to_json(path, indent=4)


def pull_industry_skills(industry_skills):
    skill_list = []
    data = industry_skills["data"]

    # print(data)
    for k, v in data.items():
        skill_list.append(k)

    return skill_list




def industry_hiring_trend(df):

    # setting type to date time format
    df['Job Posting Date'] = pd.to_datetime(df['Job Posting Date'], format="%Y-%m-%d")

    current_year = pd.Timestamp.now().year
    df["Job Posting Date"] = df["Job Posting Date"].apply(lambda x: x.replace(year=current_year))

    # extract month from data
    df["Month"] = df["Job Posting Date"].dt.to_period("M")


    # group by month and get count of drop
    df3 = df.groupby(["Month"]).size().to_frame("Count of job per month").reset_index()

    month_names = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]

    fig = px.area(df3, x=month_names, y="Count of job per month")
    fig.update_yaxes(range=[df3["Count of job per month"].min() * 0.75, df3["Count of job per month"].max() + 25])

    fig.update_layout(
        title = "Industry Hiring Trends",
        xaxis_title="Period",
        yaxis_title="No. of Job per Month",
    )

    html_code = fig.to_html(full_html=False)

    return html_code




# ============================    Job Role Section      ===============================================================

# get top 10 job roles skills and save to an analysis file
def skill_match_analysis(df, industry_name):


    # get list of unique job title
    unique_job_list = df["Job Title"].unique()
    # set skill list value to list type
    try:
        df["skills"] = df["skills"].apply(ast.literal_eval)
    except:
        print("alr converted")

    json_data = {}
    for job in unique_job_list:

        filtered_df = df[df["Job Title"] == job]
        job_skill_series = filtered_df["skills"].explode().value_counts()
        # get top 10 skill per job role
        json_dict = { job : job_skill_series.head(10).to_dict()}
        json_data.update(json_dict)
    #print(json_data)
    file_path = "analysis/job_role_skill_" + industry_name + ".json"
    pd.Series(json_data).to_json(file_path, indent=4)





def match_user_to_job_role(job_role_skills_series, user_skill_list):

    grouped = job_role_skills_series.groupby(level=0)
    # convert series to dict key value and skills to list
    job_role_skill_dict = {key: group.index.get_level_values(1).tolist() for key, group in grouped}

    match_dict = {}
    user_skill_list = list(map(str.upper, user_skill_list))
    print(user_skill_list)
    for key , value in job_role_skill_dict.items():
        # find matching percent
        value = list(map(str.upper, value))

        matched_skill = set(value) & set(user_skill_list)

        if matched_skill:
            # percentage calculated by length of match skills over len of job role skills * 100
            percentage = (len(matched_skill) / len(set(value))) * 100

            match_dict[key] = round(percentage)

    return match_dict, job_role_skill_dict



