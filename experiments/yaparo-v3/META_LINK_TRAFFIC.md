# Meta link-traffic mapping preview

This isolated contract exercise describes one website link ad using a static
image. It is not connected to the Yaparo UI or a Meta account and makes no
network calls.

The versioned preview names the v26 campaign, ad set, creative and ad fields
seen in Meta Business SDK v26.0.2. The fixture uses synthetic identifiers and
`example.invalid`; all generated objects remain `PAUSED`. Only country-code
targeting is represented. Other objectives, placements, radius/city targeting,
audiences, video and Instagram identity are outside this first slice.

`daily_budget` is passed through from an explicitly named integer input, but
its currency-unit interpretation, account minima, and regional rules have not
been verified. The SDK confirms field names/enums, not the complete nested
payload's acceptance by Meta. The output therefore always remains
`preview_only_unverified`, with dispatch disabled. It must not be interpreted
as a validated ad or forecast.

## Verification

Run from this directory:

```powershell
node meta-link-traffic.test.cjs
```

The test checks the synthetic contract, required-field blocking, URL/currency
input shape, targeting scope, paused states, and zero-call/zero-spend results.

## Pinned official sources

- [Meta Business SDK v26.0.2 release](https://github.com/meta/facebook-nodejs-business-sdk/releases/tag/v26.0.2)
- [Campaign object](https://github.com/meta/facebook-nodejs-business-sdk/blob/v26.0.2/src/objects/campaign.js)
- [Ad Set object](https://github.com/meta/facebook-nodejs-business-sdk/blob/v26.0.2/src/objects/ad-set.js)
- [Ad Creative object](https://github.com/meta/facebook-nodejs-business-sdk/blob/v26.0.2/src/objects/ad-creative.js)
- [Ad object](https://github.com/meta/facebook-nodejs-business-sdk/blob/v26.0.2/src/objects/ad.js)
