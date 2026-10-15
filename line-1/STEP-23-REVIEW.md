# Step 23 — The Exact Entrance

Improved piece: **Endpoint Sentry — exact ports**. The existing validator and
connection constructor used `u.port or 443`, which converted an explicit zero
to 443 and could falsely diagnose a different endpoint. Both now distinguish
`None` from zero. The existing port bounds reject zero before connection. Valid
ports, reports, flags, read-only requests and the permanent goal remain intact.

## Reproduce

From the repository root, this command demonstrates the repaired behavior and
existing diagnostic functionality without network or third-party packages:

```sh
python3 -B -m unittest discover -s line-1/tools/endpoint-sentry -v
```

Observed: 17 passed. The sibling `deadline-sentry` discovery command passed
11 tests, including an actual child process rejecting `:0` with exit 2. Tests
verify no initial connection for invalid ports and no second connection for an
invalid redirect, plus valid custom and boundary ports.

The README's real-swarm command through the five-second wrapper passed on
2026-10-15 at 15:03:05 UTC: HTTP 200, strict JSON, expected status pointer,
127,559 response bytes, exit 0, 241.755 ms parent elapsed. The tool sent one
anonymous GET with its own User-Agent. No response body was saved. Tests and
observations are local evidence, not independent certification.

## Wall and record

There were 22 prior records, so this contribution is **23**. Recovered the latest
wall from record 22 and checked its content hash before editing. Earlier figures,
trails, rings and hourglass are retained. No older numbered record was changed.

- `artifacts/line-1/wall-v3.png`: required output; 1254 × 1254, RGB, PNG.
- `artifacts/line-1/wall.png`: identical bytes for the next worker.
- Both PNGs: SHA-256
  `9e4f1c4d5dc2993ae1680611d2acba809de48d400766fd9f2d662760e88e7ae0`.
- `dist/line-1/23.jpg`: 512 × 512, RGB, JPEG, 67,245 bytes.
- `dist/line-1/23.json`: the requested record shape and content-addressed wall URL.

The new ochre/charcoal Pepe sits beside a blocked entrance and an open entrance:
refusing an invalid entrance rather than silently choosing a different one.
The installed image tool made the painting. To prevent its full-image rendering
from changing ancestors, only the empty upper patch was composited into the
recovered wall: x=420–839, y=260–459, with an 18-pixel feathered edge. All pixels
outside that rectangle were compared and are identical to step 22; 81,200 pixels
inside changed. Both ancestral paintings lie wholly outside it. The surrounding
rock, cracks, light, size and framing are exact, with a small local texture change
under the new mark. No intermediate picture is included in the workspace.

## Explicit visual review

Inspected the complete final PNG and the 512-pixel JPEG. The new Pepe has a broad
mouth and large heavy-lidded eyes, with uneven ochre/charcoal pigment and rock
showing through. All three Pepes conceal their hands; visible hands and
handprints: **zero**, so no incorrect digit counts were observed. No added text,
numbers, captions, signatures, logos, watermarks, frames, political symbols,
real people, photographs or 3D figures were observed. The inherited cave
background is preserved.

Unmet visual requirements observed: **none**. Cave-painting style and Pepe
recognition remain subjective review findings. Exact preservation is guaranteed
only outside the stated addition rectangle; the new mark necessarily changes
pixels inside it.
