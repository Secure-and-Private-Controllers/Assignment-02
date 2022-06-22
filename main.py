"""
Secure & Private Control
Date 02.06.2022

TU Delft | Assignment 2

Tjalling Idsardi
Theo Rieken
"""
import os
import time
import random
import matplotlib.pyplot as plt
from phe import paillier
from sympy import Symbol, solve
from modules.ot.ot import *


class RandomNumberGenerator:

    user_count = None

    def __init__(self, user_count: int):
        self.user_count = user_count
        values = []

        # Generate random numbers that sum to zero
        # sam = random.sample(range(-10, 10), k=self.user_count - 1)
        # vals = sam + [-sum(sam)]

        for val in range(self.user_count):
            values.append(bytes("{:2f}".format(random.random()), encoding='utf8'))
        if len(values) > 0:
            self.alice = Alice(values, 1, len(values[0]))
            self.alice.setup(file_name=os.path.join(os.getcwd(), 'secret', 'alice_setup.json'))
        else:
            raise ValueError("The user count has to be a positive number")

    def transmit_data(self):
        for user_id in range(self.user_count):
            self.alice.transmit(
                file_name=os.path.join(os.getcwd(), 'secret', 'mss_{:d}.json'.format(user_id)),
                bob_file_name=os.path.join(os.getcwd(), 'secret', 'bob_{}_setup.json'.format(user_id))
            )


class Agent:

    # Identifier of this agent
    id_stack = 0
    ident = None

    # State and average (for consensus)
    x = None
    x_bar = None

    # Target output signal
    u = None

    # Parameter of the problem
    q = None

    # Initialize bob
    bob = None

    # Encryption keys
    private_key = None
    public_key = None
    trusted_party_key = None

    def __init__(self, value, q, obscure_value: bool = False):

        # Attributes of the agent
        self.x = value
        self.x_bar = 0
        self.u = 0
        self.q = q

        # Save initial computation step
        self.is_initial = True

        # Give id and increment
        self.ident = Agent.id_stack
        Agent.id_stack += 1

        # Check if OT to random should be initialized
        if obscure_value:
            bob_file = os.path.join(os.getcwd(), 'secret', 'bob_{}_setup.json'.format(self.ident))
            alice_file = os.path.join(os.getcwd(), 'secret', 'alice_setup.json')
            self.bob = Bob([self.ident])
            self.bob.setup(alice_file_name=alice_file, file_name=bob_file)

    def establish_encryption(self, public_key):

        # Generate public and private key
        self.trusted_party_key = public_key

        # Generate own public and private key
        public_key, self.private_key = paillier.generate_paillier_keypair()

        # Return this agents public key
        return public_key

    def compute_step(self, rho, get_xbar):
        """
        Update of local value. We do not compute the following value using the encrypted values
        which causes a further delay. However, the way we solve the minimization (using sympy)
        it does not work with encrypted values.

        TODO: Figure out how to use the underlying data in the encrypted value (e.g. Exponent?) directly

        :param rho:
        :param get_xbar:
        """

        # Get the average value
        x_bar = get_xbar(self)

        # Receive a number from the random number generator to obscure this value
        if self.bob is not None:
            obscure_number = float(self.bob.receive(alice_file_name=os.path.join(os.getcwd(), 'secret', 'mss_{}.json'.format(self.ident)))[0])
        else:
            obscure_number = 0

        # Updates the x bar value
        self.x_bar = x_bar if self.private_key is None else self.private_key.decrypt(x_bar)

        # Construct a symbolic x
        # x = Symbol('x', real=True)

        # The problem to solve (encoded directly in agent object)
        # problem_to_solve = x**2 * self.q

        # Construct the total problem to solve and solve it
        # f = problem_to_solve + (rho/2) * (abs(x - self.x_bar + self.u))**2
        # derivative = f.diff(x)
        # x_next = solve(derivative, x)

        # Laura's hint (much easier than computing everytime)
        x_next = rho / (self.q + rho) * (self.x_bar - self.u)

        # Add the obscure number to the value
        if self.is_initial:

            # Add one time pad to the number
            x_next += obscure_number
            self.is_initial = False

        # Simulate different speeds and delays in the bus-system (usually parallel processing)
        if random.random() > 0.2:

            # Compute the next value of x
            if type(x_next) is list:
                if len(x_next) > 1:
                    raise ValueError("More then one solution to the minimization problem")
                self.x = x_next[0]
            else:
                self.x = x_next

            # Compute the control signal (to change next time)
            self.u = self.x - self.x_bar

    def get_state(self):
        if self.trusted_party_key is not None:
            return self.trusted_party_key.encrypt(float(self.x))
        return self.x

    @staticmethod
    def reset_agent_ids():
        Agent.id_stack = 0


class TrustedParty:

    # List of agents that this trusted party "works" for
    agents = None
    agent_keys = None

    # Storage for plotting results later on
    state_store = None
    x_bar_store = None
    duration_store = None

    # Remember whether random number generator and OT is used as well
    include_rng = None

    # The start time of the consensus process
    start_time = None

    # Save the encryption keys
    public_key = None
    private_key = None

    def __init__(self, initial_values: list, encrypted: bool = False, include_rng: bool = False):

        # Setup the storage lists
        self.state_store = []
        self.x_bar_store = []
        self.duration_store = []

        # Save information about usage of RNG and OT for later
        self.include_rng = include_rng

        # Generate public and private key (or leave none if desired)
        key_tuple = paillier.generate_paillier_keypair() if encrypted else (None, None)
        public_key, self.private_key = key_tuple

        # Setup agents and data storage
        self.agents = []
        self.agent_keys = []
        for setup in initial_values:

            # Create a new agent
            new_agent = Agent(value=setup['x'], q=setup['q'], obscure_value=include_rng)

            # Create an agent and append it to the records
            self.agents.append(new_agent)

            # Establish an encrypted information pathway with the agent
            if encrypted:
                agents_key = new_agent.establish_encryption(public_key)
                self.agent_keys.append(agents_key)
            else:
                self.agent_keys.append(None)

            # Setup the storage for agents state
            self.state_store.append([])

        # Start a timer to measure the duration
        self.start_time = time.time()

    def step(self):

        # Measure the time to compute iteration duration
        iteration_start_time = time.time()

        # Compute the next state values for the agents
        for i, agent in enumerate(self.agents):
            agent.compute_step(rho=1, get_xbar=self.get_average)

            agent_state = agent.get_state()
            agent_state = agent_state if self.private_key is None else self.private_key.decrypt(agent_state)

            self.state_store[i].append(agent_state)

        # Append the duration of the iteration
        self.duration_store.append(time.time() - iteration_start_time)

        # Append the development of the average
        self.x_bar_store.append(self.get_average())

    def get_average(self, agent=None):
        state_sum = 0
        for u in self.agents:
            state_sum += u.x
        x_bar = state_sum / len(self.agents)
        if agent is not None and self.private_key is not None:
            for i, a in enumerate(self.agents):
                if a == agent:
                    return self.agent_keys[i].encrypt(float(x_bar))
            raise ValueError("Agent not known to trusted party")
        return x_bar

    def finish_experiment(self, show_figures: bool = True, image_path: str = "experiment_outcome", figure_counter: int = 1):

        # Obtain the full duration in seconds
        duration = time.time() - self.start_time
        print("Experiment {:d} took {:.2f} {:s}".format(figure_counter, ((duration * 1000) if duration < 1 else duration), ("ms" if duration < 1 else "s")))

        # Print the final agent state values
        for i, agent in enumerate(self.agents):
            agent_state = agent.get_state()
            agent_state = agent_state if self.private_key is None else self.private_key.decrypt(agent_state)
            print("Agent {:d} has final value {:.4f}".format(i + 1, agent_state))

        # Plot the iterations duration
        fig = plt.figure(figsize=(15, 8))
        plt.plot(self.duration_store)
        plt.title("Computation Time (" + ("plaintext" if self.private_key is None else "encrypted") + ")")
        plt.legend(["Iteration Duration"])
        plt.xlabel("Iterations")
        plt.ylabel("Duration")
        if show_figures:
            plt.show()
        fig.savefig(os.path.join(os.getcwd(), "figures", "{:s}_{:s}_{:d}.png".format(image_path, "duration", figure_counter)))

        # Plot the iterations duration
        fig = plt.figure(figsize=(15, 8))
        labels = ["Average (x_bar)"]
        plt.plot(self.x_bar_store)
        for i, x_track in enumerate(self.state_store):
            plt.plot(x_track)
            labels.append("Agent " + str(i + 1))
        plt.title("Consensus Development (" + ("plaintext" if self.private_key is None else "encrypted") + ")")
        plt.legend(labels)
        plt.xlabel("Iterations")
        plt.ylabel("x value")
        if show_figures:
            plt.show()
        fig.savefig(os.path.join(os.getcwd(), "figures", "{:s}_{:s}_{:d}.png".format(image_path, "consensus", figure_counter)))


class Experiment:

    # A trusted party that mediates between the agents
    trusted_party = None

    # The number of experiment that has been run
    experiment_number = None

    # Random number generator (if agents don't trust trusted party)
    rng = None

    def __init__(self):

        # Initialize the number of experiments
        self.experiment_number = 1

    def run_experiment(self, initial_values, max_iters: int = 20, encrypted: bool = False, include_rng: bool = False):

        # Tell user about current step
        print("\n––––––––––\nStarted Experiment\nSetting up the trusted party and the agents ...")

        # Reset the agent's ids
        Agent.reset_agent_ids()

        # Setup random number generator if usage is desired
        if include_rng:

            # Initialize a random number generator
            self.rng = RandomNumberGenerator(len(initial_values))

        # Create instances that interact with each other
        self.trusted_party = TrustedParty(initial_values, encrypted=encrypted, include_rng=include_rng)

        # Transmit data via OT if all setup
        if include_rng:
            self.rng.transmit_data()

        # Perform ADMM steps
        for i in range(max_iters):

            # Tell user about current step
            print("Computing Step {:d}/{:d} ...".format(i, max_iters))

            # Perform a step
            self.trusted_party.step()

        # Call the finish method (for plotting and measurements)
        self.trusted_party.finish_experiment(figure_counter=self.experiment_number)

        # Increase the number of experiments
        self.experiment_number += 1


# Create an experiment
experiment = Experiment()

# Create a variable with the agents configuration
agents_setup = [{'x': 1, 'q': 1}, {'x': 0.3, 'q': 1}, {'x': 0.1, 'q': 1}]

# Run the plaintext experiment
experiment.run_experiment(agents_setup, max_iters=18, encrypted=False)

# Run the encrypted experiment
experiment.run_experiment(agents_setup, max_iters=18, encrypted=True)

# Run the encrypted experiment where also the agent does not trust the trusted party
experiment.run_experiment(agents_setup, max_iters=18, encrypted=True, include_rng=True)
