'''
emails all the messages from logs/messages.log.0 so I can add to the training data without having to ssh into the box. 
'''
import os
import logging
import sys
import json
from collections import defaultdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from emailer import Emailer

# Format of EMAIL_MAPPING IS {'chat name: [list of emails], 'chat name 2': [emails], etc}
EMAIL_MAPPING_RAW = os.getenv('EMAIL_MAPPING')
if not EMAIL_MAPPING_RAW:
    print('no email found')
    sys.exit(1)

try:
    EMAIL_MAPPING = json.loads(EMAIL_MAPPING_RAW)
except json.JSONDecodeError as e:
    print(f'EMAIL_MAPPING is not valid JSON: {e}')
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

def read_messages_from_log(log_file_path) -> dict:
    '''Returns dictionary like: {'chat name': [{message}, {message}, ...]}
    '''
    messages = defaultdict(list)
    try:
        with open(log_file_path) as f:
            for line in f:
                message = json.loads(line)
                message_time = datetime.fromtimestamp(message['ts'], tz=ZoneInfo('America/Los_Angeles'))
                messages[message['chat']].append({'chat': message['chat'], 
                                                  'sender': message['sender'], 
                                                  'body': message['body'], 
                                                  'time': message_time.strftime('%H:%M:%S %Z')})

    except Exception as e:
        logger.error(f"Error reading log file {log_file_path}: {e}")
        messages = None

    for v in messages.values():
        for m in v:
            if not m['body']:
                m['body'] = "(empty message, probably sent a photo)"

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
        for k, v in EMAIL_MAPPING.items():
            if len(messages[k]) == 0:
                continue
            body = '\n'.join(f"{m['time']} - {m['sender']}: {m['body']}" for m in messages[k])
            success = emailer.send(
                sender=sender_email,
                recipients=v,
                subject=f'{k} WhatsApp Messages for {formatted_date}',
                body=body
            )
            
            if success:
                logger.info(f"Successfully sent messages to {v}")
            else:
                logger.error(f"Failed to send email for {k}")
    else:
        logger.info("No messages found to send")
