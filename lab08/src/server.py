import socket
import random


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


def run_server(host, port, output_filename, timeout):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    expected_seq = 0
    f = open(output_filename, "wb")
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            if random.random() < 0.3:
                continue
            seq = data[0]
            csum = (data[1] << 8) + data[2]
            payload = data[3:]
            if verify_checksum(payload, csum) and seq == expected_seq:
                if payload == b"__end__":
                    ack = bytes([seq])
                    if random.random() >= 0.3:
                        sock.sendto(ack, addr)
                    f.close()
                    break
                f.write(payload)
                ack = bytes([seq])
                if random.random() >= 0.3:
                    sock.sendto(ack, addr)
                expected_seq ^= 1
            else:
                ack = bytes([(expected_seq ^ 1)])
                if random.random() >= 0.3:
                    sock.sendto(ack, addr)
        except socket.timeout:
            pass


if __name__ == "__main__":
    run_server("0.0.0.0", 9999, "received.bin", 2)
