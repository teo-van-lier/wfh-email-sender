"""
Main CLI interface for WFH Email Automation System
Provides user-friendly command-line interface for scheduling emails
"""

import sys
import signal
from datetime import datetime, timedelta
import scheduler
import config_loader as config

class WFHEmailApp:
    """Main application class"""
    
    def __init__(self):
        self.scheduler = scheduler.WFHScheduler()
        self.running = True
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\nShutting down gracefully...")
        self.running = False
        self.scheduler.cleanup()
        sys.exit(0)
    
    def display_menu(self):
        """Display main menu"""
        print("\n" + "="*50)
        print("WFH Email Automation System")
        print("="*50)
        print("1. Schedule emails for a date")
        print("2. View scheduled emails")
        print("3. Cancel scheduled email")
        print("4. Send test email now")
        print("5. Start scheduler (run in background)")
        print("6. Exit")
        print("="*50)
    
    def schedule_emails_for_date(self):
        """Schedule emails for a specific date"""
        print("\n--- Schedule Emails ---")
        
        while True:
            date_input = input("Enter date (YYYY-MM-DD), 'today' for today, 'tomorrow' for tomorrow, or 'back' to return: ").strip()
            
            if date_input.lower() == 'back':
                return
            elif date_input.lower() == 'today':
                date_str = datetime.now().strftime("%Y-%m-%d")
                break
            elif date_input.lower() == 'tomorrow':
                date_str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                break
            else:
                try:
                    # Validate date format
                    datetime.strptime(date_input, "%Y-%m-%d")
                    date_str = date_input
                    
                    # Check if date is in the past
                    if datetime.strptime(date_str, "%Y-%m-%d").date() < datetime.now().date():
                        print("Error: Cannot schedule emails for past dates.")
                        continue
                    
                    break
                except ValueError:
                    print("Invalid date format. Please use YYYY-MM-DD format.")
        
        if self.scheduler.schedule_emails(date_str):
            print(f"✓ Emails scheduled successfully for {date_str}")
            print(f"  Start email: Will be sent between {config.MORNING_START_TIME} and {config.MORNING_END_TIME}")
            print(f"  Stop email: Will be sent approximately {config.WORK_DURATION_HOURS} hours + {config.STOP_TIME_RANDOM_MINUTES_MIN}-{config.STOP_TIME_RANDOM_MINUTES_MAX} minutes later")
        else:
            print("✗ Failed to schedule emails. Please check the logs.")
    
    def view_scheduled_emails(self):
        """Display all scheduled emails"""
        print("\n--- Scheduled Emails ---")
        
        emails = self.scheduler.get_scheduled_emails()
        
        if not emails:
            print("No scheduled emails found.")
            return
        
        print(f"{'ID':<5} {'Date':<12} {'Start Time':<12} {'Stop Time':<12} {'Status':<15}")
        print("-" * 65)
        
        for email_id, date, start_time, stop_time, start_sent, stop_sent in emails:
            if start_sent and stop_sent:
                status = "Completed"
            elif start_sent:
                status = "Stop pending"
            else:
                status = "Pending"
            
            print(f"{email_id:<5} {date:<12} {start_time:<12} {stop_time:<12} {status:<15}")
    
    def cancel_scheduled_email(self):
        """Cancel a scheduled email"""
        print("\n--- Cancel Scheduled Email ---")
        
        emails = self.scheduler.get_scheduled_emails()
        
        if not emails:
            print("No scheduled emails to cancel.")
            return
        
        print("Current scheduled emails:")
        self.view_scheduled_emails()
        
        try:
            email_id = input("\nEnter the ID of the email to cancel (or 'back' to return): ").strip()
            
            if email_id.lower() == 'back':
                return
            
            email_id = int(email_id)
            
            if self.scheduler.cancel_scheduled_email(email_id):
                print(f"✓ Scheduled email with ID {email_id} has been cancelled.")
            else:
                print(f"✗ Failed to cancel scheduled email with ID {email_id}.")
                
        except ValueError:
            print("Invalid ID. Please enter a valid number.")
    
    def send_test_email(self):
        """Send a test email immediately"""
        print("\n--- Send Test Email ---")
        
        print("Select email type:")
        print("1. Start work email")
        print("2. Stop work email")
        print("3. Back to main menu")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '3':
            return
        elif choice == '1':
            date_str = datetime.now().strftime("%d/%m/%Y")
            if self.scheduler.email_sender.send_start_email(date_str):
                print("✓ Test start email sent successfully!")
            else:
                print("✗ Failed to send test start email. Check the logs.")
        elif choice == '2':
            date_str = datetime.now().strftime("%d/%m/%Y")
            if self.scheduler.email_sender.send_stop_email(date_str):
                print("✓ Test stop email sent successfully!")
            else:
                print("✗ Failed to send test stop email. Check the logs.")
        else:
            print("Invalid choice. Please enter a number between 1 and 3.")
    
    def start_scheduler_background(self):
        """Start the scheduler in background"""
        print("\n--- Start Scheduler ---")
        
        try:
            self.scheduler.start_scheduler()
            print("✓ Scheduler started successfully!")
            print("  The scheduler will run in the background and automatically send emails at scheduled times.")
            print("  Press Ctrl+C to stop the scheduler.")
            
            # Keep the main thread alive
            while self.running:
                try:
                    import time
                    time.sleep(1)
                except KeyboardInterrupt:
                    break
                    
        except Exception as e:
            print(f"✗ Failed to start scheduler: {e}")
    
    def run(self):
        """Run the main application loop"""
        print("Welcome to WFH Email Automation System!")
        print("This system helps you automate work-from-home email notifications.")
        
        while self.running:
            try:
                self.display_menu()
                
                choice = input("\nEnter your choice (1-6): ").strip()
                
                if choice == '1':
                    self.schedule_emails_for_date()
                elif choice == '2':
                    self.view_scheduled_emails()
                elif choice == '3':
                    self.cancel_scheduled_email()
                elif choice == '4':
                    self.send_test_email()
                elif choice == '5':
                    self.start_scheduler_background()
                elif choice == '6':
                    print("\nGoodbye!")
                    self.running = False
                else:
                    print("Invalid choice. Please enter a number between 1 and 6.")
                
                if self.running and choice != '5':
                    input("\nPress Enter to continue...")
                    
            except KeyboardInterrupt:
                print("\n\nExiting...")
                self.running = False
            except Exception as e:
                print(f"\nAn error occurred: {e}")
                input("Press Enter to continue...")
        
        # Cleanup
        self.scheduler.cleanup()

def main():
    """Main entry point"""
    app = WFHEmailApp()
    app.run()

if __name__ == "__main__":
    main()
