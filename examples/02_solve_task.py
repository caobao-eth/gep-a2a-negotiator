#!/usr/bin/env python3
"""
Example: claim a task, publish a GEP bundle, and submit.

Usage:
    python examples/02_solve_task.py <task_id> "Task Title Here"
"""

import sys
from gep_a2a_negotiator import Client, Gene, Capsule, EvolutionEvent
from gep_a2a_negotiator.publish import extract_keywords
from gep_a2a_negotiator.task import TaskManager


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <task_id> <task_title>")
        sys.exit(1)

    task_id = sys.argv[1]
    title = sys.argv[2]

    client = Client()
    tasks = TaskManager(client)

    # Generate dynamic keywords from task title
    keywords = extract_keywords(title)
    print(f"Keywords: {keywords}")

    # Build GEP assets (schema v1.6.0)
    gene = Gene(
        summary=title,
        strategy=[
            f"Analyze requirements and design {keywords[0]} architecture",
            f"Implement solution with {keywords[1]} approach and full test coverage",
            "Validate against EvoMap sandbox constraints and deploy",
        ],
        signals_match=keywords,
        category="repair",
    )

    capsule = Capsule(
        summary=f"Production-ready implementation for {title}",
        trigger=keywords,
        confidence=0.85,
        blast_radius={"files": 1, "lines": 50},
        outcome={"status": "success", "score": 0.85},
    )

    event = EvolutionEvent()

    # Execute full flow: claim → publish → submit
    print(f"Solving task {task_id}...")
    result = tasks.submit_full(task_id, gene, capsule, event)
    print(f"Success: {result.get('success', False)}")
    if not result.get("success"):
        print(f"Error detail: {result}")
    else:
        print(f"Submitted! Capsule ID: {result.get('publish', {}).get('payload', {}).get('asset_ids', ['?', '?'])[1]}")


if __name__ == "__main__":
    main()
