# Offline prototype assets

No CDN is used at runtime. All assets are served by the loopback allowlist.
`../asset-hashes.json` pins the exact two third-party/data files. Directory
attributes preserve LF for byte-stable hashes on Windows/Linux.

- `polygon-clipping`0.15.7: MIT, npm registry package, exact dependency and
  transitive resolution in package-lock.json. Unmodified UMD minified bundle is
  copied to dist/vendor. Retain included MIT notices and robust-predicates public
  domain license. Upstream: https://github.com/mfogel/polygon-clipping
  Current npm audit passed with no reported vulnerabilities (27 October 2026).
  This is an isolated experiment dependency, not an application dependency or
  production adoption decision. No package installation scripts were run.
- Natural Earth 10m admin0 Turkey: public-domain source geometry extracted from
  the official author's vector repository. Exact source URL/revision and original
  whole-dataset SHA256 are embedded in dist/turkey-boundary.js; no simplification
  or invented border polygon. Six polygon parts with possible interior holes.
  Revision:9380cca83db5f9aef52d5e762765100745f84b27.
  Dataset accuracy is approximate and is not an official/legal border record.
  https://www.naturalearthdata.com/about/terms-of-use/

Reproducible installation: `npm ci --ignore-scripts --omit=optional --no-fund`
inside this experiment. The preview itself needs no Node process or installation:
the pinned bundle and Turkey data are already tracked. Update upstream source,
licenses, lock and hashes together, then run check.py. Do not substitute a CDN or
automatic download during page load. Data upgrades need coastline/border tests.
