import socket
import subprocess
import threading

def handle_client(conn, addr):
    print(f"Connected by {addr}")
    
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
            
        print(f"Received command: {data}")
        
        try:
            result = subprocess.run(data, shell=True, capture_output=True, text=True, timeout=15)
            output = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\nExitcode: {result.returncode}"
            conn.sendall(output.encode())
        except subprocess.TimeoutExpired:
            conn.sendall("Command execution timed out".encode())
        except Exception as e:
            conn.sendall(f"Error executing command: {str(e)}".encode())
    
    conn.close()
    print(f"Connection with {addr} closed")

def start_server(host='0.0.0.0', port=5555):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")
    
    try:
        while True:
            conn, addr = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.daemon = True
            client_thread.start()
    except KeyboardInterrupt:
        print("Server shutting down")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
