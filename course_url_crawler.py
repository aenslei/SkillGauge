import requests

def search_courses(search_terms):
    all_courses = []  # List to store all course results
    url = "https://www.coursera.org/api/courses.v1"
    for term in search_terms:
        params = {
            "q": "search",
            "query": term,
            "includes": "instructor_ids",
            "limit": 5
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Referer': 'https://www.coursera.org/'
        }
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            courses = data['elements']
            if courses:
                # Limit to the top 3 courses
                for idx, course in enumerate(courses[:3], 1):
                    course_info = f"{course['name']} - https://www.coursera.org/learn/{course['slug']}"
                    all_courses.append(course_info)
            else:
                continue

    # Print all collected courses
    for course in all_courses:
        print(course)
    
if __name__ == '__main__':
    search_terms = ['java', 'UI', 'python programming']
    search_courses(search_terms)
