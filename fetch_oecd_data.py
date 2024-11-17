import requests
import json
import pandas as pd

def get_oecd_data(agency_identifier, dataflow_identifier):
   
    # Create the OECD API URL for the dataset
    api_url = f"https://sdmx.oecd.org/public/rest/data/{agency_identifier},{dataflow_identifier}/all"
    
    # Set headers to request data in JSON format
    headers = {
        "Accept": "application/vnd.sdmx.data+json; charset=utf-8; version=1.0"
    }

     # Send the request to the OECD API
    response = requests.get(api_url, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        
        # Try different paths to find the dimensions
        dimensions = (
            data.get('data', {}).get('structure', {}).get('dimensions', {}).get('observations') or
            data.get('data', {}).get('structure', {}).get('series', {}).get('dimensions') or
            data.get('data', {}).get('structure', {}).get('dimensions', {}).get('series') or
            []
        )
        # Try different paths to find the time periods
        time_period = (
            data.get('data', {}).get('structure', {}).get('dimensions', {}).get('observation') or
            []
        )

        # Try different paths to find the name
        data_set_name = (
            data.get('data', {}).get('structure', {}).get('name', {}) or
            []
        )

        # Extract observations using a similar approach
        data_sets = (data.get('data', {}).get('dataSets') 
                     or []
                     )
        observations = (
            data_sets[0].get('observations') or
            data_sets[0].get('series')
            if data_sets else {}
            )

        # Handle unexpected structures
        if not dimensions or not observations:
            print("Unexpected JSON structure. Printing the response for inspection:")
            print(json.dumps(data, indent=4))
            return None, None
        
        try:
            # Create lists for each dimension based on 'keyPosition'
            dimension_columns = {dim['id']: [] for dim in dimensions}
            dimension_columns['Observation Value'] = []
            
            # Loop through the observations to split the keys and map them to dimension values
            for obs_key, obs_value in observations.items():                
                # Append the actual observation value
                    # Extract the observation value based on its structure
                if isinstance(obs_value, list) and len(obs_value) > 0:
                    # If obs_value is a list, use the first element (common case)
                    observation_value = obs_value[0]
                elif isinstance(obs_value, dict) and 'observations' in obs_value:
                    # If obs_value is a dictionary containing 'observations', extract the value
                    observation_value = obs_value.get('observations')
                else:
                    # If none of the above, use obs_value directly (fallback)
                    observation_value = obs_value

                observation_values = {}
                    
                # Append the extracted observation value to the list
                for i, obs in observation_value.items():
                   
                    # Extract the year from the time period using the index
                    observation_year = time_period[0]['values'][int(i)]['id']
                    
                    # Store the observation value for the corresponding year
                    observation_values[observation_year] = obs[0]

                obs_zero_check_sum = 0
                for i, obs_zero_check in observation_values.items():
                    obs_zero_check_sum = obs_zero_check_sum + obs_zero_check
                    
                if not obs_zero_check_sum == 0:
                    key_parts = obs_key.split(':')
                    # Map each part to the corresponding dimension
                    for i, part in enumerate(key_parts):
                        if i < len(dimensions):
                            dimension_id = dimensions[i]['id']
                            # Dynamically extract dimension value names or codes
                            value_info = dimensions[i].get('values', [])
                            dimension_value = value_info[int(part)]['name'] if value_info and int(part) < len(value_info) else part
                            dimension_columns[dimension_id].append(dimension_value)
                    # Append a copy of observation_values to the list
                    dimension_columns['Observation Value'].append(observation_values.copy())
           
            # Construct the DataFrame
            df = pd.DataFrame(dimension_columns)
            
            return df, dimensions, data_set_name

        except KeyError as e:
            print(f"KeyError: {e} - Check the JSON structure for expected keys.")
            return None, None
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None, None
    

        