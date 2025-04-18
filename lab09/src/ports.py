import socket
import sys
import argparse

def check_port_availability(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result != 0
    except socket.error:
        return False

def scan_ports(ip, start_port, end_port):
    available_ports = []
    total_ports = end_port - start_port + 1
    
    print(f"Сканирование портов с {start_port} по {end_port} на {ip}...")
    for i, port in enumerate(range(start_port, end_port + 1)):
        percent = int(((i + 1) / total_ports) * 100)
        bar_length = 30
        filled_length = int(bar_length * (i + 1) // total_ports)
        bar = '=' * filled_length + '-' * (bar_length - filled_length)
        
        sys.stdout.write(f'\r[{bar}] {percent}%\t\t\tТекущий: {port}')
        sys.stdout.flush()
        
        if check_port_availability(ip, port):
            available_ports.append(port)
    
    sys.stdout.write('\n')
    return available_ports

def compress_port_list(ports):
    """Элегантная версия без itertools для группировки последовательных портов"""
    if not ports:
        return "Нет доступных портов"
    
    # Сортируем порты
    ports = sorted(ports)
    
    # Используем одностроничный генератор для группировки последовательных портов
    ranges = []
    i = 0
    while i < len(ports):
        start = ports[i]
        # Находим конец текущей последовательности
        while i + 1 < len(ports) and ports[i + 1] == ports[i] + 1:
            i += 1
        # Добавляем результат (одиночное число или диапазон)
        ranges.append(f"{start}" if start == ports[i] else f"{start}-{ports[i]}")
        i += 1
    
    return ", ".join(ranges)

def main():
    parser = argparse.ArgumentParser(description='Проверка доступных портов')
    parser.add_argument('ip', help='IP-адрес для проверки')
    parser.add_argument('start_port', type=int, help='Начальный порт диапазона')
    parser.add_argument('end_port', type=int, help='Конечный порт диапазона')
    
    args = parser.parse_args()
    
    if args.start_port > args.end_port:
        print("Ошибка: начальный порт должен быть меньше или равен конечному порту")
        return 1
    
    if args.start_port < 1 or args.end_port > 65535:
        print("Ошибка: порты должны быть в диапазоне от 1 до 65535")
        return 1
    
    available_ports = scan_ports(args.ip, args.start_port, args.end_port)
    
    print(f"\nДоступные порты на {args.ip}: {compress_port_list(available_ports)}")
    print(f"Всего найдено доступных портов: {len(available_ports)}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
