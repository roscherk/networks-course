import socket
import struct
import time
import sys
import select

def calculate_checksum(data):
    sum = 0
    countTo = (len(data) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = data[count+1] * 256 + data[count]
        sum = sum + thisVal
        sum = sum & 0xffffffff
        count = count + 2

    if countTo < len(data):
        sum = sum + data[-1]
        sum = sum & 0xffffffff

    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def create_icmp_packet(id_num, seq_num):
    header = struct.pack("bbHHh", 8, 0, 0, id_num, seq_num)
    data = struct.pack("d", time.time())
    
    checksum = calculate_checksum(header + data)
    header = struct.pack("bbHHh", 8, 0, socket.htons(checksum), id_num, seq_num)
    
    return header + data

def traceroute(destination, max_hops=30, timeout=1, num_packets=3):
    try:
        dest_ip = socket.gethostbyname(destination)
        print(f"Tracing route to {destination} [{dest_ip}] over a maximum of {max_hops} hops:")
        print(f"Sending {num_packets} packets per hop")
        print("-" * 60)
    except socket.gaierror:
        print(f"Could not resolve hostname: {destination}")
        return
    
    try:
        icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        icmp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, 1)
    except socket.error as e:
        if e.errno == 1:
            print("Operation not permitted: ICMP messages can only be sent from processes running as root.")
            return
        raise
    
    for ttl in range(1, max_hops + 1):
        print(f"{ttl:2d}", end=" ")
        
        icmp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
        address = None
        
        for i in range(num_packets):
            packet_id = id(destination) & 0xFFFF
            packet_seq = ttl + i
            packet = create_icmp_packet(packet_id, packet_seq)
            
            try:
                icmp_socket.sendto(packet, (dest_ip, 0))
                start_time = time.time()
                
                ready = select.select([icmp_socket], [], [], timeout)
                
                if ready[0]:
                    recv_packet, addr = icmp_socket.recvfrom(1024)
                    end_time = time.time()
                    
                    rtt = (end_time - start_time) * 1000
                    
                    ip_header = recv_packet[:20]
                    icmp_header = recv_packet[20:28]
                    
                    icmp_type = icmp_header[0]
                    
                    if address is None:
                        address = addr[0]
                    
                    print(f"{rtt:.2f} ms", end=" ")
                    
                    if icmp_type == 0 and addr[0] == dest_ip:
                        print(f"\nReached destination: {addr[0]}")
                        return
                else:
                    print("* ", end="")
            except socket.error:
                print("Socket error", end=" ")
        
        if address:
            try:
                hostname = socket.gethostbyaddr(address)[0]
                print(f"\n    {address} [{hostname}]")
            except socket.herror:
                print(f"\n    {address}")
        else:
            print("\n    Request timed out.")
    
    print("\nTrace complete.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python traceroute.py <destination> [max_hops] [timeout] [packets_per_hop]")
        sys.exit(1)
    
    destination = sys.argv[1]
    max_hops = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    timeout = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    num_packets = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    
    traceroute(destination, max_hops, timeout, num_packets)
