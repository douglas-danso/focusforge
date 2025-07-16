# MCP orchestrator: initializes agents and routes calls

from agents import llm_decomposer, reward_engine, accountability

def run_pomodoro(task_desc, duration):
    blocks = llm_decomposer.decompose_task(task_desc, duration)
    return blocks

def reward_completion(points):
    reward_engine.add_currency(points)

def log_mood(feeling, note=""):
    accountability.log_mood(feeling, note)
