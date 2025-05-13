import socket
import sys

def run_client(host='::1', port=8888):
    client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((host, port))
        print(f"Connected to IPv6 echo server at [{host}]:{port}")
        
        while True:
            message = input("Enter message (or 'exit' to quit): ")
            
            if message.lower() == 'exit':
                break
                
            client_socket.send(message.encode('utf-8'))
            
            response = client_socket.recv(1024).decode('utf-8')
            print(f"Server response: {response}")
            
    except ConnectionRefusedError:
        print(f"Could not connect to server at [{host}]:{port}")
    except KeyboardInterrupt:
        print("\nClient shutting down...")
    finally:
        client_socket.close()

if __name__ == "__main__":
    host = '::1'
    port = 8888
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
        
    run_client(host, port)
