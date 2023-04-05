import socket
import time
import threading 
import sys
import signal

HOST = "127.0.0.1"
PATH = 'config/'
DELAY = 5
STARTUP = 5

class Communication:

    def __init__(self, ID, portNO, cost):
        self.ID = ID
        self.PortNO = int(portNO)
        self.LastComm = None
        self.Live = False
        self.UpToDate = False
        self.Cost = cost

class Edge:
    
    def __init__(self, node1, node2, cost):
        self.Nodes = [node1, node2]
        self.Cost = cost
        self.Changed = True
        self.Broadcast = False

class Neighbour:

    def __init__(self, node, cost):
        self.Node = node
        self.Cost = round(float(cost),1)

class Routing:

    def __init__(self, path, cost):
        self.Path = path
        self.Cost = round(float(cost),1)

class Router:

    def __init__(self, ID, portNO, filename):
        self.ID = ID
        self.PortNO = int(portNO)
        self.Config = PATH + filename
        
        self.Socket = None

        self.NumNeighbours = 0
        self.Neighbours = {} # neighbour is dict of form {ID: Communication(ID, portNO, cost)}
        self.NetworkConnections = [] # a list of all the edges in the network List[Edges(node1,node2,cost)]
        self.Graph = {} # a graph created from the network knowledge of form {node: list[Neighbour(neighbour, cost)]}
        self.RoutingTable = {} # contains the routing to every node in the network of form {node: Routing(path, dist)}

        self.Started = time.time()

    def run(self):
        
        # generate local network visibility from config file
        self.ReadConfigFiles()

        # create socket
        self.SocketCreation()

        # thread for listening to neighbouring nodes
        t1 = threading.Thread(target=self.ListenNeighbours)
        t1.daemon = True
        t1.start()

        # thread for broadcasting to neighbouring nodes
        t2 = threading.Thread(target=self.BroadcastNeighbours)
        t2.daemon = True
        t2.start()

        # thread for updating link costs
        t4 = threading.Thread(target=self.MonitorTerminal)
        t4.daemon = True
        t4.start()

        # thread for checking that all neighbour nodes are still broadcasting
        t5 = threading.Thread(target=self.CheckDropout)
        t5.daemon = True
        t5.start()

        # gracefully disconnect
        signal.signal(signal.SIGINT, self.Disconnect)
        signal.siginterrupt(signal.SIGUSR1, False)
        signal.pause()

    def ReadConfigFiles(self):

        with open(self.Config, 'r') as f:
            self.NumNeighbours = int(f.readline())
            for i in range(0, self.NumNeighbours):
                line = f.readline()
                args = line.split(' ')

                # update neighbour communication
                neighbourComm = Communication(args[0], args[2], args[1])
                self.NewNeighbour(neighbourComm)

        return

    # add a new network edge and set the changed flag to true
    def NewNetworkEdge(self, node1, node2, cost):
        
        for edge in self.NetworkConnections:
            # if this edge is already in the list of network connections
            if node1 in edge.Nodes and node2 in edge.Nodes:
                if edge.Cost != cost:
                    # if the edge cost has changed, change it and set flag
                    edge.Cost = cost
                    edge.Changed = True
                    edge.Broadcast = False
                # # if we have a response bounced back to us, we know it has been read
                # else :
                #     edge.Changed = False
                #     edge.Broadcast = True
                return
            
        # otherwise, we have a new edge so add it to the list of edges
        edge = Edge(node1,node2,cost)
        self.NetworkConnections.append(edge)
  
        return
        
    def NewNeighbour(self, comm):
        self.Neighbours.update({comm.ID: comm})
        return
    
    def SocketCreation(self):
        try:
            self.Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.Socket.bind((HOST, self.PortNO))
            self.Socket.listen(self.NumNeighbours)
        except:
            print("Can't connect to socket")
            exit()
        
        return
    
    def ListenNeighbours(self):
        while(1):
            
            c, addr = self.Socket.accept()
       
            data_recv = c.recv(1024).decode('utf-8')
            
            if data_recv:

                # add data to the queue for the routing calculations
                self.DecodeMessage(data_recv)

                # run routing algorithm
                self.Routing()

            c.close()

    def DecodeMessage(self, data):

        sendingNode, networkEdges = data.split('||')

        # update last time we received router communication
        self.Neighbours.get(sendingNode).LastComm = time.time()

        # if we receive a message from a node that is not currently live
        if self.Neighbours.get(sendingNode).Live != True:

            # change that node to live
            self.Neighbours.get(sendingNode).Live = True
            # we have received a link cost change so set the change flag
            self.NewNetworkEdge(self.ID, sendingNode, self.Neighbours.get(sendingNode).Cost)
            # we also need to broadcast all our current information to this new node
            for edge in self.NetworkConnections:
                edge.Broadcast = False
            # build message for neighbour
            message = self.EncodeMessage()
            comm = self.Neighbours.get(sendingNode)
            self.Broadcast(comm, message)
            

        edgeData = networkEdges.split('|')

        if edgeData[0] == '':
            # if we dont receive any new edge data, assume we are up to date with this node
            self.Neighbours.get(sendingNode).UpToDate = True
            return

        for edge in edgeData:

            node1, node2, cost = edge.split(',')

            # we have received a changed DV from a neighbour so add it to the network and set the change flag
            self.NewNetworkEdge(node1, node2, cost)   
    
    def BroadcastNeighbours(self):
            while(1):

                for ID, routerComm in self.Neighbours.items():
                    
                    # build message for neighbour
                    message = self.EncodeMessage()

                    self.Broadcast(routerComm, message)

                # # we have now broadcast all changed connections to neighbours
                for edge in self.NetworkConnections:
                    edge.Broadcast = True

                time.sleep(DELAY)

    def EncodeMessage(self):

        message = self.ID + '||'
        for edge in self.NetworkConnections:

            # only broadcast changed nodes
            if edge.Broadcast == False:

                node1 = edge.Nodes[0]
                node2 = edge.Nodes[1]

                message += '{},{},{}|'.format(node1, node2, edge.Cost)

        if message == self.ID + '||':
            return message

        return message[:-1]
    
    def Broadcast(self, routerComm, message):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try: 
                 s.connect((HOST, routerComm.PortNO))

                 self.Message(s, message)

            except Exception as e:
                # print('Failed to connect to ' + str(routerComm.PortNO) + ' ' + str(e))
                pass

    def Message(self, socketComm, message):

        socketComm.sendall(message.encode('utf-8'))
        # print('sent ' + message)
        return

    # builds a graph from the list of network connections to help run djikstras algorithm
    def BuildGraph(self):

        self.Graph = {}

        for edge in self.NetworkConnections:
            # we have read this change and implemented it
            edge.Changed = False
            if edge.Cost != float('inf'):
                node1 = edge.Nodes[0]
                node2 = edge.Nodes[1]

                # if the node doesnt yet exist in the graph, add it
                if self.Graph.get(node1) == None:
                    self.Graph.update({node1 : [Neighbour(node2, edge.Cost)]})
                # otherwise, append this node to the list of existing neighbours
                else :
                    self.Graph.get(node1).append(Neighbour(node2, edge.Cost))

                if self.Graph.get(node2) == None:
                    self.Graph.update({node2 : [Neighbour(node1, edge.Cost)]})
                else :
                    self.Graph.get(node2).append(Neighbour(node1, edge.Cost))
        return
            
    def PrintGraph(self):
        print('Graph looks like:')
        for key, value in self.Graph.items():
            print(key)
            for v in value:
                print(v.Node, v.Cost)

    def PrintNetworkConnections(self):
        print('Current connections')
        for edge in self.NetworkConnections:
            print(edge.Nodes, edge.Cost)

    def Routing(self):
        # if there has been a link change and the network has converged

        if self.DVChange():

            # if after startup time
            if STARTUP < time.time()-self.Started:

                # run routing algorithm
                t3 = threading.Thread(target=self.Djikstra)
                t3.daemon = True
                t3.start()

    def Converged(self):
        for router in self.Neighbours.values():
            if router.UpToDate == False:
                return
        return True

    def DVChange(self):
        for edge in self.NetworkConnections:
            if edge.Changed == True:
                return True
            
        return False
    
    def Djikstra(self):

        # build graph from network connections list
        self.BuildGraph()
        
        # self.PrintGraph()
        # self.PrintNetworkConnections()

        # for every vertex in the graph, set the intial routing to infinite cost
        for vertex in self.Graph:
            self.RoutingTable.update({vertex: Routing(None, float('inf'))})

        # set the source node to zero cost
        self.RoutingTable.update({self.ID: Routing(self.ID, 0)})

        # create Q list
        Q = self.Graph

        while Q.keys():

            # get the lowest cost vertex still in Q
            u, adjacent = self.MinDist(Q)

            if u == None:
                break

            # remove this vertex from Q
            del Q[u]

            for neighbour in adjacent:
                
                # if this node is still unexpanded
                if neighbour.Node in Q.keys():

                    alt = self.RoutingTable.get(u).Cost + neighbour.Cost

                    # if this alternate route is shorter than the current route
                    if alt < self.RoutingTable.get(neighbour.Node).Cost:

                        path =  self.RoutingTable.get(u).Path + neighbour.Node 
                        newRoute = Routing(path, alt)
                        self.RoutingTable.update({neighbour.Node: newRoute})
 
           
        # when routing algorithm is complete, print routing table
        self.PrintRoutingTable() 
        
        return

    def MinDist(self, Q):
        u = None
        listV = None
        dist = float('inf')
        for vertex, adjacent in Q.items():
            if self.RoutingTable.get(vertex).Cost < dist:
                u = vertex
                listV = adjacent
                dist = self.RoutingTable.get(u).Cost
        
        return u, listV
    
    def PrintRoutingTable(self):

        print('I am Node ' + self.ID)
        for target, routing in sorted(self.RoutingTable.items()):
 
            # dont print self 
            if self.ID != target:
                # dont print nodes with no current path
                if routing.Path != None:
                    print('Least cost path from {} to {}: {}, link cost: {}'.format(self.ID, target, routing.Path, routing.Cost))

    def MonitorTerminal(self):
        while 1:

            if 'update' == input():

                # read input from user
                node, config, cost = self.ReadInput()

                # update the config file for the calling node
                self.UpdateConfigFile(node, self.Config, cost, self.Neighbours.get(node).Cost)
                # update the config file for the other node
                self.UpdateConfigFile(self.ID, config, cost, self.Neighbours.get(node).Cost)

                # update the link cost
                self.NewNetworkEdge(self.ID, node, cost)

            else :
                print("To update link cost, please use command \"update\" ")

    def ReadInput(self):
        
        while 1:
            print("Enter Router ID:")
            router = input().strip()
            
            # Check input values against rules
            if router not in self.Neighbours.keys():
                print(f"Can only update existing links for Router {self.ID}. Existing links are: {', '.join(self.Neighbours.keys())}")
            else :
                break

        config = PATH + router + 'config.txt'
        
        while 1:
            print("Enter New Value for Link Cost:")
            try:
                cost = float(input().strip())
                if 0 < cost:
                    break
                else :
                    print("Link cost Must be Non-Negative Value")
            except ValueError:
                print("Link Cost Must be a Numeric Value")
            
        print("Confirmed! Updating link {}--{}--{} ...".format(self.ID, cost, router))
        
        return router, config, cost
    
    # update the config file
    def UpdateConfigFile(self, node, filename, new_cost, old_cost):

        with open(filename, 'r') as file:
            file_content = file.read()

        # find the link information and replace it with the updated data
        updated_content = file_content.replace(f'{node} {old_cost}', f'{node} {new_cost}')

        with open(filename, 'w') as file:
            file.write(updated_content)

        return

    def Disconnect(self, sig, frame):

        print('\nDisconnecting...')
        self.Socket.close()
        sys.exit(0)

    def CheckDropout(self):
        while 1:
            
            # for each router
            for router in self.Neighbours.values():
                if router.Live:
                    # if we have not received a message for a while, assume disconnected
                    if time.time() - router.LastComm > 2*DELAY:
                            router.Live = False
                            for edge in self.NetworkConnections:
                                if router.ID in edge.Nodes:
                                    self.NewNetworkEdge(self.ID, router.ID, float('inf'))
                            self.Routing()

            time.sleep(DELAY)              

def main():   

    router = Router(sys.argv[1], sys.argv[2], sys.argv[3])

    router.run()

if __name__ == "__main__":
    main()


        

