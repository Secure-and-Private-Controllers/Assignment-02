"""
Secure & Private Control
Date 02.06.2022

TU Delft | Assignment 2

Tjalling Idsardi
Theo Rieken
"""
import time
import matplotlib.pyplot as plt
from sympy import Symbol, solve


class User:

    # State and average (for consensus)
    x = None
    x_bar = None

    # Target output signal
    u = None

    # Parameter of the problem
    q = None

    def __init__(self, value, q):

        self.x = value
        self.x_bar = 0
        self.u = 0
        self.q = q

    def compute_step(self, rho, get_xbar):

        # Get the average value
        self.x_bar = get_xbar()

        # Construct a symbolic x
        x = Symbol('x', real=True)

        # The problem to solve (encoded directly in user object)
        problem_to_solve = x**2 * self.q

        # Construct the total problem to solve
        f = problem_to_solve + (rho/2) * (abs(x - self.x_bar + self.u))**2

        derivative = f.diff(x)
        x_next = solve(derivative, x)

        # Compute the next value of x
        if type(x_next) is list:
            if len(x_next) > 1:
                raise ValueError("More then one solution to the minimization problem")
            self.x = x_next[0]
        else:
            self.x = x_next

        # Compute the control signal (to change next time)
        self.u = self.x - self.x_bar


class TrustedParty:

    # List of users that this trusted party "works" for
    users = None

    # Storage for plotting results later on
    state_store = None
    x_bar_store = None
    duration_store = None

    # The start time of the consensus process
    start_time = None

    def __init__(self, initial_values: list):

        # Setup the storage lists
        self.state_store = []
        self.x_bar_store = []
        self.duration_store = []

        # Setup users and data storage
        self.users = []
        for setup in initial_values:
            self.users.append(User(value=setup['x'], q=setup['q']))
            # Setup the storage for users state
            self.state_store.append([])

        # Start a timer to measure the duration
        self.start_time = time.time()

    def step(self):

        # Measure the time to compute iteration duration
        iteration_start_time = time.time()

        # Compute the next state values for the users
        for i, user in enumerate(self.users):
            user.compute_step(rho=1, get_xbar=self.get_average)
            self.state_store[i].append(user.x)

        # Append the duration of the iteration
        self.duration_store.append(time.time() - iteration_start_time)

        # Append the development of the average
        self.x_bar_store.append(self.get_average())

    def get_average(self):

        state_sum = 0
        for u in self.users:
            state_sum += u.x
        x_bar = state_sum / len(self.users)
        return x_bar

    def finish_experiment(self):

        # Obtain the full duration in seconds
        duration = time.time() - self.start_time
        print("Experiment took {:.2f}".format(duration * 1000))

        # Plot the iterations duration
        plt.figure(figsize=(15, 8))
        plt.plot(self.duration_store)
        plt.title("Computation Time")
        plt.legend(["Iteration Duration"])
        plt.xlabel("Iterations")
        plt.ylabel("Duration")
        plt.show()

        # Plot the iterations duration
        plt.figure(figsize=(15, 8))
        labels = ["Average (x_bar)"]
        plt.plot(self.x_bar_store)
        for i, x_track in enumerate(self.state_store):
            plt.plot(x_track)
            labels.append("User " + str(i + 1))
        plt.title("Users local values")
        plt.legend(labels)
        plt.xlabel("Iterations")
        plt.ylabel("x value")
        plt.show()


class Experiment:

    # A trusted party that mediates between the users
    trusted_party = None

    # Maximum allowed number of iterations
    max_iters = None

    def __init__(self, initial_values: list, max_iters: int = 20):

        # Maximum number of iterations while solving
        self.max_iters = max_iters

        # Create instances that interact with each other
        self.trusted_party = TrustedParty(initial_values)

    def run_experiment(self):

        # Perform ADMM steps
        for i in range(self.max_iters):
            # Perform a step
            self.trusted_party.step()

        # Call the finish method (for plotting and measurements)
        self.trusted_party.finish_experiment()


# Create an experiment
experiment = Experiment([{'x': 1, 'q': 1}, {'x': 0.3, 'q': 1}, {'x': 0.1, 'q': 1}], 18)
# Run the experiment
experiment.run_experiment()
