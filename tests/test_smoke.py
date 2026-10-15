import json
import os
import unittest
from environment import MissionEnvironment
from agent import WallEAgent, entropy

class SmokeTests(unittest.TestCase):
    def setUp(self):
        config_path=os.path.join(os.path.dirname(__file__),"..","configs","sample_mission.json")
        with open(config_path,encoding="utf-8") as f:
            self.config=json.load(f)

    def test_environment_observation(self):
        env=MissionEnvironment(self.config)
        obs=env.initial_observation()
        self.assertIn("strength",obs["signal"])
        self.assertIn("bearing_degrees",obs["signal"])

    def test_belief_normalized(self):
        env=MissionEnvironment(self.config)
        agent=WallEAgent(env.width,env.height,self.config["map"]["obstacles"],
                         self.config["start"],self.config["resources"],home=self.config["home"])
        agent.update_belief(env.initial_observation()["signal"])
        self.assertAlmostEqual(sum(agent.belief.values()),1.0,places=6)

    def test_hidden_state_not_in_public_status(self):
        env=MissionEnvironment(self.config)
        public=env.public_status()
        self.assertNotIn("eve",public)
        self.assertNotIn("clues",public)

    def test_belief_entropy_nonnegative(self):
        env=MissionEnvironment(self.config)
        agent=WallEAgent(env.width,env.height,self.config["map"]["obstacles"],
                         self.config["start"],self.config["resources"])
        self.assertGreaterEqual(entropy(agent.belief.values()),0)

    def test_scan_returns_status(self):
        env=MissionEnvironment(self.config)
        result=env.step({"type":"scan"})
        self.assertIn("status",result)

if __name__=="__main__":
    unittest.main()
