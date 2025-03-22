import socket
import time
import datetime

def start_broadcast_server(port=5555):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server_socket.settimeout(0.2)
    
    print(f"Broadcasting time server started on port {port}")
    try:
        while True:
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message = f"Server time: {current_time}"
            
            server_socket.sendto(message.encode(), ('<broadcast>', port))
            print(f"Broadcasted: {message}")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Server shutting down")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_broadcast_server()
