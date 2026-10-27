# SPDX-License-Identifier: MIT
"""Rig naming and the face pipeline's weight oracles on rigs with all 52 ARKit shapes (no mesh needed)."""
from pathlib import Path
import sys
import unittest

try:
    import shared_pack
except ModuleNotFoundError:  # run by file path from the repository root
    from tests import shared_pack

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'examples'))
import face_pipeline  # noqa: E402
import ict_facekit  # noqa: E402
import rcef_translate  # noqa: E402
import rigs  # noqa: E402
import vrm_presets  # noqa: E402

ARKIT_52 = list(face_pipeline.source_routes())
ROCKETBOX_LIKE = ([f'AA_VI_{i:02d}_{n}' for i, n in enumerate(rigs.ROCKETBOX_VISEMES)]
                  + [f'AK_{i + 1:02d}_{a[0].upper()}{a[1:]}' for i, a in enumerate(ARKIT_52)]
                  + ['AU_01_InnerBrowRaiser', 'AU_02_L_OuterBrowRaiser', 'AU_02_OuterBrowRaiser',
                     'AU_02_R_OuterBrowRaiser', 'AU_14_Dimpler', 'AU_43_L_EyeClosed', 'AU_43_R_EyeClosed', '_Neutral'])


def compiled():
    return {m: shared_pack.mapping(m, 'openxr.fb2', 'arkit.coefficient') for m in ('fb2.to_arkit', 'fb2_gaze.to_arkit')}


class RigNames(unittest.TestCase):
    def test_rocketbox_arkit_names_become_apple_names(self):
        arkit = rigs.rocketbox_arkit(ROCKETBOX_LIKE)
        self.assertEqual(sorted(arkit.values()), sorted(ARKIT_52))
        self.assertEqual(ROCKETBOX_LIKE[next(i for i, a in arkit.items() if a == 'eyeBlinkLeft')], 'AK_09_EyeBlinkLeft')

    def test_rocketbox_visemes_follow_the_meta_order(self):
        visemes = rigs.rocketbox_visemes(ROCKETBOX_LIKE)
        self.assertEqual(list(visemes), rigs.META_VISEME_ORDER)
        self.assertEqual(ROCKETBOX_LIKE[visemes['IH']], 'AA_VI_12_I')
        with self.assertRaises(SystemExit):
            rigs.rocketbox_visemes(['AA_VI_03_PP'])

    def test_facs_shapes_by_au_and_side(self):
        names = ROCKETBOX_LIKE
        self.assertEqual([names[i] for i in rigs.facs_targets(names, '2')], ['AU_02_OuterBrowRaiser'])
        self.assertEqual([names[i] for i in rigs.facs_targets(names, 'R2')], ['AU_02_R_OuterBrowRaiser'])
        self.assertEqual([names[i] for i in rigs.facs_targets(names, '43')], ['AU_43_L_EyeClosed', 'AU_43_R_EyeClosed'])
        self.assertIsNone(rigs.facs_targets(names, 'R14'))
        self.assertIsNone(rigs.facs_targets(names, '30'))

    def test_ict_shapes_name_their_arkit_coefficient_and_halves(self):
        shapes = {ict_facekit.SHAPES[i]: (a, side) for i, a, side in rigs.ict_shapes(ict_facekit.SHAPES)}
        self.assertEqual(shapes['eyeBlink_L'], ('eyeBlinkLeft', None))
        self.assertEqual(shapes['jawOpen'], ('jawOpen', None))
        self.assertEqual(shapes['cheekPuff_R'], ('cheekPuff', 'R'))


class VrmPresets(unittest.TestCase):
    EXPRESSIONS = {
        'aa': {'isBinary': False, 'morphTargetBinds': [{'node': 1, 'index': 36, 'weight': 1}]},
        'ee': {'isBinary': False, 'morphTargetBinds': [{'node': 1, 'index': 36, 'weight': 0.5},
                                                      {'node': 2, 'index': 3, 'weight': 0.25}]},
        'blink': {'isBinary': True, 'morphTargetBinds': [{'node': 1, 'index': 12, 'weight': 1}]},
        'happy': {'morphTargetBinds': [{'node': 1, 'index': 3, 'weight': 1}], 'overrideMouth': 'blend'},
        'lookUp': {'isBinary': False},
    }

    def test_binds_accumulate_per_morph_target(self):
        weights, labels = vrm_presets.morph_weights(self.EXPRESSIONS, {'aa': 0.5, 'ee': 0.5})
        self.assertEqual(weights, {1: {36: 0.75}, 2: {3: 0.125}})
        self.assertEqual(labels, [])

    def test_values_are_clamped_and_binary_expressions_snap(self):
        self.assertEqual(vrm_presets.morph_weights(self.EXPRESSIONS, {'aa': 1.5})[0], {1: {36: 1.0}})
        self.assertEqual(vrm_presets.morph_weights(self.EXPRESSIONS, {'blink': 0.5})[0], {})
        self.assertEqual(vrm_presets.morph_weights(self.EXPRESSIONS, {'blink': 0.51})[0], {1: {12: 1.0}})

    def test_what_is_not_rendered_is_labelled(self):
        _, labels = vrm_presets.morph_weights(self.EXPRESSIONS, {'happy': 0.2, 'lookUp': 0.3, 'oh': 0.1})
        self.assertEqual(labels, ['happy: overrideMouth not applied', 'lookUp: no morph target binds on this model',
                                  'oh: this model has no such expression'])


class FullArkitRig(unittest.TestCase):
    """On a rig with all 52 ARKit shapes, shapes without an RCEF rule are shown direct-only and labelled."""

    @classmethod
    def setUpClass(cls):
        cls.translator = rcef_translate.fb2_to_arkit(pack=shared_pack.pack(), compiled=compiled())
        cls.targets = face_pipeline.face_targets([(i, a, None) for i, a in rigs.rocketbox_arkit(ROCKETBOX_LIKE).items()],
                                                 ROCKETBOX_LIKE)
        cls.frames = cls.translator.read(ROOT / 'examples/data/fb2_expression_frames.csv')
        cls.results = cls.translator.translate(cls.frames)
        cls.channels = [face_pipeline.check_channels(cls.translator, f, r, cls.targets)
                        for f, r in zip(cls.frames, cls.results)]

    def test_averaged_coefficients_are_exact_on_a_rig_that_does_not_split_them(self):
        brow = next(t for t in self.targets if t['arkit'] == 'browInnerUp')
        self.assertEqual(brow['route'], {'INNER_BROW_RAISER_L': 0.5, 'INNER_BROW_RAISER_R': 0.5})
        statuses = {c['status'] for frame in self.channels for c in frame if c['arkit'] == 'browInnerUp'}
        self.assertEqual(statuses, {'exact (moving)', 'at rest in both paths'})

    def test_every_oracle_passes_and_uncovered_shapes_are_labelled(self):
        self.assertTrue(all(c['passes'] for frame in self.channels for c in frame))
        uncovered = {c['arkit'] for frame in self.channels for c in frame
                     if c['status'] == 'no RCEF rule yet (direct only)'}
        self.assertIn('mouthFrownLeft', uncovered)
        self.assertNotIn('jawOpen', uncovered)
        anger = [c for f, frame in zip(self.frames, self.channels) if f['segment'] == 'anger' for c in frame]
        self.assertTrue(any(c['arkit'] == 'browDownLeft' and c['direct'] and c['translated'] is None for c in anger))

    def test_a_halved_rule_fails_on_the_expression_frames(self):
        changed = [{**r, 'values': {**r['values'], 'arkit.coefficient.jawOpen': r['values']['arkit.coefficient.jawOpen'] / 2}}
                   for r in self.results]
        self.assertFalse(all(c['passes'] for f, r in zip(self.frames, changed)
                             for c in face_pipeline.check_channels(self.translator, f, r, self.targets)))


if __name__ == '__main__':
    unittest.main()
