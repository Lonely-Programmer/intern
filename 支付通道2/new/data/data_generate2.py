import numpy as np
import matplotlib.pyplot as plt
import random

def binary_chop(alist, data):
    """
    非递归解决二分查找
    :param alist:
    :return:
    """
    n = len(alist)
    first = 0
    last = n - 1
    while first <= last:
        mid = (last + first) // 2
        if alist[mid] > data:
            last = mid - 1
        elif alist[mid] < data:
            first = mid + 1
        else:
            return mid
    return -1

def work():
    values = np.zeros(100000)
    degrees_in = np.zeros(100000)
    degrees_out = np.zeros(100000)
    edges = []
    dat = []
    zero_cnt = 0

    for i in range(100000):
        edges.append([])

    with open('ripple-lcc.graph_CREDIT_LINKS', 'r') as f:
        for line in f:
            source = int(line.split()[0])
            destination = int(line.split()[1])

            total_channel_cap = (float(line.split()[3])-float(line.split()[2])) + (float(line.split()[4])-float(line.split()[3]))
            #print(total_channel_cap)
            # add only channels with positive capacity
            if total_channel_cap > 0:
                values[source] += total_channel_cap/2
                values[destination] += total_channel_cap/2
                degrees_out[source] += 1
                degrees_out[destination] += 1
                degrees_in[source] += 1
                degrees_in[destination] += 1
                edges[source].append(destination)
                edges[destination].append(source)

    for i in range(len(values)):
        if degrees_out[i] > 0:
            dat.append(values[i])
        elif degrees_in[i] == 0:
            zero_cnt += 1
    print("#Accounts with zero degree: ",zero_cnt)
    print("#Accounts with non-zero degree: ",len(dat))
    print("Max degree: ",max(degrees_out))

    bins=np.arange(0,10,1)#设置连续的边界值，即直方图的分布区间[0,10],[10,20]...
    #直方图会进行统计各个区间的数值
    plt.hist(degrees_out,bins,color='fuchsia',alpha=0.5)#alpha设置透明度，0为完全透明
    plt.xlabel('scores')
    plt.ylabel('count')
    plt.xlim(0,10)#设置x轴分布范围
    plt.show()

    degrees_out_idx = np.argsort(degrees_out)
    degrees_out = np.sort(degrees_out)

    print("Top 200 degrees:")
    for i in range(40):
        print(10*i+1,"-",10*(i+1),degrees_out[-i*10-1:-(i+1)*10:-1])

    dat = np.sort(dat)
    np.save("data2.npy",values)
    #return
    print("Min money: ",dat[0],"Max money: ",dat[-1])

    test = [29,6,5]
    for m in test:
        passages = []
        supervisors = []
        connected = np.zeros(100000)
        
        i = -1
        while degrees_out[i] >= m:
            passages.append([degrees_out_idx[i]])
            supervisors.append([degrees_out_idx[i]])
            connected[degrees_out_idx[i]] = 1
            for j in edges[degrees_out_idx[i]]:
                passages[-1].append(j)
                connected[j] = 1
            i -= 1

##        print(passages[3])
##        print(len(passages[3]))
##        return

        print("z",len(passages),len(supervisors))

        isolate_cnt = 0
        for i in range(100000):
            if connected[i] == 0 and len(edges[i]) > 0:
                isolate_cnt += 1
                #print(len(edges[i]))
        print("m = ",m," Isolated nodes: ",isolate_cnt)

        passage_zero_degree = 0
        passage_edge = np.zeros((len(passages),len(passages)))
        passage_degree = np.zeros(len(passages))
        
        for i in range(len(passages)):
            passages[i].sort()
        print(len(passages))
        for i in range(len(passages)):
            for j in range(0,i):
                for k in passages[i]:
                    if binary_chop(passages[j],k) != -1:
                        passage_edge[i][j] = 1
                        passage_edge[j][i] = 1
                        passage_degree[i] += 1
                        passage_degree[j] += 1
                        break

        failure = 0
        zlist = [2,0,1] + list(range(3,100000))
        for i in zlist:
            if connected[i] > 0 or len(edges[i]) == 0:
                continue
            bfs_visited = np.zeros(100000)
            bfs = [i]
            while len(bfs) > 0:
                tmp = bfs[0]
                del bfs[0]
                if bfs_visited[tmp] == 1:
                    continue
                flag = False
                for j in range(len(passages)):
                    if binary_chop(passages[j],tmp) != -1:
                        passages[j].append(i)
                        passages[j].sort()
                        flag = True
                        break
                if flag:
                    break
                
                bfs_visited[tmp] = 1
                for j in range(len(edges[tmp])):
                    if edges[tmp][j] == 1 and bfs_visited[j] == 0:
                        bfs.append(j)


        print("#Failure of dividing nodes to passage: ",failure)

        tmp = 10000000
        isolated_passages = []
        for i in range(len(passages)):
            if passage_degree[i] < tmp:
                tmp = passage_degree[i]
            if int(passage_degree[i]) == 0:
                passage_zero_degree += 1
                isolated_passages.append(i)
                print(i)
        print("Isolated passages: ",passage_zero_degree)
        print("Min passage degree: ",tmp)

        passage_branches = 0
        passage_edges = []
        bfs_visited = np.zeros(len(passages))
        depth = 0
        for j in range(len(passages)):
            if bfs_visited[j] == 1:
                continue
            bfs = [(j,0,-1)]
            passage_branches += 1

            while len(bfs) > 0:
                tmp = bfs[0][0]
                tmp2 = bfs[0][1]
                tmp3 = bfs[0][2]
                del bfs[0]
                if bfs_visited[tmp] == 1:
                    continue
                bfs_visited[tmp] = 1
                if tmp3 >= 0:
                    passage_edges.append([tmp3,tmp])
                if tmp2 > depth:
                    depth = tmp2
                for i in range(len(passages)):
                    if passage_edge[tmp][i] == 1 and bfs_visited[i] == 0:
                        bfs.append((i,tmp2+1,tmp))
        print("Branches: ",passage_branches)
        print("Depth: ",depth)
        #print(passage_edges)
        print(len(passages))
        #print(len(supervisors))
        print(len(passage_edges))
        print(len(isolated_passages))
        np.save("data_"+str(m)+"_2",[passages,passage_edges,isolated_passages])

def main():
    work()

main()
