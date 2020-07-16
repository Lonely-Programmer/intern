import numpy as np
import random

def work():
    cnt = 0
    dat = np.zeros((1000000,3))
    with open('ripple_val.csv', 'r') as f:
        for line in f:
            source = int(line.split(',')[0])
            destination = int(line.split(',')[1])
            money = float(line.split(',')[2])
            dat[cnt][0] = source
            dat[cnt][1] = destination
            dat[cnt][2] = money
            cnt += 1

    np.save("trans_dat.npy",dat)

def main():
    work()
    dat = np.load("trans_dat.npy")
    print(len(dat))
    print(dat[0:10],dat[-1])

main()
