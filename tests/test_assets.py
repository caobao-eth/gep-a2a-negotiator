"""Tests for GEP asset models and keyword extraction (schema v1.6.0)."""

from gep_a2a_negotiator.publish import Gene, Capsule, EvolutionEvent, extract_keywords


def test_gene_to_dict():
    gene = Gene(
        summary="Rate limiting via sliding window",
        strategy=["Use Redis Lua script for atomic rate checking", "Per-route configurable limits with whitelist"],
        signals_match=["rate", "limit", "sliding"],
    )
    d = gene.to_dict()
    assert d["type"] == "Gene"
    assert d["schema_version"] == "1.6.0"
    assert d["category"] == "repair"
    assert d["model_name"] == "sub-agent-1"
    assert len(d["strategy"]) >= 2
    assert all(len(s) >= 15 for s in d["strategy"])
    assert "asset_id" not in d
    assert "body" not in d  # v1.6.0 has summary, not body
    assert "title" not in d  # v1.6.0 has summary, not title


def test_capsule_to_dict():
    cap = Capsule(summary="Rate limit solution", trigger=["rate", "limit"])
    d = cap.to_dict()
    assert d["type"] == "Capsule"
    assert d["schema_version"] == "1.6.0"
    assert d["confidence"] == 0.85
    assert d["trigger"] == ["rate", "limit"]
    assert d["blast_radius"] == {"files": 1, "lines": 50}
    assert d["outcome"] == {"status": "success", "score": 0.85}
    assert d["gene"] == ""  # empty until Publisher sets it
    assert "env_fingerprint" in d
    assert "success_streak" in d


def test_evolution_event_to_dict():
    event = EvolutionEvent(capsule_id="sha256:cap", genes_used=["sha256:gene"])
    d = event.to_dict()
    assert d["type"] == "EvolutionEvent"
    assert d["intent"] == "repair"
    assert d["capsule_id"] == "sha256:cap"
    assert d["genes_used"] == ["sha256:gene"]
    assert d["mutations_tried"] == 3
    assert d["total_cycles"] == 5
    assert "outcome" in d


def test_extract_keywords_basic():
    keywords = extract_keywords("Implement rate limiting middleware")
    assert len(keywords) >= 3
    assert "rate" in keywords
    assert "limiting" in keywords
    # Last item should be a salt word
    assert keywords[-1] in {
        "adaptive", "robust", "streamlined", "optimized", "hardened",
        "modular", "scalable", "resilient", "distributed", "async",
    }


def test_extract_keywords_filters_stopwords():
    keywords = extract_keywords("How do I implement rate limiting in a Node.js API")
    assert "how" not in keywords
    assert "implement" not in keywords
    assert "rate" in keywords
    assert "limiting" in keywords


def test_extract_keywords_uniqueness():
    """Repeated calls should produce different triggers (salt rotation)."""
    results = set()
    for _ in range(20):
        kws = extract_keywords("Implement caching strategy")
        results.add(tuple(kws))
    assert len(results) >= 2


def test_extract_keywords_empty_title():
    keywords = extract_keywords("")
    assert len(keywords) >= 3
