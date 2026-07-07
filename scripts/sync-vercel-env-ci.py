#!/usr/bin/env python3
"""Push GitHub Actions env (already in os.environ) to Vercel project env."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / ".github" / "env.manifest.json"
TARGETS = ["production", "preview", "development"]


def main() -> int:
    token = os.environ.get("VERCEL_TOKEN", "").strip()
    project_id = os.environ.get("VERCEL_PROJECT_ID", "").strip()
    team_id = os.environ.get("VERCEL_ORG_ID", "").strip()

    if not token or not project_id:
        print("VERCEL_TOKEN and VERCEL_PROJECT_ID are required.", file=sys.stderr)
        return 1

    manifest = json.loads(MANIFEST.read_text())
    vercel_cfg = manifest.get("vercel", {})
    secret_keys = vercel_cfg.get("deploySecrets", [])
    variable_keys = vercel_cfg.get("deployVariables", [])
    defaults = manifest.get("productionDefaults", {})

    values: dict[str, tuple[str, str]] = {}
    for key in secret_keys + variable_keys:
        value = os.environ.get(key, "").strip()
        if not value and key in defaults:
            value = str(defaults[key]).strip()
        if not value:
            continue
        env_type = "encrypted" if key in secret_keys else "plain"
        values[key] = (value, env_type)

    if not values:
        print("No env values found to sync.", file=sys.stderr)
        return 1

    team_query = f"?teamId={team_id}" if team_id else ""
    list_url = f"https://api.vercel.com/v9/projects/{project_id}/env{team_query}"
    existing = _request("GET", list_url, token)
    existing_by_key: dict[str, list[str]] = {}
    for item in existing.get("envs", []):
        existing_by_key.setdefault(item["key"], []).append(item["id"])

    synced = 0
    for key, (value, env_type) in sorted(values.items()):
        for env_id in existing_by_key.get(key, []):
            delete_url = f"https://api.vercel.com/v9/projects/{project_id}/env/{env_id}{team_query}"
            _request("DELETE", delete_url, token)

        create_url = f"https://api.vercel.com/v10/projects/{project_id}/env{team_query}"
        _request(
            "POST",
            create_url,
            token,
            {
                "key": key,
                "value": value,
                "type": env_type,
                "target": TARGETS,
            },
        )
        print(f"synced {key} ({env_type})")
        synced += 1

    print(f"Synced {synced} variables to Vercel.")
    return 0


def _request(method: str, url: str, token: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode()
        raise RuntimeError(f"{method} {url} failed ({exc.code}): {detail}") from exc


if __name__ == "__main__":
    raise SystemExit(main())
