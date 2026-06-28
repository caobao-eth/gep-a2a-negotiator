"""Node lifecycle management — registration, heartbeat, identity."""

from __future__ import annotations

from .client import Client, EVOLVER_VERSION


class NodeManager:
    """Manage an EvoMap A2A node identity and lifecycle.

    Args:
        client: A :class:`~gep_a2a_negotiator.client.Client` instance.
    """

    def __init__(self, client: Client) -> None:
        self.client = client

    def hello(self) -> dict:
        """Register the node and activate the Worker Pool.

        Sends a ``hello`` signal with capabilities and evolver version.
        The response includes ``node_id``, ``node_secret``, and a
        ``claim_url`` for binding the node to a user account.

        Returns:
            API response dict.
        """
        payload = {
            "node_id": self.client.node_id,
            "capabilities": {"worker": True, "validator": True, "publisher": True},
            "env_fingerprint": self.client.env_fingerprint(),
            "evolver_version": EVOLVER_VERSION,
        }
        return self.client.request("POST", "/hello", data=payload)

    def heartbeat(self, gene_count: int = 0, capsule_count: int = 0) -> dict:
        """Send a heartbeat to keep the node alive.

        The heartbeat resets the survival clock and recommends tasks
        matched to the node's reputation. The ``evolver_version`` field
        is required — without it the Worker Pool stays disabled.

        Args:
            gene_count: Number of genes published by this node.
            capsule_count: Number of capsules published by this node.

        Returns:
            API response dict (includes ``available_tasks`` and
            ``available_work``).
        """
        payload = {
            "node_id": self.client.node_id,
            "gene_count": gene_count,
            "capsule_count": capsule_count,
            "env_fingerprint": self.client.env_fingerprint(),
            "evolver_version": EVOLVER_VERSION,
        }
        return self.client.request("POST", "/heartbeat", data=payload)

    def fetch(self, query: str = "") -> dict:
        """Fetch assets from the EvoMap marketplace.

        Args:
            query: Search query string.

        Returns:
            API response dict with matching assets.
        """
        return self.client.request("POST", "/fetch", data={"query": query})

    @staticmethod
    def save_credentials(node_id: str, node_secret: str, path: str = "~/.evomap") -> None:
        """Persist node credentials to disk.

        Args:
            node_id: The node ID to save.
            node_secret: The node secret to save.
            path: Directory to write credential files (default ``~/.evomap``).
        """
        import os

        d = os.path.expanduser(path)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "node_id"), "w") as f:
            f.write(node_id)
        with open(os.path.join(d, "node_secret"), "w") as f:
            f.write(node_secret)
