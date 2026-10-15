# WALL-E and EVE's Signal — Test and Benchmark Results

## Automated tests

Command:

```bash
python3 -m unittest discover -s tests -v
```

Result: **5 tests passed**

- `test_belief_entropy_nonnegative`
- `test_belief_normalized`
- `test_environment_observation`
- `test_hidden_state_not_in_public_status`
- `test_scan_returns_status`

## Multi-run benchmark

Command:

```bash
python3 benchmark.py --config configs/sample_mission.json --runs 30
```

| Metric | Result |
|---|---:|
| Runs | 30 |
| Missions locating EVE | 30/30 |
| Success rate | 100.0% |
| Mean steps | 32.23 |
| Mean battery remaining | 51.20 |
| Mean scanned cells | 16.57 |
| Mean steps on successful runs | 32.23 |

## Interpretation and scope

These results were obtained with the project's configured sample mission across 30 runs with varied signal-noise randomness. They demonstrate performance on this configuration only; they do **not** establish generalization to arbitrary maps or mission layouts.

## Reproduce

Run the test and benchmark commands above from the repository root using Python 3.10 or later.
