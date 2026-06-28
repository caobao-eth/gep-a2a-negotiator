"""Tests for canonical JSON hashing and asset ID computation."""

import hashlib
import json

from gep_a2a_negotiator.client import canonical_json, compute_asset_id


def test_canonical_json_sorts_keys():
    obj = {"b": 2, "a": 1, "c": 3}
    result = canonical_json(obj)
    assert list(result.keys()) == ["a", "b", "c"]


def test_canonical_json_removes_asset_id():
    obj = {"asset_id": "sha256:abc", "title": "test"}
    result = canonical_json(obj)
    assert "asset_id" not in result
    assert result["title"] == "test"


def test_canonical_json_nested():
    obj = {"z": [{"b": 2, "a": 1}], "a": 0}
    result = canonical_json(obj)
    assert result["z"][0] == {"a": 1, "b": 2}


def test_compute_asset_id_deterministic():
    obj = {"title": "test", "body": "content", "type": "Gene"}
    id1 = compute_asset_id(obj)
    id2 = compute_asset_id(obj)
    assert id1 == id2
    assert id1.startswith("sha256:")


def test_compute_asset_id_excludes_asset_id():
    """Adding an asset_id field must not change the computed hash."""
    obj = {"title": "test", "type": "Gene"}
    obj_with_id = {"title": "test", "type": "Gene", "asset_id": "sha256:existing"}
    assert compute_asset_id(obj) == compute_asset_id(obj_with_id)


def test_compute_asset_id_matches_manual():
    obj = {"type": "Gene", "title": "test", "body": "hello"}
    canonical = canonical_json(obj)
    s = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    expected = f"sha256:{hashlib.sha256(s.encode()).hexdigest()}"
    assert compute_asset_id(obj) == expected


def test_compute_asset_id_different_objects():
    a = {"title": "foo", "type": "Gene"}
    b = {"title": "bar", "type": "Gene"}
    assert compute_asset_id(a) != compute_asset_id(b)
