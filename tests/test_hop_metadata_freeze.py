# SPDX-License-Identifier: MIT
"""The metadata of every hop signal, except its reason, is as in the B pack of the latest passing A/B freeze.

Definitions, zero and one, FACS codes, aligned names and the viseme validity fields are metadata, and a change
to any of them needs a "revise" freeze first (ab/README.md). tests/test_pivot_structure.py freezes the rest of
each signal record; this file freezes its metadata, from tests/fixtures/b-maps-ab.pivot-v4.json.
"""
import hashlib
import json
from pathlib import Path
import unittest

try:
    import shared_pack
except ModuleNotFoundError:  # run by file path from the repository root
    from tests import shared_pack

ROOT = Path(__file__).resolve().parents[1]


def metadata_digests(document: dict, signal_ids) -> dict:
    signals = {s['id']: s for s in document['signals']}
    return {sid: hashlib.sha256(json.dumps({k: v for k, v in signals[sid].get('metadata', {}).items() if k != 'reason'},
                                           sort_keys=True, separators=(',', ':'), ensure_ascii=False)
                                .encode('utf-8')).hexdigest() for sid in signal_ids}


class HopMetadataFreeze(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen = json.loads((ROOT / 'tests/fixtures/b-maps-ab.pivot-v4.json').read_text(encoding='utf-8'))

    def test_every_hop_signal_has_a_frozen_metadata_digest(self):
        self.assertEqual(set(self.frozen['signal_metadata']), set(self.frozen['signals']))

    def test_the_pack_keeps_the_metadata_of_every_hop_signal(self):
        self.assertEqual(metadata_digests(shared_pack.document(), self.frozen['signal_metadata']),
                         self.frozen['signal_metadata'])

    def test_the_registered_pack_has_the_frozen_metadata(self):
        registered = shared_pack.registered_pack(self.frozen['registration'])
        if registered is None:
            self.skipTest('no Git history for the registered pack')
        self.assertEqual(metadata_digests(registered, self.frozen['signal_metadata']), self.frozen['signal_metadata'])


if __name__ == '__main__':
    unittest.main()
