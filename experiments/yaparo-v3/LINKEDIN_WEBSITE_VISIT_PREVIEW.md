# LinkedIn website-visit image preview

This local-only contract describes a candidate Sponsored Updates / single-image
website-visit path. It does not connect to Yaparo, LinkedIn, an advertiser
account, a model, or the network. The fixture uses synthetic URNs and
`example.invalid`.

The candidate pins Marketing API version `202610` and records
`SPONSORED_UPDATES`, `STANDARD_UPDATE`, `SPONSORED_STATUS_UPDATE`,
`WEBSITE_VISITS`, `MAX_CLICK`, `costType: CPM`, `bidType: CPC`, and `DRAFT`.
The current Campaign API schema and change log list `WEBSITE_VISITS`; the
objective overview still displays `WEBSITE_VISIT`. For the pinned API schema,
the plural enum is selected. The current Website Traffic table maps
Standard Update with AUTO / MAX_CLICK to CPM cost type and CPC bid type. These
are source-derived candidates, not provider validation. The contract emits no
provider request body. DRAFT campaigns are documented as ineligible for
serving, with some validation deferred until activation.

The campaign shape also needs an authorized ad account and matching account
role/scope, campaign-group URN, organization URN for Sponsored Content, a
supported locale, account-matching currency, and provider location URNs. Turkey
account eligibility, TRY support, Turkish locale support for the specific
account, the location URN, and creative body/upload schema have not been
verified. The pinned `202610` Marketing API version and per-account access
must be rechecked before any provider integration or request.

The contract always returns `providerBody: null`, `canDispatch: false`,
`externalCallMade: false`, and `spendTry: 0`. It is not a validated LinkedIn ad,
forecast, account-readiness result, or authorization to publish.

## Focused check

Run from this directory:

```powershell
node linkedin-website-visit.test.cjs
```

## Official sources checked 30 October 2026

- [Create and Manage Campaigns](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-campaigns?view=li-lms-2026-10)
- [Campaign Objectives](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/campaign-objectives?view=li-lms-2026-10)
- [Build an Ad Campaign / access scopes](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/getting-started?view=li-lms-2026-10)
- [Recent Marketing API changes](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/recent-changes?view=li-lms-2026-10)
