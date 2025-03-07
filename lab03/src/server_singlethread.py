import sys
import socket
import os

def main():
    if len(sys.argv) != 2:
        print("Usage: python server_single.py <server_port>")
        sys.exit(1)
    port = int(sys.argv[1])
    host = ''

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(5)
        print(f"[Single-threaded] Listening on port {port}...")
        
        try:
            while True:
                conn, addr = s.accept()
                with conn:
                    print(f"Connected by {addr}")
                    request = conn.recv(1024).decode()
                    print("Request received:")
                    print(request)
                    
                    lines = request.splitlines()
                    if lines:
                        request_line = lines[0]
                        parts = request_line.split()
                        if len(parts) >= 2 and parts[0] == "GET":
                            filename = parts[1].lstrip('/')
                            if os.path.isfile(filename):
                                with open(filename, 'rb') as f:
                                    content = f.read()
                                header = "HTTP/1.1 200 OK\r\n"
                                header += f"Content-Length: {len(content)}\r\n"
                                header += "Connection: close\r\n"
                                header += "\r\n"
                                conn.sendall(header.encode() + content)
                            else:
                                response = ("HTTP/1.1 404 Not Found\r\n"
                                            "Connection: close\r\n"
                                            "\r\n"
                                            "404 Not Found")
                                conn.sendall(response.encode())
                        else:
                            response = ("HTTP/1.1 400 Bad Request\r\n"
                                        "Connection: close\r\n"
                                        "\r\n"
                                        "Only GET method is supported.")
                            conn.sendall(response.encode())
                    conn.close()
        except KeyboardInterrupt:
            print("\nServer is shutting down.")

if __name__ == '__main__':
    main()
