import socket
import random

def start_server(host="0.0.0.0", port=9999):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    print(f"Server listening on {host}:{port}")
    while True:
        data, addr = server_socket.recvfrom(1024)
        message = data.decode()
        print(f"Received from {addr} --> ", end="")
        if random.random() < 0.2:
            print("Packet loss")
            continue
        upper_data = message.upper()
        server_socket.sendto(upper_data.encode(), addr)
        print("Reply sent")

if __name__ == "__main__":
    start_server()