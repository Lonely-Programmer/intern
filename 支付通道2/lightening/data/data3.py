import random
import numpy as np

def work():
    dat = np.load("data2.npy")
    random.shuffle(dat)
    accounts = []
    group_num = 64
    low_bound = 2
    high_bound = 2500
    
    for i in range(group_num):
        accounts.append([])

    cnt = 0
    for i in range(0,2467):
            if cnt < low_bound * group_num:
                boundary = low_bound
            else:
                boundary = high_bound
            while True:
                tmp = random.randint(0,group_num-1)
                if len(accounts[tmp]) < boundary:
                    accounts[tmp].append(i)
                    cnt += 1
                    break
                
    #每个通道shuffle
    for i in range(len(accounts)):
        random.shuffle(accounts[i])

    np.save("group_64.npy",accounts)

def main():
    work()
    z = np.load("group_64.npy")
    for i in range(10):
        print(len(z[i]))

main()
            
        
