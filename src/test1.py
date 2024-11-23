"""
Euler method 
The differential equation is  "dy/dx = f = 1 + y/x "
input parameter : x = 1.0, y(1) = 0 (initial value), h = 0.1 (step width)
output parameter : x , y (solutiion of Euler method), xlogx
Auther : Shunsuke Motoi, Data: 2024/11/12, Version : 1.00
"""

import math

def Euler_method(x, y, h):
    return h * (1 + y/x)

def main():
    x, y, h = 1.0, 0.0, 0.1
    print("x  |     y    |  xlogx")

    # calculate the value of y where x(1.1 ~ 2.0)
    for i in range(10):
        y = y + Euler_method(x, y, h)

        # update x (1.1 ... 2.0)
        x = 1 + (i + 1) * 0.1

        print(f"{'{:.1f}'.format(x)}| {'{:.6f}'.format(y)} | {'{:.6f}'.format(x * math.log(x))}")

if __name__ == "__main__":
    main()

