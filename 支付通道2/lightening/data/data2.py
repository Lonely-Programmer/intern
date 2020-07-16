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
    values = [0] * len(nodes)
    
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
                source = np.searchsorted(nodes, source)
                destination = np.searchsorted(nodes, destination)
                values[source] += float(capacity)

    values.sort()
    for i in range(len(values)):
        if values[i] > 0:
            break

    values = values[i:len(values)]
    print(len(values))
    print(i)
    print(values[0],values[-1])
    np.save("data2.npy", values)

def main():
    #work()
    z = np.load("data2.npy")
    print(len(z))

main()
            
        
