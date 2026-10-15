# WALL-E and EVE's Signal — Information-Gain Planner

A self-contained Python grid-world project for an autonomous search agent.

## What changed in v2
- The agent receives observations and a public mission view; it does not read EVE's true coordinates or hidden clue placements.
- Bayesian belief updates use noisy signal strength and bearing.
- Candidate actions are scored using approximate expected information gain, posterior probability, travel cost, and battery reserve.
- The agent estimates shortest-path return cost before committing to exploration.
- Recharge decisions and low-battery return behavior are explicit.
- Trace logs include action rationale, belief entropy, route cost and resource reserve.
- A multi-seed benchmark script reports mission success and resource use.

## Requirements
Python 3.10+. No third-party dependencies.

## Run a mission
```bash
python3 main.py --config configs/sample_mission.json
```

## Run tests
```bash
python3 -m unittest discover -s tests -v
```

## Benchmark multiple seeds
```bash
python3 benchmark.py --config configs/sample_mission.json --runs 30
```

## Outputs
- `reports/trace.jsonl`: step-by-step actions, observations, belief summaries and reasoning
- `reports/mission_report.json`: outcome, evidence, confidence and recommendation
- Benchmark output: summary table printed to the terminal

## Design
The environment owns hidden mission truth. The agent receives only its current position, battery, signal observations, and clues discovered by scanning. The belief state is a probability distribution over traversable cells. The planner approximates information gain by measuring how much a hypothetical signal reading at a candidate cell is expected to distinguish candidate EVE positions, then balances that benefit against travel and resource costs.

## Notes
This is a compact educational planner, not a formal POMDP solver. The information-gain estimate is heuristic; benchmark it across seeds before drawing conclusions. A useful next extension is a Monte Carlo expected-information-gain calculation using multiple possible signal outcomes.
