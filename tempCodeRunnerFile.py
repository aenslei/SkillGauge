@app.route('/industry_details', methods=['POST'])
def industry_details():
    industry_name = request.form.get('industry_name')
    print(f"Received industry_name: {industry_name}")

    industry = next((ind for ind in industry_list if ind.title == industry_name), None)
    data = load_data(file_path)
    app.logger.debug(f"Column names in the dataset: {data.columns}")
   

    os.makedirs('static/charts', exist_ok=True)

    # Generate the bubble chart for job titles in the selected industry (Broader Category)
    output_file = f'static/charts/{industry_name}_job_titles_bubble_chart.html'
    create_job_title_bubble_chart(data, industry_name, output_file) # Call the bubble chart function


    # Generate the salary variation bar chart for the selected industry
    output_file_salary = f'static/charts/{industry_name}_salary_variation.html'
    create_salary_variation_chart(data, industry_name, output_file_salary)  # Call the salary chart function



        #industry_data_path = "data/V1 group"+ industry_id +".csv"
    """ once data is in can uncomment
    with open("data/V1 group0.csv") as datafile:
    df = pd.read_csv(datafile, index_col=False)

    job_trend_code = industry_job_trend(df)

    """


    other_industries = [ind for ind in industry_list if ind.title != industry_name][:4]  # Limit to 4 buttons

    return render_template('industry_details.html',  
                           industry=industry, 
                           other_industries=other_industries, 
                           job_trend_fig=None,
                           job_title_chart=f'charts/{industry_name}_job_titles_bubble_chart.html',
                           salary_chart=f'charts/{industry_name}_salary_variation.html')

