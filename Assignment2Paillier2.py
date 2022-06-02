# -*- coding: utf-8 -*-
"""
Secure & Private Control
Date

TU Delft | Assignment 2

Tjalling Idsardi
Theo Rieken
"""

import numpy as np
from phe import paillier
import matplotlib.pyplot as plt

"Parameters"
public_key, private_key = paillier.generate_paillier_keypair()

n = 3
iter_max = 18

x0 = [1, 0.3, 0.1]
xenc = [public_key.encrypt(x) for x in x0]
x = np.zeros((iter_max, n))
x = np.vstack([xenc, x])

q = [1, 1, 1]

rho = 1

xg = np.zeros(iter_max)
xg0 = 1/n * np.sum(x0)
xgenc = [public_key.encrypt(xg0)]
#xg = xg.insert(xgenc, 0)

u = np.zeros((iter_max+1, n))

"Encryption"
# public_key, private_key = paillier.generate_paillier_keypair()
# x = [public_key.encrypt(x) for x in x]
# xg = [public_key.encrypt(x) for x in xg]

"ADMM"
# for k in range(iter_max):
    
#     for i in range(3):
#         x[k+1, i] = np.argmin(x[k, i].transpose()*q[i]*x[k, i] + rho/2 * (np.absolute(x[k, i] - xg[k] + u[k, i]))**2) #Not sure how to do this
        
#     xg [k+1] = 1/n * np.sum(x[k+1])
    
#     for i in range(3):
#         u[k+1, i] = u[k, i] + x[k+1, i] - xg[k+1]

"Decryption"
#x_decr = 

"How to record time?"

"Plots"
