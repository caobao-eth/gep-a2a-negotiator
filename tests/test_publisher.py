"""Test for Publisher response parsing and publish gate logic."""

from gep_a2a_negotiator.publish import Publisher


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
