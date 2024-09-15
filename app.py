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


class Industry:
    def __init__(self, id, title , img_url):
        self.id = id
        self.title = title
        self.img_url = img_url
@app.route('/')
def Home():
    return render_template('home.html')


# makes industry_list global to be accessed by industries.html and industry_details. html
id1 = Industry(1, "Technology", 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTIcaOM2XaTeH5vOikuxKHRQsG2PhgekdUrOQ&s')
id2 = Industry(2, "Healthcare", 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ8MYlim_ijBm8roz-lAl9oynaGbry7UzApPQ&s')
id3 = Industry(3, "Engineering", 'https://www.omazaki.co.id/system/uploads/2019/06/Engineering-1024x480.jpg')
id4 = Industry(4, "Manufacturing", 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSc01U4PoycmtCsXTk3zjHm07PZ_GXGt6o74A&s')
id5 = Industry(5, "Finance", 'https://www.wealthandfinance-news.com/wp-content/uploads/2021/07/Finance-technology.jpg')
id6 = Industry(6, "Hospitality", 'https://cdn.vysokeskoly.cz/czech-universities/uploads/2021/05/group-hotel-staffs-standing-kitchen.jpg')
industry_list = [id1, id2, id3, id4, id5, id6]

@app.route('/industries')
def Industries():                   
    return render_template('industries.html', industry=industry_list)


# POST request
@app.route('/industry_details', methods=['POST'])
def industry_details():
    industry_id = request.form.get('industry_id')
    industry = next((ind for ind in industry_list if ind.id == int(industry_id)), None)

    if industry is None:
        return "Industry not found", 404

    print(f"Received industry_id: {industry_id}")
    print(f"Received industry.title: {industry.title}")

    other_industries = [ind for ind in industry_list if ind.id != industry.id][:5]  # Limit to 5 buttons
    
    
    return render_template('industry_details.html', industry_id=industry_id, industry=industry, other_industries=other_industries)

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
    
    #get skills 
    skills_found = resume_skills_extractor.RunTest(pdf_path)

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