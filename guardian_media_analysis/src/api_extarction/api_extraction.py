import configparser
import requests
from datetime import datetime
import json
import os
from src.utility import setup_logger, fetch_config
import pandas as pd
import time

class GuardianAPI:
    def __init__(self):
        self.config, self.config_path = fetch_config() 
        self.GUARDIAN_API_KEY = self.config.get('guardian_api2', 'api_key')
        # 'f155b662-7be4-4e65-8a36-110369468534'
        self.logger = setup_logger(__name__)
        self.session = requests.Session()  

    def guardian_search(self, search_query, from_date, to_date, max_retries=3):
        url = 'http://content.guardianapis.com/search'
        params = {
            'q': search_query.replace(' ', '%20'),
            'from-date': from_date,
            'to-date': to_date,
            'page-size': 200,
            'api-key': self.GUARDIAN_API_KEY,
            'show-fields': 'headline,byline,sectionName,webPublicationDate'
        }
        all_results = []
        current_page = 1
        total_pages = 1
        retry_count = 0
        retry_delay = 5  # Initial delay

        while current_page <= total_pages:
            params['page'] = current_page
            response = self.session.get(url, params=params)
           
            if response.status_code == 200:
                data = response.json()
                all_results.extend(data['response']['results'])
                total_pages = data['response']['pages']
                self.logger.info(f"Processed page {current_page}/{total_pages}. Total results so far: {len(all_results)}.")
                current_page += 1
                retry_count = 0  # Reset retry count after a successful request
                retry_delay = 5  # Reset delay
            else:
                retry_count += 1
                if retry_count <= max_retries:
                    self.logger.warning(f"API request failed with status code {response.status_code}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential back-off
                else:
                    self.logger.error(f"API request failed with status code {response.status_code} after {max_retries} retries.")
                    raise Exception(f"API request failed with status code {response.status_code} after {max_retries} retries.")

        self.logger.info(f"Retrieved {len(all_results)} articles for search query: {search_query}")
        return all_results
        
    def results_to_dataframe(self, results, filter_query=None):
        try:
            if filter_query:
                filtered_results = [
                    result for result in results
                    if filter_query.lower() in result.get('webTitle', '').lower()
                    or filter_query.lower() in result.get('fields', {}).get('headline', '').lower()
                ]
                
                df = pd.DataFrame(filtered_results)
                
                if df.empty:
                    self.logger.warning(f"No data found for '{filter_query}'.")
                    return None
                
                self.logger.info(f"Data filtered for '{filter_query}': {len(df)} rows")
                return df
            else:
                df = pd.DataFrame(results)
                if df.empty:
                    self.logger.warning("No data was extracted from the API.")
                    return None
                
                self.logger.info(f"No filter query provided. Returning the entire DataFrame with {len(df)} rows")
                return df
        
        except Exception as e:
            self.logger.error("An error occurred while converting results to a DataFrame.")
            self.logger.exception(e)
            return None