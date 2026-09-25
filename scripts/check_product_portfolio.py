#!/usr/bin/env python3
"""Validate the public-safe canonical product portfolio index."""

import datetime
import json
import pathlib
import re
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "docs" / "product-portfolio-index.json"
ROOT_FIELDS = {
    "schema_version",
    "tracker",
    "observed_at",
    "max_age_days",
    "scope",
    "records",
}
SCOPE_FIELDS = {
    "organizations",
    "public_repository_inventory_reference",
    "private_metadata_disposition",
    "private_inventory_reference",
    "private_inventory_completeness",
}
RECORD_FIELDS = {
    "id",
    "display_name",
    "record_kind",
    "canonical_repository",
    "repository_visibility",
    "repository_subpath",
    "lifecycle_state",
    "owning_tracker",
    "evidence_revision",
    "evidence_source",
    "product_prd_reference",
    "public_claim",
}
EXPECTED_RECORD_BINDINGS = {
    "nownest": {
        "display_name": "NowNest",
        "record_kind": "product",
        "canonical_repository": "edoworks/nownest",
        "repository_visibility": "public",
        "repository_subpath": None,
        "lifecycle_state": "VALIDATING",
        "owning_tracker": "edoworks/factory#54",
        "evidence_revision": "eafd67708bfdf87b81cfa0a7abecb8f0af703179",
        "evidence_source": "https://api.github.com/repos/edoworks/nownest/commits/main",
        "product_prd_reference": "edoworks/nownest@eafd67708bfdf87b81cfa0a7abecb8f0af703179:docs/customer-zero-prd.md",
        "public_claim": "qualification_only",
    },
    "rung": {
        "display_name": "Rung",
        "record_kind": "developer_product",
        "canonical_repository": "edoworks/rung",
        "repository_visibility": "public",
        "repository_subpath": None,
        "lifecycle_state": "RELEASED",
        "owning_tracker": "edoworks/factory#48",
        "evidence_revision": "e1f2d922ed88623abb8b6800031dea8cf04cf880",
        "evidence_source": "https://raw.githubusercontent.com/edoworks/rung/e1f2d922ed88623abb8b6800031dea8cf04cf880/product-manifest.json",
        "product_prd_reference": "edoworks/rung@e1f2d922ed88623abb8b6800031dea8cf04cf880:product-manifest.json",
        "public_claim": "released",
    },
    "mews-and-woofs": {
        "display_name": "Mews & Woofs",
        "record_kind": "internal_reference_fixture",
        "canonical_repository": "edoworks/factory",
        "repository_visibility": "public",
        "repository_subpath": "reference-apps/MewsAndWoofs",
        "lifecycle_state": "INTERNAL_REFERENCE",
        "owning_tracker": "edoworks/factory#13",
        "evidence_revision": "ad2e5fd2a15373b334df297815ddabbff2dab293",
        "evidence_source": "docs/MewsAndWoofs-PRD.md",
        "product_prd_reference": "edoworks/factory@ad2e5fd2a15373b334df297815ddabbff2dab293:docs/MewsAndWoofs-PRD.md",
        "public_claim": "internal_only",
    },
    "vorynce": {
        "display_name": "Vorynce",
        "record_kind": "product",
        "canonical_repository": "PRIVATE-REPOSITORY-001",
        "repository_visibility": "private",
        "repository_subpath": None,
        "lifecycle_state": "PAUSED",
        "owning_tracker": "edoworks/factory#70",
        "evidence_revision": "cbdb9928d5c0c81b77442b06909b28811a2a0b7e",
        "evidence_source": "docs/product-lifecycle-admissions.json",
        "product_prd_reference": "PRIVATE_EVIDENCE_REQUIRED",
        "public_claim": "none",
    },
    "lumen-vault": {
        "display_name": "Lumen Vault",
        "record_kind": "unknown_product",
        "canonical_repository": "PRIVATE-REPOSITORY-002",
        "repository_visibility": "private",
        "repository_subpath": None,
        "lifecycle_state": "UNKNOWN",
        "owning_tracker": "edoworks/factory#70",
        "evidence_revision": None,
        "evidence_source": "edoworks/factory#70",
        "product_prd_reference": "UNKNOWN",
        "public_claim": "none",
    },
    "kinetic-foundry": {
        "display_name": "Kinetic Foundry",
        "record_kind": "unknown_product",
        "canonical_repository": "PRIVATE-REPOSITORY-003",
        "repository_visibility": "private",
        "repository_subpath": None,
        "lifecycle_state": "UNKNOWN",
        "owning_tracker": "edoworks/factory#70",
        "evidence_revision": None,
        "evidence_source": "edoworks/factory#70",
        "product_prd_reference": "UNKNOWN",
        "public_claim": "none",
    },
    "jumpyloo": {
        "display_name": "Jumpyloo",
        "record_kind": "unknown_product",
        "canonical_repository": "PRIVATE-REPOSITORY-004",
        "repository_visibility": "private",
        "repository_subpath": None,
        "lifecycle_state": "UNKNOWN",
        "owning_tracker": "edoworks/factory#70",
        "evidence_revision": None,
        "evidence_source": "edoworks/factory#70",
        "product_prd_reference": "UNKNOWN",
        "public_claim": "none",
    },
    "edglex": {
        "display_name": "Edglex",
        "record_kind": "historical_public_surface",
        "canonical_repository": "foculoom/edglex.com",
        "repository_visibility": "public",
        "repository_subpath": None,
        "lifecycle_state": "ARCHIVED",
        "owning_tracker": "edoworks/factory#48",
        "evidence_revision": "fd4b99f2e461ee1270d077c94835628d9a2ac4fd",
        "evidence_source": "edoworks/factory#48",
        "product_prd_reference": "NOT_APPLICABLE",
        "public_claim": "retired",
    },
    "noraze": {
        "display_name": "Noraze",
        "record_kind": "historical_public_surface",
        "canonical_repository": "foculoom/noraze.com",
        "repository_visibility": "public",
        "repository_subpath": None,
        "lifecycle_state": "ARCHIVED",
        "owning_tracker": "edoworks/factory#48",
        "evidence_revision": "22726d02deb310e8b6d7d60346e0fb43637d3ada",
        "evidence_source": "edoworks/factory#48",
        "product_prd_reference": "NOT_APPLICABLE",
        "public_claim": "retired",
    },
}
EXPECTED_RECORD_IDS = set(EXPECTED_RECORD_BINDINGS)
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
PUBLIC_REPOSITORY_PATTERN = re.compile(r"^(?:edoworks|foculoom)/[a-z0-9._-]+$")
PRIVATE_REFERENCE_PATTERN = re.compile(r"^PRIVATE-REPOSITORY-[0-9]{3}$")
PRIVATE_VALUE_PATTERNS = {
    "absolute local path": re.compile(
        r"(?:^|\s)(?:/(?:Users|home|private|tmp|var)/|[A-Za-z]:\\)"
    ),
    "home-relative path": re.compile(r"(?:^|\s)~/"),
    "email address": re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    ),
    "secret-like token": re.compile(
        r"\b(?:AKIA[A-Z0-9]{16}|gh[opsu]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,})\b"
    ),
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "credential-bearing URL": re.compile(r"\bhttps?://[^/\s:@]+:[^/\s@]+@"),
    "backup route": re.compile(r"\b(?:file|s3|ssh)://", re.IGNORECASE),
    "SSH repository identity": re.compile(r"\bgit@[A-Za-z0-9.-]+:"),
}


def reject_duplicate_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON key")
        value[key] = item
    return value


def parse_timestamp(value, label):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"{label} must be a UTC timestamp")
    try:
        return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{label} must be a UTC timestamp") from error


def validate_public_values(value, path="root"):
    errors = []
    if isinstance(value, dict):
        for key, item in value.items():
            errors.extend(validate_public_values(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            errors.extend(validate_public_values(item, f"{path}[{index}]"))
    elif isinstance(value, str):
        for description, pattern in PRIVATE_VALUE_PATTERNS.items():
            if pattern.search(value):
                errors.append(f"{path} contains {description}")
    return errors


def validate(index, now=None):
    errors = []
    if not isinstance(index, dict) or set(index) != ROOT_FIELDS:
        return ["index fields must match the fixed schema"]
    if type(index.get("schema_version")) is not int or index.get("schema_version") != 1:
        errors.append("schema_version must be integer 1")
    if index.get("tracker") != "edoworks/factory#78":
        errors.append("tracker must be edoworks/factory#78")
    try:
        observed_at = parse_timestamp(index.get("observed_at"), "observed_at")
    except ValueError as error:
        errors.append(str(error))
        observed_at = None
    max_age_days = index.get("max_age_days")
    if type(max_age_days) is not int or not 1 <= max_age_days <= 31:
        errors.append("max_age_days must be an integer from 1 through 31")
    if observed_at is not None and type(max_age_days) is int:
        current = now or datetime.datetime.now(datetime.timezone.utc)
        if observed_at > current + datetime.timedelta(minutes=5):
            errors.append("observed_at cannot be in the future")
        elif current - observed_at > datetime.timedelta(days=max_age_days):
            errors.append("portfolio evidence is stale")

    scope = index.get("scope")
    if not isinstance(scope, dict) or set(scope) != SCOPE_FIELDS:
        errors.append("scope fields must match the fixed schema")
        scope = {}
    if scope.get("organizations") != ["edoworks", "foculoom"]:
        errors.append("scope organizations must match the fixed inventory boundary")
    if scope.get("public_repository_inventory_reference") != "EVIDENCE-HOSTED-METADATA":
        errors.append("public repository inventory must use the opaque evidence reference")
    if scope.get("private_metadata_disposition") != "owner_controlled_private":
        errors.append("private metadata must remain owner-controlled and private")
    if scope.get("private_inventory_reference") != "EVIDENCE-HOSTED-METADATA":
        errors.append("private inventory must use the fixed opaque reference")
    if scope.get("private_inventory_completeness") != "UNKNOWN":
        errors.append("private inventory completeness must fail closed as UNKNOWN")

    records = index.get("records")
    if not isinstance(records, list):
        errors.append("records must be an array")
        records = []
    record_ids = []
    canonical_repositories = []
    for position, record in enumerate(records):
        label = f"records[{position}]"
        if not isinstance(record, dict) or set(record) != RECORD_FIELDS:
            errors.append(f"{label} fields must match the fixed schema")
            continue
        record_id = record["id"]
        if not isinstance(record_id, str) or not re.fullmatch(r"[a-z0-9-]+", record_id):
            errors.append(f"{label}.id is invalid")
            continue
        record_ids.append(record_id)
        expected = EXPECTED_RECORD_BINDINGS.get(record_id)
        if expected is None:
            errors.append(f"{label}.id is not in the approved public-safe inventory")
        elif record != {"id": record_id, **expected}:
            errors.append(f"{record_id}: record does not match its approved canonical binding")

        canonical = record["canonical_repository"]
        visibility = record["repository_visibility"]
        if isinstance(canonical, str):
            canonical_repositories.append(canonical)
        if visibility == "public":
            if not isinstance(canonical, str) or not PUBLIC_REPOSITORY_PATTERN.fullmatch(canonical):
                errors.append(f"{label} public repository identity is invalid")
        elif visibility == "private":
            if not isinstance(canonical, str) or not PRIVATE_REFERENCE_PATTERN.fullmatch(canonical):
                errors.append(f"{label} private repository must use an opaque reference")
        else:
            errors.append(f"{label}.repository_visibility is invalid")
        revision = record["evidence_revision"]
        if revision is not None and (
            not isinstance(revision, str) or not SHA_PATTERN.fullmatch(revision)
        ):
            errors.append(f"{label}.evidence_revision must be a full SHA or null")
        prd_reference = record["product_prd_reference"]
        if not isinstance(prd_reference, str):
            errors.append(f"{label}.product_prd_reference must be a string")
        elif visibility == "public" and prd_reference != "NOT_APPLICABLE":
            expected_prefix = f"{canonical}@{revision}:"
            if not prd_reference.startswith(expected_prefix) or prd_reference == expected_prefix:
                errors.append(f"{label} public PRD reference must bind the evidence revision and path")

    if len(record_ids) != len(set(record_ids)):
        errors.append("portfolio record IDs must be unique")
    if set(record_ids) != EXPECTED_RECORD_IDS:
        errors.append("portfolio records must match the approved public-safe inventory")
    if len(canonical_repositories) != len(set(canonical_repositories)):
        errors.append("canonical repository ownership must be unique")
    errors.extend(validate_public_values(index))
    return errors


def main(argv):
    if argv:
        print("ERROR: usage: check_product_portfolio.py", file=sys.stderr)
        return 2
    try:
        index = json.loads(INDEX_PATH.read_text(), object_pairs_hook=reject_duplicate_keys)
        errors = validate(index)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        print("ERROR: canonical portfolio index is unavailable or invalid", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
