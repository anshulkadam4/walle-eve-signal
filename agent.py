"""Belief-based agent using heuristic expected information gain and resource-aware planning."""
from __future__ import annotations
import math
from collections import deque

def manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def entropy(probabilities):
    return -sum(p * math.log(p, 2) for p in probabilities if p > 1e-15)

class WallEAgent:
    def __init__(self, width, height, obstacles, start, resource_config, home=None):
        self.width, self.height = width, height
        self.obstacles = {tuple(p) for p in obstacles}
        self.position = tuple(start)
        self.home = tuple(home if home is not None else start)
        self.resource_config = resource_config
        cells = [(x,y) for x in range(width) for y in range(height)
                 if (x,y) not in self.obstacles]
        self.belief = {p: 1.0/len(cells) for p in cells}
        self.visited = {self.position}
        self.scanned = set()
        self.known_clues = []
        self.evidence = []
        self.eve_found = False
        self.eve_position = None
        self.steps = 0
        self.last_signal = None

    def neighbors(self, p):
        x,y=p
        return [(nx,ny) for nx,ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
                if 0 <= nx < self.width and 0 <= ny < self.height and (nx,ny) not in self.obstacles]

    def shortest_path(self, start, goal):
        start, goal = tuple(start), tuple(goal)
        q=deque([start]); prev={start:None}
        while q:
            p=q.popleft()
            if p == goal: break
            for n in self.neighbors(p):
                if n not in prev: prev[n]=p; q.append(n)
        if goal not in prev: return []
        path=[]; p=goal
        while p is not None: path.append(p); p=prev[p]
        return list(reversed(path))

    def _normalize(self, weights):
        total=sum(weights.values())
        if total <= 1e-300:
            n=len(self.belief); self.belief={p:1/n for p in self.belief}
        else:
            self.belief={p:w/total for p,w in weights.items()}

    def update_belief(self, signal):
        if not signal: return
        strength=signal.get("strength")
        bearing=signal.get("bearing_degrees")
        if strength is None: return
        self.last_signal=dict(signal)
        weights={}
        sigma_strength=max(8.0, float(self.resource_config.get("signal_noise_stddev", 5.0))*2.5)
        sigma_bearing=max(25.0, float(self.resource_config.get("direction_noise_degrees", 12.0))*2.5)
        for p,prior in self.belief.items():
            dx,dy=p[0]-self.position[0],p[1]-self.position[1]
            d=max(1.0, math.hypot(dx,dy))
            expected=100.0/(1.0+d)
            ls=math.exp(-0.5*((strength-expected)/sigma_strength)**2)
            if bearing is None:
                lb=1.0
            else:
                expected_bearing=math.degrees(math.atan2(dy,dx))
                delta=abs((bearing-expected_bearing+180)%360-180)
                lb=math.exp(-0.5*(delta/sigma_bearing)**2)
            weights[p]=max(1e-300,prior*ls*lb)
        self._normalize(weights)

    def update_clue(self, clue):
        normalized={"position":tuple(clue["position"]),"kind":clue["kind"]}
        self.known_clues.append(normalized)
        cp=normalized["position"]
        weights={}
        for p,prior in self.belief.items():
            d=math.dist(p,cp)
            weights[p]=prior*(0.25+0.75*math.exp(-d/3.5))
        self._normalize(weights)
        self.evidence.append({"type":"clue","position":list(cp),"kind":normalized["kind"]})

    def top_beliefs(self,n=5):
        return [{"position":list(p),"probability":round(v,5)}
                for p,v in sorted(self.belief.items(),key=lambda kv:kv[1],reverse=True)[:n]]

    def _expected_information_gain(self, candidate):
        """Heuristic distinguishability score from predicted signals at candidate."""
        prior_entropy=entropy(self.belief.values())
        # Expected observation is approximated by evaluating likely noisy signal outcomes
        # around each candidate's weighted expected strength and bearing.
        hypotheses=sorted(self.belief.items(),key=lambda kv:kv[1],reverse=True)[:min(12,len(self.belief))]
        if not hypotheses: return 0.0
        # Candidate observation can separate hypotheses whose predicted signals differ.
        predictions=[]
        for p,prob in hypotheses:
            dx,dy=p[0]-candidate[0],p[1]-candidate[1]
            d=max(1.0,math.hypot(dx,dy))
            strength=100.0/(1.0+d)
            bearing=math.degrees(math.atan2(dy,dx))
            predictions.append((prob,strength,bearing))
        weighted_strength=sum(w*s for w,s,b in predictions)/sum(w for w,s,b in predictions)
        strength_var=sum(w*(s-weighted_strength)**2 for w,s,b in predictions)/sum(w for w,s,b in predictions)
        # Circular bearing dispersion, downweighted when candidate is far from hypotheses.
        bearing_vec_x=sum(w*math.cos(math.radians(b)) for w,s,b in predictions)
        bearing_vec_y=sum(w*math.sin(math.radians(b)) for w,s,b in predictions)
        total_w=sum(w for w,s,b in predictions)
        concentration=math.hypot(bearing_vec_x,bearing_vec_y)/max(total_w,1e-12)
        bearing_spread=1.0-concentration
        strength_term=min(1.0, strength_var/180.0)
        score=0.55*strength_term+0.45*bearing_spread
        # Prefer points that provide a useful new measurement rather than repeat a cell.
        if candidate in self.visited: score *= 0.65
        return max(0.0,min(1.0,score))

    def choose_action(self, public):
        pos=tuple(public["position"])
        self.position=pos
        battery=float(public["battery"])
        move_cost=float(public["move_cost"])
        scan_cost=float(public["scan_cost"])
        signal_cost=float(public["signal_cost"])
        max_battery=float(public["max_battery"])
        low_threshold=float(public["low_battery_threshold"])
        self.scanned={tuple(p) for p in public.get("scanned_cells",[])}
        self.visited.add(pos)
        path_home=self.shortest_path(pos,self.home)
        return_cost=max(0,len(path_home)-1)*move_cost
        # Safety reserve includes the return trip and one small contingency margin.
        reserve=return_cost + move_cost + scan_cost
        if pos == self.home and battery < max_battery*0.8:
            return {"type":"recharge","reason":"restore battery at home before exploration",
                    "score":None,"estimated_return_cost":0.0}
        if battery <= max(low_threshold, reserve) + move_cost:
            if pos != self.home and len(path_home)>1:
                return {"type":"move","target":list(path_home[1]),
                        "reason":"return-to-home reserve would otherwise be breached",
                        "score":None,"estimated_return_cost":round(return_cost,2)}
            if pos == self.home and battery < max_battery:
                return {"type":"recharge","reason":"battery reserve requires recharge",
                        "score":None,"estimated_return_cost":0.0}

        # Scanning is the only way to confirm EVE or discover a clue at the current cell.
        # Prefer scanning each newly visited cell when the return reserve remains intact.
        if pos not in self.scanned and battery >= scan_cost + return_cost + move_cost:
            pprob=self.belief.get(pos,0.0)
            ig=self._expected_information_gain(pos)
            score=2.2*pprob + 0.25*ig - 0.015*scan_cost
            return {"type":"scan","reason":"scan newly visited cell while preserving estimated return reserve",
                    "score":round(score,4),"information_gain_estimate":round(ig,4),
                    "posterior_at_cell":round(pprob,5),
                    "estimated_return_cost":round(return_cost,2)}

        # Score reachable unscanned candidate cells.
        candidates=[]
        for candidate,prob in self.belief.items():
            if candidate in self.scanned: continue
            path=self.shortest_path(pos,candidate)
            if len(path)<2: continue
            travel=len(path)-1
            required=(travel*move_cost)+scan_cost+max(0,len(self.shortest_path(candidate,self.home))-1)*move_cost
            if battery < required + move_cost:
                continue
            ig=self._expected_information_gain(candidate)
            # Probability rewards plausible cells; IG rewards useful observation locations.
            # Distance penalty and return cost discourage wasteful or unsafe detours.
            candidate_home_path=self.shortest_path(candidate,self.home)
            candidate_return=max(0,len(candidate_home_path)-1)*move_cost
            score=(2.0*prob)+(1.15*ig)-(0.055*travel)-(0.025*candidate_return)
            candidates.append((score,candidate,path,ig,travel,candidate_return))
        if candidates:
            score,target,path,ig,travel,ret=max(candidates,key=lambda x:x[0])
            return {"type":"move","target":list(path[1]),
                    "reason":f"information-gain and posterior utility toward candidate {target}",
                    "target_candidate":list(target),"score":round(score,4),
                    "information_gain_estimate":round(ig,4),"planned_travel_steps":travel,
                    "estimated_return_cost":round(ret,2)}
        if pos != self.home and len(path_home)>1:
            return {"type":"move","target":list(path_home[1]),
                    "reason":"no safe candidate remains; return to recharge",
                    "score":None,"estimated_return_cost":round(return_cost,2)}
        if pos == self.home and battery < max_battery:
            return {"type":"recharge","reason":"no safe candidate remains; recharge at home",
                    "score":None,"estimated_return_cost":0.0}
        return {"type":"stop","reason":"no safe feasible action remains","score":None}

