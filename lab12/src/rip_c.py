import json
import random
import ipaddress
import socket
import threading
import time
import pickle
from typing import Dict, List, Set, Optional

class ThreadedRouter:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.routing_table: Dict[str, Dict] = {}
        self.neighbors: Dict[str, int] = {}
        self.routing_table[ip] = {
            'destination': ip,
            'next_hop': ip,
            'metric': 0
        }
        self.lock = threading.Lock()
        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('localhost', port))
        self.socket.settimeout(1.0)
        
    def add_neighbor(self, neighbor_ip: str, neighbor_port: int):
        with self.lock:
            self.neighbors[neighbor_ip] = neighbor_port
            self.routing_table[neighbor_ip] = {
                'destination': neighbor_ip,
                'next_hop': neighbor_ip,
                'metric': 1
            }
    
    def update_routing_table(self, neighbor_ip: str, neighbor_table: Dict[str, Dict]) -> bool:
        updated = False
        
        with self.lock:
            for dest_ip, route_info in neighbor_table.items():
                if dest_ip == self.ip:
                    continue
                    
                new_metric = route_info['metric'] + 1
                
                if new_metric >= 16:
                    continue
                    
                if dest_ip not in self.routing_table:
                    self.routing_table[dest_ip] = {
                        'destination': dest_ip,
                        'next_hop': neighbor_ip,
                        'metric': new_metric
                    }
                    updated = True
                elif new_metric < self.routing_table[dest_ip]['metric']:
                    self.routing_table[dest_ip] = {
                        'destination': dest_ip,
                        'next_hop': neighbor_ip,
                        'metric': new_metric
                    }
                    updated = True
                elif (self.routing_table[dest_ip]['next_hop'] == neighbor_ip and 
                      new_metric != self.routing_table[dest_ip]['metric']):
                    self.routing_table[dest_ip]['metric'] = new_metric
                    updated = True
        
        return updated
    
    def get_routing_table_copy(self) -> Dict[str, Dict]:
        with self.lock:
            return self.routing_table.copy()
    
    def send_routing_table(self, neighbor_ip: str, neighbor_port: int):
        try:
            table_copy = self.get_routing_table_copy()
            data = pickle.dumps(table_copy)
            self.socket.sendto(data, ('localhost', neighbor_port))
        except Exception as e:
            pass
    
    def listen_for_updates(self):
        while self.running:
            try:
                data, addr = self.socket.recvfrom(4096)
                neighbor_table = pickle.loads(data)
                
                sender_ip = None
                for ip, port in self.neighbors.items():
                    if addr[1] == port:
                        sender_ip = ip
                        break
                
                if sender_ip:
                    self.update_routing_table(sender_ip, neighbor_table)
                    
            except socket.timeout:
                continue
            except Exception as e:
                break
    
    def broadcast_updates(self):
        while self.running:
            for neighbor_ip, neighbor_port in self.neighbors.items():
                self.send_routing_table(neighbor_ip, neighbor_port)
            time.sleep(2)
    
    def start(self):
        listener_thread = threading.Thread(target=self.listen_for_updates)
        broadcaster_thread = threading.Thread(target=self.broadcast_updates)
        
        listener_thread.start()
        broadcaster_thread.start()
        
        return listener_thread, broadcaster_thread
    
    def stop(self):
        self.running = False
        self.socket.close()
    
    def print_routing_table(self, title: str = ""):
        with self.lock:
            if title:
                print(f"\n{title}")
            else:
                print(f"\nFinal state of router {self.ip} table:")
            
            print(f"{'[Source IP]':<16} {'[Destination IP]':<19} {'[Next Hop]':<17} {'[Metric]'}")
            
            for dest_ip in sorted(self.routing_table.keys()):
                route = self.routing_table[dest_ip]
                print(f"{self.ip:<16} {dest_ip:<19} {route['next_hop']:<17} {route['metric']:>8}")

class ThreadedRIPNetwork:
    def __init__(self):
        self.routers: Dict[str, ThreadedRouter] = {}
        self.connections: List[tuple] = []
        self.base_port = 5000
        
    def generate_random_ip(self) -> str:
        return str(ipaddress.IPv4Address(random.randint(0, 2**32 - 1)))
    
    def create_random_network(self, num_routers: int = 5):
        router_ips = []
        
        for i in range(num_routers):
            while True:
                ip = self.generate_random_ip()
                if ip not in self.routers:
                    break
            
            router_ips.append(ip)
            self.routers[ip] = ThreadedRouter(ip, self.base_port + i)
        
        num_connections = random.randint(num_routers - 1, min(num_routers * 2, num_routers * (num_routers - 1) // 2))
        
        for i in range(num_routers - 1):
            ip1, ip2 = router_ips[i], router_ips[i + 1]
            self.add_connection(ip1, ip2)
        
        for _ in range(num_connections - (num_routers - 1)):
            ip1, ip2 = random.sample(router_ips, 2)
            if (ip1, ip2) not in self.connections and (ip2, ip1) not in self.connections:
                self.add_connection(ip1, ip2)
    
    def load_from_config(self, config_file: str):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            for i, router_config in enumerate(config['routers']):
                ip = router_config['ip']
                self.routers[ip] = ThreadedRouter(ip, self.base_port + i)
            
            for connection in config['connections']:
                self.add_connection(connection['router1'], connection['router2'])
                
        except FileNotFoundError:
            print(f"Config file {config_file} not found. Generating random network...")
            self.create_random_network()
    
    def add_connection(self, ip1: str, ip2: str):
        if (ip1, ip2) not in self.connections and (ip2, ip1) not in self.connections:
            self.connections.append((ip1, ip2))
            router1 = self.routers[ip1]
            router2 = self.routers[ip2]
            router1.add_neighbor(ip2, router2.port)
            router2.add_neighbor(ip1, router1.port)
    
    def simulate_rip_threaded(self, duration: int = 30):
        print("Starting threaded RIP simulation with socket communication...")
        print(f"Network topology: {len(self.routers)} routers, {len(self.connections)} connections")
        
        threads = []
        
        for router in self.routers.values():
            router_threads = router.start()
            threads.extend(router_threads)
        
        print(f"All routers started. Running simulation for {duration} seconds...")
        
        for i in range(duration // 5):
            time.sleep(5)
            print(f"\n--- Simulation Step {i + 1} (after {(i + 1) * 5} seconds) ---")
            for router_ip in sorted(self.routers.keys()):
                self.routers[router_ip].print_routing_table(f"Router {router_ip} routing table:")
        
        print("\nStopping all routers...")
        for router in self.routers.values():
            router.stop()
        
        for thread in threads:
            thread.join(timeout=2)
        
        print("\n" + "="*80)
        print("FINAL ROUTING TABLES")
        print("="*80)
        
        for router_ip in sorted(self.routers.keys()):
            self.routers[router_ip].print_routing_table()

def main():
    network = ThreadedRIPNetwork()
    
    try:
        network.load_from_config('network_config.json')
    except:
        print("No config file found or error loading config. Generating random network...")
        network.create_random_network(5)
    
    network.simulate_rip_threaded(duration=20)

if __name__ == "__main__":
    main()
