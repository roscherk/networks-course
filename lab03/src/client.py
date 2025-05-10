import sys
import socket

def main():
    if len(sys.argv) != 4:
        print("Usage: python client.py <server_host> <server_port> <filename>")
        sys.exit(1)
    
    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    filename = sys.argv[3]

    request = f"GET /{filename} HTTP/1.1\r\n"
    request += f"Host: {server_host}\r\n"
    request += "Connection: close\r\n"
    request += "\r\n"
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_host, server_port))
        s.sendall(request.encode())
        response = b""
        while True:
            data = s.recv(1024)
            if not data:
                break
            response += data
        print("Response received:")
        print(response.decode(errors='replace'))

if __name__ == '__main__':
    main()
