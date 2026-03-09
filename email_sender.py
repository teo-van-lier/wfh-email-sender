"""
Email sender module for WFH Email Automation System
Handles Outlook integration for sending emails
"""

import logging
import pythoncom
from datetime import datetime
from win32com.client import Dispatch
import config_loader as config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)

class EmailSender:
    """Handles email sending through Outlook"""
    
    def __init__(self):
        self.outlook = None
        
    def _initialize_outlook(self):
        """Initialize Outlook application"""
        try:
            pythoncom.CoInitialize()
            self.outlook = Dispatch("Outlook.Application")
            logging.info("Outlook initialized successfully")
            return True
        except Exception as e:
            logging.error(f"Failed to initialize Outlook: {e}")
            return False
    
    def send_start_email(self, date_str):
        """Send start work email"""
        subject = config.START_EMAIL_SUBJECT_TEMPLATE.format(date=date_str)
        body = config.START_EMAIL_BODY
        
        return self._send_email(subject, body, "start")
    
    def send_stop_email(self, date_str):
        """Send stop work email"""
        subject = config.STOP_EMAIL_SUBJECT_TEMPLATE.format(date=date_str)
        body = config.STOP_EMAIL_BODY
        
        return self._send_email(subject, body, "stop")
    
    def _send_email(self, subject, body, email_type):
        """Send email through Outlook"""
        try:
            if not self.outlook:
                if not self._initialize_outlook():
                    return False
            
            mail = self.outlook.CreateItem(0)  # 0 = Mail item
            
            mail.To = config.EMAIL_RECIPIENT
            mail.Subject = subject
            mail.Body = body
            
            # Send the email
            mail.Send()
            
            logging.info(f"Successfully sent {email_type} email: {subject}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send {email_type} email: {e}")
            return False
    
    def cleanup(self):
        """Clean up COM resources"""
        if self.outlook:
            try:
                pythoncom.CoUninitialize()
                logging.info("Outlook COM resources cleaned up")
            except Exception as e:
                logging.error(f"Error cleaning up COM resources: {e}")
