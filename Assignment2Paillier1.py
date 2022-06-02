# -*- coding: utf-8 -*-
"""
Secure & Private Control
Date

TU Delft | Assignment 2

Tjalling Idsardi
Theo Rieken
"""

import numpy as np
import matplotlib.pyplot as plt

"Parameters"
n = 3
iter_max = 18
x = np.zeros((iter_max, n))
x = np.vstack([[1, 0.3, 0.1], x])

q = [1, 1, 1]

rho = 1

xg = np.zeros(iter_max+1)
u = np.zeros((iter_max+1, n))

for k in range(iter_max+1):
    
    for i in range(3):
        x[k+1, i] = np.argmin(x[i].transpose()*q[i]*x[i] + rho/2 * (np.absolute(x[i] - xg[k] + u[k, i]))^2) #Not sure how to do this
        
    xg = 1/n * np.sum(x, axis=1)
    
    for i in range(3):
        u[k+1, i] = u[k, i] + x[k+1, i] - xg[k+1]

"How to record time?"

"Plots"
    