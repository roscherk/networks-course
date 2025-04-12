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


def run_client(server_host, server_port, input_filename, timeout):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    seq = 0
    
    try:
        with open(input_filename, "rb") as f:
            file_size = 0
            total_sent = 0
            print(f"Client started, sending {input_filename} to {server_host}:{server_port}")
            
            while True:
                chunk = f.read(512)
                if not chunk:
                    chunk = b"__end__"
                    
                csum = compute_checksum(chunk)
                packet = bytes([seq, (csum >> 8) & 0xff, csum & 0xff]) + chunk
                sent = False
                retry_count = 0
                
                print(f"Sending packet with seq={seq}, size={len(chunk)} bytes")
                
                while not sent and retry_count < 10:
                    if random.random() >= 0.3:
                        sock.sendto(packet, (server_host, server_port))
                        print(f"Packet sent, waiting for ACK...")
                    else:
                        print("Packet dropped (simulated loss)...")
                    
                    try:
                        data, addr = sock.recvfrom(1024)
                        if len(data) > 0 and data[0] == seq:
                            if chunk != b"__end__":
                                total_sent += len(chunk)
                            seq ^= 1
                            sent = True
                            print(f"ACK received, seq={data[0]}")
                        else:
                            print(f"Wrong ACK received, expected={seq}, got={data[0]}")
                    except socket.timeout:
                        print(f"Timeout, retransmitting... (retry {retry_count+1}/10)")
                        retry_count += 1
                
                if not sent:
                    print("Max retries reached, giving up on this packet")
                    raise Exception("Failed to send packet after maximum retries")
                
                if chunk == b"__end__":
                    print(f"Transfer complete! Total bytes sent: {total_sent}")
                    break

    except FileNotFoundError:
        print(f"Error: File {input_filename} not found")
    except Exception as e:
        print(f"Error during file transfer: {str(e)}")
    finally:
        sock.close()
        print("Socket closed")


if __name__ == "__main__":
    import sys
    
    server_host = "127.0.0.1"
    server_port = 9999
    input_file = "file_to_send.bin"
    timeout = 2
    
    if len(sys.argv) > 1:
        server_host = sys.argv[1]
    if len(sys.argv) > 2:
        server_port = int(sys.argv[2])
    if len(sys.argv) > 3:
        input_file = sys.argv[3]
    if len(sys.argv) > 4:
        timeout = float(sys.argv[4])
        
    print(f"Using: Server={server_host}:{server_port}, File={input_file}, Timeout={timeout}s")
    run_client(server_host, server_port, input_file, timeout)
