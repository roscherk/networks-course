import socket
import ssl
import base64
import argparse
import os
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders

def send_email_with_image(recipient, subject, message, image_path):
    sender = "prokhor03@gmail.com"
    with open("password.txt", "r") as file:
        password = file.readline().strip()
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    
    try:
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject
        
        msg.attach(MIMEText(message, 'plain'))
        
        with open(image_path, 'rb') as img_file:
            img_data = img_file.read()
        
        image_mime = MIMEImage(img_data, name=os.path.basename(image_path))
        msg.attach(image_mime)
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((smtp_server, smtp_port))
        
        response = s.recv(1024).decode()
        print(f"Server: {response}")
        if not response.startswith('2'):
            raise Exception(f"Server did not greet properly: {response}")
        
        hostname = socket.gethostname()
        s.send(f"EHLO {hostname}\r\n".encode())
        response = s.recv(1024).decode()
        print(f"Server: {response}")
        
        s.send("STARTTLS\r\n".encode())
        response = s.recv(1024).decode()
        print(f"Server: {response}")
        
        context = ssl.create_default_context()
        secure_sock = context.wrap_socket(s, server_hostname=smtp_server)
        
        secure_sock.send(f"EHLO {hostname}\r\n".encode())
        response = secure_sock.recv(1024).decode()
        print(f"Server: {response}")
        
        secure_sock.send("AUTH LOGIN\r\n".encode())
        response = secure_sock.recv(1024).decode()
        print(f"Server: {response}")
        
        secure_sock.send(f"{base64.b64encode(sender.encode()).decode()}\r\n".encode())
        response = secure_sock.recv(1024).decode()
        print(f"Server: {response}")
        
        secure_sock.send(f"{base64.b64encode(password.encode()).decode()}\r\n".encode())
        response = secure_sock.recv(1024).decode()
        print(f"Server: {response}")
        
        secure_sock.send(f"MAIL FROM:<{sender}>\r\n".encode())
        response = secure_sock.recv(1024).decode()
        print(f"Server: {response}")
        
        secure_sock.send(f"RCPT TO:<{recipient}>\r\n".encode())
        response = secure_sock.recv(1024).decode()
        print(f"Server: {response}")
        
        secure_sock.send("DATA\r\n".encode())
        response = secure_sock.recv(1024).decode()
        print(f"Server: {response}")
        
        secure_sock.send(msg.as_string().encode() + b"\r\n.\r\n")
        response = secure_sock.recv(1024).decode()
        print(f"Server: {response}")
        
        secure_sock.send("QUIT\r\n".encode())
        response = secure_sock.recv(1024).decode()
        print(f"Server: {response}")
        
        secure_sock.close()
        print(f"Email with image sent successfully to {recipient}")
        
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send email with image attachment')
    parser.add_argument('recipient', help='Email recipient address')
    parser.add_argument('--subject', default='Test email with image', help='Email subject')
    parser.add_argument('--message', default='This is a test email with an image attachment.', help='Email message')
    parser.add_argument('--image', required=True, help='Path to image file')
    
    args = parser.parse_args()
    send_email_with_image(args.recipient, args.subject, args.message, args.image)
