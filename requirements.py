"""Validate active PRD evidence declarations; never certify evidence authenticity."""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re

HEADING = '## Factory reuse and contribution'
FIELDS = {'id', 'status', 'source', 'artifact_sha256', 'scope', 'limitations',
          'consumer', 'interface', 'evidence', 'gap', 'contribution'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def known(value):
    return text(value) and value.strip().lower() not in ('unknown', 'unverified', 'pending', 'none', 'n/a')


def sha(value):
    return isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value) is not None


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON field: ' + key)
        result[key] = value
    return result


def active_section(document):
    # Recognize our deliberately narrow Markdown format, not rendered examples.
    lines, headings = [], []
    fence = None
    comment = False
    for original in document.splitlines():
        line = original
        if fence is None:
            visible = ''
            while line:
                if comment:
                    end = line.find('-->')
                    if end < 0:
                        line = ''
                    else:
                        comment = False; line = line[end + 3:]
                else:
                    start = line.find('<!--')
                    if start < 0:
                        visible += line; line = ''
                    else:
                        visible += line[:start]; line = line[start + 4:]; comment = True
            line = visible
        boundary = re.fullmatch(r' {0,3}(`{3,}|~{3,})(.*)', line)
        if fence is not None:
            if boundary and boundary[1][0] == fence[0] and len(boundary[1]) >= len(fence) and not boundary[2].strip():
                fence = None
        elif boundary:
            fence = boundary[1]
        elif line.startswith('## '):
            headings.append((len(lines), line))
        lines.append(line)
    selected = [index for index, title in headings if title == HEADING]
    require(len(selected) == 1, 'One active factory reuse and contribution section required')
    start = selected[0]
    end = next((index for index, _ in headings if index > start), len(lines))
    return '\n'.join(lines[start + 1:end])


def json_declarations(section):
    blocks, contents = [], []
    fence = None
    is_json = False
    for line in section.splitlines():
        boundary = re.fullmatch(r' {0,3}(`{3,}|~{3,})(.*)', line)
        if fence is None:
            if boundary:
                fence = boundary[1]; is_json = boundary[2].strip() == 'json'; contents = []
        elif boundary and boundary[1][0] == fence[0] and len(boundary[1]) >= len(fence) and not boundary[2].strip():
            if is_json:
                blocks.append('\n'.join(contents))
            fence = None
        elif is_json:
            contents.append(line)
    require(fence is None, 'Unclosed evidence section fence')
    return blocks


def validate_prd(path):
    path = Path(path)
    document = path.read_text()
    section = active_section(document)
    blocks = json_declarations(section)
    require(len(blocks) == 1, 'One JSON declaration required in factory section')
    value = json.loads(blocks[0], object_pairs_hook=unique_object)
    require(type(value) is dict and set(value) == {'schema_version', 'capabilities'}, 'Invalid requirements fields')
    require(type(value['schema_version']) is int and value['schema_version'] == 1, 'Unsupported requirements version')
    require(type(value['capabilities']) is list and bool(value['capabilities']), 'At least one capability required')
    ids = set()
    for item in value['capabilities']:
        require(type(item) is dict and set(item) == FIELDS, 'Missing or unknown capability fields')
        require(text(item['id']) and item['id'] not in ids, 'Invalid or duplicate capability ID')
        ids.add(item['id'])
        require(item['status'] in ('unknown', 'candidate', 'verified', 'reused'), 'Unsupported capability status')
        source = item['source']
        require(type(source) is dict and set(source) == {'reference', 'revision', 'license', 'attribution'}, 'Invalid source fields')
        require(all(v is None or text(v) for v in source.values()), 'Source fields must be text or null')
        require(item['artifact_sha256'] is None or sha(item['artifact_sha256']), 'Invalid artifact digest')
        require(text(item['scope']) and text(item['gap']), 'Scope and gap disposition required')
        require(type(item['limitations']) is list and bool(item['limitations']) and all(text(x) for x in item['limitations']), 'Explicit limitations required')
        require(all(item[k] is None or text(item[k]) for k in ('consumer', 'interface')), 'Consumer/interface must be text or null')
        contribution = item['contribution']
        require(type(contribution) is dict and set(contribution) == {'change', 'behavior_test'} and all(text(x) for x in contribution.values()), 'Testable contribution or explicit stop disposition required')
        evidence = item['evidence']
        receipt = None
        if evidence is not None:
            require(type(evidence) is dict and set(evidence) == {'path', 'sha256'} and sha(evidence['sha256']), 'Invalid evidence reference')
            relative = evidence['path']
            require(text(relative), 'Relative evidence path required')
            relative = Path(relative)
            require(not relative.is_absolute() and '..' not in relative.parts, 'Evidence must stay beside the PRD')
            root = path.parent.resolve()
            target = root / relative
            require(target.resolve() == target and root in target.parents, 'Evidence symlinks or escaping paths forbidden')
            raw = target.read_bytes()
            require(hashlib.sha256(raw).hexdigest() == evidence['sha256'], 'Evidence digest mismatch')
            receipt = json.loads(raw, object_pairs_hook=unique_object)
            require(type(receipt) is dict and set(receipt) == {'result', 'source', 'recorded_at', 'artifact_sha256', 'scope', 'command', 'environment', 'consumer', 'interface'}, 'Invalid evidence receipt fields')
            require(receipt['source'] == {k: source[k] for k in ('reference', 'revision')}, 'Evidence source mismatch')
            require(text(receipt['recorded_at']), 'Evidence timestamp required')
            require(datetime.fromisoformat(receipt['recorded_at'].replace('Z', '+00:00')).utcoffset() is not None, 'Evidence timestamp must include timezone')
            require(receipt['result'] in ('passed', 'failed', 'not_run'), 'Invalid evidence result')
            require(sha(receipt['artifact_sha256']) and all(text(receipt[k]) for k in ('scope', 'command', 'environment')), 'Receipt identity and execution context required')
            require(all(receipt[k] is None or text(receipt[k]) for k in ('consumer', 'interface')), 'Invalid receipt consumer/interface')
            require(receipt['artifact_sha256'] == item['artifact_sha256'] and receipt['scope'] == item['scope'], 'Evidence artifact or scope mismatch')
        if item['status'] in ('verified', 'reused'):
            require(all(known(source[k]) for k in ('reference', 'revision')), 'Promoted claim requires exact source reference and revision')
            require(receipt is not None and receipt['result'] == 'passed', 'Promoted claim requires a digest-bound passing receipt')
        if item['status'] == 'reused':
            require(all(known(source[k]) for k in ('license', 'attribution')), 'Reuse requires license and attribution')
            require(all(known(item[k]) and receipt[k] == item[k] for k in ('consumer', 'interface')), 'Reuse requires matching consumer and interface evidence')
    return {'status': 'declarations_valid', 'capabilities': len(ids),
            'assurance': 'Structure, evidence bytes and claim consistency only; authenticity, licensing, suitability and approval require review.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('prd', nargs='?', default='PRD.md')
    args = parser.parse_args()
    try:
        print(json.dumps(validate_prd(args.prd)))
    except (ValueError, OSError, TypeError, KeyError) as exc:
        parser.exit(1, 'Requirements rejected: ' + str(exc) + '\n')
