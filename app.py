from flask import Flask, render_template, request, redirect, url_for
import os
import resume_skills_extractor

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'  # Define a folder to save uploaded files
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class JobRole:
    def __init__(self, title , skill , match_percent):
        self.title = title
        self.skill = skill
        self.match_percent = match_percent

@app.route('/')
def Home():
    return render_template('home.html')


@app.route('/industries')
def Industries():
    return render_template('industries.html')


@app.route('/job_roles')
def Job_roles():
    # placeholder data
    j1 = JobRole("data engineer" , ["Python programming","Data analysis","Machine learning","Web development"],90 )
    j2 = JobRole("programmer", ["Python programming", "Debugging","Object-oriented programming","Algorithms and data structures", "Web development"], 90)
    j3 = JobRole("cloud engineer", ["Python programming", "Data analysis", "Machine learning", "Web development"], 75)
    j4 = JobRole("Network engineer", ["Python programming", "Data analysis", "Machine learning", "Web development"], 45)
    j5 = JobRole("data engineer", ["Python programming", "Data analysis", "Machine learning", "Web development"], 80)
    j6 = JobRole("data engineer", ["Python programming", "Data analysis", "Machine learning", "Web development"], 90)
    j7 = JobRole("data engineer", ["Python programming", "Data analysis", "Machine learning", "Web development"], 90)
    job_role_list = [j1,j2, j3,j4,j5,j6,j7]



    return render_template('job_roles.html' , job_role = job_role_list)

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
    
    # Now you can call your test4.py function with pdf_path
    # For example:
    skills_found = resume_skills_extractor.RunTest(pdf_path)
    # Convert the skills list into a string for the URL
    skills_str = ','.join(skills_found)

    return redirect(url_for('Edit_resume'), skills = skills_str)  # Redirect to a success page or back to home

@app.route('/EditResume')
def Edit_resume():
    # Get skills from the query parameter and split the string back into a list
    skills_str = request.args.get('skills', '')  # Default to an empty string if no skills are passed
    skills = skills_str.split(',') if skills_str else []  # Convert back to a list
    return render_template('edit_resume.html', skills=skills)

if __name__ == '__main__':
    app.run(debug=True)