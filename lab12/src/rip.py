import json
import random
import ipaddress
from typing import Dict, List, Set

class Router:
    def __init__(self, ip: str):
        self.ip = ip
        self.routing_table: Dict[str, Dict] = {}
        self.neighbors: Set[str] = set()
        self.routing_table[ip] = {
            'destination': ip,
            'next_hop': ip,
            'metric': 0
        }
    
    def add_neighbor(self, neighbor_ip: str):
        self.neighbors.add(neighbor_ip)
        self.routing_table[neighbor_ip] = {
            'destination': neighbor_ip,
            'next_hop': neighbor_ip,
            'metric': 1
        }
    
    def update_routing_table(self, neighbor_ip: str, neighbor_table: Dict[str, Dict]) -> bool:
        updated = False
        
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
        return self.routing_table.copy()
    
    def print_routing_table(self, title: str = ""):
        if title:
            print(f"\n{title}")
        else:
            print(f"\nFinal state of router {self.ip} table:")
        
        print(f"{'[Source IP]':<16} {'[Destination IP]':<19} {'[Next Hop]':<17} {'[Metric]'}")
        
        for dest_ip in sorted(self.routing_table.keys()):
            route = self.routing_table[dest_ip]
            print(f"{self.ip:<16} {dest_ip:<19} {route['next_hop']:<17} {route['metric']:>8}")

class RIPNetwork:
    def __init__(self):
        self.routers: Dict[str, Router] = {}
        self.connections: List[tuple] = []
    
    def generate_random_ip(self) -> str:
        return str(ipaddress.IPv4Address(random.randint(0, 2**32 - 1)))
    
    def create_random_network(self, num_routers: int = 5):
        router_ips = []
        
        for _ in range(num_routers):
            while True:
                ip = self.generate_random_ip()
                if ip not in self.routers:
                    break
            
            router_ips.append(ip)
            self.routers[ip] = Router(ip)
        
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
            
            for router_config in config['routers']:
                ip = router_config['ip']
                self.routers[ip] = Router(ip)
            
            for connection in config['connections']:
                self.add_connection(connection['router1'], connection['router2'])
                
        except FileNotFoundError:
            print(f"Config file {config_file} not found. Generating random network...")
            self.create_random_network()
    
    def add_connection(self, ip1: str, ip2: str):
        if (ip1, ip2) not in self.connections and (ip2, ip1) not in self.connections:
            self.connections.append((ip1, ip2))
            self.routers[ip1].add_neighbor(ip2)
            self.routers[ip2].add_neighbor(ip1)
    
    def simulate_rip(self, max_iterations: int = 20):
        print("Starting RIP simulation...")
        print(f"Network topology: {len(self.routers)} routers, {len(self.connections)} connections")
        
        for iteration in range(max_iterations):
            print(f"\n--- RIP Iteration {iteration + 1} ---")
            updated = False
            
            for router_ip, router in self.routers.items():
                for neighbor_ip in router.neighbors:
                    neighbor = self.routers[neighbor_ip]
                    neighbor_table = neighbor.get_routing_table_copy()
                    
                    if router.update_routing_table(neighbor_ip, neighbor_table):
                        updated = True
            
            if not updated:
                print(f"RIP converged after {iteration + 1} iterations")
                break
        else:
            print(f"RIP simulation completed after {max_iterations} iterations")
        
        self.print_final_tables()
    
    def print_final_tables(self):
        print("\n" + "="*80)
        print("FINAL ROUTING TABLES")
        print("="*80)
        
        for router_ip in sorted(self.routers.keys()):
            self.routers[router_ip].print_routing_table()

def main():
    network = RIPNetwork()
    
    try:
        network.load_from_config('network_config.json')
    except:
        print("No config file found or error loading config. Generating random network...")
        network.create_random_network(6)
    
    network.simulate_rip()

if __name__ == "__main__":
    main()
