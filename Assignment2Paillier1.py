"""
Secure & Private Control
Date 02.06.2022

TU Delft | Assignment 2

Tjalling Idsardi
Theo Rieken
"""

import numpy as np
import time
import matplotlib.pyplot as plt

# Setup the parameters
n = 3
iter_max = 18
initial_values = [1, 0.3, 0.1]

# Create a matrix storing the x values
x = np.matrix(np.zeros(shape=(iter_max, n)))
x[0] = initial_values

# Variable storing the q values
q = [1, 1, 1]

# Use a rho value of one for the ADMM algorithm
rho = 1

# Setup a vector for storing the final global value
xg = np.matrix(np.zeros(iter_max)).T
u = np.matrix(np.zeros((iter_max, n)))

# Vector that contains the iteration durations
durations = np.matrix(np.zeros(iter_max)).T

# Initiate the first global x value
xg[0] = 1/n * np.sum(x[0])

# Start measuring the execution time
start_time = time.time()

# Perform ADMM method (alternating direction method of multipliers)
for k in range(iter_max):

    iteration_start = time.time()

    if k < iter_max - 1:

        for i in range(n):

            # This is a VERY STUPID way of producing the minimizing argument xi for the function
            # We did not fully figure this formula out and were trying around with things
            upper_bound = 9e99
            x_i_min = x[k, i]
            for tv in np.arange(-100, 100, 0.01):
                s1 = tv**2 * q[i]
                s2 = 0.5 * rho * (np.abs(tv - xg[k].item() + u[k, i].item())) ** 2
                s = s1 + s2
                if s < upper_bound:
                    upper_bound = s
                    x_i_min = tv
            x_min = x_i_min

            # # This is just a VERY WEIRD and NOT OKAY way of trying things out to make the algorithm converge!!!
            # # In this case, we were testing always taking the xi that minimizes the function (not right of course)
            # x_min = 99
            # tmp = 9e19
            # for j in range(n):
            #     s1 = (np.matmul(x[k, :], x[k, :].T)**2).item() * q[i]
            #     s2 = 0.5 * rho * (np.abs(x[k, j].item() - xg[k].item() + u[k, i].item())) ** 2
            #     s = s1 + s2
            #
            #     if s < tmp:
            #         tmp = s
            #         x_min = x[k, j].item()

            # FIXME: Argmin over xi (we want to identify the xi that minimizes the function)
            x[k + 1, i] = x_min

        xg[k + 1] = np.sum(x[k + 1]) / n

        for i in range(n):
            u[k + 1, i] = u[k, i] + x[k + 1, i] - xg[k + 1]

    # Save the iteration duration
    durations[k] = time.time() - iteration_start

# Record the duration in seconds that the algorithm took
algorithm_duration = time.time() - start_time
print("Algorithm took {:.4f} milliseconds".format(algorithm_duration * 1000))

# Plot the value of x and xg over time/iterations
plt.figure(figsize=(14, 8))
plt.plot(np.arange(iter_max), durations * 1000)
plt.title("Duration of iterations")
plt.legend(["Algorithm Iteration Duration [ms]"])
plt.xlabel("Iteration")
plt.ylabel("Milliseconds")
plt.show()

# Plot the duration of each iteration
plt.figure(figsize=(14, 8))
labels = ['x_dash']
plt.plot(np.arange(iter_max), xg)
for i in range(n):
    plt.plot(np.arange(iter_max), x[:, i])
    labels.append('Agent value x_' + str(i + 1))
plt.title("Consensus Value / Agent State Values")
plt.xlabel("Iteration")
plt.legend(labels)
plt.ylabel("State")
plt.show()
