# meshrender

`meshrender.swift` renders plain triangle meshes offscreen with SceneKit on macOS and writes PNGs. RCEF's face examples write meshes in the format it reads (little-endian float32 xyz positions, uint32 triangle indices, optional float32 RGB per vertex), and calibration fits render their stimuli with it. It was written for RCEF and is MIT-licensed like RCEF's other code.

## Build

macOS with the Xcode command line tools (SceneKit and Metal are part of macOS; last built with Apple Swift 6.3.3 on macOS 27):

```sh
swiftc -O -o meshrender tools/render/meshrender.swift
```

Build outside the checkout, or delete the binary afterwards; it is not committed.

## Use

```sh
meshrender jobs.json
```

`jobs.json` gives the image size and one job per image: mesh files, camera, colours and output path. The format is described at the top of `meshrender.swift`.

## Version and hashes

The renderer has no version number: its version is the SHA-256 of `meshrender.swift`. A calibration record (see [calibration/README.md](../../calibration/README.md)) stores, under `renderer`:

- `source_sha256`: `shasum -a 256 tools/render/meshrender.swift`, the source that was built;
- `binary_sha256`: `shasum -a 256 meshrender`, the binary that actually ran;
- `compiler`: the first line of `swiftc --version`;
- `os`: `sw_vers -productVersion` and the architecture (`uname -m`);
- `gpu`: the chipset from `system_profiler SPDisplaysDataType`.

Two builds of the same source give different binary hashes (the linker writes a fresh UUID each time), so `binary_sha256` identifies one build, and `source_sha256` is what to rebuild from. Rendered images also depend on the OS and GPU, which is why the record names both.
