"""Plot WALL-E's route from reports/trace.jsonl. Requires matplotlib."""
import argparse, json, os
import matplotlib.pyplot as plt

p = argparse.ArgumentParser()
p.add_argument('--trace', default='reports/trace.jsonl')
p.add_argument('--out', default='reports/mission_visualization.png')
args = p.parse_args()
rows = []
with open(args.trace, encoding='utf-8') as f:
    for line in f:
        if line.strip(): rows.append(json.loads(line))
positions, steps = [], []
for row in rows:
    pos = row.get('agent_position')
    if pos is None: pos = row.get('observation', {}).get('position')
    if pos is not None:
        positions.append(tuple(pos)); steps.append(row.get('step', 0))
if not positions: raise SystemExit('No positions found; run main.py first.')
fig, ax = plt.subplots(figsize=(8, 6))
xs, ys = [p[0] for p in positions], [p[1] for p in positions]
ax.plot(xs, ys, marker='o', label='WALL-E route')
ax.scatter(xs[0], ys[0], marker='s', s=90, label='Start')
ax.scatter(xs[-1], ys[-1], marker='*', s=180, label='Final position')
for i, (x, y) in enumerate(positions):
    if i in (0, len(positions)-1) or i % max(1, len(positions)//10) == 0:
        ax.annotate(str(steps[i]), (x, y), xytext=(4, 4), textcoords='offset points', fontsize=8)
ax.set(title='WALL-E Search Route', xlabel='Grid X', ylabel='Grid Y')
ax.set_aspect('equal', adjustable='box'); ax.grid(True, alpha=0.3); ax.legend(); fig.tight_layout()
os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True); fig.savefig(args.out, dpi=160); plt.close(fig)
print('Saved:', args.out)
