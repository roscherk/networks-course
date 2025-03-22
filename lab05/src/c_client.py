import socket
import argparse

def start_broadcast_client(port=5555):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_socket.bind(('', port))
    
    print(f"UDP broadcast client listening on port {port}")
    print("Waiting for time broadcasts... (Press Ctrl+C to exit)")
    
    try:
        while True:
            data, addr = client_socket.recvfrom(4096)
            print(f"Received from {addr}: {data.decode()}")
            
    except KeyboardInterrupt:
        print("Client shutting down")
    finally:
        client_socket.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='UDP Broadcast Client')
    parser.add_argument('--port', type=int, default=5555, help='Port to listen on')
    
    args = parser.parse_args()
    start_broadcast_client(args.port)
