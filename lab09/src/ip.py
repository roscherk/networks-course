import netifaces

def get_ip_and_mask():
    interfaces = netifaces.interfaces()
    results = []
    
    for iface in interfaces:
        addrs = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addrs:
            for addr in addrs[netifaces.AF_INET]:
                if 'addr' in addr and 'netmask' in addr:
                    results.append((iface, addr['addr'], addr['netmask']))
    
    return results

def main():
    print("Информация о сетевых интерфейсах:")
    print("-" * 50)
    
    ip_info = get_ip_and_mask()
    
    if not ip_info:
        print("Не удалось найти активные сетевые интерфейсы")
        return
    
    for iface, ip, mask in ip_info:
        print(f"Интерфейс: {iface}")
        print(f"IP-адрес:  {ip}")
        print(f"Маска сети: {mask}")
        print("-" * 50)

if __name__ == "__main__":
    main()
