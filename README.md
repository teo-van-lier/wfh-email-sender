# WFH Email Automation System

Automated email system for sending work-from-home start and stop notifications through Outlook.

## Features

- **Automatic Scheduling**: Plan emails days or weeks in advance
- **Smart Timing**: Morning emails sent randomly between 7:45-8:10 AM
- **Calculated Stop Times**: Stop emails sent approximately 9 hours after start
- **Outlook Integration**: Uses your existing Outlook account
- **Dutch Language Support**: Email content in Dutch as specified
- **Simple CLI**: Easy-to-use command-line interface
- **Persistent Storage**: SQLite database for scheduled emails

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure Microsoft Outlook is installed and configured on your system.

## Usage

### Running the Application

```bash
python main.py
```

### Main Menu Options

1. **Schedule emails for a date**: Plan start and stop emails for a specific day
2. **View scheduled emails**: See all scheduled emails and their status
3. **Cancel scheduled email**: Remove a scheduled email
4. **Start scheduler**: Run the background service that sends emails automatically
5. **Exit**: Close the application

### Daily Workflow

1. Run `python main.py`
2. Choose option 1 to schedule emails for your work days
3. Choose option 4 to start the background scheduler
4. The system will automatically send emails at the scheduled times

### Email Content

**Start Email:**
- Subject: `Start remote werk DD/MM/YYYY`
- Body: `Ik start nu met werken van thuis.` followed by signature

**Stop Email:**
- Subject: `Einde remote werk DD/MM/YYYY`
- Body: `Ik stop nu met werken van thuis.` followed by signature

## File Structure

```
wfh-email/
├── main.py              # Main CLI interface
├── email_sender.py       # Outlook integration
├── scheduler.py         # Database and scheduling logic
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── wfh_emails.db       # SQLite database (auto-created)
├── wfh_email.log       # Log file (auto-created)
└── README.md           # This file
```

## Configuration

You can modify the following settings in `config.py`:

- Email addresses (sender/recipient)
- Time windows for morning emails
- Work duration for calculating stop times
- Email templates and content

## Troubleshooting

### Common Issues

1. **Outlook not responding**: Ensure Outlook is properly installed and you can send emails manually
2. **Permission errors**: Make sure the script has permission to create files in the directory
3. **Database errors**: Delete `wfh_emails.db` and restart the application

### Logs

Check `wfh_email.log` for detailed error messages and operation logs.

## Requirements

- Windows operating system
- Python 3.7+
- Microsoft Outlook
- pywin32 package

## Security Notes

- The script uses your existing Outlook configuration
- Email credentials are not stored in the application
- All data is stored locally in the SQLite database
