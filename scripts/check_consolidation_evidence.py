#!/usr/bin/env python3
"""Validate the consolidation evidence boundary and public projections."""

import json
import pathlib
import re
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs" / "consolidation-evidence-classification.json"
REQUIRED_EVIDENCE_CLASSES = {
    "repository_history",
    "hosted_metadata",
    "local_overlays",
    "obligations",
    "checksums",
    "recovery_receipts",
}
CANONICAL_PUBLIC_RECORD_FILES = ["docs/consolidation-evidence-public.json"]
EXPECTED_CONTRACT_FIELDS = {
    "schema_version",
    "tracker",
    "parent_tracker",
    "default_disposition",
    "public_record_files",
    "storage_classes",
    "public_record_contract",
    "evidence_inventory",
}
EXPECTED_STORAGE_CLASSES = {
    "owner_controlled_private": {
        "visibility": "private",
        "status": "REQUIRED_NOT_PROVISIONED",
    },
    "repository_public_record": {
        "visibility": "public",
        "status": "ACTIVE",
    },
}
EXPECTED_REQUIRED_FIELDS = {
    "evidence_class",
    "disposition",
    "provenance_reference",
}
EXPECTED_ALLOWED_FIELDS = EXPECTED_REQUIRED_FIELDS | {
    "inventory_reference",
    "checksum_sha256",
    "recovery_receipt_reference",
}
EXPECTED_PROHIBITED_FIELDS = {
    "archive_path",
    "backup_routing",
    "credential",
    "credentials",
    "email",
    "local_path",
    "payload",
    "person_name",
    "personal_information",
    "preservation_destination",
    "private_metadata",
    "private_repository",
    "remote_identity",
    "remote_url",
    "restore_path",
    "secret",
    "token",
    "tokens",
}
EXPECTED_INVENTORY_REFERENCES = {
    "repository_history": "EVIDENCE-REPOSITORY-HISTORY",
    "hosted_metadata": "EVIDENCE-HOSTED-METADATA",
    "local_overlays": "EVIDENCE-LOCAL-OVERLAYS",
    "obligations": "EVIDENCE-OBLIGATIONS",
    "checksums": "EVIDENCE-CHECKSUMS",
    "recovery_receipts": "EVIDENCE-RECOVERY-RECEIPTS",
}
APPROVED_PUBLIC_CHECKSUMS = set()
APPROVED_PUBLIC_RECOVERY_RECEIPTS = set()
PUBLIC_RECORD_ROOT_FIELDS = {"schema_version", "records"}
PRIVATE_VALUE_PATTERNS = {
    "absolute local path": re.compile(
        r"(?:^|\s)(?:/(?:Users|home|private|tmp|var)/|~/|[A-Za-z]:\\)"
    ),
    "email address": re.compile(r"\b[^\s@]+@[^\s@]+\.[^\s@]+\b"),
    "secret-like token": re.compile(
        r"\b(?:AKIA[A-Z0-9]{16}|gh[opsu]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,})\b"
    ),
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "credential-bearing URL": re.compile(r"\bhttps?://[^/\s:@]+:[^/\s@]+@"),
    "backup route": re.compile(r"\b(?:file|s3|ssh)://", re.IGNORECASE),
}


def reject_duplicate_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def load_json(path):
    try:
        return json.loads(path.read_text(), object_pairs_hook=reject_duplicate_keys)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"{path}: cannot read valid JSON: {error}") from error


def validate_contract(contract):
    errors = []
    if not isinstance(contract, dict):
        return ["contract root must be an object"]
    if set(contract) != EXPECTED_CONTRACT_FIELDS:
        errors.append("contract fields must match the fixed schema")
    if contract.get("schema_version") != 1:
        errors.append("contract schema_version must be 1")
    if contract.get("tracker") != "edoworks/factory#77":
        errors.append("contract tracker must be edoworks/factory#77")
    if contract.get("parent_tracker") != "edoworks/factory#68":
        errors.append("contract parent tracker must be edoworks/factory#68")
    if contract.get("default_disposition") != "private":
        errors.append("unknown evidence must default to private")

    if contract.get("storage_classes") != EXPECTED_STORAGE_CLASSES:
        errors.append("storage classes must match the fixed private/public schema")

    if contract.get("public_record_files") != CANONICAL_PUBLIC_RECORD_FILES:
        errors.append("tracked public record files must match the pinned canonical manifest")

    public_contract = contract.get("public_record_contract", {})
    if not isinstance(public_contract, dict) or set(public_contract) != {
        "required_fields",
        "allowed_fields",
        "allowed_disposition",
        "prohibited_fields",
    }:
        errors.append("public record contract fields must match the fixed schema")
        public_contract = {}
    required_fields = set(public_contract.get("required_fields", []))
    allowed_fields = set(public_contract.get("allowed_fields", []))
    prohibited_fields = set(public_contract.get("prohibited_fields", []))
    if required_fields != EXPECTED_REQUIRED_FIELDS:
        errors.append("public record required fields are invalid")
    if allowed_fields != EXPECTED_ALLOWED_FIELDS:
        errors.append("public record allowed fields are invalid")
    if prohibited_fields != EXPECTED_PROHIBITED_FIELDS:
        errors.append("public record prohibited fields are invalid")
    if public_contract.get("allowed_disposition") != "public_safe_reference":
        errors.append("public records must be reference-only")

    inventory = contract.get("evidence_inventory", [])
    inventory_classes = [item.get("evidence_class") for item in inventory if isinstance(item, dict)]
    if len(inventory_classes) != len(set(inventory_classes)):
        errors.append("evidence inventory classes must be unique")
    if set(inventory_classes) != REQUIRED_EVIDENCE_CLASSES:
        errors.append("evidence inventory must classify every required class")
    for item in inventory:
        if not isinstance(item, dict):
            errors.append("evidence inventory entries must be objects")
            continue
        if set(item) != {
            "evidence_class",
            "source_disposition",
            "storage_class",
            "public_projection",
        }:
            errors.append("evidence inventory fields must match the fixed schema")
        evidence_class = item.get("evidence_class", "<unknown>")
        if item.get("source_disposition") != "private":
            errors.append(f"{evidence_class}: source evidence must remain private")
        if item.get("storage_class") != "owner_controlled_private":
            errors.append(f"{evidence_class}: private storage class is required")
        if item.get("public_projection") != "public_safe_reference":
            errors.append(f"{evidence_class}: public projection must be reference-only")
    return errors


def validate_public_record(contract, record, source="public record", require_complete=False):
    errors = []
    if not isinstance(record, dict):
        return [f"{source}: root must be an object"]
    unknown_root_fields = set(record) - PUBLIC_RECORD_ROOT_FIELDS
    if unknown_root_fields:
        errors.append(f"{source}: unknown root fields: {', '.join(sorted(unknown_root_fields))}")
    if record.get("schema_version") != 1:
        errors.append(f"{source}: schema_version must be 1")
    records = record.get("records")
    if not isinstance(records, list):
        errors.append(f"{source}: records must be an array")
        return errors

    public_contract = contract["public_record_contract"]
    required_fields = set(public_contract["required_fields"])
    allowed_fields = set(public_contract["allowed_fields"])
    prohibited_fields = set(public_contract["prohibited_fields"])
    allowed_disposition = public_contract["allowed_disposition"]
    observed_classes = []

    for index, item in enumerate(records):
        label = f"{source}: records[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        fields = set(item)
        missing = required_fields - fields
        unknown = fields - allowed_fields
        prohibited = fields & prohibited_fields
        if missing:
            errors.append(f"{label} missing required fields: {', '.join(sorted(missing))}")
        if unknown:
            errors.append(f"{label} contains non-public fields: {', '.join(sorted(unknown))}")
        if prohibited:
            errors.append(f"{label} contains prohibited fields: {', '.join(sorted(prohibited))}")
        if item.get("evidence_class") not in REQUIRED_EVIDENCE_CLASSES:
            errors.append(f"{label} has an unknown evidence_class")
        else:
            observed_classes.append(item["evidence_class"])
        if item.get("disposition") != allowed_disposition:
            errors.append(f"{label} disposition must be {allowed_disposition}")
        if item.get("provenance_reference") not in {
            "edoworks/factory#68",
            "edoworks/factory#77",
        }:
            errors.append(f"{label} provenance_reference is not an approved public source")
        expected_inventory = EXPECTED_INVENTORY_REFERENCES.get(item.get("evidence_class"))
        if "inventory_reference" in item and item["inventory_reference"] != expected_inventory:
            errors.append(f"{label} inventory_reference is not the fixed opaque identifier")
        recovery_reference = item.get("recovery_receipt_reference")
        if recovery_reference is not None and not re.fullmatch(
            r"RECOVERY-[0-9]{8}-[0-9]{2}", str(recovery_reference)
        ):
            errors.append(f"{label} recovery_receipt_reference is not an opaque receipt identifier")
        elif recovery_reference is not None and (
            item.get("evidence_class"), recovery_reference
        ) not in APPROVED_PUBLIC_RECOVERY_RECEIPTS:
            errors.append(f"{label} recovery_receipt_reference is not approved for public disclosure")
        checksum = item.get("checksum_sha256")
        if checksum is not None and not re.fullmatch(r"[0-9a-f]{64}", str(checksum)):
            errors.append(f"{label} checksum_sha256 must be lowercase SHA-256")
        elif checksum is not None and (
            item.get("evidence_class"), checksum
        ) not in APPROVED_PUBLIC_CHECKSUMS:
            errors.append(f"{label} checksum_sha256 is not approved for public disclosure")
        for field, value in item.items():
            if not isinstance(value, str):
                errors.append(f"{label}.{field} must be a string")
                continue
            for description, pattern in PRIVATE_VALUE_PATTERNS.items():
                if pattern.search(value):
                    errors.append(f"{label}.{field} contains {description}")
    if len(observed_classes) != len(set(observed_classes)):
        errors.append(f"{source}: evidence classes must be unique")
    if require_complete and set(observed_classes) != REQUIRED_EVIDENCE_CLASSES:
        errors.append(f"{source}: canonical public inventory must contain every evidence class")
    return errors


def main(argv):
    try:
        contract = load_json(CONTRACT_PATH)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1
    errors = validate_contract(contract)
    inputs = (
        [(ROOT / name, True) for name in CANONICAL_PUBLIC_RECORD_FILES]
        if not errors
        else []
    )
    inputs.extend((pathlib.Path(name), False) for name in argv)
    for path, require_complete in inputs:
        try:
            public_record = load_json(path)
        except ValueError as error:
            errors.append(str(error))
            continue
        errors.extend(
            validate_public_record(
                contract,
                public_record,
                str(path),
                require_complete=require_complete,
            )
        )
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
