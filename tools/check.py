#!/usr/bin/env python3
"""Validate a Package Store catalog and every local package it names.

Checks the catalog shape, paths, manifest identity and the artifact/icon SHA-256 and
size, so a broken publish is caught before Grimoire fetches it.

    python3 tools/check.py
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ID = re.compile(r"^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")
HTTP = re.compile(r"^https://", re.I)


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    return 1


def local_path(value):
    if not isinstance(value, str) or not value:
        return None
    if HTTP.match(value):
        return None
    if value.startswith("/") or "\\" in value or ".." in Path(value).parts:
        return None
    return ROOT / value


def scalar(block, key):
    m = re.search(rf"(?m)^\s*{re.escape(key)}:\s*(.*?)\s*(?:#.*)?$", block)
    if not m:
        return None
    return m.group(1).strip().strip("'\"")


def check_package(entry, seen):
    errors = []
    kind = entry.get("type")
    pid = entry.get("id")
    if not isinstance(pid, str) or not ID.fullmatch(pid):
        return [f"bad package id: {pid!r}"]
    if pid in seen:
        errors.append(f"duplicate package id: {pid}")
    seen.add(pid)
    for key in ("name", "version", "author", "summary", "description", "license", "repository", "manifest", "icon"):
        if not isinstance(entry.get(key), str) or not entry[key].strip():
            errors.append(f"{pid}: missing {key}")
    if kind not in ("app", "widget"):
        errors.append(f"{pid}: type must be app or widget")
    shots = entry.get("screenshots")
    if not isinstance(shots, list) or not shots:
        errors.append(f"{pid}: at least one screenshot is required")
    manifest = local_path(entry.get("manifest"))
    if manifest is None:
        return errors
    if not manifest.is_file():
        return errors + [f"{pid}: manifest not found: {entry['manifest']}"]
    text = manifest.read_text(encoding="utf-8")
    for key in ("name", "id", "version", "type", "author"):
        got = scalar(text, key)
        want = entry.get(key)
        if got != want:
            errors.append(f"{pid}: manifest {key} {got!r} != catalog {want!r}")
    def beside_manifest(value):
        if not isinstance(value, str) or not value or HTTP.match(value):
            return None
        if value.startswith("/") or "\\" in value or ".." in Path(value).parts:
            return None
        return manifest.parent / value

    artifact = scalar(text, "path")
    artifact_sha = scalar(text, "sha256")
    artifact_size = scalar(text, "size")
    if not artifact or not artifact_sha or artifact_size is None:
        errors.append(f"{pid}: manifest artifact path/sha256/size is incomplete")
    else:
        ap = beside_manifest(artifact)
        if ap is None or not ap.is_file():
            errors.append(f"{pid}: artifact not found: {artifact}")
        else:
            data = ap.read_bytes()
            if len(data) != int(artifact_size):
                errors.append(f"{pid}: artifact is {len(data)} bytes, manifest says {artifact_size}")
            got = hashlib.sha256(data).hexdigest()
            if got.lower() != artifact_sha.lower():
                errors.append(f"{pid}: artifact sha256 {got} != {artifact_sha}")
    # An app's own icon is another published file with its own digest in the manifest.
    icon_name = scalar(text, "icon")
    icon_sha = scalar(text, "icon_sha256")
    icon_size = scalar(text, "icon_size")
    if icon_name and re.search(r"\.(?:ico|png|jpe?g)$", icon_name, re.I):
        ip = beside_manifest(icon_name)
        if ip is None or not ip.is_file():
            errors.append(f"{pid}: package icon not found: {icon_name}")
        else:
            data = ip.read_bytes()
            if icon_size is not None and len(data) != int(icon_size):
                errors.append(f"{pid}: package icon is {len(data)} bytes, manifest says {icon_size}")
            if icon_sha:
                got = hashlib.sha256(data).hexdigest()
                if got.lower() != icon_sha.lower():
                    errors.append(f"{pid}: package icon sha256 {got} != {icon_sha}")
    icon = entry.get("icon")
    if isinstance(icon, str) and re.search(r"\.(?:ico|png|jpe?g)$", icon, re.I):
        ip = local_path(icon)
        if ip is None or not ip.is_file():
            errors.append(f"{pid}: icon image not found: {icon}")
    for shot in entry.get("screenshots", []):
        sp = local_path(shot)
        if sp is None or not sp.is_file():
            errors.append(f"{pid}: screenshot not found: {shot}")
    return errors


def main():
    try:
        index = json.loads((ROOT / "index.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return fail(f"index.json: {e}")
    if index.get("version") != 1:
        return fail("index.json: version must be 1")
    packages = index.get("packages")
    if not isinstance(packages, list) or not packages:
        return fail("index.json: packages must be a non-empty list")
    seen = set()
    errors = []
    for entry in packages:
        if not isinstance(entry, dict):
            errors.append("index.json: every package must be an object")
            continue
        errors.extend(check_package(entry, seen))
        for shot in entry.get("screenshots", []):
            if not isinstance(shot, str):
                errors.append(f"{entry.get('id')}: screenshot paths must be strings")
    if index.get("featured") and index["featured"] not in seen:
        errors.append(f"featured package {index['featured']!r} is not in packages")
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 1
    print(f"ok: {len(packages)} package(s), {len(seen)} unique id(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
