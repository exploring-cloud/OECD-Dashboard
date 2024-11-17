
import pandas as pd
import os
from tqdm import tqdm
from fetch_oecd_data import get_oecd_data
from fetch_oecd_agencies import get_oecd_agencies

#try:
for dataflow in get_oecd_agencies():
    oecd_data = get_oecd_data(dataflow['agency_identifier'], dataflow['dataflow_identifier'])
    df = oecd_data[0]
    df_name = oecd_data[2]
    #df = get_oecd_data(dataflow['agency_identifier'], dataflow['dataflow_identifier'])[0]

    # Define the folder name you want to save the CSV in
    folder_name = "01 - Datasets"

    # Check if the folder exists; if not, create it
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Define the path for the CSV file inside the folder
    file_path = os.path.join(folder_name, df_name+ '.csv')

    if df is not None:
        # Drop the last column using iloc (select all rows and all columns except the last one)
        #df_without_last_column = df.iloc[:, :-1]

        # Create the CSV file using tqdm to show the progress bar
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            # Write the header first
            df.head(0).to_csv(f, index=False)
        
            # Write the data rows with a progress bar
            for i in tqdm(range(0, len(df)), desc="Saving CSV", unit="rows"):
                df.iloc[[i]].to_csv(f, index=False, header=False)
    
        print(f"Data saved successfully to {file_path}")

#except:
#    print(f"Error in data retrieval")