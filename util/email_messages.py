'''
emails all the messages from logs/messages.log.0 so I can add to the training data without having to ssh into the box. 
'''
import os
import logging
import sys
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage
from emailer import Emailer

MY_EMAIL = os.getenv('MY_EMAIL')
if not MY_EMAIL:
    print('no email found')
    sys.exit(1)

script_path = os.path.dirname(os.path.abspath(__file__))
log_file_path = sys.argv[1] if len(sys.argv) > 1 else f'{script_path}/../logs/messages.log.0'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{script_path}/../logs/email_messages.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def read_messages_from_log(log_file_path):
    try:
        with open(log_file_path) as f:
            messages = f.read()

    except Exception as e:
        logger.error(f"Error reading log file {log_file_path}: {e}")
        messages = None

    return messages


if __name__ == "__main__":
    messages = read_messages_from_log(log_file_path)
    if messages:
        logger.info(f"Read {len(messages)} characters from {log_file_path}")
        
        # Initialize emailer with AWS SES
        emailer = Emailer()
        
        # Get sender email from environment
        sender_email = os.getenv('SENDER_EMAIL')
        if not sender_email:
            logger.error('sender email not set')
            sys.exit(1)
        
        # Get yesterday's date in the format "10 May 2026"
        yesterday = datetime.now() - timedelta(days=1)
        formatted_date = yesterday.strftime("%d %B %Y")
        
        # Send email with message content
        success = emailer.send(
            sender=sender_email,
            recipients=[MY_EMAIL],
            subject=f'WhatsApp Messages for {formatted_date}',
            body=messages
        )
        
        if success:
            logger.info(f"Successfully sent messages to {MY_EMAIL}")
        else:
            logger.error("Failed to send email")
            sys.exit(1)
    else:
        logger.info("No messages found to send")
