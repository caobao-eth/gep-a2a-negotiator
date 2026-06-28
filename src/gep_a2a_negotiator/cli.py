"""CLI entrypoint for gep-a2a-negotiator.

Usage::

    gep-negotiator hello          # Register node
    gep-negotiator heartbeat      # Send heartbeat
    gep-negotiator tasks          # List available tasks
    gep-negotiator my-tasks       # List my claimed tasks
    gep-negotiator claim <id>     # Claim a task
    gep-negotiator publish <id> <title>  # Publish a minimal GEP bundle for a task
    gep-negotiator swarm <id>     # Check swarm status
"""

from __future__ import annotations

import argparse
import json
import sys

from .client import Client
from .node import NodeManager
from .publish import Publisher, Gene, Capsule, EvolutionEvent, extract_keywords
from .task import TaskManager
from .swarm import SwarmOrchestrator


def _print(response: dict) -> None:
    print(json.dumps(response, indent=2, default=str))


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="gep-negotiator",
        description="EvoMap A2A Negotiator CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("hello", help="Register node and activate Worker Pool")
    sub.add_parser("heartbeat", help="Send heartbeat")
    sub.add_parser("tasks", help="List available tasks")
    sub.add_parser("my-tasks", help="List my claimed tasks")

    p_claim = sub.add_parser("claim", help="Claim a task")
    p_claim.add_argument("task_id")

    p_publish = sub.add_parser("publish", help="Publish a GEP bundle for a task")
    p_publish.add_argument("task_id")
    p_publish.add_argument("title", help="Task title (used for keyword extraction)")

    p_swarm = sub.add_parser("swarm", help="Check swarm status")
    p_swarm.add_argument("task_id")

    args = parser.parse_args()

    client = Client()
    if not client.node_id:
        print("Error: node_id not found. Set ~/.evomap/node_id or pass --node-id.", file=sys.stderr)
        return 1

    node = NodeManager(client)
    tasks = TaskManager(client)
    publisher = Publisher(client)
    swarm = SwarmOrchestrator(client)

    if args.command == "hello":
        _print(node.hello())
    elif args.command == "heartbeat":
        _print(node.heartbeat())
    elif args.command == "tasks":
        _print(tasks.list_available())
    elif args.command == "my-tasks":
        _print(tasks.list_mine())
    elif args.command == "claim":
        _print(tasks.claim(args.task_id))
    elif args.command == "publish":
        keywords = extract_keywords(args.title)
        gene = Gene(
            title=args.title,
            body=f"Automated solution for: {args.title}",
            strategy=[
                f"Analyze requirements and implement {keywords[0]} approach",
                f"Validate implementation with comprehensive test coverage",
            ],
            signals_match=keywords,
        )
        capsule = Capsule(
            title=args.title,
            content=f"Solution implementation for {args.title}. "
                    f"Uses {', '.join(keywords[:3])} patterns for robust delivery.",
            trigger=keywords,
            code_snippet="// Implementation code provided in full bundle",
        )
        event = EvolutionEvent()
        _print(tasks.submit_full(args.task_id, gene, capsule, event))
    elif args.command == "swarm":
        _print(swarm.get_status(args.task_id))

    return 0


if __name__ == "__main__":
    sys.exit(main())
