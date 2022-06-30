# Encrypted Consensus Problems

### Secure and Private Control - Assignment II

To run the simulations, simply run the `main.py` file. All classes and code are contained
in that file. The different experiments that are run can be found at the bottom of the file.

```commandline
python main.py
```

Results of the experiments in terms of figures are opened while the experiment runs. Log
messages will also appear in the CLI for better understanding. The figures are saved in 
the location `/figrues/*`.

### Running Experiments

At the bottom of `main.py`, three experiment function calls that appear like what is shown
below are present. By commenting in our out different parts the desired experiment can be
run. The parameter `include_rng` stands for `RandomNumberGenerator` and introduces the third
party which sends random numbers for 1-time pad to the agents via OT.

```python
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
```

When running (e.g. here, the third experiment) the experiments, the console output shows
what is currently happening. 

```commandline
Started Experiment
Setting up the trusted party and the agents ...
Pubkey and hashes published.
Polynomial published.
Polynomial published.
Polynomial published.
G has been published.
G has been published.
G has been published.
Computing Step 0/18 ...
Computing Step 1/18 ...
Computing Step 2/18 ...
Computing Step 3/18 ...
Computing Step 4/18 ...
Computing Step 5/18 ...
Computing Step 6/18 ...
Computing Step 7/18 ...
Computing Step 8/18 ...
Computing Step 9/18 ...
Computing Step 10/18 ...
Computing Step 11/18 ...
Computing Step 12/18 ...
Computing Step 13/18 ...
Computing Step 14/18 ...
Computing Step 15/18 ...
Computing Step 16/18 ...
Computing Step 17/18 ...
Experiment 1 took 58.31 s
```

### Results of Experiments

Experiments were conducted on consensus problems with encrypted and not-encrypted
communication between a `TrustedParty` and `Agents` (those classes are modelled in the
main file). As can be seen in the following figure, the agents reach consensus. The
strangely shaped plots arise from a simulation of different clock speeds. The agents update
their value only if `random.random() > 0.5`, thus also not updating in some iterations.
This way, more real-world conditions are modeled.  

#### Experiment 1
![Experiment Outcome (not encrypted)](figures/experiment_outcome_consensus_1.png)
![Experiment Outcome (not encrypted)](figures/experiment_outcome_duration_1.png)

The update of the agents' internal state `x_i` is only done with a 80% probability
to also model real conditions where messages might be delayed sometimes or don't get
delivered at all. A proper way would have been to use `threading` to let them run 
in parallel but this approach was taken instead. 

#### Experiment 2
![Experiment Outcome (not encrypted)](figures/experiment_outcome_consensus_2.png)
![Experiment Outcome (not encrypted)](figures/experiment_outcome_duration_2.png)

Clearly, the introduction of Pallier encryption in the second experiment boosted the
duration of the experiment. In the first experiment, the setup (and allocation of memory)
took longest, while in the second experiment much more activity in the 
computation of the consensus problem can be seen.

#### Experiment 3
![Experiment Outcome (not encrypted)](figures/experiment_outcome_consensus_3.png)
![Experiment Outcome (not encrypted)](figures/experiment_outcome_duration_3.png)

In the third experiment, which also introduces OT and another party, the RandomNumberGenerator
that produces a vector of random numbers for a 1-time pad for the agents internal value
to obscure it and not show it to the (now also untrusted) trusted party. A further delay can be
seen in the setup (generation of hashes etc.) of OT. In the computation the duration
is a about the same. However, Experiment 2 took about `40s` and Experiment 3 took about `1 min`
which makes the differences visible. 