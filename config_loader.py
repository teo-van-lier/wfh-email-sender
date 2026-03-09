"""
Configuration loader for WFH Email Automation System
Loads configuration from config file
"""

import os
from pathlib import Path

def load_config():
    """Load configuration from config file"""
    config_file = Path(__file__).parent / "config"
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    
    config = {}
    with open(config_file, 'r', encoding='utf-8') as f:
        current_key = None
        for line in f:
            line = line.rstrip('\n')  # Remove trailing newline but keep other whitespace
            
            if line.strip() and not line.strip().startswith('#'):
                if '=' in line:
                    # New key-value pair
                    if current_key is not None:
                        # Finalize previous multi-line value
                        config[current_key] = config[current_key].strip()
                    
                    key, value = line.split('=', 1)
                    current_key = key.strip()
                    config[current_key] = value
                elif current_key is not None:
                    # Continuation of multi-line value
                    config[current_key] += '\n' + line
            elif current_key is not None and not line.strip():
                # Empty line - add to multi-line value
                config[current_key] += '\n'
        
        # Finalize the last key
        if current_key is not None:
            config[current_key] = config[current_key].strip()
    
    return config

# Load configuration
CONFIG = load_config()

# Database settings
DB_NAME = CONFIG.get('DB_NAME', 'wfh_emails.db')
DB_PATH = Path(__file__).parent / DB_NAME

# Email settings
EMAIL_SENDER = CONFIG.get('EMAIL_SENDER', '')
EMAIL_RECIPIENT = CONFIG.get('EMAIL_RECIPIENT', '')

# Email templates
START_EMAIL_SUBJECT_TEMPLATE = CONFIG.get('START_EMAIL_SUBJECT_TEMPLATE', 'Start remote werk {date}')
START_EMAIL_BODY = CONFIG.get('START_EMAIL_BODY', 'Ik start nu met werken van thuis.')
STOP_EMAIL_SUBJECT_TEMPLATE = CONFIG.get('STOP_EMAIL_SUBJECT_TEMPLATE', 'Einde remote werk {date}')
STOP_EMAIL_BODY = CONFIG.get('STOP_EMAIL_BODY', 'Ik stop nu met werken van thuis.')

# Scheduling settings
MORNING_START_TIME = CONFIG.get('MORNING_START_TIME', '07:45')
MORNING_END_TIME = CONFIG.get('MORNING_END_TIME', '08:10')
WORK_DURATION_HOURS = int(CONFIG.get('WORK_DURATION_HOURS', '9'))
STOP_TIME_RANDOM_MINUTES_MIN = int(CONFIG.get('STOP_TIME_RANDOM_MINUTES_MIN', '10'))
STOP_TIME_RANDOM_MINUTES_MAX = int(CONFIG.get('STOP_TIME_RANDOM_MINUTES_MAX', '30'))

# Logging settings
LOG_FORMAT = CONFIG.get('LOG_FORMAT', '%(asctime)s - %(levelname)s - %(message)s')
LOG_FILE = Path(__file__).parent / CONFIG.get('LOG_FILE', 'wfh_email.log')
