"""Fail-closed validator for the repository-owned Rubberduck ledger."""
import json
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LEDGER = ROOT / "docs" / "rubberduck-research-2026-09-26.json"
REPORT = ROOT / "docs" / "rubberduck-research-2026-09-26.md"
GATES = {"ai_essential", "independent_demand", "two_week_test", "distribution", "recurrence", "economics", "defensibility", "risk", "validation_design"}
DISPOSITIONS = {"INVESTIGATE NOW", "WATCH", "REJECT"}
DATE = re.compile(r"\d{4}-\d{2}-\d{2}\Z")
ECONOMICS = {"workload_assumptions", "model_calls", "infrastructure_calls", "human_review_exposure", "cost_range", "pricing_hypothesis", "gross_margin_risks", "cheaper_fallback"}
SOURCE_FIELDS = {"id", "title", "publisher", "published_at", "accessed_at", "url"}
RECEIPT_FIELDS = {"available", "command", "captured_at", "git_revision", "dirty", "doctor_ready", "write_ready", "launch_ready", "policy_status", "routing_contradictions", "errors", "source"}
APPROVED_PASS_ASSERTIONS = {}
APPROVED_RECEIPTS = {
    "pre": {
        "available": True,
        "command": "bin/factory-dev doctor",
        "captured_at": "2026-09-26",
        "git_revision": "0eb7484bb34c07a750761cdce9959d083ef68773",
        "dirty": False,
        "doctor_ready": True,
        "write_ready": True,
        "launch_ready": True,
        "policy_status": "valid",
        "routing_contradictions": [],
        "errors": [],
        "source": "docs/issue-intents/113/rubberduck-gates-progress.md",
    },
    "post": {
        "available": True,
        "command": "bin/factory-dev doctor",
        "captured_at": "2026-09-26",
        "git_revision": "0eb7484bb34c07a750761cdce9959d083ef68773",
        "dirty": True,
        "doctor_ready": True,
        "write_ready": False,
        "launch_ready": False,
        "policy_status": "valid",
        "routing_contradictions": [],
        "errors": [],
        "source": "docs/issue-intents/113/rubberduck-gates-progress.md",
    },
}


def load_json(path):
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise ValueError(f"duplicate JSON key: {key}")
            value[key] = item
        return value
    return json.loads(Path(path).read_text(), object_pairs_hook=pairs)


def fail(message):
    raise ValueError(message)


def git(args):
    result = subprocess.run(
        ["/usr/bin/git", *args], cwd=ROOT, text=True, capture_output=True, check=False,
        env={"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null"},
    )
    return result


def revision_exists(revision):
    return git(["cat-file", "-e", f"{revision}^{{commit}}"]).returncode == 0


def repository_head():
    result = git(["rev-parse", "HEAD"])
    if result.returncode != 0 or not re.fullmatch(r"[0-9a-f]{40}", result.stdout.strip()):
        fail("repository HEAD is unavailable")
    return result.stdout.strip()


def validate_policy_manifest():
    source = ROOT / "development" / "opencode"
    manifest = load_json(source / "policy-manifest.json")
    if set(manifest) != {"schema_version", "files"} or manifest["schema_version"] != 1 or not isinstance(manifest["files"], dict):
        fail("policy manifest schema is invalid")
    actual = {
        path.relative_to(source).as_posix()
        for path in source.rglob("*")
        if path.is_file() and "node_modules" not in path.relative_to(source).parts and path.name != "policy-manifest.json"
    }
    if actual != set(manifest["files"]):
        fail("policy manifest inventory does not match policy source")
    for relative, expected in manifest["files"].items():
        path = source / relative
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if not re.fullmatch(r"[0-9a-f]{64}", expected) or digest != expected:
            fail(f"policy manifest digest mismatch: {relative}")


def valid_evidence(evidence, sources, state, candidate_id, gate_id):
    if not isinstance(evidence, list) or not evidence or any(not isinstance(item, str) or not item for item in evidence):
        fail("gate evidence is missing")
    unknown = [item for item in evidence if item.startswith("UNKNOWN:") and len(item) > len("UNKNOWN:")]
    bound = []
    for item in evidence:
        if item in unknown:
            continue
        source_id, separator, claim = item.partition(": ")
        if not separator or source_id not in sources or not claim.startswith(f"{gate_id}: "):
            fail("gate evidence is not a source-bound assertion")
        bound.append(source_id)
    if state == "PASS" and unknown:
        fail("PASS cannot cite UNKNOWN evidence")
    if state == "PASS" and (not bound or any(sources[source_id]["published_at"] == "undated" for source_id in bound)):
        fail("PASS requires published, source-bound evidence")
    if state == "PASS":
        assertions = frozenset(
            (item.partition(": ")[0], item.partition(": ")[2])
            for item in evidence
        )
        if APPROVED_PASS_ASSERTIONS.get((candidate_id, gate_id)) != assertions:
            fail(f"PASS evidence is not validator-approved for {candidate_id}:{gate_id}")
    if state == "MISSING" and not unknown:
        fail("MISSING requires an UNKNOWN explanation")


def validate_receipt(name, receipt, as_of):
    if not isinstance(receipt, dict):
        fail(f"{name} receipt must be an object")
    if set(receipt) != RECEIPT_FIELDS:
        fail(f"{name} receipt schema is not closed")
    if receipt["command"] != "bin/factory-dev doctor" or not receipt["source"]:
        fail(f"{name} receipt identity is invalid")
    if receipt["available"]:
        for field in ("available", "dirty", "doctor_ready", "write_ready", "launch_ready"):
            if type(receipt[field]) is not bool:
                fail(f"{name} receipt {field} must be boolean")
        if not receipt["captured_at"] or not DATE.fullmatch(receipt["captured_at"]) or receipt["captured_at"] != as_of:
            fail(f"{name} receipt capture date is invalid")
        if not isinstance(receipt["git_revision"], str) or not re.fullmatch(r"[0-9a-f]{40}", receipt["git_revision"]) or not revision_exists(receipt["git_revision"]):
            fail(f"{name} receipt revision is missing")
        if not isinstance(receipt["routing_contradictions"], list) or not isinstance(receipt["errors"], list):
            fail(f"{name} receipt diagnostics must be arrays")
        if receipt["policy_status"] != "valid" or receipt["routing_contradictions"] or receipt["errors"] or not receipt["doctor_ready"]:
            fail(f"{name} doctor receipt is failed")
        if name == "pre" and (receipt["dirty"] or not receipt["write_ready"] or not receipt["launch_ready"]):
            fail("pre receipt is not clean and ready")
        if name == "post" and not receipt["dirty"]:
            fail("post receipt must represent expected dirty state")
        progress = ROOT / "docs" / "issue-intents" / "113" / "rubberduck-gates-progress.md"
        if receipt["source"] != "docs/issue-intents/113/rubberduck-gates-progress.md" or receipt["git_revision"] not in progress.read_text():
            fail(f"{name} receipt is not bound to the progress record")
    elif name == "post":
        fail("post doctor receipt is unavailable")
    else:
        fail("pre doctor receipt is unavailable")
    approved = APPROVED_RECEIPTS[name]
    if approved is None or receipt != approved:
        fail(f"{name} doctor receipt is not validator-approved")


def validate(ledger_path=LEDGER, report_path=REPORT):
    ledger = load_json(ledger_path)
    report = Path(report_path).read_text()
    root_fields = {"schema_version", "report_file", "as_of", "mandatory_gates", "sources", "candidates", "receipts"}
    if set(ledger) != root_fields or ledger["schema_version"] != 1 or ledger["report_file"] != "docs/rubberduck-research-2026-09-26.md":
        fail("ledger schema or identity is invalid")
    if not isinstance(ledger["as_of"], str) or not DATE.fullmatch(ledger["as_of"]):
        fail("ledger as-of date is invalid")
    gates = ledger["mandatory_gates"]
    if not isinstance(gates, list) or any(not isinstance(item, dict) for item in gates):
        fail("mandatory gates are not the fixed nine-gate set")
    if len(gates) != len(GATES) or {item.get("id") for item in gates} != GATES or any(set(item) != {"id", "label"} or not isinstance(item["label"], str) or not item["label"] for item in gates):
        fail("mandatory gates are not the fixed nine-gate set")

    if not isinstance(ledger["sources"], list) or not ledger["sources"]:
        fail("sources must be a nonempty array")
    sources = {}
    for source in ledger["sources"]:
        if not isinstance(source, dict) or set(source) != SOURCE_FIELDS or source["id"] in sources or not all(isinstance(source[key], str) and source[key] for key in SOURCE_FIELDS):
            fail("source is missing, malformed, or duplicated")
        if not source["url"].startswith("https://") or source["accessed_at"] != ledger["as_of"]:
            fail("source URL or accessed date is invalid")
        if source["published_at"] != "undated" and not DATE.fullmatch(source["published_at"]):
            fail("source publication date is invalid")
        sources[source["id"]] = source

    candidates = ledger["candidates"]
    if not isinstance(candidates, list) or not candidates:
        fail("candidates must be a nonempty array")
    candidate_ids = set()
    dispositions = []
    for candidate in candidates:
        base = {"id", "title", "report_section", "disposition", "gates"}
        if not isinstance(candidate, dict) or not base.issubset(candidate) or set(candidate) - (base | {"unit_economics"}) or candidate["id"] in candidate_ids:
            fail("candidate schema is not closed or candidate is duplicated")
        if any(not isinstance(candidate[key], str) or not candidate[key] for key in ("id", "title", "report_section", "disposition")):
            fail("candidate identity fields must be nonempty strings")
        candidate_ids.add(candidate["id"])
        if candidate["report_section"] != candidate["id"]:
            fail(f"report_section must equal candidate id: {candidate['id']}")
        disposition = candidate["disposition"]
        dispositions.append(disposition)
        if disposition not in DISPOSITIONS or not isinstance(candidate["gates"], dict) or set(candidate["gates"]) != GATES:
            fail(f"invalid disposition or gate set: {candidate['id']}")
        states = []
        for gate_id, gate in candidate["gates"].items():
            if not isinstance(gate, dict) or set(gate) != {"state", "evidence"} or gate["state"] not in {"PASS", "MISSING", "FAIL"}:
                fail(f"gate schema is invalid: {candidate['id']}:{gate_id}")
            valid_evidence(gate["evidence"], sources, gate["state"], candidate["id"], gate_id)
            states.append(gate["state"])
        if disposition == "INVESTIGATE NOW" and states != ["PASS"] * len(GATES):
            fail(f"investigate-now candidate lacks all passes: {candidate['id']}")
        if disposition == "WATCH" and ("FAIL" in states or "MISSING" not in states):
            fail(f"watch candidate has invalid gate states: {candidate['id']}")
        if disposition == "REJECT" and "FAIL" not in states:
            fail(f"reject candidate lacks a failed gate: {candidate['id']}")
        if disposition != "REJECT":
            economics = candidate.get("unit_economics", {})
            if not isinstance(economics, dict) or set(economics) != ECONOMICS or any(not isinstance(economics[key], str) or not economics[key] for key in ECONOMICS):
                fail(f"unit economics is incomplete: {candidate['id']}")
        elif "unit_economics" in candidate:
            fail(f"rejected candidate has unit economics: {candidate['id']}")

    section_order = ["INVESTIGATE NOW", "WATCH", "REJECT"]
    headings = re.findall(r"^## (INVESTIGATE NOW|WATCH|REJECT)$", report, re.MULTILINE)
    if headings != section_order:
        fail("report disposition headings are missing or duplicated")
    candidate_headings = re.findall(r"^### Candidate: ([^\n]+)$", report, re.MULTILINE)
    expected_candidate_order = [candidate["id"] for candidate in candidates]
    if candidate_headings != expected_candidate_order:
        fail("report candidates and ledger candidates do not match")
    occurrences = {candidate_id: 0 for candidate_id in candidate_ids}
    current_disposition = None
    candidate_dispositions = {}
    for line in report.splitlines():
        if line.startswith("## "):
            current_disposition = line[3:]
        match = re.fullmatch(r"### Candidate: (.+)", line)
        if match:
            candidate_dispositions[match.group(1)] = current_disposition
            occurrences[match.group(1)] += 1
    for candidate in candidates:
        if occurrences[candidate["id"]] != 1 or candidate_dispositions[candidate["id"]] != candidate["disposition"]:
            fail(f"candidate section or disposition mismatch: {candidate['id']}")
        marker = f"### Candidate: {candidate['id']}\n"
        body = report.split(marker, 1)[1]
        body = re.split(r"\n(?:### Candidate:|## )", body, maxsplit=1)[0]
        if body.count(f"Disposition: {candidate['disposition']}") != 1:
            fail(f"candidate disposition text mismatch: {candidate['id']}")
    investigate_body = report.split("## INVESTIGATE NOW\n", 1)[1].split("\n## WATCH", 1)[0].strip()
    if not any(disposition == "INVESTIGATE NOW" for disposition in dispositions) and investigate_body != "No candidate is INVESTIGATE NOW.":
        fail("no-candidate sentence is absent or not exact")
    if any(disposition == "INVESTIGATE NOW" for disposition in dispositions) and "No candidate is INVESTIGATE NOW." in investigate_body:
        fail("investigate section contradicts its candidates")

    claim_pattern = re.compile(r"^- (FACT|INFERENCE|HYPOTHESIS|UNKNOWN) \[([^\]]+)\]: (.+)$")
    for line in (line for line in report.splitlines() if line.startswith("- ")):
        match = claim_pattern.fullmatch(line)
        if not match:
            fail(f"report claim is not mechanically classified: {line}")
        classification, references, statement = match.groups()
        reference_ids = [item.strip() for item in references.split(",")]
        if not statement or any(not item for item in reference_ids):
            fail("report claim is empty")
        if classification != "UNKNOWN" and reference_ids == ["none"]:
            fail(f"{classification} claim requires a source")
        if any(item != "none" and item not in sources for item in reference_ids):
            fail("report claim cites an unknown source")

    receipts = ledger["receipts"]
    if not isinstance(receipts, dict) or set(receipts) != {"pre", "post"}:
        fail("receipt pair is incomplete")
    validate_receipt("pre", receipts["pre"], ledger["as_of"])
    validate_receipt("post", receipts["post"], ledger["as_of"])
    validate_policy_manifest()
    return True


if __name__ == "__main__":
    try:
        args = sys.argv[1:]
        if len(args) not in {0, 2}:
            raise ValueError("usage: validate_rubberduck.py [LEDGER REPORT]")
        validate(*(args or (LEDGER, REPORT)))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"INVALID: {error}", file=sys.stderr)
        raise SystemExit(1)
    print("VALID")
