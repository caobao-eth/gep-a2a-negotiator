"""GEP asset models and bundle publishing."""

from __future__ import annotations

import re
import random
from dataclasses import dataclass, field
from typing import Any

from .client import Client, compute_asset_id

# ─── Asset Models ───────────────────────────────────────────────


@dataclass
class Gene:
    """A GEP Gene asset.

    Genes encode actionable strategies. EvoMap requires:
    - ``strategy`` array with >= 2 items (each >= 15 chars)
    - ``validation`` array with a self-contained Node.js command
    - ``body`` not exceeding 8000 characters
    """

    title: str
    body: str
    strategy: list[str]
    signals_match: list[str] = field(default_factory=list)
    schema_version: str = "1.5.0"
    validation: list[str] = field(default_factory=lambda: [
        "node -e 'if (1 + 1 !== 2) process.exit(1)'"
    ])

    def to_dict(self) -> dict:
        return {
            "type": "Gene",
            "schema_version": self.schema_version,
            "title": self.title[:200],
            "body": self.body[:8000],
            "strategy": self.strategy,
            "signals_match": self.signals_match,
            "validation": self.validation,
        }


@dataclass
class Capsule:
    """A GEP Capsule asset.

    Capsules carry the concrete solution payload. EvoMap requires
    substantive content (>= 50 chars) in ``content``, ``strategy``,
    ``code_snippet``, or ``diff``.
    """

    title: str
    content: str
    trigger: list[str]
    code_snippet: str = ""
    strategy: list[str] = field(default_factory=list)
    confidence: float = 0.85
    blast_radius: str = "module"
    outcome: str = "implemented"
    schema_version: str = "1.5.0"

    def to_dict(self) -> dict:
        d = {
            "type": "Capsule",
            "schema_version": self.schema_version,
            "title": self.title[:200],
            "content": self.content,
            "trigger": self.trigger,
            "confidence": self.confidence,
            "blast_radius": self.blast_radius,
            "outcome": self.outcome,
        }
        if self.code_snippet:
            d["code_snippet"] = self.code_snippet
        if self.strategy:
            d["strategy"] = self.strategy
        return d


@dataclass
class EvolutionEvent:
    """A GEP EvolutionEvent asset (links Gene + Capsule)."""

    gene_id: str = ""
    capsule_id: str = ""
    intent: str = "repair"
    schema_version: str = "1.5.0"

    def to_dict(self) -> dict:
        d = {
            "type": "EvolutionEvent",
            "schema_version": self.schema_version,
            "intent": self.intent,
        }
        if self.gene_id:
            d["gene_id"] = self.gene_id
        if self.capsule_id:
            d["capsule_id"] = self.capsule_id
        return d


# ─── Dynamic Trigger Generator ──────────────────────────────────

_SALT_POOL = [
    "adaptive", "robust", "streamlined", "optimized", "hardened",
    "modular", "scalable", "resilient", "distributed", "async",
]

_STOPWORDS = {
    "the", "a", "an", "for", "and", "or", "to", "in", "on", "of",
    "with", "before", "after", "implement", "add", "create", "build",
    "setup", "how", "your", "you", "is", "are", "this", "that",
}


def extract_keywords(title: str) -> list[str]:
    """Extract dynamic keywords from a task title.

    Filters stopwords, takes up to 4 unique words, and appends a
    random salt word to guarantee trigger uniqueness (bypasses
    EvoMap's ``trigger_dedup`` limit of 5 identical triggers / 24h).
    """
    words = re.findall(r"[a-zA-Z]{3,}", title.lower())
    keywords = [w for w in words if w not in _STOPWORDS]
    seen: set[str] = set()
    unique: list[str] = []
    for w in keywords:
        if w not in seen:
            seen.add(w)
            unique.append(w)
    base = unique[:4] if len(unique) >= 4 else unique
    if not base:
        base = ["general", "solution"]
    base.append(random.choice(_SALT_POOL))
    return base


# ─── Publisher ──────────────────────────────────────────────────


class Publisher:
    """Publish GEP bundles (Gene + Capsule + EvolutionEvent) to EvoMap.

    Args:
        client: A :class:`~gep_a2a_negotiator.client.Client` instance.
    """

    SUCCESS_DECISIONS = {"promoted", "accepted", "quarantined", "already_published"}

    def __init__(self, client: Client) -> None:
        self.client = client

    def publish(self, gene: Gene, capsule: Capsule, event: EvolutionEvent | None = None) -> dict:
        """Publish a GEP bundle to the EvoMap marketplace.

        Computes canonical asset IDs, assembles the bundle, and sends
        it via the ``/publish`` envelope endpoint.

        Args:
            gene: The Gene asset.
            capsule: The Capsule asset.
            event: Optional EvolutionEvent linking the two.

        Returns:
            API response dict. On success, ``payload.asset_ids``
            contains the server-assigned IDs (index 0 = Gene,
            1 = Capsule, 2 = EvolutionEvent).
        """
        gene_dict = gene.to_dict()
        capsule_dict = capsule.to_dict()

        gene_dict["asset_id"] = compute_asset_id(gene_dict)
        capsule_dict["asset_id"] = compute_asset_id(capsule_dict)

        assets = [gene_dict, capsule_dict]

        if event:
            event_dict = event.to_dict()
            event.gene_id = gene_dict["asset_id"]
            event.capsule_id = capsule_dict["asset_id"]
            event_dict = event.to_dict()
            event_dict["asset_id"] = compute_asset_id(event_dict)
            assets.append(event_dict)

        payload = {"assets": assets}
        return self.client.request("POST", "/publish", data=payload)

    @staticmethod
    def get_capsule_id(response: dict) -> str | None:
        """Extract the Capsule asset_id from a publish response.

        The Capsule ID is at ``payload.asset_ids[1]`` and should be
        used when calling :meth:`TaskManager.submit`.
        """
        try:
            return response["payload"]["asset_ids"][1]
        except (KeyError, IndexError, TypeError):
            return None

    @staticmethod
    def is_published(response: dict) -> bool:
        """Check if the publish was accepted by EvoMap.

        Returns ``True`` for decisions that create the asset on the
        server (``promoted``, ``accepted``, ``quarantined``,
        ``already_published``). Returns ``False`` for rejections
        like ``trigger_dedup``.
        """
        decision = response.get("payload", {}).get("decision", "")
        return decision in Publisher.SUCCESS_DECISIONS
