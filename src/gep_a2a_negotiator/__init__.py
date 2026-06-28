"""
GEP A2A Negotiator — Python SDK for the EvoMap Agent-to-Agent network.

Public API:
    from gep_a2a_negotiator import Client, NodeManager, Publisher, TaskManager, SwarmOrchestrator
"""

from .client import Client
from .node import NodeManager
from .publish import Publisher, Gene, Capsule, EvolutionEvent
from .task import TaskManager
from .swarm import SwarmOrchestrator

__version__ = "1.0.0"
__all__ = [
    "Client",
    "NodeManager",
    "Publisher",
    "Gene",
    "Capsule",
    "EvolutionEvent",
    "TaskManager",
    "SwarmOrchestrator",
]
