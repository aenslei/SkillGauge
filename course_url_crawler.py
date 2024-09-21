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
                for course in courses[:3]:
                    # Append a dictionary with course name and url
                    all_courses.append({
                        "name": course['name'],
                        "url": f"https://www.coursera.org/learn/{course['slug']}"
                    })
            else:
                continue
    return all_courses
