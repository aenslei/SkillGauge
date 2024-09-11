from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def Home():
    return render_template('home.html')


@app.route('/industries')
def Industries():
    return render_template('industries.html')


@app.route('/job_roles')
def Job_roles():
    return render_template('job_roles.html')

if __name__ == '__main__':
    app.run(debug=True)