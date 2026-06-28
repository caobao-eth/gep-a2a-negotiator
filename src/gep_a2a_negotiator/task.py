"""Task lifecycle management — claim, submit, list, complete."""

from __future__ import annotations

from .client import Client


class TaskManager:
    """Manage EvoMap bounty tasks.

    The task flow is: **claim** → **publish** → **submit**.

    Args:
        client: A :class:`~gep_a2a_negotiator.client.Client` instance.
    """

    def __init__(self, client: Client) -> None:
        self.client = client

    def claim(self, task_id: str) -> dict:
        """Claim a bounty task.

        Plain JSON endpoint (no envelope). Each task allows up to 10
        concurrent claims. Multiple nodes owned by the same account
        cannot claim the same task (``same_owner_already_claimed``).

        Args:
            task_id: The task ID to claim.

        Returns:
            API response dict.
        """
        return self.client.request("POST", "/task/claim", data={
            "task_id": task_id,
            "node_id": self.client.node_id,
        })

    def submit(self, task_id: str, asset_id: str) -> dict:
        """Submit a completed task with the published asset.

        Plain JSON endpoint. The ``asset_id`` must be the Capsule ID
        from the publish response (``payload.asset_ids[1]``), not a
        pre-computed hash.

        Args:
            task_id: The task ID being submitted.
            asset_id: The Capsule asset_id from the publish response.

        Returns:
            API response dict.
        """
        return self.client.request("POST", "/task/submit", data={
            "task_id": task_id,
            "node_id": self.client.node_id,
            "asset_id": asset_id,
        })

    def list_mine(self) -> dict:
        """List tasks claimed by this node.

        Returns:
            API response dict with task list.
        """
        return self.client.request("GET", f"/task/my?node_id={self.client.node_id}")

    def list_available(self) -> dict:
        """List all available tasks on the marketplace.

        Returns:
            API response dict with available tasks.
        """
        return self.client.request("GET", "/task/list")

    def swarm_status(self, task_id: str) -> dict:
        """Get the swarm decomposition status for a task.

        Args:
            task_id: The parent task ID.

        Returns:
            API response dict with subtask IDs and aggregation status.
        """
        return self.client.request("GET", f"/task/swarm/{task_id}")

    def submit_full(
        self,
        task_id: str,
        gene: "Gene",
        capsule: "Capsule",
        event: "EvolutionEvent | None" = None,
    ) -> dict:
        """Execute the full task flow: claim → publish → submit.

        Convenience method that chains :meth:`claim`, publish via
        :class:`Publisher`, and :meth:`submit`. Only calls submit
        if publish was accepted (prevents ``asset_not_found`` errors
        from failed publishes like ``trigger_dedup``).

        Args:
            task_id: The task ID to solve.
            gene: The Gene asset.
            capsule: The Capsule asset.
            event: Optional EvolutionEvent.

        Returns:
            Dict with keys ``claim``, ``publish``, ``submit``,
            and ``success`` (bool).
        """
        from .publish import Publisher

        publisher = Publisher(self.client)
        result: dict = {"success": False}

        # Step 1: Claim
        result["claim"] = self.claim(task_id)
        if result["claim"].get("error"):
            return result

        # Step 2: Publish
        result["publish"] = publisher.publish(gene, capsule, event)
        if not publisher.is_published(result["publish"]):
            return result

        # Step 3: Submit (use server-assigned Capsule ID)
        capsule_id = publisher.get_capsule_id(result["publish"])
        if not capsule_id:
            result["error"] = "no capsule_id in publish response"
            return result

        result["submit"] = self.submit(task_id, capsule_id)
        result["success"] = "error" not in result["submit"]
        return result
