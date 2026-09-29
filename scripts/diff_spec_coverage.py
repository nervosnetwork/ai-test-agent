"""Raw-diff accounting for design review; semantic mapping is still B's judgment."""
from __future__ import annotations

import re

from workflow_lib import digest


def diff_inventory(text: str, source: str) -> list[dict]:
    """Index every hunk, retaining file metadata with the first hunk (or alone)."""
    lines = text.splitlines(keepends=True)
    starts = [i for i, line in enumerate(lines) if line.startswith('diff --git ')]
    if not text.strip():
        return []
    if not starts or starts[0] != 0:
        raise ValueError('expected a complete git unified diff; regenerate raw inputs')
    units = []
    for start, end in zip(starts, starts[1:] + [len(lines)]):
        hunks = [i for i in range(start, end)
                 if re.match(r'^@@ -\d+(?:,\d+)? \+\d+(?:,\d+)? @@', lines[i])]
        # A rename, deletion, binary change or mode-only change remains an indexed unit.
        boundaries = [start] + hunks[1:] + [end]
        for index, (left, right) in enumerate(zip(boundaries, boundaries[1:])):
            content = lines[start] + ''.join(lines[left:right])
            units.append({'change_id': 'DIFF-' + digest(content.encode()),
                          'location': f'{source}:{left + 1}-{right}',
                          'file_header': lines[start].rstrip(),
                          'hunk_header': lines[hunks[index]].rstrip() if hunks else ''})
    return units


def validate_diff_coverage(state: dict, value: dict):
    if 'diff_inventory' not in state or 'all_spec_refs' not in state:
        raise ValueError('missing diff/Spec inventory; prepare and review the design again')
    if 'diff_coverage' not in value:
        raise ValueError('missing diff_coverage; B must review the raw diff, not only existing Cases')
    rows = value['diff_coverage']
    records = {item['change_id']: item for item in rows}
    if len(records) != len(rows):
        raise ValueError('duplicate diff coverage change ID')
    expected = {item['change_id'] for item in state['diff_inventory']}
    if set(records) != expected:
        raise ValueError(f'diff coverage set mismatch: missing={sorted(expected - set(records))}, extra={sorted(set(records) - expected)}')
    finding_ids = {item['finding_id'] for item in value['findings']}
    specs = set(state['all_spec_refs'])
    for change, item in records.items():
        status = item['status']
        if not item['reason'].strip():
            raise ValueError(f'{change}: diff coverage needs a concrete reason')
        if not set(item['spec_refs']).issubset(specs):
            raise ValueError(f'{change}: unknown Spec reference')
        if not set(item['finding_ids']).issubset(finding_ids):
            raise ValueError(f'{change}: unknown diff coverage finding')
        if status == 'mapped':
            if not item['spec_refs']:
                raise ValueError(f'{change}: mapped diff needs Spec references')
        elif status in {'gap', 'unanalysed'}:
            if not item['finding_ids']:
                raise ValueError(f'{change}: incomplete diff coverage needs a B finding')
        elif status in {'no_behavior_change', 'out_of_scope'}:
            if item['spec_refs']:
                raise ValueError(f'{change}: excluded diff must not claim Spec coverage')
        else:
            raise ValueError(f'{change}: invalid diff coverage status')


def require_complete_diff_coverage(value: dict):
    incomplete = [item['change_id'] for item in value['diff_coverage']
                  if item['status'] in {'gap', 'unanalysed'}]
    if incomplete:
        raise ValueError('diff-to-Spec coverage incomplete; update design and obtain B re-review: '
                         + ', '.join(incomplete))
