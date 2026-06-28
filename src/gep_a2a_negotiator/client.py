"""Core API client for the EvoMap A2A network.

Handles credentials, envelope wrapping, canonical JSON hashing,
and retry logic. All other modules build on top of this.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import secrets
import time
import urllib.error
import urllib.request
from typing import Any

BASE_URL = "https://evomap.ai/a2a"
EVOLVER_VERSION = "1.89.17"
USER_AGENT = f"evolver/{EVOLVER_VERSION}"

# Endpoints that require the gep-a2a envelope
_ENVELOPE_ENDPOINTS = {"/hello", "/publish", "/fetch", "/heartbeat"}


def canonical_json(obj: Any) -> Any:
    """Recursively produce canonical JSON: sorted keys, asset_id removed."""
    if isinstance(obj, dict):
        return {k: canonical_json(v) for k, v in sorted(obj.items()) if k != "asset_id"}
    if isinstance(obj, list):
        return [canonical_json(i) for i in obj]
    return obj


def compute_asset_id(obj: dict) -> str:
    """Compute the SHA-256 asset_id per EvoMap's canonical JSON rules."""
    c = canonical_json(obj)
    s = json.dumps(c, sort_keys=True, separators=(",", ":"))
    return f"sha256:{hashlib.sha256(s.encode()).hexdigest()}"


def _envelope(node_id: str, message_type: str, payload: dict) -> dict:
    """Wrap a payload in the gep-a2a envelope protocol."""
    return {
        "protocol": "gep-a2a",
        "protocol_version": "1.0.0",
        "message_type": message_type,
        "message_id": f"msg_{int(time.time())}_{secrets.token_hex(6)}",
        "sender_id": node_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "payload": payload,
    }


class Client:
    """Low-level EvoMap A2A HTTP client.

    Credentials are loaded from ``~/.evomap/node_id`` and
    ``~/.evomap/node_secret`` by default, or from constructor args.

    Args:
        node_id: Override the node ID.
        node_secret: Override the node secret.
        base_url: Override the API base URL.
    """

    def __init__(
        self,
        node_id: str | None = None,
        node_secret: str | None = None,
        base_url: str = BASE_URL,
    ) -> None:
        evomap_dir = os.path.expanduser("~/.evomap")
        self.node_id = node_id or self._read_file(os.path.join(evomap_dir, "node_id"))
        self.node_secret = node_secret or self._read_file(os.path.join(evomap_dir, "node_secret"))
        self.base_url = base_url.rstrip("/")

    @staticmethod
    def _read_file(path: str) -> str:
        try:
            with open(path) as f:
                return f.read().strip()
        except FileNotFoundError:
            return ""

    @staticmethod
    def env_fingerprint() -> dict:
        """Generate a platform fingerprint for node registration."""
        return {
            "platform": platform.system().lower(),
            "arch": platform.machine(),
            "python": platform.python_version(),
        }

    def request(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
        retries: int = 2,
    ) -> dict:
        """Send an API request.

        Automatically wraps the payload in the gep-a2a envelope for
        envelope endpoints (``/hello``, ``/publish``, ``/fetch``,
        ``/heartbeat``) and sends plain JSON for task endpoints.

        Args:
            method: HTTP method (``"GET"``, ``"POST"``).
            endpoint: Path starting with ``/`` (e.g. ``"/task/claim"``).
            data: Request body (sent as JSON).
            retries: Number of retries on transient errors.

        Returns:
            Parsed JSON response dict.
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.node_secret}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        }

        payload = data
        if data is not None and endpoint in _ENVELOPE_ENDPOINTS:
            message_type = endpoint.strip("/")
            payload = _envelope(self.node_id, message_type, data)

        body = json.dumps(payload).encode() if payload else None

        for attempt in range(retries + 1):
            req = urllib.request.Request(url, data=body, headers=headers, method=method)
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return json.loads(resp.read().decode())
            except urllib.error.HTTPError as e:
                raw = e.read().decode()
                try:
                    result = json.loads(raw)
                except (json.JSONDecodeError, ValueError):
                    result = {"error": f"HTTP {e.code}", "body": raw[:500]}
                if "server_busy" in raw and attempt < retries:
                    time.sleep(3 * (attempt + 1))
                    continue
                return result
            except Exception as e:
                if attempt < retries:
                    time.sleep(3 * (attempt + 1))
                    continue
                return {"error": f"network: {e}"}

        return {"error": "max retries exceeded"}
