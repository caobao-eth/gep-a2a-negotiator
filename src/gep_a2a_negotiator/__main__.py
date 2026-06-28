"""GEP A2A Negotiator CLI.

Usage::

    gep-negotiator hello          # Register node
    gep-negotiator heartbeat      # Send heartbeat
    gep-negotiator tasks          # List available tasks
    gep-negotiator my-tasks       # List my claimed tasks
    gep-negotiator claim <id>     # Claim a task
    gep-negotiator publish <id> <title>  # Publish a minimal GEP bundle
    gep-negotiator swarm <id>     # Check swarm status
"""

from .cli import main

__all__ = ["main"]
