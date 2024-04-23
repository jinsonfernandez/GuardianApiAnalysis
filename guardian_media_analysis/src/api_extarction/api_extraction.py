import configparser
import requests
from datetime import datetime
import json
import os
from src.utility import setup_logger, fetch_config
import pandas as pd

# base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# config_path = os.path.join(base_dir, 'config.ini')
# config = configparser.ConfigParser()
# config.read(config_path)

class GuardianAPI:
    def __init__(self):
        self.config = fetch_config()
        self.GUARDIAN_API_KEY = self.config.get('guardian_api', 'api_key')
        self.logger = setup_logger(__name__)

    def guardian_search(self, search_query, from_date, to_date):
        url = 'https://content.guardianapis.com/search'
        params = {
            'q': search_query,
            'from-date': from_date,
            'to-date': to_date,
            'page-size': 100,
            'api-key': self.GUARDIAN_API_KEY,
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
                self.logger.error(f"API request failed with status code {response.status_code}")
                raise Exception(f"API request failed with status code {response.status_code}")

        self.logger.info(f"Retrieved {len(all_results)} articles for search query: {search_query}")
        return all_results
    
    def convert_to_dataframe(self, json_data):
            try:
                data_dict = json.loads(json_data)
                if 'response' in data_dict and 'results' in data_dict['response']:
                    results = data_dict['response']['results']
                    df = pd.DataFrame(results)
                    self.logger.info(f"Converted data to DataFrame with {len(df)} rows and {len(df.columns)} columns")
                    return df
                else:
                    self.logger.warning("No results found or incorrect JSON format")
                    return pd.DataFrame()  
            except json.JSONDecodeError:
                self.logger.error("Error parsing JSON data")
                return pd.DataFrame() 
