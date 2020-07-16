import random
import numpy as np

def work():
    trans_value = []
    with open('BitcoinVal.txt', 'r', encoding='UTF-8') as f: 
        f.readline()
        for line in f:
            trans_value.append(float(line))
    trans_value.sort()

    np.save("trans_dat.npy", trans_value)

def main():
    work()
    a = np.load("trans_dat.npy")
    print(len(a),a[0],a[-1])

main()
            
        
