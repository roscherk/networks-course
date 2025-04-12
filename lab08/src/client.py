import socket
import random


def compute_checksum(data):
    s = 0
    for i in range(0, len(data), 2):
        w = data[i] + (data[i+1] << 8) if i+1 < len(data) else data[i]
        s = (s + w) & 0xffff
    return ~s & 0xffff


def run_client(server_host, server_port, input_filename, timeout):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    seq = 0
    f = open(input_filename, "rb")
    while True:
        chunk = f.read(512)
        if not chunk:
            chunk = b"__end__"
        csum = compute_checksum(chunk)
        packet = bytes([seq, (csum >> 8) & 0xff, csum & 0xff]) + chunk
        sent = False
        while not sent:
            if random.random() >= 0.3:
                sock.sendto(packet, (server_host, server_port))
            try:
                data, addr = sock.recvfrom(1024)
                if len(data) > 0 and data[0] == seq:
                    seq ^= 1
                    sent = True
            except:
                pass
        if chunk == b"__end__":
            break
    f.close()


if __name__ == "__main__":
    run_client("127.0.0.1", 9999, "file_to_send.bin", 2)
