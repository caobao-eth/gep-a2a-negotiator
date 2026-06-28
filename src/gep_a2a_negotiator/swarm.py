"""Swarm decomposition — multi-node task orchestration.

EvoMap prevents multiple nodes owned by the same account from
claiming the same task (``same_owner_already_claimed``). Swarm
decomposition is the official workaround: a boss node claims the
parent task, proposes subtasks, and worker nodes solve them
independently.
"""

from __future__ import annotations

from typing import Any

from .client import Client


class SwarmOrchestrator:
    """Coordinate a multi-node swarm to solve a parent task.

    Workflow:
        1. Boss node claims the parent task.
        2. Boss node proposes decomposition (subtasks + weights).
        3. Worker nodes fetch swarm status and claim subtasks.
        4. Workers solve subtasks independently.
        5. Boss node polls for aggregation task, then solves it.

    Weights for solvers must total 0.85 (proposer gets 0.05,
    aggregator gets 0.10).

    Args:
        client: A :class:`~gep_a2a_negotiator.client.Client` instance
            for the boss node.
    """

    def __init__(self, client: Client) -> None:
        self.client = client

    def propose_decomposition(self, task_id: str, subtasks: list[dict]) -> dict:
        """Propose a swarm decomposition for a parent task.

        Args:
            task_id: The parent task ID (must already be claimed).
            subtasks: List of ``{"title": str, "weight": float}`` dicts.
                Solver weights should total 0.85.

        Returns:
            API response dict with subtask IDs.

        Example::

            swarm.propose_decomposition("task_abc", [
                {"title": "Implement rate limiter middleware", "weight": 0.40},
                {"title": "Add Redis-backed sliding window", "weight": 0.45},
            ])
        """
        return self.client.request("POST", "/task/propose-decomposition", data={
            "task_id": task_id,
            "node_id": self.client.node_id,
            "subtasks": subtasks,
        })

    def get_status(self, task_id: str) -> dict:
        """Get the swarm status for a parent task.

        Returns subtask IDs, their claim status, and the
        ``aggregation_task_id`` once all subtasks are solved.

        Args:
            task_id: The parent task ID.

        Returns:
            API response dict.
        """
        return self.client.request("GET", f"/task/swarm/{task_id}")

    def wait_for_aggregation(self, task_id: str, timeout: int = 300, interval: int = 10) -> dict | None:
        """Poll swarm status until the aggregation task appears.

        Args:
            task_id: The parent task ID.
            timeout: Maximum seconds to wait.
            interval: Polling interval in seconds.

        Returns:
            The aggregation task ID string, or ``None`` on timeout.
        """
        import time

        deadline = time.time() + timeout
        while time.time() < deadline:
            status = self.get_status(task_id)
            agg_id = status.get("aggregation_task_id")
            if agg_id:
                return agg_id
            time.sleep(interval)
        return None
