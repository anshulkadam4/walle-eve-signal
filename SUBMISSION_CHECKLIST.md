# Submission Checklist

## Run these commands
```bash
python3 -m unittest discover -s tests -v
python3 main.py --config configs/sample_mission.json
python3 benchmark.py --config configs/sample_mission.json --runs 30
python3 -m pip install matplotlib
python3 visualize.py
```

## Explain during the demo
1. The environment owns hidden EVE and clue coordinates.
2. WALL-E receives noisy signal readings and only discovers clues by scanning.
3. Bayesian updates maintain a probability distribution over candidate locations.
4. The planner balances posterior probability, information value, path distance, and return-battery reserve.
5. Direct scanning confirms success; otherwise the mission can end when no safe action remains.

## Report honestly
Use actual benchmark output. State the number of seeds tested and list limitations. A small benchmark is preliminary evidence, not proof of universal reliability.
