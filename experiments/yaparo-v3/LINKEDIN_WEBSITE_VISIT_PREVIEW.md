# LinkedIn website-visit image preview

This local-only contract describes a candidate Sponsored Updates / single-image
website-visit path. It does not connect to Yaparo, LinkedIn, an advertiser
account, a model, or the network. The fixture uses synthetic URNs and
`example.invalid`.

The candidate records `SPONSORED_UPDATES`, `STANDARD_UPDATE`,
`SPONSORED_STATUS_UPDATE`, `MAX_CLICK`, and `DRAFT` as documented inputs or
values. It deliberately emits no provider request body. LinkedIn's campaign
schema lists `WEBSITE_VISITS`, while its objective mapping page uses
`WEBSITE_VISIT`; the MAX_CLICK cost-type table also requires interpretation
before a versioned request can be formed. These conflicts are surfaced as
blockers, not silently guessed. DRAFT campaigns are documented as ineligible
for serving, with some validation deferred until activation.

The campaign shape also needs an authorized ad account and matching account
role/scope, campaign-group URN, organization URN for Sponsored Content, a
supported locale, account-matching currency, and provider location URNs. Turkey
account eligibility, TRY support, Turkish locale support for the specific
account, the location URN, creative body/upload schema, and a current
Marketing-Version header have not been verified. The docs warn that Marketing
version 202511 sunsets on 16 November 2026, so this preview does not pin it.

The contract always returns `providerBody: null`, `canDispatch: false`,
`externalCallMade: false`, and `spendTry: 0`. It is not a validated LinkedIn ad,
forecast, account-readiness result, or authorization to publish.

## Focused check

Run from this directory:

```powershell
node linkedin-website-visit.test.cjs
```

## Official sources checked 30 October 2026

- [Create and Manage Campaigns](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-campaigns?view=li-lms-2026-04)
- [Campaign Objectives](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/campaign-objectives?view=li-lms-2026-09)
- [Build an Ad Campaign / access scopes](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/getting-started?view=li-lms-2026-10)
