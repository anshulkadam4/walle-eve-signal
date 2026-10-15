"""Run one WALL-E mission with information-gain and resource-aware planning."""
from __future__ import annotations
import argparse, json, os
from environment import MissionEnvironment
from agent import WallEAgent

def run(config, out_dir=None, max_steps=None, render=None):
    out_dir = out_dir or config.get("output", {}).get("directory", "reports")
    os.makedirs(out_dir, exist_ok=True)
    env = MissionEnvironment(config)
    agent = WallEAgent(
        env.width, env.height, config["map"].get("obstacles", []),
        config.get("start", [0,0]), config["resources"],
        home=config.get("home", config.get("start", [0,0]))
    )
    if render is None:
        render = bool(config.get("output", {}).get("render_ascii", True))
    limit = min(max_steps or env.max_steps, env.max_steps)
    trace_path = os.path.join(out_dir, "trace.jsonl")
    report_path = os.path.join(out_dir, "mission_report.json")
    initial = env.initial_observation()
    agent.update_belief(initial["signal"])
    with open(trace_path, "w", encoding="utf-8") as trace:
        trace.write(json.dumps({
            "event":"initial_observation",
            "observation":initial,
            "belief_entropy_bits":round(__import__("agent").entropy(agent.belief.values()),5),
            "belief_top":agent.top_beliefs()
        }) + "\n")
        while not env.done and agent.steps < limit:
            public = env.public_status()
            action = agent.choose_action(public)
            result = env.step(action)
            agent.steps += 1
            if result.get("status") == "moved":
                agent.position = tuple(result["position_after"])
                agent.visited.add(agent.position)
            if action.get("type") == "scan" and result.get("status") in ("scan_complete","eve_located"):
                agent.scanned.add(tuple(result["position_after"]))
            if result.get("observation", {}).get("signal"):
                agent.update_belief(result["observation"]["signal"])
            for clue in result.get("clues_found", []):
                agent.update_clue(clue)
            if result.get("eve_found"):
                agent.eve_found = True
                agent.eve_position = tuple(result["position_after"])
                agent.evidence.append({"type":"direct_confirmation","position":list(agent.eve_position)})
            entry = {
                "step":agent.steps,
                "action":action,
                "result":result,
                "agent_position":list(agent.position),
                "battery_remaining":round(env.battery,2),
                "belief_entropy_bits":round(__import__("agent").entropy(agent.belief.values()),5),
                "belief_top":agent.top_beliefs(),
                "known_clues":len(agent.known_clues)
            }
            trace.write(json.dumps(entry) + "\n")
            if render and (agent.steps % 10 == 0 or env.done):
                print(f"\nStep {agent.steps} | battery={env.battery:.1f} | action={action['type']} | entropy={entry['belief_entropy_bits']}")
                print(env.ascii_map(agent.position))
            if result.get("status") in ("time_budget_exhausted","agent_stopped"):
                break

    top = agent.top_beliefs(5)
    status = "located" if env.eve_found else ("budget_exhausted" if agent.steps >= limit else "not_located")
    report = {
        "mission":"WALL-E and EVE's Signal",
        "planner":"heuristic expected information gain + resource-aware path planning",
        "status":status,
        "steps_used":agent.steps,
        "step_budget":limit,
        "battery_remaining":round(env.battery,2),
        "visited_cells":len(agent.visited),
        "scanned_cells":len(agent.scanned),
        "clues_discovered":[{"position":list(c["position"]),"kind":c["kind"]} for c in agent.known_clues],
        "eve_location":list(agent.eve_position) if agent.eve_position else None,
        "inferred_location":top[0]["position"] if top else None,
        "top_hypotheses":top,
        "confidence":round(top[0]["probability"],5) if top else 0.0,
        "belief_entropy_bits":round(__import__("agent").entropy(agent.belief.values()),5),
        "evidence":agent.evidence,
        "recommended_next_step":(
            "EVE was directly confirmed; end the search and report the location." if env.eve_found else
            "Continue from the highest-utility safe frontier; recalibrate signal likelihoods and preserve return battery."
        ),
        "trace_file":os.path.basename(trace_path)
    }
    with open(report_path,"w",encoding="utf-8") as f:
        json.dump(report,f,indent=2)
    print("\n=== MISSION REPORT ===")
    print(json.dumps(report,indent=2))
    print(f"\nTrace: {trace_path}\nReport: {report_path}")
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config",default="configs/sample_mission.json")
    parser.add_argument("--out",default=None)
    parser.add_argument("--max-steps",type=int,default=None)
    parser.add_argument("--quiet-map",action="store_true")
    args=parser.parse_args()
    with open(args.config,encoding="utf-8") as f:
        config=json.load(f)
    run(config,args.out,args.max_steps,render=not args.quiet_map)

if __name__=="__main__":
    main()
