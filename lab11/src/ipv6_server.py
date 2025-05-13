import socket
import sys

def run_server(host='::1', port=8888):
    server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"IPv6 Echo server started on [{host}]:{port}")
        
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connection from: [{client_address[0]}]:{client_address[1]}")
            
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                print(f"Received: {data}")
                
                upper_data = data.upper()
                client_socket.send(upper_data.encode('utf-8'))
                print(f"Sent: {upper_data}")
                
            finally:
                client_socket.close()
                
    except KeyboardInterrupt:
        print("\nServer shutting down...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    host = '::1'
    port = 8888
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
        
    run_server(host, port)
