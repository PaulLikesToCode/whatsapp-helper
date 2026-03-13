import boto3
from botocore.exceptions import ClientError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

AWS_REGION = os.getenv('AWS_REGION')


class Emailer:
    def __init__(self, aws_region=AWS_REGION):
        """
        Initialize the Emailer with AWS SES.
        
        Args:
            aws_region: AWS region for SES (default: us-east-1)
        """
        self.aws_region = aws_region
        self.ses_client = boto3.client('ses', region_name=aws_region)

    def send(self, sender:str, recipients:list, subject:str, body:str, html=False):
        """
        Send a basic email using AWS SES.
        
        Args:
            sender: Sender email address (must be verified in SES)
            recipients: Recipient email addresses
            subject: Email subject
            body: Email body (plain text or HTML)
            html: If True, body is treated as HTML
        """
        try:
            # Prepare the email content
            body_content = {
                'Text': {
                    'Charset': 'UTF-8',
                    'Data': body,
                }
            }
            
            if html:
                body_content['Html'] = {
                    'Charset': 'UTF-8',
                    'Data': body,
                }
            
            # Send email via SES
            response = self.ses_client.send_email(
                Destination={
                    'ToAddresses': recipients,
                },
                Message={
                    'Body': body_content,
                    'Subject': {
                        'Charset': 'UTF-8',
                        'Data': subject,
                    },
                },
                Source=sender,
            )
            
            print(f"Email sent successfully to {recipients}. Message ID: {response['MessageId']}")
            return True
            
        except ClientError as e:
            print(f"Failed to send email: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    def send_with_attachment(self, sender, recipient, subject, body, file_path):
        """
        Send an email with an attachment using AWS SES raw email.
        
        Args:
            sender: Sender email address (must be verified in SES)
            recipient: Recipient email address
            subject: Email subject
            body: Email body
            file_path: Path to the file to attach

        TODO: update with multiple recipients, but I'm not planning on attachments atm.
        """
        
        try:
            # Create multipart message
            msg = MIMEMultipart()
            msg["From"] = sender
            msg["To"] = recipient
            msg["Subject"] = subject
            
            # Attach body
            msg.attach(MIMEText(body, "plain"))
            
            # Attach file
            with open(file_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            filename = os.path.basename(file_path)
            part.add_header("Content-Disposition", f"attachment; filename= {filename}")
            msg.attach(part)
            
            # Send raw email via SES
            response = self.ses_client.send_raw_email(
                Source=sender,
                Destinations=[recipient],
                RawMessage={
                    'Data': msg.as_string(),
                }
            )
            
            print(f"Email with attachment sent successfully to {recipient}. Message ID: {response['MessageId']}")
            return True
            
        except ClientError as e:
            print(f"Failed to send email: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False