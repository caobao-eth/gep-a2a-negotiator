"""Tests for Publisher response parsing, publish gate, and asset linking."""

from gep_a2a_negotiator.publish import Publisher, Gene, Capsule, EvolutionEvent, extract_keywords
from gep_a2a_negotiator.client import compute_asset_id


def test_is_published_success():
    for decision in ["promoted", "accepted", "quarantined", "already_published"]:
        resp = {"payload": {"decision": decision}}
        assert Publisher.is_published(resp) is True


def test_is_published_failure():
    for decision in ["trigger_dedup", "rejected", "duplicate", ""]:
        resp = {"payload": {"decision": decision}}
        assert Publisher.is_published(resp) is False


def test_get_capsule_id():
    resp = {"payload": {"asset_ids": ["sha256:gene_id", "sha256:capsule_id", "sha256:event_id"]}}
    assert Publisher.get_capsule_id(resp) == "sha256:capsule_id"


def test_get_capsule_id_missing():
    assert Publisher.get_capsule_id({}) is None
    assert Publisher.get_capsule_id({"payload": {}}) is None
    assert Publisher.get_capsule_id({"payload": {"asset_ids": []}}) is None


def test_gene_asset_id_computed_correctly():
    """Gene asset_id must be deterministic and exclude the asset_id field."""
    gene = Gene(
        summary="Test gene",
        strategy=["Strategy step one is here", "Strategy step two is here"],
        signals_match=["test", "gene"],
    )
    d = gene.to_dict()
    d["asset_id"] = compute_asset_id(d)
    # Recompute and verify match
    d2 = gene.to_dict()
    d2["asset_id"] = compute_asset_id(d2)
    assert d["asset_id"] == d2["asset_id"]
    assert d["asset_id"].startswith("sha256:")


def test_capsule_gene_link():
    """Capsule.gene should be empty until Publisher sets it."""
    cap = Capsule(summary="Test", trigger=["test"])
    assert cap.gene == ""
    # Simulate Publisher linking
    cap.gene = "sha256:gene123"
    d = cap.to_dict()
    assert d["gene"] == "sha256:gene123"
