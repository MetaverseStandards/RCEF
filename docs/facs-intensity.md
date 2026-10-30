<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# FACS intensity: the letter codec (draft)

Original documentation: CC-BY-SA-4.0. Copyright (c) 2026 Metaverse Standards Forum.

This page says how RCEF turns FACS codes with intensity letters, such as `1C+2C+L12B`, into the numbers of the `facs.code` profile, and back. It goes with the draft [canonical expression set](canonical-set.md#facs).

**This is not FACS coding, and the values are not FACS scores.** RCEF does not code faces, and it makes no claim about FACS proficiency. RCEF uses FACS code numbers, short names, table membership and intensity letters from a public list, as facts: the Wikipedia article "Facial Action Coding System", revision 1357638399 (record `facs_wikipedia`, CC-BY-SA-4.0). Nothing comes from the FACS manual ([THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md)). "FACS" here means facial action codes. The profile ID `facs.code` names code numbers from a public list. Its numeric encoding is RCEF's own and is not a FACS interface.

## Why a codec

- FACS writes intensity as a letter from A (trace) to E (maximum) after the code number. E is the maximum possible for the individual person (`facs_wikipedia` raw lines 69-75). FACS defines no numeric scale.
- msf-character-tools 0.5.0 holds scalar values only. So letters cannot be in the pack.
- A `piecewise_linear` step from letters to numbers would only imitate a step with steep segments. That adds precision that the source does not have. RCEF does not do this.
- So the conversion happens outside the pack, in this documented codec. The example `examples/facs_codec.py` implements it, and `tests/test_facs_codec.py` checks every rule. It reads its code and region tables from a CC-BY-SA-4.0 data file, `examples/data/facs_codes.json`, not from code.

## Inputs

- A string of codes joined by `+`, for example `1C+2C+L12B`. Each code is an optional side letter (`L`, `R`, `U` or `A`), an optional `M`, a code number (`97*` and `98*` keep their star) and an optional intensity letter.
- The dictionary form of RCEF's expression library (`examples/data/expressions.json`), whose keys are codes such as `12`, `L12` or `R30` and whose values are letters or numbers.

## Rules

Every rule below is an RCEF assumption. None is a FACS fact.

### Letters

| Letter | Value |
|---|---:|
| A | 0.2 |
| B | 0.4 |
| C | 0.6 |
| D | 0.8 |
| E | 1.0 |

- The table is named `rcef.facs.letters.v1`. It is the table of `examples/data/expressions.json` lines 13-20.
- A code with no letter is C, 0.6, for every code, 27, 45 and 46 included. This is the library's rule (`examples/data/expressions.json` line 13).
- A number in the library's dictionary form is RCEF's own example value. It is used as it is.
- Letters on the gross behaviour codes (29, 30, 34, 35 and 43) use the same table. The source gives these codes no intensity scale (raw lines 65 and 224), so this carries the loss `facs_gross_code_no_intensity`.
- Equal steps between letters are not claimed. Every FACS hop carries the loss `facs_ordinal_intensity`.

### Absent codes

Every in-scope signal that a scored frame does not list is 0, "absent". This is FACS practice as RCEF reads it, not a measured fact. A frame that nobody scored is not a frame of zeros: the codec returns no frame for it.

### Sides

- A code with no side letter sets both sides of a sided signal to the same value.
- `L` or `R` sets one side. RCEF reads L and R as the subject's own left and right. Wikipedia does not say whose side (raw line 78), so this is an assumption, with the loss key `facs_side_frame_unresolved`.
- `L30` and `R30` are directions: the jaw moves toward the subject's own left or right. Loss key `facs_au30_direction_unresolved`.
- RCEF splits a code by side where the canonical signal is split by side. Which codes FACS lets be one-sided is in the closed manual.

### Refusals

The codec returns no frame, and names each problem with its codes, when the input has any of these:

- a token that is not FACS notation, or a dictionary key that is not a code, or a dictionary value that is neither a letter nor a number;
- a code that is not in the Wikipedia list;
- the side letter `U` (one side, side not stated) or `A` (both sides, one stronger);
- `30` or `46` with no side letter: a direction or a side is needed;
- a side letter where every signal that the code writes, is read as or leaves out has no sides: on a mapped shared code (8, 17, 19, 26 and 29, for example `L17`), on 27 (read as 26), on 37 (leaves out only `tongue_out`) and on the visibility codes 70-74;
- the same code twice;
- two codes that write one signal: 26 with 27; two of 43, 45 and 46 on one eye; or a code both with and without a side letter, such as `1+L1`.

### Codes that are not mapped

Some codes have no canonical signal. Where a coder scores such a code *instead of* a mapped code, the mapped code's absence says nothing. So the codec reads the code as that mapped code, or it leaves the mapped code's signals out. Where a coder would score both codes, "absent" still holds, and the codec does not read the other code.

A signal that is left out is never 0. A left-out signal wins over any value that another code gives it. msf-character-tools then refuses the in-map that reads it (`E_MISSING_SAMPLE`), and the route labels those outputs "refused upstream".

| Codes (Wikipedia name) | Rule | Side letter | Reason and record |
|---|---|---|---|
| 27 (Mouth stretch) | read as 26 at its own letter | refused | Wikipedia's muscles for 27 open the jaw (raw line 139), and public crosswalks read 27 as jawOpen (`ict_facekit` line 174; `pyfeat_au_reference` line 91). Loss key `facs_mouth_opening_split` |
| 45 (Blink) | read as AU43 | optional: none means both eyes, `L` or `R` one eye | blink is closure scored as an event (raw line 261); RCEF carries closure per frame. Loss key `facs_eyelid_events` |
| 46 (Wink) | read as AU43 on that eye | required | a wink is one eye closing (raw line 263); `examples/face_pipeline.py` lines 142-147 already show it as one-sided AU43. Loss key `facs_eyelid_events` |
| 41 (Lid droop), 42 (Slit) | leave out the `blink` signals | optional: none means both eyes, `L` or `R` narrows to one | the FACS 2002 edition turned the old 41, 42 and 44 scores into AU43 intensities (`facs_hager_2002`), but no public source gives those letters |
| 44 (Squint) | leave out the `blink` signals and `lid_tighten` | optional, as for 41 | as for 41 (`facs_hager_2002`); also, Py-Feat relates 44 to eyeSquint, the ARKit shape that `lid_tighten` takes (`pyfeat_au_reference` line 107). A frame with 44 gives no `face` output |
| 33 (Cheek blow) | leave out the `cheek_puff` signals | optional: none means both cheeks, `L` or `R` narrows to one | ICT-FaceKit relates 33 to cheekPuff (`ict_facekit` line 179), the ARKit shape that `cheek_puff` takes |
| 37 (Lip wipe) | leave out `tongue_out` | refused | a lip wipe moves the tongue over the lips; Py-Feat lists a tongue muscle, genioglossus, for 37 (`pyfeat_au_reference` line 100), so a coder may score 37 instead of 19 |
| 0, 11, 13, 21, 25, 31, 32, 36, 38, 39, 40, 61-66, 69, every excluded code (50-58, 80-98\*) and every M code, with or without a letter | not read: their actions set no mapped signal | ignored | the codec lists them, and the route reports them as dropped |

### Visibility codes

Codes 70-74 say that part of the face could not be seen (raw lines 206-221). The codec leaves out every signal of the codes listed for that region. A side letter on a visibility code is refused.

| Code (Wikipedia name) | Signals left out |
|---|---|
| 70 (Brows and forehead not visible) | the signals of codes 1, 2 and 4 |
| 71 (Eyes not visible) | the signals of codes 5, 6, 7 and 43 |
| 72 (Lower face not visible) | the signals of every other mapped code: 8, 9, 10, 12, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 26, 28, 29, 30, 34 and 35 |
| 73 (Entire face not visible), 74 (Unscorable) | every mapped signal |

Wikipedia gives only the region names. The table that links regions to codes is RCEF's assumption. One in-map reads a whole group, so 70 refuses every `face` output, not only the brows.

### Decoding values to letters

For display only, a value becomes a letter by these ranges. The midpoints are also an assumption.

| Value | Letter |
|---|---|
| from 0 up to 0.1 | absent |
| from 0.1 up to 0.3 | A |
| from 0.3 up to 0.5 | B |
| from 0.5 up to 0.7 | C |
| from 0.7 up to 0.9 | D |
| from 0.9 to 1 | E |

## The numbers in the pack

- **Main codes:** 0 is absent, and 1 is intensity E, the maximum possible for the person (raw line 70). Values between are RCEF's encoding, not a FACS measure.
- **Gross behaviour codes 29, 30, 34, 35 and 43:** 1 is the action at its fullest, as RCEF assumes. The source gives no intensity scale for these codes (raw lines 65 and 224). AU43 is in Wikipedia's gross behaviour table (raw line 257). The FACS 2002 edition scores 43 by intensity, but no public source gives its letters.
- The calibration strings of the `facs.code` signals say this ([canonical-set.md](canonical-set.md#facs)).

## What the codec does not claim

- It does not measure intensity. No gain is measured.
- It does not claim that the letters span equal ranges. Only the closed manual says.
- It does not claim which codes FACS allows to be one-sided, or whose left FACS means.
- It does not produce or check FACS scores, and it is not a FACS coding tool.
