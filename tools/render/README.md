# meshrender

`meshrender.swift` renders plain triangle meshes offscreen with SceneKit on macOS and writes PNGs. RCEF's face examples write meshes in the format it reads: little-endian float32 xyz positions, uint32 triangle indices and optional float32 RGB per vertex. Calibration fits use it to render their stimuli. It was written for RCEF and has the MIT licence, like RCEF's other code.

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

The renderer has no version number. The SHA-256 of `meshrender.swift` is its version. A calibration record (see [calibration/README.md](../../calibration/README.md)) stores, under `renderer`:

- `source_sha256`: `shasum -a 256 tools/render/meshrender.swift`, the source that was built;
- `binary_sha256`: `shasum -a 256 meshrender`, the binary that actually ran;
- `compiler`: the first line of `swiftc --version`;
- `os`: `sw_vers -productVersion` and the architecture (`uname -m`);
- `gpu`: the chipset from `system_profiler SPDisplaysDataType`.

Two builds of the same source can give different binary hashes, because the linker can write a new UUID each time. So `binary_sha256` identifies one build, and `source_sha256` is the source to rebuild from. Rendered images also depend on the OS and GPU, so the record names both.
