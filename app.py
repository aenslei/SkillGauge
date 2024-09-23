from flask import Flask, render_template, request, redirect, url_for
from Analysis_Visualisation import load_data, analyse_industry_distribution

import os
# import resume_skills_extractor

import pandas as pd
import course_url_crawler
from data_analysis import industry_job_trend , industry_general_skills, pull_industry_skills


app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'  # Define a folder to save uploaded files
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Path to dataset
file_path = r'Datasets\\Cleaned_Jobs_Dataset(FInal).csv'

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class Industry:
    def __init__(self,title):
        self.title = title

    def __repr__(self):
        return f"Industry(title='{self.title}')"

    def __str__(self):
        return self.title

class JobRole:
    def __init__(self, id, title , skill , match_percent):
        self.id = id
        self.title = title
        self.skill = skill
        self.match_percent = match_percent


@app.route('/')
def Home():
    data = load_data(file_path)  # Load the data

    return render_template('home.html')

industry_list = []
@app.route('/industries')
def Industries():    
    #load csv file:
    data = load_data(file_path)
    industry_list.clear()

    # Count occurrences of each industry
    industry_counts = data['Industry Name'].value_counts().reset_index()
    industry_counts.columns = ['Industry Name', 'count']  # Rename columns to 'Industry' and 'count'

    # Get all industries (sorted alphabetically)
    all_industries = industry_counts.sort_values(by='Industry Name').reset_index(drop=True)

    # Analyze the industry distribution
    industry_distribution, total_jobs = analyse_industry_distribution(data)

    # Create industry list to pass to the template
    industry_list.clear()
    for idx, row in all_industries.iterrows():
        industry = Industry(title=row['Industry Name'])
        industry_list.append(industry)

    return render_template('industries.html', all_industries=industry_list, total_jobs=total_jobs, 
                           industry_distribution=industry_distribution)

def load_data(file_path):
    data = pd.read_csv(file_path)
    return data

def analyse_industry_distribution(data):
    industry_distribution = data['Industry Name'].value_counts()
    total_jobs = len(data)

    return industry_distribution, total_jobs

# POST request
@app.route('/industry_details', methods=['POST'])
def industry_details():
    industry_name = request.form.get('industry_name')
    print(f"Received industry_name: {industry_name}")

    industry = next((ind for ind in industry_list if ind.title == industry_name), None)

    # print(f"Received industry: {industry_name}")



    # find industry general skills

    industry_path = "Datasets/(Final)_past_" + industry_name + ".csv"

    with open(industry_path) as csvfile:
        df = pd.read_csv(csvfile, index_col=False)

    industry_general_skills(df,2,industry_name)


    with open("analysis/industry_skills.json") as file:
        industry_skills_pd = pd.read_json(file)

    skill_list = pull_industry_skills(industry_skills_pd)


    # end of find industry general skills

    # start of job trends
    #industry_data_path = "data/V1 group"+ industry_id +".csv"
    with open(industry_path) as datafile:
        df = pd.read_csv(datafile, index_col=False)

    job_trend_code = industry_job_trend(df)

    # end of job trends

    other_industries = [ind for ind in industry_list if ind.title != industry_name][:4]  # Limit to 5 buttons
    
    
    return render_template('industry_details.html',  industry=industry, other_industries=other_industries,
                           job_trend_fig = job_trend_code, skill_list = skill_list)




@app.route('/job_roles')
def Job_roles():
    # placeholder data
    j1 = JobRole(1,"data engineer" , ["Python programming","Data analysis","Machine learning","Web development"],70 )
    j2 = JobRole(2,"programmer", ["Python programming", "Debugging","Object-oriented programming","Algorithms and data structures", "Web development"], 90)
    j3 = JobRole(3,"cloud engineer", ["Python programming", "Data analysis", "Machine learning", "Web development"], 50)
    j4 = JobRole(4,"Network engineer", ["Python programming", "Data analysis", "Machine learning", "Web development"], 49)
    j5 = JobRole(5,"data engineer", ["Python programming", "Data analysis", "Machine learning", "Web development"], 69)
    j6 = JobRole(6,"data engineer", ["Python programming", "Data analysis", "Machine learning", "Web development"], 90)
    #j7 = JobRole("data engineer", ["Python programming", "Data analysis", "Machine learning", "Web development"], 90)
    job_role_list = [j1,j2, j3,j4,j5,j6]
    # sort by best matching percent
    job_role_list.sort(key=lambda x:x.match_percent, reverse=True)

    return render_template('job_roles.html' , job_role = job_role_list)

@app.route("/job_roles/<job_title>")
def expanded_job_roles(job_title):
    j1 = JobRole("data engineer", ["Python programming", "Data analysis", "Machine learning", "Web development"], 70)

    skillsLacking = ['java', 'UI', 'python programming']
    urlCourses = course_url_crawler.search_courses(skillsLacking)

    return render_template("expanded_job_roles.html" , job_title = job_title , job_role = j1, courses = urlCourses)

@app.route('/resume')
def Resume():
    return render_template('resume.html')

@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return redirect(request.url)
    
    file = request.files['resume']
    
    if file.filename == '':
        return redirect(request.url)
    
    # Save the file
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(pdf_path)
    
    #get skills 
    skills_found = resume_skills_extractor.GatherSkills(pdf_path,"tech")

    return render_template('edit_resume.html', skills=skills_found)

@app.route('/add_skills', methods=['POST'])
def add_skills():
    # Get the list of skills from the form
    skills = request.form.getlist('skills')
    return render_template('edit_resume.html', skills=skills)

@app.route('/update_skills', methods=['POST'])
def update_skills():
    updated_skills = request.form.getlist('skills')
    #remove all resumes once skills is submitted
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
    return redirect(url_for('Job_roles', skills=updated_skills))

if __name__ == '__main__':
    app.run(debug=True)