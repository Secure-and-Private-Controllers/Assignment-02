"""
Secure & Private Control
Date 02.06.2022

TU Delft | Assignment 2

Tjalling Idsardi
Theo Rieken
"""

import numpy as np
from phe import paillier
import time
import matplotlib.pyplot as plt

start_time = time.time()

#Generating keys
public_key, private_key = paillier.generate_paillier_keypair()

# Setup the parameters
n = 3
iter_max = 18
x0 = [1, 0.3, 0.1]

#Matrix storing x-values with encrypted initial values
xenc = [public_key.encrypt(x) for x in x0]
x = np.zeros((iter_max, n))
x = np.vstack([xenc, x])

#Variable storing the q-values
q = [1, 1, 1]

# Use a rho value of one for the ADMM algorithm
rho = 1

#Vector storing global x with encrypted initial x
xg = np.zeros(iter_max)
xg0 = 1/n * np.sum(x0)
xgenc = [public_key.encrypt(xg0)]
xg = np.hstack([xgenc, xg])

#Matrix storing u-values
u = np.zeros((iter_max+1, n))

# Start measuring the execution time
start_time = time.time()


#ADMM (from Assignment2Paillier1.py)


#Decryption
x_decr = [private_key.decrypt(x) for x in xenc]
#for x in x #(Full x-matrix)
xg_decr = [private_key.decrypt(x) for x in xgenc]
#xg_decr = private_key.decrypt(xg[17]) #(Final xg)

# Record the duration in seconds that the algorithm took
algorithm_duration = time.time() - start_time
print("Algorithm took {:.4f} seconds".format(algorithm_duration))


#Plots (same as Assignment2Paillier1.py)

