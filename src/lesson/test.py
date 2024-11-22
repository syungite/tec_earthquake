"""
Runge-Kutta method 
The differential equation is  "dy/dx = f = 1 + y/x "
input parameter : x = 1.0, y(1) = 0 (initial value), h = 0.1 (step width)
output parameter : x , y (solution of runge-kutta), xlogx (exact solution)
Auther : Shunsuke Motoi, Date: 2024/11/12, Version : 1.00
"""
import math 

def rungeKutta_method(x, y, h):
    k1 = h * f(x, y)
    k2 = h * f(x + h/2.0, y + k1/2.0)
    k3 = h * f(x + h/2.0, y + k2/2.0)
    k4 = h                                                                                          * f(x + h, y + k3)
    return (k1 + 2*k2 + 2*k3 + k4)/6.0

def f(x, y):
    return 1 + y/x

def main():
    x, y, h = 1.0, 0.0, 0.1
    print("x  |     y    |   xlogx")

    # calculate the value of y where x(1.1 ~ 2.0)
    for i in range(10):
        y = y + rungeKutta_method(x, y, h)

        # update x (1.1 ... 2.0)
        x = 1 + (i + 1)*0.1
    
        print(f"{'{:.1f}'.format(x)}| {'{:.6f}'.format(y)} | {'{:.6f}'.format(x * math.log(x))}")

if __name__ == "__main__":
    main()