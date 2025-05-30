import socket
import struct
import time
import sys
import os
import select
import argparse

def calculate_checksum(data):
    checksum = 0
    count_to = (len(data) // 2) * 2
    
    for count in range(0, count_to, 2):
        this_val = data[count + 1] * 256 + data[count]
        checksum += this_val
        checksum &= 0xffffffff
    
    if count_to < len(data):
        checksum += data[count_to]
        checksum &= 0xffffffff
    
    checksum = (checksum >> 16) + (checksum & 0xffff)
    checksum += (checksum >> 16)
    answer = ~checksum & 0xffff
    
    answer = ((answer >> 8) & 0xff) | ((answer << 8) & 0xff00)
    return answer

def create_icmp_packet(id, seq):
    header = struct.pack("!BBHHH", 8, 0, 0, id, seq)
    data = struct.pack("!d", time.time())
    
    checksum = calculate_checksum(header + data)
    header = struct.pack("!BBHHH", 8, 0, checksum, id, seq)
    
    return header + data

def parse_icmp_header(packet):
    icmp_header = packet[20:28]
    type, code, checksum, id, seq = struct.unpack("!BBHHH", icmp_header)
    return type, code, checksum, id, seq

def get_icmp_error_message(type, code):
    if type == 0:
        return "Echo Reply"
    elif type == 3:
        if code == 0:
            return "Network Unreachable"
        elif code == 1:
            return "Host Unreachable"
        elif code == 2:
            return "Protocol Unreachable"
        elif code == 3:
            return "Port Unreachable"
        else:
            return f"Destination Unreachable (code {code})"
    elif type == 11:
        return "Time Exceeded"
    else:
        return f"ICMP Type {type}, Code {code}"

def ping(host, count=4):
    try:
        dest_addr = socket.gethostbyname(host)
        print(f"PING {host} ({dest_addr})")
    except socket.gaierror:
        print(f"Unknown host: {host}")
        return
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    except socket.error as e:
        if e.errno == 1:
            print("Error: ICMP messages can only be sent from processes running as root.")
            print("Try running the script with sudo.")
            return
        raise
    
    pid = os.getpid() & 0xFFFF
    sent = 0
    received = 0
    rtts = []
    
    for seq in range(count):
        sent += 1
        packet = create_icmp_packet(pid, seq)
        
        sock.sendto(packet, (dest_addr, 0))
        
        try:
            ready = select.select([sock], [], [], 1)
            if not ready[0]:
                print("Request timed out")
                continue
            
            recv_packet, addr = sock.recvfrom(1024)
            recv_time = time.time()
            
            icmp_type, icmp_code, _, icmp_id, icmp_seq = parse_icmp_header(recv_packet)
            
            if icmp_type == 0 and icmp_id == pid:
                received += 1
                data = recv_packet[28:36]
                send_timestamp = struct.unpack("!d", data)[0]
                rtt = (recv_time - send_timestamp) * 1000
                rtts.append(rtt)
                
                print(f"64 bytes from {addr[0]}: icmp_seq={icmp_seq} ttl={recv_packet[8]} time={rtt:.3f} ms")
                
                if len(rtts) > 0:
                    min_rtt = min(rtts)
                    max_rtt = max(rtts)
                    avg_rtt = sum(rtts) / len(rtts)
                    loss = ((sent - received) / sent) * 100
                    print(f"rtt min/avg/max = {min_rtt:.3f}/{avg_rtt:.3f}/{max_rtt:.3f} ms, {loss:.1f}% packet loss")
            
            elif icmp_type != 0:
                error_message = get_icmp_error_message(icmp_type, icmp_code)
                print(f"Error from {addr[0]}: {error_message}")
                
        except socket.timeout:
            print("Request timed out")
        
        if seq < count - 1:
            time.sleep(1)
    
    loss = ((sent - received) / sent) * 100
    print(f"\n--- {host} ping statistics ---")
    print(f"{sent} packets transmitted, {received} packets received, {loss:.1f}% packet loss")
    
    if rtts:
        min_rtt = min(rtts)
        max_rtt = max(rtts)
        avg_rtt = sum(rtts) / len(rtts)
        print(f"rtt min/avg/max = {min_rtt:.3f}/{avg_rtt:.3f}/{max_rtt:.3f} ms")
    
    sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Python ICMP Ping Implementation")
    parser.add_argument("host", help="Target host to ping")
    parser.add_argument("-c", "--count", type=int, default=4, help="Number of packets to send")
    
    args = parser.parse_args()
    
    if os.geteuid() != 0:
        print("Error: This script requires root privileges.")
        print("Try running with sudo.")
        sys.exit(1)
    
    ping(args.host, args.count)
