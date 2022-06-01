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
import random

"Parameters"
n = 3
iter_max = 18
x = np.zeros((iter_max, n))
x = np.vstack([[1, 0.3, 0.1], x])

q = [1, 1, 1]

rho = 1

for k in range(iter_max+1):
    
    for i in range(3):
        x(k+1, i) = np.argmin()
    end
        
    xg = 1/n * np.sum(x, axis=1)
    
    for i in range(3):
        u(k+1, i) = u(k, i) + x(k+1, i) - xg(k+1)
    end
    
end

"How to record time?"

"Plots"
    