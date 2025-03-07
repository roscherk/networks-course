import sys
import socket
import os
import threading
import traceback
from threading import Semaphore

def handle_client(conn, addr, semaphore=None):
    try:
        print(f"Connected by {addr}")
        request = conn.recv(1024).decode()
        print(f"Request from {addr}:")
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
    except Exception as e:
        print("Error handling client:", e)
        traceback.print_exc()
    finally:
        conn.close()
        if semaphore:
            semaphore.release()

def main():
    if len(sys.argv) not in [2, 3]:
        print("Usage: python server_multi.py <server_port> [concurrency_level]")
        sys.exit(1)
    port = int(sys.argv[1])
    
    semaphore = None
    if len(sys.argv) == 3:
        concurrency_level = int(sys.argv[2])
        semaphore = Semaphore(concurrency_level)
        print(f"[Multi-threaded] Concurrency level set to {concurrency_level}")

    host = ''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    print(f"[Multi-threaded] Listening on port {port}...")

    try:
        while True:
            conn, addr = s.accept()
            if semaphore:
                semaphore.acquire()
            t = threading.Thread(target=handle_client, args=(conn, addr, semaphore))
            t.start()
    except KeyboardInterrupt:
        print("\nServer is shutting down.")
    finally:
        s.close()

if __name__ == '__main__':
    main()
