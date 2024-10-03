import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import random
from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent
import time
import threading
import os
import csv

'''
- Author: Ainsley Cabading
What's changed with Version 2?

1. Added parallel processing using ThreadPoolExecutor to be able to have up to X threads rotating across a queue of pages based on the page_count set Y.
2. Added dynamic user agents and random rate-limiting to the scraping functions to prevent the website from reaching the rate limit.
3. Added exponential backoff to manage retries in commmunicating with the web server, progressively increasing wait time between retries.
4. Made the Chromium drivers headless to reduce overhead.
5. Added time-keeping to roughly track how long it takes for the webscraper to run in full.
7. Did some housekeeping and documentation on my code as well as made some functions for re-used statements.

Current main() variables in this version you can change:
1. page_count - Number of pages to scrape
2. max_workers - Number of threads to run concurrently
3. industry_input - Industry to scrape job listings from (based on website input)

'''

#--------------------INITIALIZATION--------------------

# Initialize the UserAgent object
ua = UserAgent()

#--------------------FUNCTIONS--------------------
# Function to wait for an element to be present
def wait_for_element(driver, by, value, timeout=15):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))

# Function to initialize a new WebDriver instance with a random user-agent
def create_driver():
    options = Options()
    options.add_argument('--headless')  # Run Chromium in headless mode
    options.add_argument('--disable-gpu')  # Disable GPU acceleration
    options.add_argument('--no-sandbox')  # Bypass OS security model
    options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
    options.add_argument('--window-size=1920x1080')  # Set window size to avoid issues with elements not being visible
    
    # Set a random user-agent
    user_agent = ua.random
    options.add_argument(f'user-agent={user_agent}')

    # Initialize the WebDriver with the specified options
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Example of using the create_driver function
driver = create_driver()


# #Function to calculate the exponential backoff delay with optional jitter
def exponential_backoff(retries, base_delay=2, max_delay=120):
    """
    Calculate the exponential backoff delay with optional jitter.
    :param retries: Number of retries attempted.
    :param base_delay: Initial delay in seconds.
    :param max_delay: Maximum delay in seconds.
    :return: Delay time in seconds.
    """
    delay = min(base_delay * (2 ** retries), max_delay) #Increases delay time through exponential grrowth based on number of current retries
    jitter = random.uniform(0, delay / 2) # Random value chosen forr jitter that is between 0 and Half of the delay count
    return delay + jitter #Returns both.

# Function to scrape job information from a specific element on the page
def scrape_job_info(driver, selector):
    retries = 0
    max_retries = 5
    while retries < max_retries:
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            return element.text
        except (NoSuchElementException, StaleElementReferenceException) as e:
            delay = exponential_backoff(retries)
            print(f"[{threading.current_thread().name}] Exception: {e}. Retrying in {delay:.2f} seconds... (Attempt {retries + 1}/{max_retries})")
            time.sleep(delay)
            retries += 1
        # print(f"[{threading.current_thread().name}] Failed to scrape job info after {max_retries} attempts.")
    return None

# Function to write job listings to a CSV file
def write_jobs_to_csv(job_list, csv_file):
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=job_list[0].keys())
        writer.writeheader()
        writer.writerows(job_list)

# Function to scrape a single page
def scrape_page(page):
    """
    Scrapes job listings from a specified page on the MyCareersFuture website.
    Args:
        page (int): The page number to scrape.
    Returns:
        list: A list of dictionaries, each containing job details such as URL, title, location, employment type, seniority, minimum experience, industry, salary range, description, and required skills.
    The function performs the following steps:
    1. Creates a web driver instance and sets an implicit wait time.
    2. Constructs the query URL based on user input for the industry and the specified page number.
    3. Fetches the page using the web driver.
    4. Checks for any error messages on the page.
    5. Waits for the job card container to be present on the page.
    6. Iterates through job cards, extracting job details and storing them in a list.
    7. Handles various exceptions such as `NoSuchElementException`, `ElementClickInterceptedException`, and `StaleElementReferenceException`.
    8. Adds random delays to avoid rate-limiting.
    9. Returns the list of job details.
    """
    # Create a new WebDriver instance with a random user-agent
    driver = create_driver()
    driver.implicitly_wait(10)  # Set to 10 seconds

    #Take in user input for industry and create query_final based on industry input
    query_initial = "https://www.mycareersfuture.gov.sg/search?sortBy=relevancy&page="
    query_final = query_initial + str(page)
    print(query_final)

    #Fetch page with driver
    driver.get(query_final)

    # Wait for the card container to be present on the page
    wait_for_element(driver, By.CSS_SELECTOR, "div[data-testid='card-list']", 15)
    try:
        card_container = driver.find_element(By.CSS_SELECTOR, "div[data-testid='card-list']")
        print(f"[{threading.current_thread().name}] Card container found.")
    except NoSuchElementException:
        print(f"[{threading.current_thread().name}] Card container not found.")
        driver.quit()
        return []

    job_count = 0
    job_num = 0
    all_jobs = []

    while True:
        try:
            job_card_id = f"job-card-{job_num}"
            job_card = card_container.find_element(By.ID, job_card_id)
            job_count += 1
            print(f"[{threading.current_thread().name}] Found job card with ID: {job_card_id}")
            job_num += 1
        except:
            print(f"[{threading.current_thread().name}] Finished searching. Total job listings found: {job_count}")
            break

    for counter in range(0, job_count):
        try:
            driver.refresh()
            job_url = job_title = job_location = job_employment_type = job_seniority = job_min_exp = job_industry = job_salary_range = job_desc = job_skills_needed = ""
            job_card_id = f"job-card-{counter}"
            print(f"[{threading.current_thread().name}] Trying to find job card with ID: {job_card_id}")

            retries = 5
            while retries > 0:
                try:
                    card_container = driver.find_element(By.CSS_SELECTOR, "div[data-testid='card-list']")
                    job_card = card_container.find_element(By.ID, job_card_id)
                    print(f"[{threading.current_thread().name}] Job Card {counter} found. Clicking on it.")

                    try:
                        job_card.click()

                    except ElementClickInterceptedException:
                        print(f"[{threading.current_thread().name}] ElementClickInterceptedException encountered for job card {counter}. Using JavaScript click.")
                        driver.execute_script("arguments[0].click();", job_card)

                    print(f"[{threading.current_thread().name}] Currently Searching through: Job-Card-{counter}")

                    # Explicit wait until the job details are found before continuing
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "h1[data-testid='job-details-info-job-title']"))
                    )
                    
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='description-content']"))
                    )

                    job_url = driver.current_url
                    print(f"[{threading.current_thread().name}] Job URL: {job_url}")

                    #-----------EXTRACTION----------
                    # Add in scrape_job_info

                    job_title = scrape_job_info(driver, "h1[data-testid='job-details-info-job-title']")
                    #job_location = scrape_job_info(driver, "a[data-testid='job-details-info-location-map']")
                    job_employment_type = scrape_job_info(driver, "p[data-testid='job-details-info-employment-type']")
                    job_seniority = scrape_job_info(driver, "p[data-testid='job-details-info-seniority']")
                    job_min_exp = scrape_job_info(driver, "p[data-testid='job-details-info-min-experience']")
                    job_industry = scrape_job_info(driver, "p[data-testid='job-details-info-job-categories']")
                    job_salary_range = scrape_job_info(driver, "span[data-testid='salary-range']")
                    job_desc = scrape_job_info(driver, "div[data-testid='description-content']")
                    job_skills_needed = scrape_job_info(driver, "div[data-testid='multi-pill-button']")

                    #-----------STORAGE------------

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

                    # Print statement to confirm the job data has been added
                    print(f"[{threading.current_thread().name}] Job data added for job-card-{counter}")

                    #-----------RELOAD-----------
                    driver.get(query_final)

                    # Explicit wait until the card container is found before continuing
                    wait_for_element(driver, By.CSS_SELECTOR, "div[data-testid='card-list']", 15)

                    break

                except StaleElementReferenceException: # Handle StaleElementReferenceException
                    print(f"[{threading.current_thread().name}] StaleElementReferenceException encountered for job card {counter}. Retrying...")
                    retries -= 1
                    if retries == 0:
                        print(f"[{threading.current_thread().name}] Failed to interact with job card {counter} after multiple retries.")
                        driver.back()
                        wait_for_element(driver, By.CSS_SELECTOR, "div[data-testid='card-list']", 15)
                        raise
                    else:
                        driver.back()
                        wait_for_element(driver, By.CSS_SELECTOR, "div[data-testid='card-list']", 15)

                except NoSuchElementException: #Handles NoSuchElementException
                    retries -= 1
                    if retries == 0:
                        print(f"[{threading.current_thread().name}] Failed to find job card {counter} after multiple retries.")
                        driver.back()
                        wait_for_element(driver, By.CSS_SELECTOR, "div[data-testid='card-list']", 15)
                        raise
                    else:
                        time.sleep(random.uniform(5, 10))
                        driver.back() #Reload
                        delay = exponential_backoff(retries)
                        print(f"[{threading.current_thread().name}] Retries: {retries}. Delay: {delay}")
                        time.sleep(delay)
                        wait_for_element(driver, By.CSS_SELECTOR, "div[data-testid='card-list']", 15)

        except Exception as e:
            print(f"[{threading.current_thread().name}] Job card {counter} not found. Exception: {e}")
            driver.back()

        time.sleep(random.uniform(2, 5))

    driver.quit()
    return all_jobs

# Function to check for the error message
def check_for_error_message(driver):
    try:
        error_message = driver.find_element(By.CSS_SELECTOR, "div.error-message-selector")  # Replace with the actual selector
        if "temporarily unable to showcase any job postings" in error_message.text:
            return True
    except NoSuchElementException:
        return False
    return False

# Example function to wait for an element
def wait_for_element(driver, by, value, timeout=15):
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))

#--------------------MAIN--------------------

# Main function to run the scraper in parallel
"""
Main function to scrape job listings from multiple pages concurrently and save the results to a CSV file.
This function performs the following steps:
1. Initializes the number of pages to scrape and an empty list to store job listings.
2. Uses a ThreadPoolExecutor to scrape multiple pages concurrently.
3. Collects the results from each thread and combines them into a single list.
4. Converts the list of job listings (dictionaries) into a pandas DataFrame.
5. Saves the DataFrame to a CSV file named 'job_listings.csv'.

"""
def main():

    #For testing purposes: check how long it takes for the webscraper to run.
    #Start timer
    start_time = time.time()
    print(start_time)

    page_count = 5  # MUST be same number to avoid the website crashing. All 20 per page need to be done in 1 sessions
    all_jobs = []  # List to store all job listings

    # Use ThreadPoolExecutor to scrape multiple pages concurrently
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(scrape_page, page) for page in range(page_count)]
        for future in futures:
            all_jobs.extend(future.result())  # Collect results from each thread

    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(all_jobs)

    # Define the header row of the CSV File.
    header = ["Job URL", "Job Title", "Job Location", "Job Employment Type", "Job Seniority", "Job Minimum Experience", "Job Industry", "Job Salary Range", "Job Description", "Job Skills Needed"]

    # Check if the CSV file already exists
    file_exists = os.path.isfile('job_listings.csv')

    # Open the CSV file in append mode if it exists, otherwise in write mode
    with open('job_listings.csv', 'a' if file_exists else 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        # Write the header row only if the file is being created
        if not file_exists:
            writer.writeheader()

        # Write accumulated job data to CSV
        write_jobs_to_csv(all_jobs, 'job_listings.csv')

    #Save end time
    end_time = time.time()
    print(end_time)

    # Calculate elapsed time in seconds
    elapsed_time = end_time - start_time

    # Convert elapsed time to minutes and seconds
    minutes, seconds = divmod(elapsed_time, 60)

    # Print time taken to run the webscraper
    print(f"Time taken to run the webscraper: {int(minutes)} minutes and {seconds:.2f} seconds")

    print(len(all_jobs))

if __name__ == "__main__":
    main()