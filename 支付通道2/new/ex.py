import numpy as np

class Node:
    def __init__(self,x=0,child=None):
        self.money = x
        self.child = child
        

def main():
    a = Node(1)
    a.child = Node(2)
    a.child.child = Node(3)

    y = a.child
    y.money = 10

    a.child.child.money = 100

    z = a
    while z != None:
        print(z.money)
        z = z.child

main()
