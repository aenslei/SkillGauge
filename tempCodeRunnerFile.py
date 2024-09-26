def tokenize_and_find_combined_skills(skills_str):
    if pd.isna(skills_str):  # Handle missing skills
        return []
    
    # Replace different delimiters (commas, semicolons) with a uniform delimiter (comma)
    skills_str = skills_str.replace(';', ',').replace('/', ',').replace('\\', '')  # Added this line to handle slashes
    
    # Split the string by commas
    tokens = skills_str.split(',')

    # Preserve abbreviations and multi-word combinations
    refined_tokens = []
    for token in tokens:
        token = token.strip()
        
        # Check if the token is in the list of abbreviations to preserve
        if token in preserve_abbreviations or token in abbreviations:
            refined_tokens.append(token)
        else:
            # Split by capital letters and rejoin with spaces for phrases like 'ArchitecturalDesign'
            refined_tokens.extend(re.findall(r'[A-Z][^A-Z]*', token))
    
    # Handle cases where single letters need to be merged with the next token
    merged_tokens = []
    i = 0
    while i < len(refined_tokens):
        # Check for combinations of two or three tokens in the dictionary
        token_combination_two = " ".join(refined_tokens[i:i + 2])
        token_combination_three = " ".join(refined_tokens[i:i + 3])
        
        if token_combination_three in skills_dict:
            merged_tokens.append(skills_dict[token_combination_three])
            i += 3  # Skip the next two tokens as they are already merged
        elif token_combination_two in skills_dict:
            merged_tokens.append(skills_dict[token_combination_two])
            i += 2  # Skip the next token as it is already merged
        else:
            merged_tokens.append(refined_tokens[i])
            i += 1  # Move to the next token

    # Strip extra spaces and return the final list of skills
    return [skill.strip() for skill in merged_tokens if skill.strip()]