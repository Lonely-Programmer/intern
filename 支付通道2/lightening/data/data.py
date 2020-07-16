import random
import numpy as np

def work():
    nodes = np.array([], dtype=np.str_)
    with open('allnodes.txt', 'r', encoding='UTF-8') as f: 
        f.readline()
        for line in f: 
            if 'nodeid' in line: 
                nodeid = line.split()[1]
                nodeid = nodeid.replace('"','').replace(',','')
                nodes = np.append(nodes,nodeid)
    nodes = np.sort(nodes)
    
    edges = np.zeros((len(nodes),len(nodes)))
    degrees_in = np.zeros(len(nodes), dtype=np.int)
    degrees_out = np.zeros(len(nodes), dtype=np.int)
    cnt = 0
    with open('channels.txt', 'r', encoding='UTF-8') as f: 
        f.readline()
        for line in f: 
            if 'source' in line: 
                source = line.split()[1]
                source = source.replace('"','').replace(',','')
            elif 'destination' in line: 
                destination = line.split()[1]
                destination = destination.replace('"','').replace(',','')
            elif 'satoshis' in line: 
                capacity = line.split()[1]
                capacity = capacity.replace(',','')
                cnt += 1
                #listC.append(float(capacity))
                #G.add_edge(int(nodes.index(source)), int(nodes.index(destination)), capacity = float(capacity), cost = random.random()*10)
                source = np.searchsorted(nodes, source)
                destination = np.searchsorted(nodes, destination)
                edges[source][destination] = float(capacity)
                degrees_in[destination] += 1
                degrees_out[source] += 1

    print(len(nodes),cnt)
    print()
    degrees_out_idx = np.argsort(degrees_out)
    values = np.array([])

    print(values)
    for i in range(len(nodes)):
        source = degrees_out_idx[i]
        if degrees_out[source] == 0:
            continue
        if degrees_out[source] > 8:
            break
        for j in range(len(nodes)):
            target = j
            if edges[source][target] < 0.1 or edges[target][source] < 0.1:
                continue
            values = np.append(values, edges[source][target])
            #print(source,target,edges[source][target],edges[target][source])

    print(len(values))
    print(values)
    np.save("data.npy", values)

def main():
    z = np.load("data.npy")
    print(len(z))
    #work()

main()
            
        
