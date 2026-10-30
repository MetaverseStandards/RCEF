#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Render readable reports from generated/rcef.pack.json, or by default check that they are current.

This script only presents the pack. The shared checker and the tests check
the authoring and the runtime behaviour.
"""
import argparse
from collections import Counter
import csv
import hashlib
import html
import io
import json
import math
import os
from pathlib import Path
import secrets
import stat
import sys


MAX_FILE_BYTES = 16 * 1024 * 1024
MAX_OUTPUT_BYTES = 64 * 1024 * 1024
DISPOSITIONS = {'mapped', 'unresolved', 'excluded', 'unsupported'}


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False,
                      separators=(',', ':'))


def _plain(value):
    if value is None:
        return ''
    if isinstance(value, (list, dict, bool)):
        return _json(value)
    return str(value)


def _cell(value):
    return html.escape(_plain(value), quote=False).replace('\\', '\\\\').replace('|', '\\|').replace(
        '\r\n', '\n').replace('\r', '\n').replace('\n', '<br>')


def _table(columns, rows):
    lines = ['| ' + ' | '.join(_cell(c) for c in columns) + ' |',
             '| ' + ' | '.join('---' for _ in columns) + ' |']
    lines.extend('| ' + ' | '.join(_cell(c) for c in row) + ' |' for row in rows)
    return '\n'.join(lines) + '\n'


def _csv(columns, rows):
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(columns)
    writer.writerows([_plain(cell) for cell in row] for row in rows)
    return stream.getvalue()


def _unique(rows, kind):
    result = {}
    if not isinstance(rows, list):
        raise ValueError(f'{kind} must be an array')
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get('id'), str) or not row['id']:
            raise ValueError(f'{kind} requires nonempty string IDs')
        if row['id'] in result:
            raise ValueError(f'duplicate {kind} ID: {row["id"]}')
        result[row['id']] = row
    return result


def _references(value, known, kind):
    if not isinstance(value, list) or any(not isinstance(x, str) or x not in known for x in value):
        raise ValueError(f'unknown or malformed {kind} reference')
    if len(set(value)) != len(value):
        raise ValueError(f'duplicate {kind} reference')
    return value


def _number(value):
    return f'{value:g}'


def _formula(rule, signals):
    """The rule as plain arithmetic over short signal names, e.g. y = 0.5·L + 0.5·R."""
    def name(sid):
        return signals[sid].get('native_id') or sid.rsplit('.', 1)[-1]
    operator, inputs = rule['operator'], [name(sid) for sid in rule['inputs']]
    if operator['id'] == 'identity':
        terms = inputs[0]
    elif operator['id'] == 'affine':
        terms = f'{_number(operator["scale"])}·{inputs[0]}'
        if operator['offset']:
            terms += f' + {_number(operator["offset"])}'
    elif operator['id'] == 'weighted_sum':
        terms = ' + '.join(f'{_number(w)}·{x}' for w, x in zip(operator['weights'], inputs))
    else:
        terms = _json(operator)
    return f'{name(rule["outputs"][0])} = {terms}'


def _decode(raw):
    def pairs(items):
        value = {}
        for key, child in items:
            if key in value:
                raise ValueError(f'duplicate JSON key: {key}')
            value[key] = child
        return value

    def finite(token):
        value = float(token)
        if not math.isfinite(value):
            raise ValueError('nonfinite number in pack')
        return value

    def constant(_):
        raise ValueError('nonfinite number in pack')

    pack = json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                      parse_float=finite, parse_constant=constant)
    if not isinstance(pack, dict) or not all(isinstance(pack.get(k), str)
                                             for k in ('id', 'license', 'data_version')):
        raise ValueError('pack requires id, license and data_version')
    signals = _unique(pack.get('signals'), 'signal')
    profiles = _unique(pack.get('profiles'), 'profile')
    mappings = _unique(pack.get('mappings'), 'mapping')
    evidence = _unique(pack.get('evidence'), 'evidence')
    for signal in signals.values():
        if signal.get('disposition') not in DISPOSITIONS:
            raise ValueError('unknown signal disposition')
        for key in ('label', 'units', 'calibration', 'evidence_status'):
            if not isinstance(signal.get(key), str):
                raise ValueError(f'signal requires string {key}')
        if not isinstance(signal.get('metadata', {}), dict) or not isinstance(signal.get('domain'), dict):
            raise ValueError('signal metadata and domain must be objects')
        _references(signal.get('evidence', []), evidence, 'evidence')
    for profile in profiles.values():
        if not isinstance(profile.get('label'), str):
            raise ValueError('profile requires a label')
        _references(profile.get('signal_ids'), signals, 'signal')
    rule_ids = set()
    for mapping in mappings.values():
        rules = _unique(mapping.get('rules'), 'rule')
        for rule in rules.values():
            if rule['id'] in rule_ids:
                raise ValueError('duplicate rule ID across mappings')
            rule_ids.add(rule['id'])
            _references(rule.get('inputs'), signals, 'input')
            _references(rule.get('outputs'), signals, 'output')
            _references(rule.get('evidence', []), evidence, 'evidence')
            if rule.get('disposition') not in DISPOSITIONS:
                raise ValueError('unknown rule disposition')
            if not isinstance(rule.get('operator'), dict) or not isinstance(rule['operator'].get('id'), str):
                raise ValueError('rule requires an operator')
    return pack, signals, profiles, mappings


def render(raw):
    pack, signals, profiles, mappings = _decode(raw)
    source_hash = hashlib.sha256(raw).hexdigest()
    notice = (f'Pack: {_cell(pack["id"])}; data version: {_cell(pack["data_version"])}.\n\n'
              f'Generated from rcef.pack.json; SHA-256: {source_hash}.\n\n'
              f'Original RCEF data and arrangement: RCEF contributors (2026), '
              f'{_cell(pack["license"])}. Provider attribution and source terms '
              'are in ../THIRD_PARTY_NOTICES.md.\n\n')
    memberships = []
    assigned = set()
    for profile in profiles.values():
        for ordinal, sid in enumerate(profile['signal_ids']):
            memberships.append((profile, ordinal, signals[sid]))
            assigned.add(sid)
    memberships.extend((None, None, signal) for sid, signal in signals.items() if sid not in assigned)
    columns = ['profile_id', 'profile_label', 'ordinal', 'signal_id', 'native_id', 'label',
               'native_index', 'region', 'side', 'units', 'minimum', 'maximum', 'neutral',
               'native_default', 'disposition', 'evidence_status', 'calibration', 'reason',
               'definition', 'evidence_ids', 'metadata_json', 'context_json']
    inventory = []
    for profile, ordinal, signal in memberships:
        metadata = signal.get('metadata', {})
        context = {k: v for k, v in signal.items() if k not in {
            'id', 'native_id', 'label', 'region', 'side', 'units', 'domain', 'neutral',
            'native_default', 'disposition', 'evidence_status', 'calibration', 'evidence', 'metadata'}}
        inventory.append([profile['id'] if profile else '', profile['label'] if profile else '',
                          ordinal, signal['id'], signal.get('native_id'), signal['label'],
                          metadata.get('native_index'), signal.get('region'), signal.get('side'),
                          signal['units'], signal['domain'].get('min'), signal['domain'].get('max'),
                          signal.get('neutral'), signal.get('native_default'), signal['disposition'],
                          signal['evidence_status'], signal['calibration'], metadata.get('reason'),
                          metadata.get('definition'), signal.get('evidence', []), metadata, context])
    text = '# RCEF expression inventory\n\n' + notice
    text += (f'{len(signals)} distinct signals; {len(profiles)} profiles; '
             f'{len(memberships)} inventory rows (one per profile membership, plus unassigned signals).\n\n'
             'Native defaults and calibrated neutral values are kept separate. A blank CSV value is absent '
             'from the pack. An unknown range stays unknown. Status describes the authored record.\n\n')
    summary = []
    for profile in profiles.values():
        counts = Counter(signals[sid]['disposition'] for sid in profile['signal_ids'])
        summary.append([profile['id'], profile['label'], len(profile['signal_ids']),
                        counts['mapped'], counts['unresolved'], counts['excluded'], counts['unsupported']])
    text += _table(['Profile', 'Description', 'Signals', 'Mapped', 'Unresolved', 'Excluded', 'Unsupported'], summary)
    groups = list(profiles.values()) + ([None] if len(assigned) < len(signals) else [])
    for profile in groups:
        heading = f'{profile["id"]}: {profile["label"]}' if profile else 'Unassigned inventory records'
        text += '\n## ' + _cell(heading) + '\n\n'
        rows = []
        for current, _, signal in memberships:
            if current is not profile:
                continue
            metadata = signal.get('metadata', {})
            domain = signal['domain']
            bounds = f'{domain.get("min", "unknown")} to {domain.get("max", "unknown")}' if domain else 'unknown'
            notes = [metadata.get('reason', ''), metadata.get('definition', ''),
                     'Calibration: ' + signal['calibration']]
            for key, label in [('neutral', 'Neutral'), ('native_default', 'Native default')]:
                if key in signal:
                    notes.append(label + ': ' + _plain(signal[key]))
            notes.append('Evidence: ' + ', '.join(signal.get('evidence', [])))
            name = signal['label']
            if signal.get('native_id') and signal['native_id'] != signal['label']:
                name += '\nNative: ' + signal['native_id']
            rows.append([signal['id'], name, metadata.get('native_index'),
                         signal.get('side'), signal['units'], bounds, signal['disposition'],
                         '\n'.join(x for x in notes if x)])
        text += _table(['Signal', 'Name', 'Native index', 'Side', 'Units', 'Native range', 'Status', 'Notes'], rows)
    rule_columns = ['mapping_id', 'rule_id', 'inputs', 'outputs', 'operator', 'disposition',
                    'mapping_quality', 'assumptions', 'loss_annotations', 'evidence_ids']
    rule_rows = []
    rules_by_output = {}
    mapping_text = '# RCEF authored mappings\n\n' + notice
    mapping_text += ('Each mapping keeps its declared direction, status, assumptions and losses. '
                     'An unresolved mapping is an inventory record. It cannot be executed.\n\n')
    member_of = {}
    for profile in profiles.values():
        for sid in profile['signal_ids']:
            member_of.setdefault(sid, profile['id'])

    def sides(sids):
        return ' + '.join(dict.fromkeys(member_of.get(sid, 'unassigned') for sid in sids))
    proposed = [[mapping['id'], rule['id'], f'{sides(rule["inputs"])} → {sides(rule["outputs"])}',
                 _formula(rule, signals), '; '.join(x['reason'] for x in rule.get('loss_annotations', [])),
                 rule['evidence_status']]
                for mapping in mappings.values() for rule in mapping['rules']
                if rule.get('evidence_status') == 'proposed']
    if proposed:
        mapping_text += ('## Proposed rules\n\n'
                         'Proposed mappings translate between providers. Each formula assumes the calibration '
                         'stated with its mapping below. Losses list what the translation cannot carry.\n\n')
        mapping_text += _table(['Map', 'Mapping', 'Source → target', 'Formula', 'Losses', 'Evidence status'],
                               proposed) + '\n'
    for mapping in mappings.values():
        mapping_text += '## ' + _cell(mapping['id']) + '\n\n'
        for rule in mapping['rules']:
            rule_rows.append([mapping['id'], rule['id'], rule['inputs'], rule['outputs'], rule['operator'],
                              rule['disposition'], rule.get('mapping_quality'), rule.get('assumptions', []),
                              rule.get('loss_annotations', []), rule.get('evidence', [])])
            for sid in rule['outputs']:
                rules_by_output.setdefault(sid, []).append(rule)
            mapping_text += ('### ' + _cell(rule['id']) + '\n\n' +
                             _table(['Inputs', 'Outputs', 'Operator', 'Status', 'Quality'],
                                    [[', '.join(rule['inputs']), ', '.join(rule['outputs']), rule['operator'],
                                      rule['disposition'], rule.get('mapping_quality', 'not declared')]]) + '\n')
            mapping_text += 'Assumptions:\n\n' + ''.join('- ' + _cell(x) + '\n' for x in rule.get('assumptions', []))
            mapping_text += '\nLoss annotations: ' + _cell(rule.get('loss_annotations', [])) + '\n\n'
            mapping_text += 'Evidence: ' + _cell(', '.join(rule.get('evidence', []))) + '\n\n'
    canonical = [profiles[c] for c in ('rcef.canonical_expression', 'rcef.canonical_viseme') if c in profiles]
    other_profiles = [p for p in profiles.values() if p not in canonical]
    wide_columns = ['canonical_id', 'label', 'units', 'disposition', *[p['id'] for p in other_profiles]]
    wide_rows = []
    correspondence_text = '# RCEF canonical correspondences\n\n' + notice
    correspondence_text += ('Each signal of the canonical expression and viseme sets, with the authored mappings that '
                            'write it from each other profile. Only authored mappings appear here. A dash means no '
                            'authored mapping. '
                            'Unresolved mappings stay labeled unresolved. A mapping with the `mapped` disposition keeps '
                            'its declared provider basis. It does not show cross-provider or anatomical equality.\n\n')
    for sid in [sid for profile in canonical for sid in profile['signal_ids']]:
        signal = signals[sid]
        row = [sid, signal['label'], signal['units'], signal['disposition']]
        details = []
        for profile in other_profiles:
            members = set(profile['signal_ids'])
            cells = []
            for rule in rules_by_output.get(sid, []):
                if any(x in members for x in rule['inputs']):
                    inputs = [signals[x].get('native_id') or signals[x]['label'] for x in rule['inputs']]
                    cell = (' + '.join(inputs) + f' [{rule["id"]}; {rule["operator"]["id"]}; '
                            f'{rule["disposition"]}; {rule.get("mapping_quality", "quality not declared")}]')
                    cells.append(cell)
                    details.append([profile['id'], cell])
            row.append('; '.join(cells) if cells else '-')
        wide_rows.append(row)
        correspondence_text += '## ' + _cell(signal['label']) + '\n\n' + _cell(sid) + '\n\n'
        correspondence_text += _table(['Profile', 'Authored relationship'], details) if details else 'No authored mapping.\n'
        correspondence_text += '\n'
    outputs = {'inventory.csv': _csv(columns, inventory), 'inventory.md': text,
               'mappings.csv': _csv(rule_columns, rule_rows), 'mappings.md': mapping_text,
               'canonical_correspondence.csv': _csv(wide_columns, wide_rows),
               'canonical_correspondence.md': correspondence_text}
    encoded = {name: value.encode('utf-8') for name, value in outputs.items()}
    if any(len(value) > MAX_FILE_BYTES for value in encoded.values()) or sum(map(len, encoded.values())) > MAX_OUTPUT_BYTES:
        raise ValueError('readable report output exceeds presentation bounds')
    encoded['SHA256SUMS'] = ''.join(f'{hashlib.sha256(encoded[name]).hexdigest()}  {name}\n'
                                   for name in sorted(encoded)).encode('ascii')
    return encoded


def _endpoint(info):
    return info.st_dev, info.st_ino, info.st_mode, info.st_size, info.st_mtime_ns, info.st_ctime_ns


def _read_at(directory, name):
    fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_FILE_BYTES:
            raise ValueError('report input/output must be a bounded regular file')
        blocks = []
        count = 0
        while chunk := os.read(fd, min(65536, before.st_size - count + 1)):
            count += len(chunk)
            if count > before.st_size:
                raise ValueError('report file changed during read')
            blocks.append(chunk)
        if count != before.st_size or _endpoint(before) != _endpoint(os.fstat(fd)) or _endpoint(before) != _endpoint(
                os.stat(name, dir_fd=directory, follow_symlinks=False)):
            raise ValueError('report file changed during read')
        return b''.join(blocks), before
    finally:
        os.close(fd)


def _leaf(directory, name, source):
    try:
        info = os.stat(name, dir_fd=directory, follow_symlinks=False)
    except FileNotFoundError:
        return
    if not stat.S_ISREG(info.st_mode):
        raise ValueError('report output must be a regular file, without symlinks')
    if (info.st_dev, info.st_ino) == (source.st_dev, source.st_ino):
        raise ValueError('report output aliases the source pack')


def export(root, write=False):
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    root_fd = os.open(root, flags)
    try:
        generated = os.open('generated', flags, dir_fd=root_fd)
        try:
            raw, source = _read_at(generated, 'rcef.pack.json')
            outputs = render(raw)
            if _endpoint(source) != _endpoint(os.stat('rcef.pack.json', dir_fd=generated, follow_symlinks=False)):
                raise ValueError('pack changed during rendering')
            try:
                output_fd = os.open('reports', flags, dir_fd=root_fd)
            except FileNotFoundError:
                if not write:
                    return sorted(outputs)
                os.mkdir('reports', dir_fd=root_fd)
                output_fd = os.open('reports', flags, dir_fd=root_fd)
            try:
                for name in outputs:
                    _leaf(output_fd, name, source)
                drift = []
                for name, data in outputs.items():
                    try:
                        current, _ = _read_at(output_fd, name)
                    except FileNotFoundError:
                        current = None
                    if current != data:
                        drift.append(name)
                    if not write or current == data:
                        continue
                    temporary = '.report-' + secrets.token_hex(12)
                    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                                 0o644, dir_fd=output_fd)
                    try:
                        with os.fdopen(fd, 'wb') as stream:
                            stream.write(data)
                            stream.flush()
                            os.fsync(stream.fileno())
                        _leaf(output_fd, name, source)
                        os.replace(temporary, name, src_dir_fd=output_fd, dst_dir_fd=output_fd)
                    finally:
                        try:
                            os.unlink(temporary, dir_fd=output_fd)
                        except FileNotFoundError:
                            pass
                return [] if write else drift
            finally:
                os.close(output_fd)
        finally:
            os.close(generated)
    finally:
        os.close(root_fd)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--write', action='store_true', help='regenerate readable reports')
    args = parser.parse_args()
    try:
        drift = export(args.root, args.write)
        if drift:
            print('Readable report drift: ' + ', '.join(drift), file=sys.stderr)
            return 1
        print('Readable reports ' + ('written.' if args.write else 'match.'))
        return 0
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        print('Readable report error: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
