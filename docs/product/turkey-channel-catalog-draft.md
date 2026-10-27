# Turkey advertising channel research catalog — 27 October 2026

This broad digital-channel catalog is not an exhaustive inventory, an active
integration list, a media recommendation or a production eligibility decision.
Availability to register in Turkey is not proof of Turkey audience inventory.
Country, exact local targeting, account, sector and creative format need separate
verification. Unknown means unverified, not unavailable. Every prototype channel
remains disconnected and incapable of charging or publishing.

| Candidate | Primary evidence and qualified interpretation |
| --- | --- |
| Google Ads (Search/YouTube/Display family) | [Location targeting](https://developers.google.com/google-ads/api/docs/targeting/location-targeting), [minimum1km](https://support.google.com/google-ads/answer/1722043?hl=en), [maximum800km](https://developers.google.com/google-ads/api/docs/best-practices/system-limits). Family capability does not qualify every campaign/creative type. |
| Microsoft Advertising | [Turkey market](https://www.about.ads.microsoft.com/en/blog/post/january-2023/access-a-world-of-opportunity-scaling-campaigns-to-164-markets), [integer1..800km RadiusCriterion](https://learn.microsoft.com/en-us/advertising/campaign-management-service/radiuscriterion?view=bingads-13). Actual account and country-specific options still pending. |
| Meta (Facebook/Instagram) | [Primary help](https://www.facebook.com/business/help/202297959811696) was not accessible in this research. Current exact Turkey/radius conditions remain UNKNOWN; no claim of unsupported local ads. |
| TikTok | [Turkey registration](https://ads.us.tiktok.com/resources/help/article/available-countries-and-regions-for-ad-account-creation-in-bc?lang=en), [delivery market mapping](https://ads.tiktok.com/resources/help/article/placements-available-locations), [location types](https://ads.tiktok.com/resources/help/article/location-targeting). Country candidate; exact point-radius unverified. Video integration remains Phase2. |
| LinkedIn Ads | [Targeting types](https://www.linkedin.com/help/lms/answer/a424655/) document general geography; current Turkey account/target options and radius unverified. |
| X Ads | [Turkey selfservice eligibility](https://help.x.com/en/business-and-advertising/about-eligibility-for-x-ads), [geo targeting](https://help.x.com/en/business-and-advertising/geo-gender-and-language-targeting). Country candidate; exact local identifiers/radius still unverified, account verification conditions apply. |
| Pinterest | [Registration/partner path](https://help.pinterest.com/en/business/article/promoted-pins-overview), [Turkey targeting table](https://help.pinterest.com/en/business/article/location-language-device-and-gender-targeting). Turkey partner access, not direct selfservice. Exact point-radius unverified. |
| Snapchat | [Business signup countries](https://businesshelp.snapchat.com/articles/en_US/Knowledge/business-countries), [location targeting](https://businesshelp.snapchat.com/s/article/location-targeting?language=en_US), [Commercials format](https://businesshelp.snapchat.com/s/article/commercials?language=en_US). Turkey registration is not proof all formats/audience options work; exact radius remains unknown. |
| Spotify Ad Exchange | [Programmatic markets](https://ads.spotify.com/en-US/programmatic-advertising/spotify-ad-exchange/) include Turkey. Not proof of direct Ads Manager selfservice or local-radius access. |
| Amazon DSP | [Radius launch](https://advertising.amazon.com/resources/whats-new/engage-users-near-desired-locations-with-radius-targeting) lists Turkey and upper100km. Lower bound was not stated, so strict-radius candidate stays blocked pending verification. DSP is not retail Sponsored Products. |
| Yandex Direct/Maps/Navi | [Turkey products](https://ads.yandex.com/tr/direct-tr), [global0.5–10km geo docs](https://www.yandex.com/support/direct/en/efficiency/geotargeting), [fixed-country example](https://yandex.com.tr/adv/products/display/auction). Country candidate; do not apply global radius to a Turkey product without product/account verification. |
| Taboola/Realize | [Turkey usage case](https://www.taboola.com/resources/case-studies/vodafone-turkey), [targeting API](https://developers.taboola.com/backstage-api/docs/targeting-overview). Historical use is not current account/inventory/point-radius qualification. |
| Teads/Outbrain | [DSP geo options](https://intercom.help/outbrain_dsp/en/articles/8225734-setting-up-location-targeting). Turkey inventory/current account and point-radius unverified. |
| Reddit Ads | [Demographic/geo targeting](https://business.reddithelp.com/articles/Knowledge/demographics). Current granular Turkey targets need UI lookup; account route and radius remain unverified. |

## Budget and boundary rules in the prototype

Only documented geo-type candidates for the requested precision are selectable;
unknown/unsupported candidates stay0 with a reason and source. User may deselect
any eligible candidate and enter percentages directly (0..100, up to two decimal
places), or drag stable native range controls. One channel's new share is fixed;
the remainder redistributes proportionally across the other selected channels.
When all other shares are zero, the remainder splits equally. Largest-remainder
apportionment conserves10000 percentage basis points and integer-kuruş budgets.
A single selected channel stays100; all-off leaves budget unallocated. Initial
shares are equal, not a claimed performance ranking. Temporary invalid geography
allocates0 and blocks review while preserving the last valid custom mixture.
Invalid manual percentages retain their input, allocate0 and block review. No selected candidate means unallocated budget and no final
summary. Account, format, policy and actual boundary execution remain separate
closed production gates even for selectable candidates.

Turkey restriction means the geodesic radius polygon INTERSECTED with the locally
pinned Natural Earth Turkey land polygon. Offshore/foreign parts are excluded;
outside-land centers refuse instead of silently moving. This is approximate
planning geometry, not a legal border/coverage guarantee. Do not send Turkey and
radius as two positive platform locations and assume intersection: inclusion
semantics may be OR. Actual platform enforcement and presence settings need an
independent integration proof before publishing.

## Scenario math, not platform forecasts

All metrics carry a hypothetical-scenario label. No CPM/CTR/market/population
claim is made. Shared editable example defaults:100TRY CPM,1% CTR,100 fictional
people/km² and repeat factor2. These defaults do not rank platforms.

- Financial impressions = allocated TRY / assumed CPM ×1000.
- If a polygon area exists, cap by approximate km² × hypothetical density ×
  hypothetical repetitions × channel budget share. Named unresolved regions have
  no area cap and explicitly report missing boundary resolution.
- Scenario clicks = capped impressions × assumed CTR /100.
- Duration changes daily budget only, not market supply. Fixed budget may remain
  the limiting factor when radius changes; no false promise of linear geography
  effects. Goal/season/competition/real channel inventory are not modeled.
- Repeated impressions/clicks are not deduplicated persons, conversions or sales;
  never sum channel audiences as unique reach. User-entered assumptions and their
  clipped geography/channel allocations are pinned to the final local summary.

Changing plan/geo/channel/percentage/assumptions invalidates the old review. Values
cannot create network, forecast, payment, customer-data or publishing operations.


## Compact mixer interaction — owner revision

All14 catalog entries stay accessible in three collapsible groups: documented
radius candidates, broad-country candidates, and geo conditions awaiting checks.
The last group is not labelled incapable of local targeting. Each row has a
checkbox, leading numeric percent field, broad range bar, closed summary/details
and an accessible book-outline button. The book dialog gives formats, current
location reason, account/route qualifications, calculation limits and the primary
source. Unknown geo controls remain disabled0, while their guides are accessible.

Nodes remain mounted during drag/input so pointer capture/focus is not lost.
Geography changes reconcile only when valid; temporary missing coordinates do not
silently reset a user mixture. All relevant edits invalidate the previous review.
