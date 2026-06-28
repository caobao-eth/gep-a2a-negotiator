#!/usr/bin/env python3
"""
Example: swarm decomposition for multi-node task solving.

Usage:
    python examples/03_swarm_decomposition.py <task_id>
"""

import sys
from gep_a2a_negotiator import Client, SwarmOrchestrator


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <task_id>")
        sys.exit(1)

    task_id = sys.argv[1]
    client = Client()
    swarm = SwarmOrchestrator(client)

    # 1. Propose decomposition (boss node must have claimed the task first)
    print(f"Proposing decomposition for {task_id}...")
    resp = swarm.propose_decomposition(task_id, [
        {"title": "Implement core logic", "weight": 0.40},
        {"title": "Add integration tests", "weight": 0.45},
    ])
    print(f"  Response: {resp}")

    # 2. Poll for aggregation task
    print("Waiting for subtasks to be solved...")
    agg_id = swarm.wait_for_aggregation(task_id, timeout=600, interval=15)
    if agg_id:
        print(f"  Aggregation task ready: {agg_id}")
        print("  Boss node should now claim and solve the aggregation task.")
    else:
        print("  Timeout waiting for aggregation.")


if __name__ == "__main__":
    main()
