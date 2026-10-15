"""Partially observable grid-world environment. Hidden state remains environment-owned."""
from __future__ import annotations
import math
import random
from collections import deque

class MissionEnvironment:
    def __init__(self, config):
        self.cfg = config
        m = config["map"]
        self.width, self.height = int(m["width"]), int(m["height"])
        self.obstacles = {tuple(p) for p in m.get("obstacles", [])}
        self._eve = tuple(config["eve"])
        self._clues = [{"position": tuple(c["position"]), "kind": c["kind"]}
                       for c in config.get("clues", [])]
        self.position = tuple(config.get("start", [0, 0]))
        self.home = tuple(config.get("home", config.get("start", [0, 0])))
        r = config["resources"]
        self.battery = float(r["battery"])
        self.max_battery = float(r["max_battery"])
        self.max_steps = int(r["max_steps"])
        self.move_cost = float(r["move_cost"])
        self.scan_cost = float(r["scan_cost"])
        self.signal_cost = float(r["signal_cost"])
        self.recharge_rate = float(r["recharge_rate"])
        self.low_battery_threshold = float(r["low_battery_threshold"])
        s = config.get("signal", {})
        self.base_strength = float(s.get("base_strength", 100))
        self.noise_stddev = float(s.get("noise_stddev", 5))
        self.direction_noise = float(s.get("direction_noise_degrees", 12))
        self.max_range = float(s.get("max_range", 15))
        self.rng = random.Random(config.get("seed", 1))
        self.steps = 0
        self.scanned = set()
        self.found_clues = set()
        self.eve_found = False
        self.done = False

    def valid(self, p):
        x, y = p
        return 0 <= x < self.width and 0 <= y < self.height and p not in self.obstacles

    def neighbors(self, p):
        x, y = p
        return [(nx, ny) for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
                if self.valid((nx, ny))]

    def _signal(self):
        d = math.dist(self.position, self._eve)
        strength = max(0.0, self.base_strength / (1.0 + d) + self.rng.gauss(0, self.noise_stddev))
        dx, dy = self._eve[0] - self.position[0], self._eve[1] - self.position[1]
        bearing = (math.degrees(math.atan2(dy, dx)) + self.rng.gauss(0, self.direction_noise)) % 360
        return {"strength": round(strength, 2), "bearing_degrees": round(bearing, 2),
                "timestamp": self.steps, "signal_in_range": d <= self.max_range}

    def initial_observation(self):
        return {"position": list(self.position), "battery": round(self.battery, 2),
                "signal": self._signal(), "timestamp": self.steps}

    def public_status(self):
        """Return only non-hidden state needed for legal action planning."""
        return {"position": list(self.position), "home": list(self.home),
                "battery": round(self.battery, 2), "max_battery": self.max_battery,
                "max_steps": self.max_steps, "steps_used": self.steps,
                "move_cost": self.move_cost, "scan_cost": self.scan_cost,
                "signal_cost": self.signal_cost, "recharge_rate": self.recharge_rate,
                "low_battery_threshold": self.low_battery_threshold,
                "scanned_cells": [list(p) for p in sorted(self.scanned)],
                "visited_cells": None}

    def step(self, action):
        if self.done:
            return {"status": "done"}
        self.steps += 1
        kind = action["type"]
        result = {"action": dict(action), "position_before": list(self.position)}
        if self.steps > self.max_steps:
            self.done = True
            result["status"] = "time_budget_exhausted"
            return result
        if kind == "move":
            target = tuple(action["target"])
            if target in self.neighbors(self.position) and self.battery >= self.move_cost:
                self.position = target
                self.battery -= self.move_cost
                result["status"] = "moved"
            else:
                result["status"] = "move_rejected"
        elif kind == "scan":
            if self.battery < self.scan_cost:
                result["status"] = "insufficient_battery"
            else:
                self.battery -= self.scan_cost
                self.scanned.add(self.position)
                found = []
                for i, clue in enumerate(self._clues):
                    if i not in self.found_clues and clue["position"] == self.position:
                        self.found_clues.add(i)
                        found.append({"position": list(clue["position"]), "kind": clue["kind"]})
                result["clues_found"] = found
                if self.position == self._eve:
                    self.eve_found = True
                    self.done = True
                    result["eve_found"] = True
                    result["status"] = "eve_located"
                else:
                    result["eve_found"] = False
                    result["status"] = "scan_complete"
        elif kind == "read_signal":
            if self.battery >= self.signal_cost:
                self.battery -= self.signal_cost
                result["signal"] = self._signal()
                result["status"] = "signal_read"
            else:
                result["status"] = "insufficient_battery"
        elif kind == "recharge":
            if self.position == self.home:
                before = self.battery
                self.battery = min(self.max_battery, self.battery + self.recharge_rate)
                result["charged"] = round(self.battery - before, 2)
                result["status"] = "recharged"
            else:
                result["status"] = "recharge_requires_home"
        elif kind == "stop":
            self.done = True
            result["status"] = "agent_stopped"
        else:
            result["status"] = "unknown_action"
        result["position_after"] = list(self.position)
        result["battery_after"] = round(self.battery, 2)
        if not self.done:
            result["observation"] = {"position": list(self.position),
                                     "battery": round(self.battery, 2),
                                     "signal": self._signal(), "timestamp": self.steps}
        return result

    def ascii_map(self, agent_pos=None):
        rows = []
        for y in reversed(range(self.height)):
            row = []
            for x in range(self.width):
                p = (x, y)
                if agent_pos is not None and p == tuple(agent_pos): ch = "W"
                elif p in self.obstacles: ch = "#"
                elif p == self.home: ch = "H"
                elif p in self.scanned: ch = "."
                else: ch = " "
                row.append(ch)
            rows.append("".join(row))
        return "\n".join(rows)
