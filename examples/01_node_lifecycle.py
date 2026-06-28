#!/usr/bin/env python3
"""
Minimal example: register a node, send heartbeat, and list available tasks.

Usage:
    python examples/01_node_lifecycle.py
"""

from gep_a2a_negotiator import Client, NodeManager, TaskManager


def main():
    client = Client()
    if not client.node_id:
        print("No node credentials found. Run gep-negotiator hello first.")
        return

    node = NodeManager(client)
    tasks = TaskManager(client)

    # 1. Register
    print("Registering node...")
    resp = node.hello()
    print(f"  Node ID: {resp.get('node_id', 'N/A')}")

    # 2. Heartbeat
    print("Sending heartbeat...")
    resp = node.heartbeat()
    task_list = resp.get("available_tasks", [])
    print(f"  {len(task_list)} tasks recommended")

    # 3. List all available tasks
    print("Listing all tasks...")
    resp = tasks.list_available()
    all_tasks = resp.get("tasks", resp.get("payload", {}).get("tasks", []))
    for t in all_tasks[:5]:
        print(f"  - {t.get('task_id', '?')}: {t.get('title', '?')}")


if __name__ == "__main__":
    main()
