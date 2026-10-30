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
are source-derived candidates, not provider validation. The supported creative
candidate is limited to referencing an existing Share or UGC post:
`campaign`, `content.reference`, and `intendedStatus: DRAFT`. An image asset URN
alone is not the post reference needed by the creative. The contract emits no
provider request body. Inline image-post creation is not mapped.

The campaign shape also needs an authorized ad account and matching account
role/scope, campaign-group URN, organization URN for Sponsored Content, a
supported locale, account-matching currency, and provider location URNs. Turkey
account eligibility, TRY support, Turkish locale support for the specific
account, the location URN, and image upload scopes/recipe have not been
verified. The official Image Ads guide is labeled legacy and its campaign
prerequisite table conflicts with its single-image description; it is not used
to invent a format. Current Creative docs show both `content.reference` and
`inlineContent`, but the inline sample is video-specific. The pinned `202610`
Marketing API version and per-account access must be rechecked before any
provider integration or request.

The current Creative API docs also require an authorized ad-account role and
`rw_ads` for write operations. Reading an organization post requires
`r_organization_social` and an eligible organization page role. The preview
does not verify that the referenced post belongs to the selected organization
or matches the campaign's source ad format; these remain explicit blockers.

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
- [Create and Manage Creatives](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-creatives?view=li-lms-2026-10)
- [Image Ads (Legacy)](https://learn.microsoft.com/en-us/linkedin/marketing/usecases/ad-tech/image-ads-usecase?view=li-lms-2026-04)
- [Image API permissions and upload](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/images-api?view=li-lms-2026-03)
- [Posts API permissions and supported sponsored formats](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api?view=li-lms-2026-09)
