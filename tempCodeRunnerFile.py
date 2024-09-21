    # Find abbreviations (defined as tokens consisting of uppercase letters or numbers, with no spaces)
    abbreviations = []
    for token in tokens:
        token = token.strip()
        if re.match(r'^[A-Z0-9]+$', token):
            abbreviations.append(token)
    
    return abbreviations

# Apply the function to each row of the 'skills' column
data['Abbreviations'] = data['skills'].apply(find_abbreviations)

# Collect all the abbreviations into a single list
all_abbreviations = [abbr for abbr_list in data['Abbreviations'] for abbr in abbr_list]

# Get unique abbreviations
unique_abbreviations = set(all_abbreviations)

# Display the unique abbreviations
print(unique_abbreviations)