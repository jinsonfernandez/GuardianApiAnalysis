import os
import configparser

def fetch_config():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    config_path = os.path.join(base_dir, 'config.ini')
    config = configparser.ConfigParser()
    config.read(config_path)
    return config