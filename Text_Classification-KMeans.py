import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans



# Load your data
data = pd.read_csv('Datasets\sg_job_data-Cleaned.csv')

# Combine relevant columns (e.g., 'Skills', 'Benefits') into a single text feature
data['Text'] = data['Job Title'] + ' ' + data['Responsibilities'] + ' ' + data['skills']

# Ensure there are no missing values in the combined text column
data.dropna(subset=['Text'], inplace=True)

# Use TF-IDF to convert text data into numerical features
tfidf = TfidfVectorizer(stop_words='english', max_features=1000)
X = tfidf.fit_transform(data['Text'])

# Use KMeans clustering to group jobs into clusters (similar to industries)
kmeans = KMeans(n_clusters=30, random_state=42)  # You can adjust n_clusters based on your need
kmeans.fit(X)

# Assign each job a cluster (predicted industry)
data['Predicted Industry'] = kmeans.labels_


# Group jobs by predicted clusters (Predicted Industry)
grouped_jobs = data.groupby('Predicted Industry')['Job Title'].apply(list)

# Save the clusters and jobs within each cluster to a text file
with open('Datasets/clustered_jobs.txt', 'w') as f:
    for cluster, jobs in grouped_jobs.items():
        f.write(f"Cluster {cluster}:\n")
        for job in jobs:
            f.write(f"- {job}\n")
        f.write("\n")

# Print the jobs grouped by clusters to inspect
for cluster, jobs in grouped_jobs.items():
    print(f"Cluster {cluster}:")
    print(jobs)
    print("\n")


# Display the predicted industries
print(data[['Job Title', 'Predicted Industry']].head())
print(data[['Job Title', 'Predicted Industry']])

# data['Industry Name'] = data['Predicted Industry'].map(cluster_names)


# Reorder columns to insert the new columns before 'Job Title'
columns = list(data.columns)
job_title_index = columns.index('Job Title')  # Get the index of 'Job Title'
new_columns = columns[:job_title_index] + ['Predicted Industry'] + columns[job_title_index:]
data = data[new_columns]

# Save to file
data.to_csv('Datasets/sg_job_data-Cleaned-With Industry1.csv', index=False)
