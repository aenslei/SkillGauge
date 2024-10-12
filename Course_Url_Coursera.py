'''
Author: Ryan Wong
Uses the coursera API to get courses links based on which course the user is lacking 
'''
import requests

def search_courses(search_terms):
    # List to store all course results
    all_courses = [] 

    # Base URL for Coursera API that will be queried for courses
    url = "https://www.coursera.org/api/courses.v1"

    for term in search_terms:
        # Define the parameters for the API requestZ
        params = {
            "q": "search",
            "query": term,
            "includes": "instructor_ids",
            "limit": 5
        }

        # Define the headers for the request to mimic a browser request and avoid blocks
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Referer': 'https://www.coursera.org/'
        }
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Extract the course elements from the response
            courses = data['elements']

            # If there are any courses in the response
            if courses:
                # Limit to the top 3 courses
                for course in courses[:3]:
                    # Append a dictionary with course name and url
                    all_courses.append({
                        "name": course['name'],
                        "url": f"https://www.coursera.org/learn/{course['slug']}"
                    })
            else:
                continue
    return all_courses
