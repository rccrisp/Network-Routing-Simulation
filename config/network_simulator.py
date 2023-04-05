import socket
import sys
import threading
import time
import queue

HOST = "127.0.0.1"

class Node:
    def __init__(self, node_id, port_no, config_file):
        self.node_id = node_id
        self.port_no = int(port_no)
        self.config_file = config_file
        self.neighbors = {}
        self.routing_table = {}
        self.routing_table_lock = threading.Lock()
        self.send_queue = queue.Queue()
        self.running = True
        self.init_routing_table()
        self.start_listening()
        self.start_broadcasting()
        self.start_sending()

    def init_routing_table(self):
        with open(self.config_file, 'r') as f:
            num_neighbors = int(f.readline().strip())
            for i in range(num_neighbors):
                line = f.readline().strip().split()
                neighbor_id = line[0]
                cost = float(line[1])
                port_no = int(line[2])
                self.neighbors[neighbor_id] = (cost, port_no)
                self.routing_table[neighbor_id] = (cost, neighbor_id)

        self.routing_table[self.node_id] = (0, self.node_id)

    def start_listening(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((HOST, self.port_no))
        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.start()

    def start_broadcasting(self):
        self.broadcast_thread = threading.Thread(target=self.broadcast)
        self.broadcast_thread.start()

    def start_sending(self):
        self.send_thread = threading.Thread(target=self.send)
        self.send_thread.start()

    def broadcast(self):
        while self.running:
            packet = self.get_packet()
            for neighbor_id, (cost, port_no) in self.neighbors.items():
                self.sock.sendto(packet, ('localhost', port_no))
            time.sleep(10)

    def get_packet(self):
        packet = f"{self.node_id}\n"
        for neighbor_id, (cost, port_no) in self.neighbors.items():
            packet += f"{neighbor_id} {cost} {port_no}\n"
        return packet.encode('utf-8')

    def listen(self):
        while self.running:
            data, addr = self.sock.recvfrom(1024)
            packet = data.decode('utf-8')
            neighbor_id, *lines = packet.strip().split('\n')
            self.update_routing_table(neighbor_id, lines)

    def update_routing_table(self, neighbor_id, lines):
        with self.routing_table_lock:
            for line in lines:
                dest_id, cost, _ = line.split()
                cost = float(cost)
                if dest_id not in self.routing_table or cost + self.neighbors[neighbor_id][0] < self.routing_table[dest_id][0]:
                    self.routing_table[dest_id] = (cost + self.neighbors[neighbor_id][0], neighbor_id)
                    self.send_queue.put((dest_id, cost + self.neighbors[neighbor_id][0]))

    def send(self):
        while self.running:
            try:
                dest_id, cost = self.send_queue.get(timeout=1)
            except queue.Empty:
                continue
            packet = f"{self.node_id}\n{dest_id} {cost} {self.port_no}\n"
            for neighbor_id, (cost, port_no) in self.neighbors.items():
                self.sock.sendto(packet.encode('utf-8'), ('localhost', port_no))

    def print_routing_table(self):
        print(f"I am Node {self.node_id}")
        for dest, cost in self.routing_table.items():
            if dest != self.node_id:
                path = self.get_shortest_path(dest)
                print(f"Least cost path from {self.node_id} to {dest}: {''.join(path)}, link cost: {cost}")

router = Node(sys.argv[1], sys.argv[2], sys.argv[3])

