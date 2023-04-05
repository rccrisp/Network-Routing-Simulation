import networkx as nx

PATH = 'config/'

print('Generating graph...')

G = nx.Graph()

G.add_edge('A', 'B', weight=5.3)
G.add_edge('A', 'C', weight=2.1)
G.add_edge('A', 'H', weight=8.4)

G.add_edge('B', 'D', weight=0.8)

G.add_edge('C', 'E', weight=6.0)
G.add_edge('C', 'F', weight=3.7)
G.add_edge('C', 'I', weight=2.4)

G.add_edge('D', 'E', weight=4.4)

G.add_edge('E', 'G', weight=4.4)
G.add_edge('E', 'F', weight=1.9)
G.add_edge('E', 'J', weight=2.9)

G.add_edge('G', 'H', weight=3.2)
G.add_edge('G', 'J', weight=5.1)

G.add_edge('H', 'I', weight=2.5)

G.add_edge('I', 'J', weight=1.7)

PortNO = {'A': 6000, 'B': 6001, 'C': 6002, 'D': 6003, 'E': 6004, 'F': 6005, 'G': 6006, 'H': 6007, 'I': 6008, 'J': 6009}

print("Writing to files...")
for n in list(G.nodes):
    filename =  PATH + n + 'config.txt'
    f = open(filename, 'w')
    num_neighbours = len(G.edges(n))
    f.write(str(len(G.edges(n))) + '\n')
    counter = 1
    for e in G.edges(n, data=True):
        if counter < num_neighbours:
            f.write(e[1] + ' ' + str(e[2].get('weight')) + ' ' + str(PortNO[e[1]])+ '\n')
        else :
            f.write(e[1] + ' ' + str(e[2].get('weight')) + ' ' + str(PortNO[e[1]]))
        counter += 1
    f.close()

print("Finished!")
