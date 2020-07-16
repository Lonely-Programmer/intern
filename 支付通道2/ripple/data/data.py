import numpy as np
import random

def work():
    values = np.zeros(100000)
    degrees_in = np.zeros(100000)
    degrees_out = np.zeros(100000)
    dat = []

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

    for i in range(len(values)):
        if degrees_out[i] > 0:
            dat.append(values[i])

    dat = np.sort(dat)
    np.save("data2.npy",dat)

def main():
    work()
    dat = np.load("data2.npy")
    print(len(dat))
    print(dat[0:10],dat[-1])

main()
