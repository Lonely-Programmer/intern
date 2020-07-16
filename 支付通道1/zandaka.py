import numpy as np
import matplotlib.pyplot as plt

def main():
    a = np.load("data/data.npy")
    a.sort()
    print(a[0:1000])

main()

