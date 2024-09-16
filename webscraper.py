import pandas as pd
import re
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, ElementClickInterceptedException, TimeoutException
import bs4 
import nltk
from nltk.tokenize import word_tokenize

'''
When webscraper is called by website [based on a user input signal], webscraper scrapes Websites based on:
1. Job Site (mycareersfuture)
2. Industry chosen by User (based on mycareerfuture's query list)

EG: Accounting -
https://www.mycareersfuture.gov.sg/job/accounting?employmentType=Full%20Time&sortBy=relevancy&page=0

IT - 
https://www.mycareersfuture.gov.sg/job/information-technology?employmentType=Full%20Time&sortBy=relevancy&page=0 

To move page, need to manipulate the last page query + 1

Workflow Structure:
1. Web Scrape (Based on user inputted industry)
---> Query to Manipulate: https://www.mycareersfuture.gov.sg/job/XXINDUSTRYNAMEXX?employmentType=Full%20Time&sortBy=relevancy&page=0
---> Dictionary key-values in industries.txt based on query 


2. Initially store in CSV (one line, one job listing - Columns: tbc)
3. Data Processing (Tokenization - Using Collocation Extraction for Double-Words if can) 
4. Data Filtering (Remove unneeded punctuation)
5. Data Cleaning (Finalise Job Tags based on Skill Words extracted from JDs - extra column on the right as Tags)
6. Store it another CSV for Data Analytics (or multiple CSVs, depending on what Analytics needs)
---> store link of jobs
'''

#--------------------INITIALIZATION--------------------

#Initialize Selenium WebDriver for Chrome 
driver = webdriver.Chrome()
# driver = webdriver.Chrome(executable_path = '.\chromedriver-win64\chromedriver.exe')

#Initialize industry chosen by user - Taken from Website (import)
# from learn import industry
industry_input = "information-technology" #You can try changing this if you want.

#----Building the final query to be sent through the web driver----

#Initialize Job Website to Scrape
website = "https://www.mycareersfuture.gov.sg"

#Initialize Query String
query_initial = "https://www.mycareersfuture.gov.sg/job/"

#--------------------MAIN--------------------

#1. Take in user input for industry and create query_final based on industry input
employment_type = "?employmentType=Full%20Time"
sort_by = "&sortBy=relevancy&page="
page = 0
query_final = query_initial + industry_input + employment_type + sort_by + str(page)
print(query_final)

#2. Fetch page with driver and add wait time
driver.get(query_final)

# Explicit wait until the card container is found before continuing
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='card-list']"))
)

#3. Count how many job postings there are in card-list div class PER SEARCH PAGE
#*****Note: After this whole thing is done, wrap around a for page in range(page_count) loops

job_count = 0
job_num = 0
page_count = 2 #Please by wary of the page count. For this version, DO NOT CHANGE THIS!!!!!!!!

all_jobs = []

for page in range(page_count):
    # Update the query_final with the current page number
    query_final = query_initial + industry_input + employment_type + sort_by + str(page)
    print(f"Fetching page {page}: {query_final}")
    
    # Fetch page with driver and add wait time
    driver.get(query_final)
    
    # Explicit wait until the card container is found before continuing
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='card-list']"))
    )
    
    # Find the card-container that contains all the job posting divs
    try:
        card_container = driver.find_element(By.CSS_SELECTOR, "div[data-testid='card-list']")
        print("Card container found.")
    except NoSuchElementException:
        print("Card container not found.")
        continue
    
    # Loop to find all job cards with dynamic IDs
    while True:
        try:
            # Dynamically generate the ID for each job card and search within the container
            job_card_id = f"job-card-{job_num}"
            job_card = card_container.find_element(By.ID, job_card_id)
            
            # If found, increment the job count and move to the next job card
            job_count += 1
            print(f"Found job card with ID: {job_card_id}")
            
            job_num += 1  # Move to the next job-card-{num}
    
        except:
            # If no more job cards are found, break the loop
            print(f"Finished searching. Total job listings found: {job_count}")
            break
    
    # Using num of job postings, use for in range loop to iterate through every a-href link and extract all the job-related content
    for counter in range(0, job_count + 1):
        try:
            # Initiate variables that will hold all the information of each job postings
            job_url = job_title = job_location = job_employment_type = job_seniority = job_min_exp = job_industry = job_salary_range = job_desc = job_skills_needed = ""
            
            # Construct the job card ID based on the counter
            job_card_id = f"job-card-{counter}"
            print(f"Trying to find job card with ID: {job_card_id}")
            driver.implicitly_wait(5)
            
            # Retry mechanism for handling stale element reference
            retries = 3
            while retries > 0:
                try:
                    # Find the card container element
                    card_container = driver.find_element(By.CSS_SELECTOR, "div[data-testid='card-list']")
                    # Find the job card element within the card container
                    job_card = card_container.find_element(By.ID, job_card_id)
                    print(f"Job Card {counter} found. Clicking on it.")
                    
                    try:
                        # Attempt to click the job card
                        job_card.click()
                    except ElementClickInterceptedException:
                        # If click is intercepted, use JavaScript to click the element
                        print(f"ElementClickInterceptedException encountered for job card {counter}. Using JavaScript click.")
                        driver.execute_script("arguments[0].click();", job_card)
                
                    # Entering into the job posting page...
    
                    print(f"Currently Searching through: Job-Card-{counter}")
                    
                    # Explicit wait for job title
                    WebDriverWait(driver, 7).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "h1[data-testid='job-details-info-job-title']"))
                    )
    
                    # Explicit wait for job description
                    WebDriverWait(driver, 7).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='description-content']"))
                    )
    
                    # *****EXTRACT ALL THE JOB INFORMATION AND STORE INTO THE RELEVANT VARIABLES!!!!!!!******
                    # 1. Extract current Job URL and save it under the job_url variable
                    print(f"Job card {counter} link: {driver.current_url}")
                    job_url = driver.current_url
    
                    # 2. Extract Job Title and save it under job_title variable
                    try:
                        driver.implicitly_wait(7)
                        job_title = driver.find_element(By.CSS_SELECTOR, "h1[data-testid='job-details-info-job-title']").text
                        print(f"Job Title: {job_title}")
                    except NoSuchElementException:
                        print(f"Job Title not found for job card {counter}.")
    
                    # 3. Extract all the data under the section (Location,EmpType,Seniority,MinExp,Industry)
    
                    # Location
                    try:
                        driver.implicitly_wait(7)
                        job_location = driver.find_element(By.CSS_SELECTOR, "a[data-testid='job-details-info-location-map']").text
                        print(f"Job Location: {job_location}")
                    except NoSuchElementException:
                        print(f"Job Location not found for job card {counter}.")
    
                    # Employment Type
                    try:
                        driver.implicitly_wait(7)
                        job_employment_type = driver.find_element(By.CSS_SELECTOR, "p[data-testid='job-details-info-employment-type']").text
                        print(f"Job Employment Type: {job_employment_type}")
                    except NoSuchElementException:
                        print(f"Job Employment Type not found for job card {counter}.")
    
                    # Seniority
                    try:
                        driver.implicitly_wait(7)
                        job_seniority = driver.find_element(By.CSS_SELECTOR, "p[data-testid='job-details-info-seniority']").text
                        print(f"Job Seniority: {job_seniority}")
                    except NoSuchElementException:
                        print(f"Job Seniority not found for job card {counter}.")
    
                    # Min Exp
                    try:
                        driver.implicitly_wait(7)
                        job_min_exp = driver.find_element(By.CSS_SELECTOR, "p[data-testid='job-details-info-min-experience']").text
                        print(f"Job Minimum Experience: {job_min_exp}")
                    except NoSuchElementException:
                        print(f"Job Minimum Experience not found for job card {counter}.")
    
                    # Industry
                    try:
                        driver.implicitly_wait(7)
                        job_industry = driver.find_element(By.CSS_SELECTOR, "p[data-testid='job-details-info-job-categories']").text
                        print(f"Job Industry: {job_industry}")
                    except NoSuchElementException:
                        print(f"Job Industry not found for job card {counter}.")
    
                    # 4. Extract Job Salary Range
                    try:
                        driver.implicitly_wait(7)
                        job_salary_range = driver.find_element(By.CSS_SELECTOR, "span[data-testid='salary-range']").text
                        print(f"Job Salary Range: {job_salary_range}")
                    except NoSuchElementException:
                        print(f"Job Salary Range not found for job card {counter}.")
    
                    # 5. Extract Job Description
                    try:
                        driver.implicitly_wait(7)
                        job_desc = driver.find_element(By.CSS_SELECTOR, "div[data-testid='description-content']").text
                        print(f"Job Description: {job_desc}")
                    except NoSuchElementException:
                        print(f"Job Description not found for job card {counter}.")
    
                    # 6. Extract Job Skills Needed
                    try:
                        driver.implicitly_wait(7)
                        job_skills_needed = driver.find_element(By.CSS_SELECTOR, "div[data-testid='multi-pill-button']").text
                        print(f"Job Skills Needed: {job_skills_needed}")
                    except NoSuchElementException:
                        print(f"Job Skills Needed not found for job card {counter}.")
    
                    # Store the extracted data into a dictionary
                    job_data = {
                        "Job URL": job_url,
                        "Job Title": job_title,
                        "Job Location": job_location,
                        "Job Employment Type": job_employment_type,
                        "Job Seniority": job_seniority,
                        "Job Minimum Experience": job_min_exp,
                        "Job Industry": job_industry,
                        "Job Salary Range": job_salary_range,
                        "Job Description": job_desc,
                        "Job Skills Needed": job_skills_needed
                    }
    
                    # Append the job data to the list
                    all_jobs.append(job_data)
    
                    # Wait, then change back to the query search page
                    driver.implicitly_wait(3)
                    driver.get(query_final)
                    
                    # Explicit wait until the card container is found before continuing
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='card-list']"))
                    )
    
                    break  # Exit the retry loop if successful
    
                except StaleElementReferenceException:
                    # Handle stale element reference exception by retrying
                    print(f"StaleElementReferenceException encountered for job card {counter}. Retrying...")
                    retries -= 1
                    if retries == 0:
                        # If retries are exhausted, raise the exception
                        print(f"Failed to interact with job card {counter} after multiple retries.")
                        # Change back to the query search page
                        driver.get(query_final)
    
                        # Explicit wait until the card container is found before continuing
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='card-list']"))
                        )
                        raise
                    else:
                        # Reload the search query page before retrying
                        driver.get(query_final)
    
                        # Explicit wait until the card container is found before continuing
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='card-list']"))
                        )
    
                except NoSuchElementException:
                    # Handle case where job card is not found
                    print(f"Job card {counter} not found. Skipping to next.")
                    break  # Exit the retry loop if the element is not found
    
        except Exception as e:
            # Handle any other exceptions and continue with the next job card
            print(f"Job card {counter} not found. Exception: {e}")
    
            # Change back to the query search page
            driver.get(query_final)

            # Explicit wait until the card container is found before continuing
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='card-list']"))
            )

#5 Store all this data in a categorized CSV

# Convert the list of dictionaries to a DataFrame
df = pd.DataFrame(all_jobs)

# Save the DataFrame to a CSV file
df.to_csv('job_listings.csv', index=False)
