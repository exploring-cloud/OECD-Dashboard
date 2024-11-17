import requests
import csv
import time
import re

# Base URL for fetching dataflows (SDMX API version 1)
base_url = "https://sdmx.oecd.org/public/rest/dataflow"

# Headers to request JSON response
headers = {
    "Accept": "application/vnd.sdmx.structure+json; charset=utf-8; version=1.0"
}

# Function to strip HTML tags
def clean_html(raw_html):
    clean_text = re.sub(r'<.*?>', '', raw_html)  # Removes all content within <>
    return clean_text

# Function to get the list of dataflows including agency identifiers with retry logic
def get_dataflows(max_retries=5):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(f"{base_url}/ALL", headers=headers)
            response.raise_for_status()
            data = response.json()

            # Extract relevant dataflows with agency identifiers
            dataflows = []
            for flow in data['data']['dataflows']:
                agency_id = flow['id']
                name = flow['name'] if flow.get('name', {}) else 'No name available'
                raw_description = flow['description'] if flow.get('description', {}) else 'No description available'
                description = clean_html(raw_description)
                version = flow['version']
                agency_identifier = flow['agencyID']

                dataflows.append({
                    "agency_identifier": agency_identifier,
                    "dataflow_identifier": agency_id,
                    "dataflow_version": version,
                    "name": name,
                    "description": description
                })

            return dataflows

        except requests.exceptions.HTTPError as e:
            if response.status_code == 503:
                retries += 1
                wait_time = 2 ** retries  # Exponential backoff
                print(f"Service unavailable (503). Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"HTTP error occurred: {e}")
                break
        except requests.exceptions.RequestException as e:
            print(f"Error fetching dataflows: {e}")
            break

    print("Failed to retrieve dataflows after multiple retries.")
    return []

# Function to save dataflows to a CSV file
def save_to_csv(dataflows, filename="oecd_dataflows.csv"):
    keys = ["agency_identifier", "dataflow_identifier", "dataflow_version", "name", "description"]
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(dataflows)
    print(f"Data saved to {filename}")

# Main function to execute the process
def get_oecd_agencies():
    dataflows = get_dataflows()
    
    if dataflows:
        return dataflows
        
    else:
        print("No dataflows retrieved.")
