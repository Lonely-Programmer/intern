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
                source = np.searchsorted(nodes, source)
                destination = np.searchsorted(nodes, destination)
                degrees_in[destination] += 1
                degrees_out[source] += 1

    print(len(nodes),cnt)
    degrees_out_idx = np.argsort(degrees_out)
    print(degrees_out_idx[-1], degrees_out[degrees_out_idx[-1]])
    
def main():
    work()

main()
            
        
