import socket
import os
import re
import sys

class FTPClient:
    def __init__(self):
        self.control_socket = None
        self.data_socket = None
        self.encoding = "utf-8"
        
    def connect(self, server, port=21):
        try:
            self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.control_socket.connect((server, port))
            response = self.get_response()
            print(f"Соединение с {server}:{port} установлено")
            return True
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            return False
    
    def login(self, username="anonymous", password="anonymous@example.com"):
        if not self.control_socket:
            print("Нет соединения")
            return False
        
        self.send_command(f"USER {username}")
        response = self.get_response()
        
        if response.startswith('331'):
            self.send_command(f"PASS {password}")
            response = self.get_response()
            
            if response.startswith('230'):
                print(f"Успешная авторизация")
                return True
        
        print(f"Ошибка авторизации")
        return False
    
    def send_command(self, command):
        if not self.control_socket:
            return False
        
        cmd = command + "\r\n"
        self.control_socket.send(cmd.encode(self.encoding))
        return True
    
    def get_response(self):
        if not self.control_socket:
            return "425 Соединение не установлено"
        
        response = ""
        while True:
            data = self.control_socket.recv(8192).decode(self.encoding, errors='replace')
            if not data:
                break
            response += data
            if re.search(r'\d{3} ', response) or re.search(r'\r\n\d{3} ', response):
                break
        
        return response.strip()
    
    def enter_passive_mode(self):
        self.send_command("PASV")
        response = self.get_response()
        
        if response.startswith('227'):
            pattern = r'(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)'
            match = re.search(pattern, response)
            if match:
                h1, h2, h3, h4, p1, p2 = [int(x) for x in match.groups()]
                ip = f"{h1}.{h2}.{h3}.{h4}"
                port = (p1 * 256) + p2
                
                self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.data_socket.connect((ip, port))
                return True
        
        print("Ошибка пассивного режима")
        return False
    
    def list_directory(self, path="."):
        if not self.enter_passive_mode():
            return None
        
        self.send_command(f"LIST {path}")
        response = self.get_response()
        
        if response.startswith('150') or response.startswith('125'):
            data = b""
            while True:
                chunk = self.data_socket.recv(8192)
                if not chunk:
                    break
                data += chunk
            
            self.data_socket.close()
            self.data_socket = None
            
            self.get_response()
            return data.decode(self.encoding, errors='replace')
        
        return None
    
    def download_file(self, remote_file, local_file=None):
        if not local_file:
            local_file = os.path.basename(remote_file)
        
        if not self.enter_passive_mode():
            return False
        
        self.send_command("TYPE I")
        self.get_response()
        
        self.send_command(f"RETR {remote_file}")
        response = self.get_response()
        
        if response.startswith('150') or response.startswith('125'):
            with open(local_file, 'wb') as file:
                while True:
                    chunk = self.data_socket.recv(8192)
                    if not chunk:
                        break
                    file.write(chunk)
            
            self.data_socket.close()
            self.data_socket = None
            
            self.get_response()
            print(f"Файл {remote_file} успешно загружен")
            return True
        
        print(f"Ошибка загрузки файла")
        return False
    
    def upload_file(self, local_file, remote_file=None):
        if not os.path.exists(local_file):
            print(f"Файл {local_file} не найден")
            return False
        
        if not remote_file:
            remote_file = os.path.basename(local_file)
        
        if not self.enter_passive_mode():
            return False
        
        self.send_command("TYPE I")
        self.get_response()
        
        self.send_command(f"STOR {remote_file}")
        response = self.get_response()
        
        if response.startswith('150') or response.startswith('125'):
            with open(local_file, 'rb') as file:
                while True:
                    chunk = file.read(8192)
                    if not chunk:
                        break
                    self.data_socket.send(chunk)
            
            self.data_socket.close()
            self.data_socket = None
            
            self.get_response()
            print(f"Файл {local_file} успешно отправлен")
            return True
        
        print(f"Ошибка отправки файла")
        return False
    
    def quit(self):
        if self.control_socket:
            self.send_command("QUIT")
            self.get_response()
            self.control_socket.close()

def main():
    ftp = FTPClient()
    print("FTP-клиент | help - список команд")
    
    while True:
        try:
            cmd_line = input("ftp> ").strip()
            
            if not cmd_line:
                continue
            
            parts = cmd_line.split()
            cmd = parts[0].lower()
            args = parts[1:]
            
            if cmd == "help":
                print("connect <сервер> [порт] - Подключиться к серверу")
                print("login <пользователь> [пароль] - Авторизоваться")
                print("ls [путь] - Список файлов")
                print("get <файл> [локальный_файл] - Скачать файл")
                print("put <локальный_файл> [удаленный_файл] - Загрузить файл")
                print("quit - Выход")
            
            elif cmd == "connect":
                server = args[0]
                port = int(args[1]) if len(args) > 1 else 21
                ftp.connect(server, port)
            
            elif cmd == "login":
                username = args[0] if args else "anonymous"
                password = args[1] if len(args) > 1 else "anonymous@example.com"
                ftp.login(username, password)
            
            elif cmd == "ls":
                path = args[0] if args else "."
                listing = ftp.list_directory(path)
                if listing:
                    print(listing)
            
            elif cmd == "get":
                if not args:
                    print("Использование: get <файл> [локальный_файл]")
                    continue
                
                remote_file = args[0]
                local_file = args[1] if len(args) > 1 else None
                ftp.download_file(remote_file, local_file)
            
            elif cmd == "put":
                if not args:
                    print("Использование: put <локальный_файл> [удаленный_файл]")
                    continue
                
                local_file = args[0]
                remote_file = args[1] if len(args) > 1 else None
                ftp.upload_file(local_file, remote_file)
            
            elif cmd == "quit" or cmd == "exit":
                ftp.quit()
                break
            
            else:
                print(f"Неизвестная команда: {cmd}")
        
        except KeyboardInterrupt:
            print("\nПрервано пользователем")
            break
        
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
