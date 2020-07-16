import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

def get_data(k):
    tmp = np.load("data/data_" + str(k) + ".npy",allow_pickle=True)
    passages = tmp[0]
    passage_edges = tmp[1]
    isolated_passages = tmp[2]
    nodes = []
    degrees = []
    for i in passages:
        #nodes.append(len(i)**0.5*20)
        if k > 10:
            nodes.append(len(i)/2)
        else:
            nodes.append(len(i)/4)
    G = nx.MultiDiGraph()
    for i in range(len(passages)):
        G.add_node(str(i))
    for i in passage_edges:
        G.add_edge(str(i[0]), str(i[1]), weight=1)
    for i in range(len(passages)):
        degrees.append(0)
    for i in passage_edges:
        degrees[i[0]] += 1
        degrees[i[1]] += 1
    for i in isolated_passages:
        G.remove_node(str(i))
        del degrees[i]
    degrees2 = []
    for i in range(len(degrees)):
        degrees2.append(np.log(np.log(degrees[i]+5)+5))
    return (G,nodes,degrees2,degrees)

def draw(k,r):
    #G = nx.generators.directed.random_k_out_graph(10, 3, 0.5)
    #print(type(G),type(nx.Graph()))
    tmp = get_data(k)
    G = tmp[0]
    pos = nx.layout.spring_layout(G)

    #node_sizes = [3 + 10 * i for i in range(len(G))]
    node_sizes = tmp[1]
    M = G.number_of_edges()
    edge_colors = range(2, M + 2)
    edge_alphas = [(5 + i) / (M + 4) for i in range(M)]
    N = G.number_of_nodes()
    node_colors = tmp[2]
    print(N,len(node_colors))
    node_alphas = [(node_colors[i] + 3) / (node_colors[0] + 4) + 0.5 for i in range(N)]
    
    #nodes = nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='blue')
    nodes = nx.draw_networkx_nodes(G, pos, node_size=node_sizes,
                                   node_color=node_colors, cmap=plt.cm.rainbow)
    edges = nx.draw_networkx_edges(G, pos, node_size=node_sizes,
                                   arrowsize=0.01, edge_color=edge_colors,
                                    edge_cmap=plt.cm.Blues,width=r)
    print(type(edges),type(nodes))
    # set alpha value for each edge
    for i in range(M):
        edges[i].set_alpha(edge_alphas[i])
        
    pc = mpl.collections.PatchCollection(edges, cmap=plt.cm.rainbow)
    pc.set_array(tmp[3])
    plt.colorbar(pc)

    ax = plt.gca()
    ax.set_axis_off()
    plt.show()

def main():
    dat1 = [29,6,5]
    dat1 = [29]
    dat2 = [1,0.1,0.1]
    for i in range(len(dat1)):
        draw(dat1[i],dat2[i])

main()
