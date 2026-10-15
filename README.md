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


## RESULTS/OUTPUT
you can check result/output in RESULTS.md
I have attached screenshots here

1.Mission execution

<img width="835" height="825" alt="Screenshot 2026-10-15 at 7 31 35 PM" src="https://github.com/user-attachments/assets/eb35e9f6-d8cf-4d45-9ee9-f90493db1f57" />

<img width="809" height="826" alt="Screenshot 2026-10-15 at 7 32 00 PM" src="https://github.com/user-attachments/assets/864cd6e1-d308-4f29-a964-f4240fb159ea" />

<img width="786" height="381" alt="Screenshot 2026-10-15 at 7 32 12 PM" src="https://github.com/user-attachments/assets/5c607048-a6da-4d1d-b29d-7a5f3d096a02" />


2.Performance evaluation

<img width="803" height="187" alt="Screenshot 2026-10-15 at 7 38 14 PM" src="https://github.com/user-attachments/assets/3943940b-2d8c-4825-9c72-7197fea5ab2c" />

4.Benchmark results

<img width="807" height="168" alt="Screenshot 2026-10-15 at 7 39 15 PM" src="https://github.com/user-attachments/assets/7ad5895d-2811-4e4a-87a7-93556160e6da" />

5.Visualization

<img width="442" height="330" alt="Screenshot 2026-10-15 at 8 39 32 PM" src="https://github.com/user-attachments/assets/e86928e0-3539-4814-9e1c-82d861847b73" />

