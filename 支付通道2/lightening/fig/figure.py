import matplotlib.pyplot as plt

def work():
    x = []
    y = []
    names = ["k = 5, depth = 4","k = 6, depth = 3","k = 7, depth = 3","k = 8, depth = 3","k = 9, depth = 3","k = 10, depth = 3"]

    y.append([0.9081, 0.89985, 0.8885, 0.88505, 0.8799799999999999])
    y.append([0.9887, 0.9859, 0.9833999999999999, 0.980675, 0.9784200000000001])
    y.append([0.9736, 0.96885, 0.9626666666666667, 0.958025, 0.95436])
    y.append([0.9359, 0.92725, 0.922, 0.9167000000000001, 0.91284])
    y.append([0.9023, 0.8899, 0.8805666666666666, 0.872925, 0.8686])
    y.append([0.8513999999999999, 0.83905, 0.8307666666666668, 0.8213250000000001, 0.8144399999999999])

    for i in range(len(y)):
        x.append(list(range(1000,6000,1000)))

    for i in range(len(y)):
        plt.plot(x[i],y[i],label=names[i],marker='o')
        
    plt.xlabel('Transaction number') 
    plt.ylabel('Success rate') 
    plt.title('Scalability')
    plt.ylim(0.7, 1.0)
    plt.legend() 
    plt.show() 

def main():
    work()

main()
