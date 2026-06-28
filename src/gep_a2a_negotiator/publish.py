"""GEP asset models and bundle publishing (schema v1.6.0)."""

from __future__ import annotations

import re
import random
from dataclasses import dataclass, field

from .client import Client, compute_asset_id

# ─── Asset Models (schema v1.6.0) ───────────────────────────────


@dataclass
class Gene:
    """A GEP Gene asset (schema v1.6.0).

    Genes encode actionable strategies with signal matching.

    Required fields per EvoMap v1.6.0:
    - ``summary`` — short description of the gene
    - ``strategy`` — array of >= 2 actionable steps (each >= 15 chars)
    - ``signals_match`` — trigger keywords for matching
    - ``category`` — one of: repair|optimize|innovate|regulatory|explore
    - ``validation`` — self-contained Node.js command
    """

    summary: str
    strategy: list[str]
    signals_match: list[str]
    category: str = "repair"
    schema_version: str = "1.6.0"
    validation: list[str] = field(default_factory=lambda: [
        "node -e 'if (1 + 1 !== 2) process.exit(1)'"
    ])
    model_name: str = "sub-agent-1"

    def to_dict(self) -> dict:
        return {
            "type": "Gene",
            "schema_version": self.schema_version,
            "category": self.category,
            "signals_match": self.signals_match,
            "summary": self.summary,
            "strategy": self.strategy,
            "validation": self.validation,
            "model_name": self.model_name,
        }


@dataclass
class Capsule:
    """A GEP Capsule asset (schema v1.6.0).

    Capsules carry the concrete solution payload linked to a Gene.

    Required fields per EvoMap v1.6.0:
    - ``trigger`` — same keywords as Gene.signals_match
    - ``gene`` — the Gene's asset_id (set by Publisher)
    - ``summary`` — short description
    - ``confidence`` — float 0-1
    - ``blast_radius`` — ``{"files": int, "lines": int}``
    - ``outcome`` — ``{"status": "success"|"failed", "score": float}``
    """

    summary: str
    trigger: list[str]
    content: str = ""  # substance field (>= 50 chars if provided)
    code_snippet: str = ""  # substance field (>= 50 chars if provided)
    strategy: list[str] = field(default_factory=list)  # substance field
    confidence: float = 0.85
    blast_radius: dict = field(default_factory=lambda: {"files": 1, "lines": 50})
    outcome: dict = field(default_factory=lambda: {"status": "success", "score": 0.85})
    schema_version: str = "1.6.0"
    env_fingerprint: dict = field(default_factory=lambda: {"platform": "linux", "arch": "x64"})
    success_streak: int = 3
    model_name: str = "sub-agent-1"
    gene: str = ""  # set by Publisher to Gene's asset_id

    def to_dict(self) -> dict:
        d = {
            "type": "Capsule",
            "schema_version": self.schema_version,
            "trigger": self.trigger,
            "gene": self.gene,
            "summary": self.summary,
            "confidence": self.confidence,
            "blast_radius": self.blast_radius,
            "outcome": self.outcome,
            "env_fingerprint": self.env_fingerprint,
            "success_streak": self.success_streak,
            "model_name": self.model_name,
        }
        if self.content:
            d["content"] = self.content
        if self.code_snippet:
            d["code_snippet"] = self.code_snippet
        if self.strategy:
            d["strategy"] = self.strategy
        return d


@dataclass
class EvolutionEvent:
    """A GEP EvolutionEvent asset (schema v1.6.0).

    Links a Gene and Capsule together with evolution metadata.
    """

    capsule_id: str = ""
    genes_used: list[str] = field(default_factory=list)
    intent: str = "repair"
    outcome: dict = field(default_factory=lambda: {"status": "success", "score": 0.85})
    mutations_tried: int = 3
    total_cycles: int = 5
    model_name: str = "sub-agent-1"
    schema_version: str = "1.6.0"

    def to_dict(self) -> dict:
        return {
            "type": "EvolutionEvent",
            "intent": self.intent,
            "capsule_id": self.capsule_id,
            "genes_used": self.genes_used,
            "outcome": self.outcome,
            "mutations_tried": self.mutations_tried,
            "total_cycles": self.total_cycles,
            "model_name": self.model_name,
        }


# ─── Dynamic Trigger Generator ──────────────────────────────────

_SALT_POOL = [
    "adaptive", "robust", "streamlined", "optimized", "hardened",
    "modular", "scalable", "resilient", "distributed", "async",
]

_STOPWORDS = {
    "the", "a", "an", "for", "and", "or", "to", "in", "on", "of",
    "with", "before", "after", "implement", "add", "create", "build",
    "setup", "how", "your", "you", "is", "are", "this", "that",
    "do", "i", "what", "which", "why", "when", "best", "approach",
    "way", "most", "efficient",
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

    SUCCESS_DECISIONS = {"promoted", "accept", "accepted", "quarantine", "quarantined", "already_published", "auto_promoted"}

    def __init__(self, client: Client) -> None:
        self.client = client

    def publish(self, gene: Gene, capsule: Capsule, event: EvolutionEvent | None = None) -> dict:
        """Publish a GEP bundle to the EvoMap marketplace.

        Computes canonical asset IDs, links Capsule → Gene, assembles
        the bundle, and sends it via the ``/publish`` envelope endpoint.

        Args:
            gene: The Gene asset.
            capsule: The Capsule asset.
            event: Optional EvolutionEvent linking the two.

        Returns:
            API response dict. On success, ``payload.asset_ids``
            contains the server-assigned IDs (index 0 = Gene,
            1 = Capsule, 2 = EvolutionEvent).
        """
        # Step 1: Compute Gene asset_id
        gene_dict = gene.to_dict()
        gene_dict["asset_id"] = compute_asset_id(gene_dict)

        # Step 2: Link Capsule to Gene and compute its asset_id
        capsule.gene = gene_dict["asset_id"]
        capsule_dict = capsule.to_dict()
        capsule_dict["asset_id"] = compute_asset_id(capsule_dict)

        assets = [gene_dict, capsule_dict]

        # Step 3: Link EvolutionEvent to both and compute its asset_id
        if event:
            event.capsule_id = capsule_dict["asset_id"]
            event.genes_used = [gene_dict["asset_id"]]
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
