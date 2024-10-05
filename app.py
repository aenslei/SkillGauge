
from flask import Flask, render_template, request, redirect, url_for,session
from Analysis_Visualisation import load_data, analyse_industry_distribution, create_job_title_bubble_chart,create_salary_variation_chart, skills_comparison,generate_wordcloud,create_salary_growth_chart,create_salary_trend_chart,skill_in_demand
import resume_skills_extractor
import os
import pandas as pd
import course_url_crawler
from data_analysis import industry_job_trend , industry_general_skills, pull_industry_skills , industry_hiring_trend , skill_match_analysis , match_user_to_job_role, filter_df_by_job_role,industry_job,pull_in_job_trend,  pull_in_hiring_trend , get_job_detail_url
import time
import threading
import copy

app = Flask(__name__)
app.secret_key = os.urandom(24)

UPLOAD_FOLDER = 'uploads'  # Define a folder to save uploaded files
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

file_path = r'Datasets\\sg_job_data-Cleaned-With Industry1.csv'

class Industry:
    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return f"Industry(title='{self.title}')"

    def __str__(self):
        return self.title

class JobRole:
    def __init__(self, title, skill, match_percent = 0):

        self.title = title
        self.skill = skill
        self.match_percent = match_percent

@app.route('/')
def Home():


    start_time = time.time()

    data = load_data(file_path)  # Load the data
    data1 = copy.deepcopy(data)
    data2 = copy.deepcopy(data)
    data3 = copy.deepcopy(data)
    
    # Start the jobs in separate threads
    thread1 = threading.Thread(target=industry_job, args=(data3,))
    thread2 = threading.Thread(target=industry_job_trend, args=(data1,))
    
    thread3 = threading.Thread(target=industry_hiring_trend, args=(data2,))
    thread4 = threading.Thread(target=industry_general_skills, args=(data,))
    
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    
    end_time  = time.time()
    
    print(f"Execution Time Home: {end_time - start_time} seconds")


    return render_template('home.html')



industry_list = []
@app.route('/industries')
def Industries():
    # Load CSV file
    data = load_data(file_path)
    industry_list.clear()

    # Count occurrences of each industry (Broader Category)
    industry_counts = data['Broader Category'].value_counts().reset_index()
    industry_counts.columns = ['Broader Category', 'count']  # Rename columns to 'Broader Category' and 'count'

    # Get all industries (sorted alphabetically)
    all_industries = industry_counts.sort_values(by='Broader Category').reset_index(drop=True)

    # Analyze the industry distribution
    industry_distribution, total_jobs = analyse_industry_distribution(data)

    # Create industry list to pass to the template
    industry_list.clear()
    for idx, row in all_industries.iterrows():
        industry = Industry(title=row['Broader Category'])
        industry_list.append(industry)

    return render_template('industries.html', all_industries=industry_list, total_jobs=total_jobs, 
                           industry_distribution=industry_distribution)

def load_data(file_path):
    data = pd.read_csv(file_path)
    return data

def analyse_industry_distribution(data):
    # Group data by 'Broader Category'
    industry_distribution = data['Broader Category'].value_counts()
    total_jobs = len(data)
    return industry_distribution, total_jobs


# POST request
@app.route('/industry_details', methods=['POST'])
def industry_details():
    start_time = time.time()
    industry_name_orig = request.form.get('industry_name')
    session["industry"] = industry_name_orig

    industry = next((ind for ind in industry_list if ind.title == industry_name_orig), None)
    data = load_data(file_path)

    #  --- Calling of Analysis and Visualisation Functions ---
    job_title_chart = create_job_title_bubble_chart(data, industry_name_orig) # Call the Bubble chart function
    salary_chart = create_salary_variation_chart(data, industry_name_orig)  # Call the Salary Box chart function
    salary_trend_chart = create_salary_trend_chart(data, industry_name_orig)  # Call the Salary trend Line chart function
    salary_growth_chart = create_salary_growth_chart(data, industry_name_orig) # Call the the salary growth chart
    # --------------------------------------------------------

    # find industry general skills
    industry_name = industry_name_orig.replace(" ", "_")
    industry_path = "Datasets/(Final)_past_" + industry_name + ".csv"

    with open(industry_path , encoding='utf-8') as csvfile:
        df = pd.read_csv(csvfile, index_col=False)



    # analysis for job role skills
    skill_match_analysis(df,industry_name)





    skill_list = pull_industry_skills( industry_name)


    # end of find industry general skills

    # start of job trends

    job_trend_code = pull_in_job_trend(industry_name)
    # end of job trends

    # start of hiring trend code
    hiring_trend_code = pull_in_hiring_trend(industry_name)




    other_industries = [ind.title for ind in industry_list if ind.title != industry_name_orig][:4]  # Limit to 4 buttons
    other_industries = other_industries[:4] 
    
    wordCloud = generate_wordcloud(industry_name)

    end_time  = time.time()
    print(f"Execution Time: {end_time - start_time} seconds")

    return render_template('industry_details.html',  
                           industry=industry, 
                           other_industries=other_industries, 
                           job_trend_fig=job_trend_code,

                           skill_list = skill_list,
                           wordCloud = wordCloud,
                           hiring_trend_fig = hiring_trend_code,

                           salary_growth_chart = salary_growth_chart,
                           job_title_chart=job_title_chart,
                           salary_chart=salary_chart,
                           salary_trend_chart = salary_trend_chart)    




@app.route('/job_roles')
def Job_roles():

    if 'userSkills' in session:
        userSkills = session['userSkills']
    else:
        userSkills = []

    if 'industry' in session:
        industry_name = session["industry"]
        industry_name = industry_name.replace(" ", "_")
        path = "analysis/job_role_skill_"+industry_name+".json"

    else:
        print("no industry")
        return redirect(url_for("Industries"))


    with open(path) as file:
        job_role_skill_df = pd.read_json(file, orient="index")
        job_role_skills_series = job_role_skill_df.stack()

    match_dict , job_role_skill_dict = match_user_to_job_role(job_role_skills_series, userSkills)

    job_role_list = []
    print(job_role_skill_dict)
    # if not match job take the first 6 job roles
    if len(match_dict) == 0:
        no_match_list  = list(job_role_skill_dict.items())[:6]

        for job in no_match_list:
            print(job)

            job_object = JobRole(job[0], job[1],0)
            job_role_list.append(job_object)

    else:

        for job, percent in match_dict.items():
            skill_list = job_role_skill_dict[job]
            job_object = JobRole(job, skill_list,int(percent))
            job_role_list.append(job_object)


    # Sort by best matching percentage
    job_role_list.sort(key=lambda x: x.match_percent, reverse=True)
    return render_template('job_roles.html', job_role=job_role_list)

@app.route("/job_roles/<job_title>")
def expanded_job_roles(job_title):

    if 'userSkills' in session:
        userSkills = session['userSkills'] 
    else:
        userSkills = []

    if 'industry' in session:
        industry_name = session["industry"]
        industry_name = industry_name.replace(" ", "_")

    else:
        return redirect(url_for("Industries"))



    with open("Datasets/(Final)_past_"+ industry_name +".csv" , encoding="utf-8") as file:
        df = pd.read_csv(file, index_col=False)
        job_df = filter_df_by_job_role(df, job_title)


    skillComparisonChart,skillsLacking , match_skills = skills_comparison(userSkills,job_title, industry_name)
    total_skill = skillsLacking + match_skills
    job = JobRole(job_title, total_skill)

    #jobMap = GeographicalMap(industry_name)
    skillsDemandChart = skill_in_demand(job_df)
    urlCourses = course_url_crawler.search_courses(skillsLacking)

    job_detail_data = get_job_detail_url(job_df)

    return render_template("expanded_job_roles.html" ,
                           job_title = job_title,
                           job_role = job,
                           courses = urlCourses,
                           chart=skillComparisonChart,
                            skillsDemand_Chart = skillsDemandChart,
                           job_detail_data = job_detail_data)

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
    resume_skills_extractor.extract_text_from_pdf(pdf_path)
    skills_found = resume_skills_extractor.outputSkillsExtracted(5)

    return render_template('edit_resume.html', skills=skills_found)

@app.route('/add_skills', methods=['POST'])
def add_skills():
    # Get the list of skills from the form
    skills = request.form.getlist('skills')
    return render_template('edit_resume.html', skills=skills)

@app.route('/update_skills', methods=['POST'])
def update_skills():
    session['userSkills'] = request.form.getlist('skills')
    
    # Remove all resumes once skills are submitted
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
    return redirect(url_for('Job_roles'))

if __name__ == '__main__':
    app.run(debug=True)
