import json
import os

CONFIG_FILE = "config.json"

def load_config():
    """Load the configuration from a JSON file."""
    try:
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_config(config):
    """Save the configuration to a JSON file."""
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file)