import socket
import ssl
import base64
import argparse

def send_email_via_socket(recipient, subject, message):
    sender = "prokhor03@gmail.com"
    with open("password.txt", "r") as file:
        password = file.readline().strip()
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    
    try:
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
        
        email_content = f"From: {sender}\r\n"
        email_content += f"To: {recipient}\r\n"
        email_content += f"Subject: {subject}\r\n"
        email_content += "\r\n"  
        email_content += f"{message}\r\n"
        email_content += ".\r\n"  
        
        secure_sock.send(email_content.encode())
        response = secure_sock.recv(1024).decode()
        print(f"Server: {response}")
        
        secure_sock.send("QUIT\r\n".encode())
        response = secure_sock.recv(1024).decode()
        print(f"Server: {response}")
        
        secure_sock.close()
        print(f"Email sent successfully to {recipient}")
        
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send email using SMTP protocol directly')
    parser.add_argument('recipient', help='Email recipient address')
    parser.add_argument('--subject', default='Test email from socket', help='Email subject')
    parser.add_argument('--message', default='This is a test email sent using SMTP sockets.', help='Email message')
    
    args = parser.parse_args()
    send_email_via_socket(args.recipient, args.subject, args.message)
