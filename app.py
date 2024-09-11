from flask import Flask, render_template

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)