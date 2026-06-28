"""Tests for envelope wrapping and client configuration."""

import json
from gep_a2a_negotiator.client import Client, _envelope, canonical_json


def test_envelope_structure():
    env = _envelope("node_123", "hello", {"key": "value"})
    assert env["protocol"] == "gep-a2a"
    assert env["protocol_version"] == "1.0.0"
    assert env["message_type"] == "hello"
    assert env["sender_id"] == "node_123"
    assert env["payload"] == {"key": "value"}
    assert env["message_id"].startswith("msg_")


def test_envelope_timestamp_format():
    env = _envelope("node_123", "heartbeat", {})
    # ISO8601 format: 2025-01-01T00:00:00Z
    assert env["timestamp"].endswith("Z")
    assert "T" in env["timestamp"]


def test_envelope_unique_message_ids():
    env1 = _envelope("node_123", "hello", {})
    env2 = _envelope("node_123", "hello", {})
    assert env1["message_id"] != env2["message_id"]


def test_client_init_with_credentials():
    client = Client(node_id="test_node", node_secret="test_secret")
    assert client.node_id == "test_node"
    assert client.node_secret == "test_secret"


def test_client_env_fingerprint():
    fp = Client.env_fingerprint()
    assert "platform" in fp
    assert "arch" in fp
    assert "python" in fp


def test_client_base_url_default():
    client = Client(node_id="n", node_secret="s")
    assert "evomap.ai" in client.base_url


def test_canonical_json_preserves_values():
    obj = {"b": [1, 2, 3], "a": "hello", "c": {"y": 2, "x": 1}}
    result = canonical_json(obj)
    assert result["a"] == "hello"
    assert result["b"] == [1, 2, 3]
    assert result["c"] == {"x": 1, "y": 2}
