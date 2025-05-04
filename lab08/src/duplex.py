import socket
import random
import sys
import time
import os


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


def server_send_file(sock, addr, filename, timeout=2):
    sock.settimeout(timeout)
    print(f"Server: sending file {filename} to {addr}")
    
    try:
        f = open(filename, "rb")
        seq = 0
        total_sent = 0
        
        while True:
            chunk = f.read(512)
            if not chunk:
                chunk = b"__end__"
                
            csum = compute_checksum(chunk)
            pkt = bytes([seq, (csum >> 8) & 0xff, csum & 0xff]) + chunk
            sent = False
            retry_count = 0
            
            print(f"Server: sending packet with seq={seq}, size={len(chunk)} bytes")
            
            while not sent and retry_count < 10:
                if random.random() >= 0.3:
                    sock.sendto(pkt, addr)
                    print(f"Server: packet sent, waiting for ACK...")
                else:
                    print(f"Server: packet dropped (simulated loss)")
                
                try:
                    data, client_addr = sock.recvfrom(1024)
                    if len(data) > 0 and data[0] == seq:
                        if chunk != b"__end__":
                            total_sent += len(chunk)
                        seq ^= 1
                        sent = True
                        print(f"Server: ACK received, seq={data[0]}")
                    else:
                        print(f"Server: wrong ACK received, expected={seq}, got={data[0]}")
                except socket.timeout:
                    print(f"Server: timeout, retransmitting... (retry {retry_count+1}/10)")
                    retry_count += 1
            
            if not sent:
                print(f"Server: max retries reached, giving up on this packet")
                return False
                
            if chunk == b"__end__":
                print(f"Server: transfer complete! Total sent: {total_sent} bytes")
                break
        
        f.close()
        return True
        
    except Exception as e:
        print(f"Server error during file sending: {str(e)}")
        return False


def server_receive_file(sock, output_filename, timeout=2):
    print(f"Server: receiving file to {output_filename}")
    seq = 0
    f = open(output_filename, "wb")
    total_received = 0
    
    try:
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                if random.random() < 0.3:
                    print(f"Server: packet dropped (simulated loss)")
                    continue
                    
                sq = data[0]
                csum = (data[1] << 8) + data[2]
                msg = data[3:]
                print(f"Server: received packet: seq={sq}, size={len(msg)} bytes")
                
                if verify_checksum(msg, csum) and sq == seq:
                    if msg == b"__end__":
                        print(f"Server: end of transmission marker received")
                        sock.sendto(bytes([sq]), addr)
                        print(f"Server: sent ACK {sq}")
                        break
                    
                    f.write(msg)
                    total_received += len(msg)
                    print(f"Server: wrote {len(msg)} bytes to file, total: {total_received}")
                    
                    sock.sendto(bytes([sq]), addr)
                    print(f"Server: sent ACK {sq}")
                    seq ^= 1
                else:
                    print(f"Server: checksum validation failed or wrong sequence number")
                    sock.sendto(bytes([seq ^ 1]), addr)
                    print(f"Server: sent NACK {seq ^ 1}")
            except socket.timeout:
                print(f"Server: timeout while waiting for data")
                
    except Exception as e:
        print(f"Server error during file receiving: {str(e)}")
        f.close()
        return False
        
    f.close()
    print(f"Server: transfer complete, total received: {total_received} bytes")
    return True


def client_send_file(sock, server_addr, filename, timeout=2):
    sock.settimeout(timeout)
    print(f"Client: sending file {filename} to server")
    
    try:
        f = open(filename, "rb")
        seq = 0
        total_sent = 0
        
        while True:
            chunk = f.read(512)
            if not chunk:
                chunk = b"__end__"
                
            csum = compute_checksum(chunk)
            pkt = bytes([seq, (csum >> 8) & 0xff, csum & 0xff]) + chunk
            sent = False
            retry_count = 0
            
            print(f"Client: sending packet with seq={seq}, size={len(chunk)} bytes")
            
            while not sent and retry_count < 10:
                if random.random() >= 0.3:
                    sock.sendto(pkt, server_addr)
                    print(f"Client: packet sent, waiting for ACK...")
                else:
                    print(f"Client: packet dropped (simulated loss)")
                
                try:
                    data, addr = sock.recvfrom(1024)
                    if len(data) > 0 and data[0] == seq:
                        if chunk != b"__end__":
                            total_sent += len(chunk)
                        seq ^= 1
                        sent = True
                        print(f"Client: ACK received, seq={data[0]}")
                    else:
                        print(f"Client: wrong ACK received, expected={seq}, got={data[0]}")
                except socket.timeout:
                    print(f"Client: timeout, retransmitting... (retry {retry_count+1}/10)")
                    retry_count += 1
            
            if not sent:
                print(f"Client: max retries reached, giving up on this packet")
                return False
                
            if chunk == b"__end__":
                print(f"Client: transfer complete! Total sent: {total_sent} bytes")
                break
        
        f.close()
        return True
        
    except Exception as e:
        print(f"Client error during file sending: {str(e)}")
        return False


def client_receive_file(sock, server_addr, output_filename, timeout=2):
    sock.settimeout(timeout)
    print(f"Client: requesting file from server")
    
    request_pkt = b"REQUEST_FILE"
    retry_count = 0
    request_sent = False
    
    while not request_sent and retry_count < 5:
        try:
            sock.sendto(request_pkt, server_addr)
            print(f"Client: file request sent, waiting for response...")
            request_sent = True
        except:
            print(f"Client: error sending file request, retrying...")
            retry_count += 1
            time.sleep(0.5)
    
    if not request_sent:
        print(f"Client: failed to send file request")
        return False
    
    print(f"Client: receiving file to {output_filename}")
    seq = 0
    f = open(output_filename, "wb")
    total_received = 0
    last_data_time = time.time()
    max_wait_time = 10  # Maximum time to wait without receiving data
    
    try:
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                last_data_time = time.time()
                
                if random.random() < 0.3:
                    print(f"Client: packet dropped (simulated loss)")
                    continue
                    
                sq = data[0]
                csum = (data[1] << 8) + data[2]
                msg = data[3:]
                print(f"Client: received packet: seq={sq}, size={len(msg)} bytes")
                
                if verify_checksum(msg, csum) and sq == seq:
                    if msg == b"__end__":
                        print(f"Client: end of transmission marker received")
                        sock.sendto(bytes([sq]), addr)
                        print(f"Client: sent ACK {sq}")
                        break
                    
                    f.write(msg)
                    total_received += len(msg)
                    print(f"Client: wrote {len(msg)} bytes to file, total: {total_received}")
                    
                    sock.sendto(bytes([sq]), addr)
                    print(f"Client: sent ACK {sq}")
                    seq ^= 1
                else:
                    print(f"Client: checksum validation failed or wrong sequence number")
                    sock.sendto(bytes([seq ^ 1]), addr)
                    print(f"Client: sent NACK {seq ^ 1}")
            except socket.timeout:
                print(f"Client: timeout while waiting for data")
                if time.time() - last_data_time > max_wait_time:
                    print(f"Client: no data received for {max_wait_time} seconds, aborting")
                    break
                
    except Exception as e:
        print(f"Client error during file receiving: {str(e)}")
        f.close()
        return False
        
    f.close()
    print(f"Client: transfer complete, total received: {total_received} bytes")
    return True


def server_mode(host, port, recv_filename, send_filename, timeout=2):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
    s.settimeout(timeout)
    print(f"Server started on {host}:{port}")
    print(f"Waiting for client connection...")
    
    try:
        data, addr = s.recvfrom(1024)
        print(f"Client connected from {addr}")
        
        if data == b"REQUEST_FILE":
            print(f"Received file request from client")
            server_send_file(s, addr, send_filename, timeout)
        else:
            print(f"Receiving file from client...")
            server_receive_file(s, recv_filename, timeout)
            
            if os.path.exists(send_filename):
                time.sleep(1)  # Give the client time to prepare
                print(f"Sending file to client...")
                server_send_file(s, addr, send_filename, timeout)
    except Exception as e:
        print(f"Server error: {str(e)}")
    finally:
        s.close()
        print(f"Server socket closed")


def client_mode(server_host, server_port, send_filename, recv_filename, timeout=2):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)
    server_addr = (server_host, server_port)
    print(f"Connecting to server at {server_host}:{server_port}")
    
    try:
        # First, send file to server if it exists
        if os.path.exists(send_filename):
            client_send_file(s, server_addr, send_filename, timeout)
        
        # Then receive file from server
        time.sleep(1)  # Give the server time to prepare
        client_receive_file(s, server_addr, recv_filename, timeout)
        
    except Exception as e:
        print(f"Client error: {str(e)}")
    finally:
        s.close()
        print(f"Client socket closed")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python duplex.py [server|client] [timeout]")
        sys.exit(1)
        
    mode = sys.argv[1]
    timeout = 2  # Default timeout
    
    if len(sys.argv) >= 3:
        try:
            timeout = float(sys.argv[2])
            print(f"Using custom timeout: {timeout} seconds")
        except:
            pass
    
    if mode == "server":
        server_mode("0.0.0.0", 9999, "received_from_client.bin", "server_to_client.bin", timeout)
    else:
        client_mode("127.0.0.1", 9999, "file_to_send.bin", "received_from_server.bin", timeout)
