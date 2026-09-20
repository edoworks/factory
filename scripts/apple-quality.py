#!/usr/bin/env python3
"""Validate lightweight Apple-platform and experience-quality review records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


INTENT_FIELDS = {
    "who",
    "feel",
    "notice_first",
    "primary_experience",
    "can_disappear",
    "motion",
    "sound",
    "physicality",
    "magic",
    "zero_explanation",
    "distinctive",
    "current_apple_capabilities",
}
DISPOSITIONS = {"USE_NOW", "EVALUATE", "EXPERIMENT", "NOT_RELEVANT", "BLOCKED_BY_DEPLOYMENT_TARGET", "REJECT"}
MATURITY = {"AVAILABLE", "SUPPORTED", "STABLE", "BETA", "EXPERIMENTAL"}
EVIDENCE_LEVELS = {"SIMULATOR_VERIFIED", "DEVICE_VERIFIED", "EMPIRICALLY_VERIFIED"}


def validate_intent(intent: dict[str, Any]) -> list[str]:
    missing = sorted(INTENT_FIELDS - intent.keys())
    return [f"missing design-intent field: {field}" for field in missing] + [
        f"design-intent field is empty: {field}"
        for field in sorted(INTENT_FIELDS & intent.keys())
        if not str(intent[field]).strip()
    ]


def validate_capabilities(review: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for index, capability in enumerate(review.get("capabilities", [])):
        prefix = f"capabilities[{index}]"
        for field in ("name", "source", "maturity", "deployment_target", "disposition", "reason"):
            if not str(capability.get(field, "")).strip():
                errors.append(f"{prefix} missing {field}")
        if capability.get("maturity") not in MATURITY:
            errors.append(f"{prefix} has invalid maturity")
        if capability.get("disposition") not in DISPOSITIONS:
            errors.append(f"{prefix} has invalid disposition")
        if capability.get("disposition") == "BLOCKED_BY_DEPLOYMENT_TARGET" and not capability.get("fallback"):
            errors.append(f"{prefix} needs fallback when deployment-target blocked")
    if not review.get("capabilities"):
        errors.append("capability review must contain at least one capability")
    return errors


def validate_evidence(evidence: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not evidence.get("rendered"):
        errors.append("rendered evidence is required")
    if evidence.get("verification") not in EVIDENCE_LEVELS:
        errors.append("verification must distinguish simulator, device, or empirical evidence")
    for field in ("attention_first", "generic_or_distinctive", "remove_next", "critic_findings"):
        if not str(evidence.get(field, "")).strip():
            errors.append(f"evidence missing {field}")
    return errors


def validate(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_intent(record.get("design_intent", {})))
    errors.extend(validate_capabilities(record.get("apple_capability_review", {})))
    errors.extend(validate_evidence(record.get("experience_evidence", {})))
    for key in ("design_debt", "apple_platform_debt"):
        if key not in record or not isinstance(record[key], list):
            errors.append(f"{key} must be a list, including an empty list when none is known")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    record = json.loads(args.record.read_text(encoding="utf-8"))
    errors = validate(record)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Apple experience review passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
