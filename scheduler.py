"""
Scheduler module for WFH Email Automation System
Handles database operations and email scheduling
"""

import sqlite3
import threading
import time
import logging
import random
from datetime import datetime, timedelta
import email_sender
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

class WFHScheduler:
    """Handles scheduling and sending of WFH emails"""
    
    def __init__(self):
        self.db_path = config.DB_PATH
        self.email_sender = email_sender.EmailSender()
        self.running = False
        self.scheduler_thread = None
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scheduled_emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    stop_time TEXT NOT NULL,
                    start_sent INTEGER DEFAULT 0,
                    stop_sent INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logging.info("Database initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize database: {e}")
    
    def schedule_emails(self, date_str):
        """Schedule emails for a specific date"""
        try:
            # Parse date
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            # Generate random morning time between 7:45 and 8:10
            morning_start = datetime.strptime(config.MORNING_START_TIME, "%H:%M")
            morning_end = datetime.strptime(config.MORNING_END_TIME, "%H:%M")
            
            # Calculate random minutes between start and end
            total_minutes = (morning_end - morning_start).seconds // 60
            random_minutes = random.randint(0, total_minutes)
            
            start_time = (morning_start + timedelta(minutes=random_minutes)).time()
            
            # Calculate stop time: 9 hours + random 10-30 minutes
            base_stop_time = datetime.combine(date_obj, start_time) + timedelta(hours=config.WORK_DURATION_HOURS)
            random_extra_minutes = random.randint(config.STOP_TIME_RANDOM_MINUTES_MIN, config.STOP_TIME_RANDOM_MINUTES_MAX)
            stop_time = (base_stop_time + timedelta(minutes=random_extra_minutes)).time()
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO scheduled_emails (date, start_time, stop_time)
                VALUES (?, ?, ?)
            ''', (date_str, start_time.strftime("%H:%M"), stop_time.strftime("%H:%M")))
            
            conn.commit()
            conn.close()
            
            logging.info(f"Scheduled emails for {date_str}: Start at {start_time}, Stop at {stop_time}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to schedule emails for {date_str}: {e}")
            return False
    
    def get_scheduled_emails(self):
        """Get all scheduled emails"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, date, start_time, stop_time, start_sent, stop_sent
                FROM scheduled_emails
                ORDER BY date, start_time
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            return results
            
        except Exception as e:
            logging.error(f"Failed to get scheduled emails: {e}")
            return []
    
    def cancel_scheduled_email(self, email_id):
        """Cancel a scheduled email"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM scheduled_emails WHERE id = ?', (email_id,))
            
            conn.commit()
            changes = conn.total_changes
            conn.close()
            
            if changes > 0:
                logging.info(f"Cancelled scheduled email with ID {email_id}")
                return True
            else:
                logging.warning(f"No scheduled email found with ID {email_id}")
                return False
                
        except Exception as e:
            logging.error(f"Failed to cancel scheduled email {email_id}: {e}")
            return False
    
    def _check_and_send_emails(self):
        """Check if any emails need to be sent and send them"""
        try:
            now = datetime.now()
            current_date = now.date().strftime("%Y-%m-%d")
            current_time = now.time().strftime("%H:%M")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check for start emails
            cursor.execute('''
                SELECT id, date FROM scheduled_emails
                WHERE date = ? AND start_time <= ? AND start_sent = 0
            ''', (current_date, current_time))
            
            start_emails = cursor.fetchall()
            
            for email_id, date_str in start_emails:
                date_formatted = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
                if self.email_sender.send_start_email(date_formatted):
                    cursor.execute('UPDATE scheduled_emails SET start_sent = 1 WHERE id = ?', (email_id,))
                    logging.info(f"Start email sent for {date_str}")
            
            # Check for stop emails
            cursor.execute('''
                SELECT id, date FROM scheduled_emails
                WHERE date = ? AND stop_time <= ? AND stop_sent = 0
            ''', (current_date, current_time))
            
            stop_emails = cursor.fetchall()
            
            for email_id, date_str in stop_emails:
                date_formatted = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
                if self.email_sender.send_stop_email(date_formatted):
                    cursor.execute('UPDATE scheduled_emails SET stop_sent = 1 WHERE id = ?', (email_id,))
                    logging.info(f"Stop email sent for {date_str}")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Error checking and sending emails: {e}")
    
    def start_scheduler(self):
        """Start the background scheduler thread"""
        if self.running:
            logging.warning("Scheduler is already running")
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        logging.info("Scheduler started")
    
    def stop_scheduler(self):
        """Stop the background scheduler thread"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logging.info("Scheduler stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            try:
                self._check_and_send_emails()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logging.error(f"Error in scheduler loop: {e}")
                time.sleep(60)
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_scheduler()
        self.email_sender.cleanup()
