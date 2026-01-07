'''
emails all the messages from logs/messages.log.0 so I can add to the training data without having to ssh into the box. 
'''
import os
import logging
import sys
import smtplib
from email.message import EmailMessage

MY_EMAIL = 'schrage.paul@gmail.com'

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

def email_messages(messages):
    msg = EmailMessage()
    msg["From"] = MY_EMAIL
    msg["To"] = MY_EMAIL
    msg["Subject"] = f'messages for '
    msg.set_content("Hello! This email was sent using Python and SMTP.")



# if __name__ == "__main__":
#     messages = read_messages_from_log(log_file_path)
#     if messages:

    # Add your email functionality here






