import pandas as pd
import os

# Split whole industry csv into individual industry csv
def convert_df_list_to_csv(df_list, folder_path):

    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    """

    for df in df_list:
        # Extract the unique industry name from the "Broader Category" column
        industry_name = df["Broader Category"].unique()
        industry_name = str(industry_name)
        industry_name = industry_name[2:-2]
        industry_name = industry_name.replace(" ", "_")

        # Save CSV to the specified folder
        csv_file_path = os.path.join(folder_path, f"(Final)_past_{industry_name}.csv")
        df.to_csv(csv_file_path, index=False)
        print(f"File saved: {csv_file_path}")

def main():
    with open("Datasets/sg_job_data_cleaned.csv", encoding='utf-8') as csvfile:
        df = pd.read_csv(csvfile, index_col=False)
    # Group the DataFrame by the "Broader Category" column (industry)
    df = df.groupby("Broader Category")
    df_list = [df.get_group(x) for x in df.groups]

    # Convert the list of DataFrames to CSV files in the specified folder
    flask_dataset_folder = r"Datasets"
    convert_df_list_to_csv(df_list, flask_dataset_folder)
    print("Individual industry csv files created!")

if __name__ == "__main__":
    main()