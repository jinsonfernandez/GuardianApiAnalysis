import configparser
import requests
from datetime import datetime
import json
import os
from src.utility import setup_logger
import pandas as pd

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_path = os.path.join(base_dir, 'config.ini')
config = configparser.ConfigParser()
config.read(config_path)

GUARDIAN_API_KEY = config.get('guardian_api', 'api_key')

logger = setup_logger(__name__)

def guardian_search(search_query, from_date, to_date):
    url = 'https://content.guardianapis.com/search'
    params = {
        'q': search_query,
        'from-date': from_date,
        'to-date': to_date,
        'page-size': 100,
        'api-key': GUARDIAN_API_KEY,
        'show-fields': 'headline,byline,sectionName,webPublicationDate'
    }
    
    all_results = []
    current_page = 1
    total_pages = 1
    
    while current_page <= total_pages:
        params['page'] = current_page
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            all_results.extend(data['response']['results'])
            total_pages = data['response']['pages']
            current_page += 1
        else:
            logger.error(f"API request failed with status code {response.status_code}")
            raise Exception(f"API request failed with status code {response.status_code}")
    
    logger.info(f"Retrieved {len(all_results)} articles for search query: {search_query}")
    return all_results

def convert_to_dataframe(json_data):
    try:
        # Parse JSON data
        data_dict = json.loads(json_data)
        
        # Check if the response has the necessary key
        if 'response' in data_dict and 'results' in data_dict['response']:
            # Extract results
            results = data_dict['response']['results']
            # Convert results to DataFrame
            df = pd.DataFrame(results)
            logger.info(f"Converted data to DataFrame with {len(df)} rows and {len(df.columns)} columns")
            return df
        else:
            logger.warning("No results found or incorrect JSON format")
            return pd.DataFrame()  # Return an empty DataFrame if no results
    except json.JSONDecodeError:
        logger.error("Error parsing JSON data")
        return pd.DataFrame()  # Return an empty DataFrame if JSON parsing fails
