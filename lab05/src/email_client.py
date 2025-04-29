import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import argparse

def send_email(recipient, subject, message, message_type):
    sender = "prokhor03@gmail.com"
    with open("password.txt", "r") as file:
        password = file.readline()
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject
    
    if message_type.lower() == 'html':
        msg.attach(MIMEText(message, 'html'))
    else:
        msg.attach(MIMEText(message, 'plain'))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login("prokhor03@gmail.com", password)
        server.send_message(msg)
        server.quit()
        print(f"Email sent successfully to {recipient}")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send email to recipient')
    parser.add_argument('recipient', help='Email recipient address')
    parser.add_argument('--subject', default='Test email', help='Email subject')
    parser.add_argument('--message', default='This is a test email', help='Email message')
    parser.add_argument('--type', choices=['txt', 'html'], default='txt', help='Message format')
    
    args = parser.parse_args()
    
    if args.type == 'html':
        if args.message == 'This is a test email':
            args.message = '<html><body><h1>Test Email</h1><p>This is a <b>HTML</b> test email.</p></body></html>'
    
    send_email(args.recipient, args.subject, args.message, args.type)
