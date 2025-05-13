class Router:
    def __init__(self, id):
        self.id = id
        self.neighbors = {}  # {neighbor_id: cost}
        self.routing_table = {}  # {destination: (next_hop, cost)}
        
    def add_neighbor(self, neighbor_id, cost):
        self.neighbors[neighbor_id] = cost
        self.routing_table[neighbor_id] = (neighbor_id, cost)
        
    def get_distance_vector(self):
        return {dest: cost for dest, (_, cost) in self.routing_table.items()}
    
    def update_routing_table(self, from_router_id, dv):
        updated = False
        
        if from_router_id not in self.neighbors:
            return updated
        
        neighbor_cost = self.neighbors[from_router_id]
        
        for dest, cost in dv.items():
            if dest == self.id:
                continue
                
            new_cost = neighbor_cost + cost
            
            if (dest not in self.routing_table) or (new_cost < self.routing_table[dest][1]):
                self.routing_table[dest] = (from_router_id, new_cost)
                updated = True
                
        return updated
    
    def get_routing_table_lines(self):
        lines = []
        lines.append(f"Router {self.id} Routing Table:")
        lines.append("Destination | Next Hop | Cost")
        lines.append("-" * 30)
        
        for dest in sorted(self.routing_table.keys()):
            next_hop, cost = self.routing_table[dest]
            lines.append(f"{dest:11} | {next_hop:8} | {cost}")
        return lines
        
class Network:
    def __init__(self):
        self.routers = {}  # {router_id: Router}
        
    def add_router(self, router_id):
        if router_id not in self.routers:
            self.routers[router_id] = Router(router_id)
            
    def add_connection(self, router1_id, router2_id, cost):
        self.add_router(router1_id)
        self.add_router(router2_id)
        
        self.routers[router1_id].add_neighbor(router2_id, cost)
        self.routers[router2_id].add_neighbor(router1_id, cost)
        
    def update_connection(self, router1_id, router2_id, new_cost):
        if router1_id in self.routers and router2_id in self.routers:
            self.routers[router1_id].neighbors[router2_id] = new_cost
            self.routers[router2_id].neighbors[router1_id] = new_cost
            
            self.routers[router1_id].routing_table[router2_id] = (router2_id, new_cost)
            self.routers[router2_id].routing_table[router1_id] = (router1_id, new_cost)
            
            return True
        return False
        
    def run_distance_vector_algorithm(self, max_iterations=100):
        iteration = 0
        
        while iteration < max_iterations:
            updates = 0
            
            for router_id, router in self.routers.items():
                dv = router.get_distance_vector()
                
                for neighbor_id in router.neighbors:
                    if self.routers[neighbor_id].update_routing_table(router_id, dv):
                        updates += 1
            
            if updates == 0:
                print(f"Algorithm converged after {iteration + 1} iterations.")
                break
                
            iteration += 1
            
        if iteration == max_iterations:
            print(f"Algorithm did not converge after {max_iterations} iterations.")
    
    def print_all_routing_tables_by_rows(self, tables_per_row=2):
        router_ids = sorted(self.routers.keys())
        tables = [self.routers[rid].get_routing_table_lines() for rid in router_ids]
        
        for i in range(0, len(tables), tables_per_row):
            group = tables[i:i+tables_per_row]
            max_rows = max(len(table) for table in group)
            col_width = max(max(len(line) for line in table) for table in group) + 4
            
            for j in range(max_rows):
                row = ""
                for table in group:
                    if j < len(table):
                        row += table[j].ljust(col_width)
                    else:
                        row += " " * col_width
                print(row)
            
            if i + tables_per_row < len(tables):
                print()
            
    def print_all_routing_tables(self, tables_per_row=2):
        self.print_all_routing_tables_by_rows(tables_per_row=tables_per_row)

def setup_example_network():
    network = Network()
    
    # связи со скришнота
    network.add_connection(0, 1, 1)
    network.add_connection(0, 2, 3)
    network.add_connection(1, 2, 1)
    network.add_connection(1, 3, 2)
    network.add_connection(1, 4, 3)
    network.add_connection(3, 4, 2)
    
    print("Initial network setup:")
    for r_id, router in network.routers.items():
        print(f"Router {r_id} neighbors: {router.neighbors}")
    print()
    
    return network

if __name__ == "__main__":
    network = setup_example_network()
    
    print("Running distance vector algorithm...")
    network.run_distance_vector_algorithm()
    print("\nFinal routing tables:")
    network.print_all_routing_tables(tables_per_row=3)
    
    # изменение стоимости соединения между роутерами
    print("\nUpdating connection cost between routers 1 and 2 from 1 to 5")
    network.update_connection(1, 2, 5)
    
    print("\nRunning distance vector algorithm after update...")
    network.run_distance_vector_algorithm()
    print("\nUpdated routing tables:")
    network.print_all_routing_tables(tables_per_row=3)
