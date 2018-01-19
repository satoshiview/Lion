import math
from bittrex.bittrex import Bittrex, API_V1_1
from collections import defaultdict

# constants
ETH = "eth"
BTC = "btc"
NEO = "neo"

def initialize(graph, source):
    d = {} # Stands for destination
    p = {} # Stands for predecessor
    for node in graph:
        d[node] = float('Inf') # We start admiting that the rest of nodes are very very far
        p[node] = None
    d[source] = 0 # For the source we know how to reach
    return d, p


def relax(node, neighbour, graph, d, p):
    # If the distance between the node and the neighbour is lower than the one I have now
    if d[neighbour] > d[node] + graph[node][neighbour]:
        # Record this lower distance
        d[neighbour]  = d[node] + graph[node][neighbour]
        p[neighbour] = node

 
def retrace_negative_loop(p, start):
    arbitrageLoop = [start]
    next_node = start
    while True:
        next_node = p[next_node]
        if next_node not in arbitrageLoop:
            arbitrageLoop.append(next_node)
        else:
            arbitrageLoop.append(next_node)
            arbitrageLoop = arbitrageLoop[arbitrageLoop.index(next_node):]
            return arbitrageLoop


def bellman_ford(graph, source):
    d, p = initialize(graph, source)
    for i in range(len(graph)-1): #Run this until is converges
        for u in graph:
            for v in graph[u]: #For each neighbour of u
                relax(u, v, graph, d, p) #Lets relax it


    # Step 3: check for negative-weight cycles
    for u in graph:
        for v in graph[u]:
            if d[v] < d[u] + graph[u][v]:
                return(retrace_negative_loop(p, source))

    return None


def construct_graph(bittrex_client):
    graph = defaultdict(dict)
    markets = (("btc-eth", BTC, ETH), ("btc-neo", BTC, NEO), 
        ("eth-neo", ETH, NEO))

    for market, from_coin, to_coin in markets:
        ticker = bittrex_client.get_ticker(market)
        result = ticker["result"]
        graph[to_coin][from_coin] = -math.log(1 / float(result["Bid"]))
        graph[from_coin][to_coin] = -math.log(float(result["Ask"]))

    return graph


bittrex_client = Bittrex(None, None, api_version=API_V1_1)
graph = construct_graph(bittrex_client)
paths = []

for key in graph:
    path = bellman_ford(graph, key)
    if path not in paths and path is not None:
        paths.append(path)

for path in paths:
    if path == None:
        print("No opportunity here :(")
    else:
        money = 10000
        print "Starting with %(money)i in %(currency)s" % {"money":money,"currency":path[0]}

        for i,value in enumerate(path):
            if i+1 < len(path):
                start = path[i]
                end = path[i+1]
                rate = math.exp(-graph[start][end])
                money *= rate
                print "%(start)s to %(end)s at %(rate)f = %(money)f" % {"start":start,"end":end,"rate":rate,"money":money}
print "\n"
