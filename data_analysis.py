import pandas as pd
import plotly.graph_objects as go


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






