# Offline planning assets

Exact-byte copies from the previously reviewed unified-journey experiment:

- dist/turkey-boundary.js: Natural Earth public-domain 10m admin0 Turkey,
  revision9380cca83db5f9aef52d5e762765100745f84b27. Source/revision and original
  dataset SHA256 are embedded in the copied file. Approximate land geometry,
  not an official/legal border or proof of ad-platform targeting support.
  https://www.naturalearthdata.com/about/terms-of-use/
- dist/vendor/polygon-clipping-0.15.7.js: unchanged MIT UMD bundle, including
  bundled notices; copied transitive license files accompany this directory.
  https://github.com/mfogel/polygon-clipping

Source lock/resolution remains in ../unified-journey/package-lock.json and its
third-party notes. No dependency was downloaded/installed for this integration.
plan-geo.test.cjs pins both copied SHA256 values and checks clipping geometry.
.gitattributes preserves byte hashes on Windows/Linux. No runtime CDN, geocoder,
GPS, provider request or automatic asset update. Update source, notices, hashes
and border/coastline tests together when deliberately refreshing these assets.
