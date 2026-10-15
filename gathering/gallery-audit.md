# Gathering 23 gallery audit

`python3 -B gathering/check_delivery.py` passed on the final delivery.

- All 115 numbered records occur exactly once in `dist/index.html`.
- All 15 paintings have embedded JPEG previews. There are no scripts, iframes,
  remote stylesheets, or remote image loads. Ordinary full-wall links use HTTPS.
- Within each wall, paintings and reserved slots are separately newest first.
- All 100 placeholder JSON records remain in slots 02–21, without JPEG files.
- Local record, thumbnail, source and report links resolve. Navigation anchors
  resolve. Goals exactly match the four unchanged GOAL.md files.
- The page is 80,809 bytes, below 100 KB. It opens without network access.
- Record 23 points to the actual PNG SHA-256. PNG CRCs pass; size is 1254 square.
  The thumbnail's JPEG frame is 512 square and the image was visually opened.
- All line files matched a pre-execution SHA-256 inventory, including file sets.
- All newly created/changed paths are in scope and new/changed non-artifact
  files are under 100 KB. The inherited Line 4 thumbnail exception is unchanged.

The page was checked structurally with HTMLParser, not a browser screenshot.
No browser rendering certification or independent behavioral audit is claimed.
`gathering/build_gallery.py` can rebuild it offline by retaining embedded
historical previews. It only needs Node and the included encoder if a round 23
preview must be regenerated from its PNG.
