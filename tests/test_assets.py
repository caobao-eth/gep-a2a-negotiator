"""Tests for GEP asset models and keyword extraction."""

from gep_a2a_negotiator.publish import Gene, Capsule, EvolutionEvent, extract_keywords


def test_gene_to_dict():
    gene = Gene(
        title="Rate Limiting",
        body="Implement sliding window rate limiting",
        strategy=["Use Redis Lua script for atomic rate checking", "Per-route configurable limits"],
    )
    d = gene.to_dict()
    assert d["type"] == "Gene"
    assert d["schema_version"] == "1.5.0"
    assert len(d["strategy"]) >= 2
    assert all(len(s) >= 15 for s in d["strategy"])
    assert "asset_id" not in d


def test_gene_body_truncation():
    gene = Gene(title="T", body="x" * 10000, strategy=["a" * 20, "b" * 20])
    assert len(gene.to_dict()["body"]) <= 8000


def test_capsule_to_dict():
    cap = Capsule(title="Test", content="Solution content here", trigger=["rate", "limit"])
    d = cap.to_dict()
    assert d["type"] == "Capsule"
    assert d["confidence"] == 0.85
    assert d["trigger"] == ["rate", "limit"]


def test_evolution_event_to_dict():
    event = EvolutionEvent(gene_id="sha256:gene", capsule_id="sha256:cap")
    d = event.to_dict()
    assert d["type"] == "EvolutionEvent"
    assert d["intent"] == "repair"
    assert d["gene_id"] == "sha256:gene"


def test_extract_keywords_basic():
    keywords = extract_keywords("Implement rate limiting middleware")
    assert len(keywords) >= 3
    assert "rate" in keywords
    # Last item should be a salt word
    assert keywords[-1] in {
        "adaptive", "robust", "streamlined", "optimized", "hardened",
        "modular", "scalable", "resilient", "distributed", "async",
    }


def test_extract_keywords_filters_stopwords():
    keywords = extract_keywords("How to add a JWT token for authentication")
    assert "how" not in keywords
    assert "add" not in keywords
    assert "jwt" in keywords
    assert "token" in keywords


def test_extract_keywords_uniqueness():
    """Repeated calls should produce different triggers (salt rotation)."""
    results = set()
    for _ in range(20):
        kws = extract_keywords("Implement caching strategy")
        results.add(tuple(kws))
    # At least 2 different salt words should appear
    assert len(results) >= 2


def test_extract_keywords_empty_title():
    keywords = extract_keywords("")
    assert len(keywords) >= 3
