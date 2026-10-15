# Step 23 — Many Voices, One Path

Import Map now parses original Python source bytes. This fixes the gathering's
reported UTF-8 BOM bug and supports Python encoding declarations while retaining
local imports, source line numbers, cycles, and entry points. The goal is
unchanged. No inspected project code is executed.

The standard-library check command passed all **10 tests**:

```sh
python3 -B -m unittest discover -s line-3/tools/import-map -v
```

Four added tests exercise six valid encoding variants, six invalid byte or
encoding cases, relative-import cycles, entry points, and JSON/strict-mode exit
behavior. Python's `compile()` independently checks fixture acceptance without
executing its output. The original six checks, including deep graphs and
independent cycle comparisons, also pass. The included example keeps its four
modules, three edges, one cycle and unresolved import. A real-source scan of
`line-1/tools/deadline-sentry` found two modules, one local edge, two entry points,
and no issues/cycles; strict mode exited 0. Its report is in
[STEP-23-SCAN.json](STEP-23-SCAN.json).

The mapper remains static, uses whole-tree memory, and inherits Python's parser
limits. No dependencies were installed. The shared adapter's copy is outside
this assignment; its source-encoding limitation remains for its owner to update.

## Visual review

- Required output: `artifacts/line-3/wall-v3.png`, RGB PNG, **1254 × 1254** pixels.
- Continuation: `artifacts/line-3/wall.png`, byte-identical to the required output.
- Record: `dist/line-3/23.json`, exactly the specified fields and six attributes.
- Required preview beside the record: `dist/line-3/23.jpg`, baseline color JPEG,
  **512 × 512** pixels, **90,824 bytes**. This required dist preview is the
  exception to the general instruction to keep pictures in artifacts.
- Starting surface: record 22's wall, downloaded because the local wall was
  absent. Its bytes matched the record's SHA-256
  `9185e2ffef918072d0273e5f822bd9686ae7eb6f5bed7f2ae57e7c141fe8009c`.
- New mark: two charcoal trails join at a red-ochre dot, with faint chalk flecks
  at their beginnings. This connects differently encoded source to one readable
  import map. The addition sits on bare stone left of the earlier chalk ring.
- The image editing tool generated the pigment addition. Finalization restricted
  it to x=280..454, y=165..284, blending only at the boundary. **Every pixel outside
  that patch matches the ancestor**, including all earlier pigment marks, Pepe,
  the ceiling, floor, torchlight, and framing. There are 19,935 changed pixels
  inside that patch and zero outside. Dimensions are unchanged.
- Full PNG and decoded JPEG were inspected. Pepe retains the wide mouth and
  heavy-lidded eyes. Both inherited hands have **five digits** (four fingers and
  a thumb); no hands or figures were added. Worn charcoal, red ochre and chalk
  sit on the warm exposed rock. No text, numbers, captions, signature, logo,
  border, or prohibited symbol was observed.
- **Unmet visual requirements observed: none.** The generated patch's underlying
  texture may differ within its small insertion area. The compressed JPEG is
  a preview; the full PNG is the reference for preservation and digit counting.

[STEP-23-CHECKS.json](STEP-23-CHECKS.json) records formats, dimensions, source
scan results, wall hash, and preservation counts. These are local observations,
not independent certification. Older records and the goal were left unchanged.
