#!/usr/bin/env python3
"""Validate an offline app lock against a proposed bundled release manifest."""

import hashlib
import graphlib
import json
import pathlib
import re
import sys


REPOSITORY = "edoworks/factory"
MAX_JSON_BYTES = 1024 * 1024
REVISION = re.compile(r"[0-9a-f]{40}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
TAG = re.compile(
    r"v(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
    r"(?:-(?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*))*)?\Z"
)
PATH = re.compile(r"[A-Za-z0-9._/-]+\Z")
SKILL = re.compile(r"[A-Za-z0-9._-]+\Z")
ASSET = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")

LOCK_FIELDS = {"schema_version", "release", "manifest", "payload", "workflow"}
RELEASE_FIELDS = {"repository", "tag", "source_revision"}
MANIFEST_FIELDS = {"sha256"}
PAYLOAD_FIELDS = {"asset_name", "sha256"}
WORKFLOW_FIELDS = {"path", "commit"}
FILE_FIELDS = {"path", "sha256", "origin", "license", "notices"}
SKILL_FIELDS = {"instructions", "files", "dependencies"}


def _reject_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_nonfinite(value):
    raise ValueError(f"non-finite JSON constant: {value}")


def load_json(path):
    with pathlib.Path(path).open("rb") as stream:
        raw = stream.read(MAX_JSON_BYTES + 1)
    if len(raw) > MAX_JSON_BYTES:
        raise ValueError("JSON document exceeds the 1 MiB contract limit")
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_reject_duplicates,
            parse_constant=_reject_nonfinite,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError, RecursionError) as error:
        raise ValueError(f"{path}: invalid JSON: {error}") from error
    return raw, value


def _object(value, fields, label, errors):
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return False
    unknown = set(value) - fields
    missing = fields - set(value)
    if unknown:
        errors.append(f"{label} has unknown fields: {', '.join(sorted(unknown))}")
    if missing:
        errors.append(f"{label} is missing fields: {', '.join(sorted(missing))}")
    return not unknown and not missing


def _text(value, label, errors):
    if not isinstance(value, str):
        errors.append(f"{label} must be a string")
        return False
    return True


def _identity(value, label, errors):
    if not _object(value, RELEASE_FIELDS, label, errors):
        return
    if value.get("repository") != REPOSITORY:
        errors.append(f"{label}.repository must be {REPOSITORY}")
    if not isinstance(value.get("tag"), str) or not TAG.fullmatch(value.get("tag", "")):
        errors.append(f"{label}.tag must be an exact semver-formatted tag")
    if not isinstance(value.get("source_revision"), str) or not REVISION.fullmatch(
        value.get("source_revision", "")
    ):
        errors.append(f"{label}.source_revision must be 40 lowercase hex characters")


def _digest(value, label, errors):
    if not _text(value, label, errors) or not SHA256.fullmatch(value):
        errors.append(f"{label} must be 64 lowercase hex characters")


def _path(value, label, errors):
    if not _text(value, label, errors) or not PATH.fullmatch(value):
        errors.append(f"{label} must be a safe relative POSIX path")
        return False
    if value.startswith("/") or "//" in value or "\\" in value:
        errors.append(f"{label} must be a safe relative POSIX path")
        return False
    if any(part in {"", ".", ".."} for part in value.split("/")):
        errors.append(f"{label} must not contain traversal or empty components")
        return False
    return True


def _payload(value, label, errors):
    if not _object(value, PAYLOAD_FIELDS, label, errors):
        return
    if not _text(value.get("asset_name"), f"{label}.asset_name", errors):
        return
    if not ASSET.fullmatch(value["asset_name"]):
        errors.append(f"{label}.asset_name must be a plain uploaded payload name")
    _digest(value.get("sha256"), f"{label}.sha256", errors)


def _workflow(value, label, errors):
    if not _object(value, WORKFLOW_FIELDS, label, errors):
        return
    _path(value.get("path"), f"{label}.path", errors)
    if not isinstance(value.get("commit"), str) or not REVISION.fullmatch(value.get("commit", "")):
        errors.append(f"{label}.commit must be 40 lowercase hex characters")


def _validate_lock(lock, errors):
    if not _object(lock, LOCK_FIELDS, "lock", errors):
        return
    _identity(lock.get("release"), "lock.release", errors)
    manifest = lock.get("manifest")
    if _object(manifest, MANIFEST_FIELDS, "lock.manifest", errors):
        _digest(manifest.get("sha256"), "lock.manifest.sha256", errors)
    _payload(lock.get("payload"), "lock.payload", errors)
    _workflow(lock.get("workflow"), "lock.workflow", errors)
    if type(lock.get("schema_version")) is not int or lock["schema_version"] != 1:
        errors.append("lock.schema_version must be 1")


def _validate_manifest(manifest, errors):
    fields = {"schema_version", "release", "payload", "workflow", "files", "skills"}
    if not _object(manifest, fields, "manifest", errors):
        return
    if type(manifest.get("schema_version")) is not int or manifest["schema_version"] != 1:
        errors.append("manifest.schema_version must be 1")
    _identity(manifest.get("release"), "manifest.release", errors)
    _payload(manifest.get("payload"), "manifest.payload", errors)
    _workflow(manifest.get("workflow"), "manifest.workflow", errors)

    files = manifest.get("files")
    inventory = {}
    if not isinstance(files, list):
        errors.append("manifest.files must be an array")
    else:
        for index, item in enumerate(files):
            label = f"manifest.files[{index}]"
            if not _object(item, FILE_FIELDS, label, errors):
                continue
            path = item.get("path")
            if not _path(path, f"{label}.path", errors):
                continue
            if path in inventory:
                errors.append(f"duplicate inventory path: {path}")
            inventory[path] = item
            _digest(item.get("sha256"), f"{label}.sha256", errors)
            for field in ("origin", "license"):
                if not isinstance(item.get(field), str) or not item[field].strip():
                    errors.append(f"{label}.{field} must be a meaningful reference or identifier")
            _path(item.get("notices"), f"{label}.notices", errors)

    for path, item in inventory.items():
        notices = item.get("notices")
        if not isinstance(notices, str) or notices not in inventory:
            errors.append(f"inventory file {path}.notices must refer to an inventoried file")

    skills = manifest.get("skills")
    if not isinstance(skills, dict) or not skills:
        errors.append("manifest.skills must be a non-empty object")
        return
    graph = {}
    for name, skill in skills.items():
        label = f"manifest.skills[{name!r}]"
        if not isinstance(name, str) or not SKILL.fullmatch(name):
            errors.append(f"{label} has an invalid skill name")
        if not _object(skill, SKILL_FIELDS, label, errors):
            continue
        instructions = skill.get("instructions")
        if not isinstance(instructions, str) or instructions not in inventory:
            errors.append(f"{label}.instructions must refer to an inventoried file")
        listed = skill.get("files")
        if not isinstance(listed, list) or not listed or not all(isinstance(path, str) for path in listed):
            errors.append(f"{label}.files must be a non-empty array of file paths")
        else:
            if len(set(listed)) != len(listed):
                errors.append(f"{label}.files must not contain duplicates")
            if instructions not in listed:
                errors.append(f"{label}.files must include its instructions")
            for path in listed:
                if path not in inventory:
                    errors.append(f"{label}.files refers to a missing inventoried file: {path}")
        dependencies = skill.get("dependencies")
        if not isinstance(dependencies, list) or not all(isinstance(dep, str) for dep in dependencies):
            errors.append(f"{label}.dependencies must be an array of skill names")
        else:
            if len(set(dependencies)) != len(dependencies):
                errors.append(f"{label}.dependencies must not contain duplicates")
            graph[name] = dependencies
            for dependency in dependencies:
                if dependency not in skills:
                    errors.append(f"{label} refers to missing bundled skill: {dependency}")

    try:
        graphlib.TopologicalSorter(graph).prepare()
    except graphlib.CycleError:
        errors.append("cyclic skill dependency")


def validate(lock, manifest, manifest_bytes):
    errors = []
    _validate_lock(lock, errors)
    _validate_manifest(manifest, errors)
    if isinstance(lock, dict) and isinstance(manifest, dict):
        lock_manifest = lock.get("manifest")
        locked_hash = lock_manifest.get("sha256") if isinstance(lock_manifest, dict) else None
        if locked_hash != hashlib.sha256(manifest_bytes).hexdigest():
            errors.append("lock.manifest.sha256 does not match the exact manifest file bytes")
        for section in ("release", "payload", "workflow"):
            if lock.get(section) != manifest.get(section):
                errors.append(f"lock.{section} does not match manifest.{section}")
    return errors


def main(argv):
    errors = []
    if len(argv) != 2:
        errors.append("usage: check_release_consumption.py LOCK.json MANIFEST.json")
        lock = manifest = None
        manifest_bytes = b""
    else:
        try:
            _, lock = load_json(argv[0])
        except (OSError, ValueError) as error:
            errors.append(str(error))
            lock = None
        try:
            manifest_bytes, manifest = load_json(argv[1])
        except (OSError, ValueError) as error:
            errors.append(str(error))
            manifest_bytes, manifest = b"", None
    if not errors:
        errors.extend(validate(lock, manifest, manifest_bytes))
    receipt = {
        "contract_valid": not errors,
        "release_verified": False,
        "consumption_authorized": False,
        "error_count": len(errors),
        "errors": [error[:512] for error in errors[:64]],
    }
    print(json.dumps(receipt, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
