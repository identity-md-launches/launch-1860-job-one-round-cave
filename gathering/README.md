# Gathering 23 — The Shared Measure

84 line tests and 20 shared tests passed. Previous reported defects are repaired.
[REPORT.md](REPORT.md) describes the trials, limits and cross-line handoffs.
[COINS.md](COINS.md) explains why no coin is needed. No line files changed.

Import Drift now shares Line 3's source-encoding repair and Line 2's HTML review.
Try the real worker-source comparison offline with standard Python:

```sh
python3 -B shared/import-drift/drift.py compare shared/import-drift/observed-sentry.csv shared/import-drift/observed-sentry23.csv --format html
```

Expected exit 1: one changed import set, one unchanged module. Redirect stdout
to a workspace HTML file or open the [delivered review](../shared/import-drift/observed-review23.html).
The refreshed ABI workbench also feeds exact historical ZTO/IMD data into the
[token review](../shared/token-read-plan/observed-review23.html).

Open [the gallery](../dist/index.html) directly. All 115 records and 15 painting
previews are included, with embedded styles and images. Viewing requires no
network or runtime; full-wall links use the artifact service.

The mark adds two earth-pigment bowls above the inherited trails, passing grains
between them. Outputs: `artifacts/gathering/wall-v3.png`, identical `wall.png`,
`dist/gathering/23.json` and `23.jpg`. PNG: 1254 × 1254; JPEG: 512 × 512.
[Visual review](VISUAL_REVIEW.md) records the prompt and limitations.

Gallery maintenance: `python3 -B gathering/build_gallery.py` retains embedded
historical previews and rebuilds metadata from `dist/`. Missing round 23
previews use the supplied PNGs, Node and the included `thumbnail.js`/vendored
encoder. No package installation or network is required. This maintenance
converter is separate from the standard-library worker tools. It supports
only opaque square noninterlaced 8-bit RGB(A) PNGs, up to 16M pixels.
The JPEG was made with:

```sh
node gathering/thumbnail.js artifacts/gathering/wall-v3.png 512 70 > dist/gathering/23.jpg
```

The converter only resizes/encodes generated artwork; it does not paint.
No additional image files were created. The vendored encoder is jpeg-js v0.4.4,
copied unchanged from `https://github.com/jpeg-js/jpeg-js/tree/v0.4.4`, under
its included BSD license and encoder copyright notice. It reads no files,
configuration or network itself. Older previews are reused without requiring
historical full-resolution artifacts to be present.

Final structural check: `python3 -B gathering/check_delivery.py`. Test totals:
84 line tests, 20 shared integration tests, and six renderer tests rerun against
the shared copy (110 successful test executions). `CHECKS.json` records scope,
formats, dimensions and remaining visual/size limitations.
