# WALL-E and EVE's Signal — Information-Gain Planner

A self-contained Python grid-world simulation featuring an autonomous search agent that navigates an uncertain environment to locate EVE while managing limited battery resources.

## Features

- **Partially observable environment:** The agent receives observations and public mission information without direct access to EVE's true coordinates or undiscovered clue locations.
- **Bayesian belief updates:** Updates location probabilities using noisy signal-strength and bearing observations.
- **Information-gain planning:** Scores candidate actions using estimated information gain, posterior probability, travel cost, and battery reserve.
- **Resource-aware navigation:** Estimates shortest-path return costs and accounts for battery constraints during exploration.
- **Recharge and return logic:** Implements explicit recharge decisions and low-battery return behavior.
- **Decision tracing:** Records action rationale, belief entropy, route costs, and resource reserves.
- **Multi-run evaluation:** Includes a benchmark script for measuring mission success and resource consumption across multiple runs.

## Requirements

- Python 3.10 or later
- No third-party dependencies for the core simulation

## Getting Started

Clone the repository:

```bash
git clone https://github.com/anshulkadam4/walle-eve-signal.git
cd walle-eve-signal
```

Run a mission:

```bash
python3 main.py --config configs/sample_mission.json
```

Run the automated tests:

```bash
python3 -m unittest discover -s tests -v
```

Run a 30-run benchmark:

```bash
python3 benchmark.py --config configs/sample_mission.json --runs 30
```

## Outputs

- `reports/trace.jsonl` — Step-by-step actions, observations, belief summaries, and decision rationale.
- `reports/mission_report.json` — Mission outcome, collected evidence, confidence, and recommendation.
- Benchmark results — Mission success rate and resource-use statistics printed to the terminal.

## Architecture and Planning Approach

The environment maintains the hidden mission state. The agent operates using its current position, battery level, signal observations, and clues discovered through scanning.

Its belief state represents a probability distribution over traversable cells. The planner estimates the potential information value of candidate actions and balances that value against navigation costs and remaining resources.

The system combines probabilistic belief updates, heuristic information-gain estimation, shortest-path cost calculations, and battery-aware decision-making to guide autonomous exploration.

## Limitations and Future Work

This project is an educational prototype rather than a formal Partially Observable Markov Decision Process (POMDP) solver. Its information-gain calculation is heuristic, and benchmark results depend on the configured mission environment.

Potential extensions include Monte Carlo information-gain estimation, testing across varied map layouts, and comparing the planner against baseline search strategies.
