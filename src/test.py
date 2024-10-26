import numpy as np
import sys

x_0 = [8500/33, 500/33, 500/33, 50/41]
x_before = [0, 0, 0, 0]
x_after = [0, 0, 0, 0]

k1 = [[0, 0, 0, 0],[-16/33, 0, 0, 0],[0, -16/33, 0, 0],[0, 0, -40/41, 0]]
k2 = [[0, -16/33, 0, 0],[0, 0, -16/33, 0],[0, 0, 0, -16/33],[0, 0, 0, 0]]

def inner_product(a, b):
    if(len(a) != len(b)):
        print("Can't calculate innner product")
        sys.exit()
        
    s = len(a)
    p = 0
    for i in range(s):
        p += a[i] * b[i]
    return p

def compare(x_after, x_before):
    flag = True
    for i in range(4):
        if(abs(x_after[i] - x_before[i]) >= 1e-3): flag = False
    return flag

def cal0(x_after):
    global x_0
    x_after[0] = x_0[0]
    x_after[1] = x_0[1] + (16/33)*x_after[0]
    x_after[2] = x_0[2] + (16/33)*x_after[1]
    x_after[3] = x_0[3] + (40/41)*x_after[2]
    return x_after

def main():
    global x_0, x_before, x_after
    x_after = cal0(x_after)
    cnt = 1
    while True:
        x_after = [0,0,0,0]
        for i in range(4):
            x_after[i] = x_0[i] - inner_product(k1[i], x_after) - inner_product(k2[i], x_before)
        print(f"{cnt}: {x_after}")   
        if(compare(x_after, x_before)): break  
        x_before = x_after
        cnt+=1


if __name__ == "__main__":
    main()