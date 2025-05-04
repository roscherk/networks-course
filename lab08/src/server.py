import socket
import random
import time


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
    sock.settimeout(timeout)
    expected_seq = 0
    f = open(output_filename, "wb")
    print(f"Server started on {host}:{port}, output file: {output_filename}")
    print(f"Waiting for data...")
    
    total_bytes_received = 0
    
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            if random.random() < 0.3:
                print(f"Packet dropped (simulated loss)")
                continue
                
            seq = data[0]
            csum = (data[1] << 8) + data[2]
            payload = data[3:]
            print(f"Received packet: seq={seq}, size={len(payload)} bytes")
            
            if verify_checksum(payload, csum) and seq == expected_seq:
                if payload == b"__end__":
                    print(f"End of transmission marker received")
                    ack = bytes([seq])
                    if random.random() >= 0.3:
                        sock.sendto(ack, addr)
                        print(f"Sent ACK {seq}")
                    else:
                        print(f"ACK {seq} dropped (simulated loss)")
                    break
                    
                f.write(payload)
                total_bytes_received += len(payload)
                print(f"Wrote {len(payload)} bytes to file, total: {total_bytes_received}")
                
                ack = bytes([seq])
                if random.random() >= 0.3:
                    sock.sendto(ack, addr)
                    print(f"Sent ACK {seq}")
                else:
                    print(f"ACK {seq} dropped (simulated loss)")
                expected_seq ^= 1
            else:
                print(f"Checksum validation failed or wrong sequence number. Expected seq={expected_seq}, got seq={seq}")
                ack = bytes([expected_seq ^ 1])
                if random.random() >= 0.3:
                    sock.sendto(ack, addr)
                    print(f"Sent NACK {expected_seq ^ 1}")
                else:
                    print(f"NACK {expected_seq ^ 1} dropped (simulated loss)")
        except socket.timeout:
            print("Timeout while waiting for data")
    
    f.close()
    print(f"Transfer complete, total bytes received: {total_bytes_received}")
    print(f"Output file closed")


if __name__ == "__main__":
    run_server("0.0.0.0", 9999, "received.bin", 2)
