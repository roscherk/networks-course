import socket
import random
import sys


def compute_checksum(data):
    s = 0
    for i in range(0, len(data), 2):
        w = data[i] + (data[i+1] << 8) if i+1 < len(data) else data[i]
        s = (s + w) & 0xffff
    return ~s & 0xffff


def verify_checksum(data, cs):
    s = 0
    for i in range(0, len(data), 2):
        w = data[i] + (data[i+1] << 8) if i+1 < len(data) else data[i]
        s = (s + w) & 0xffff
    s = (s + cs) & 0xffff
    return s == 0xffff


def server_mode(host, port, filename):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
    s.settimeout(2)
    f = open(filename, "wb")
    seq = 0
    while True:
        try:
            data, addr = s.recvfrom(1024)
            if random.random() < 0.3:
                continue
            sq = data[0]
            csum = (data[1] << 8) + data[2]
            msg = data[3:]
            if verify_checksum(msg, csum) and sq == seq:
                if msg == b"__end__":
                    s.sendto(bytes([sq]), addr)
                    break
                f.write(msg)
                s.sendto(bytes([sq]), addr)
                seq ^= 1
            else:
                s.sendto(bytes([seq ^ 1]), addr)
        except:
            pass
    f.close()


def client_mode(server_host, server_port, filename):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(2)
    f = open(filename, "rb")
    seq = 0
    while True:
        chunk = f.read(512)
        if not chunk:
            chunk = b"__end__"
        csum = compute_checksum(chunk)
        pkt = bytes([seq, (csum >> 8) & 0xff, csum & 0xff]) + chunk
        sent = False
        while not sent:
            if random.random() >= 0.3:
                s.sendto(pkt, (server_host, server_port))
            try:
                data, addr = s.recvfrom(1024)
                if len(data) > 0 and data[0] == seq:
                    seq ^= 1
                    sent = True
            except:
                pass
        if chunk == b"__end__":
            break
    f.close()


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "server":
        server_mode("0.0.0.0", 9999, "received_from_client.bin")
    else:
        client_mode("127.0.0.1", 9999, "file_to_send.bin")
