import socket
import time
import sys

def start_client(server_host="127.0.0.1", server_port=9999):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(1.0)
    for seq_num in range(1, 11):
        send_time = time.time()
        message = f"Ping {seq_num} {send_time}"
        try:
            client_socket.sendto(message.encode(), (server_host, server_port))
            start_wait = time.time()
            data, addr = client_socket.recvfrom(1024)
            end_wait = time.time()
            rtt = end_wait - start_wait
            print(f"Reply received: {data.decode()}, RTT = {rtt:.4f}s")
        except socket.timeout:
            print("Request timed out")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        start_client(sys.argv[1], int(sys.argv[2]))
    else:
        start_client()
