import pandas as pd
import plotly.graph_objects as go
import ast

def industry_job_trend(df):

    # change date to pd datetime format
    df['Job Posting Date'] = pd.to_datetime(df['Job Posting Date'], format="%d/%m/%Y")

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

        print(total_skill_count)
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




