"""Run a deterministic multi-seed benchmark for the configured mission."""
import argparse, copy, json, tempfile, os, contextlib
from main import run

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--config",default="configs/sample_mission.json")
    parser.add_argument("--runs",type=int,default=30)
    parser.add_argument("--max-steps",type=int,default=None)
    args=parser.parse_args()
    with open(args.config,encoding="utf-8") as f: base=json.load(f)
    results=[]
    with tempfile.TemporaryDirectory() as tmp:
        for i in range(args.runs):
            cfg=copy.deepcopy(base)
            cfg["seed"]=int(base.get("seed",1))+i
            cfg.setdefault("output",{})["render_ascii"]=False
            with open(os.devnull, "w") as sink, contextlib.redirect_stdout(sink):
                report=run(cfg,os.path.join(tmp,f"run_{i+1}"),args.max_steps,render=False)
            results.append(report)
    located=[r for r in results if r["status"]=="located"]
    n=len(results)
    print("\n=== BENCHMARK SUMMARY ===")
    print(f"Runs: {n}")
    print(f"Located EVE: {len(located)}/{n} ({100*len(located)/max(1,n):.1f}%)")
    print(f"Mean steps: {sum(r['steps_used'] for r in results)/max(1,n):.2f}")
    print(f"Mean battery remaining: {sum(r['battery_remaining'] for r in results)/max(1,n):.2f}")
    print(f"Mean scanned cells: {sum(r['scanned_cells'] for r in results)/max(1,n):.2f}")
    if located:
        print(f"Mean steps on successful runs: {sum(r['steps_used'] for r in located)/len(located):.2f}")

if __name__=="__main__":
    main()
