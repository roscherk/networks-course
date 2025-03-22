import socket
import argparse

def send_command(host, port, command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            print(f"Connected to {host}:{port}")
            
            s.sendall(command.encode())
            print(f"Sent command: {command}")
            
            response = s.recv(4096).decode()
            print("\nServer response:")
            print("=" * 50)
            print(response)
            print("=" * 50)
            
        except ConnectionRefusedError:
            print(f"Connection to {host}:{port} failed. Make sure the server is running.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Execute commands on a remote server')
    parser.add_argument('--host', default='localhost', help='Server hostname or IP')
    parser.add_argument('--port', type=int, default=5555, help='Server port')
    parser.add_argument('command', help='Command to execute on server')
    
    args = parser.parse_args()
    send_command(args.host, args.port, args.command)
