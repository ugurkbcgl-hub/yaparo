# TikTok website traffic preview

This is an isolated, local-only contract sketch for one TikTok website traffic
campaign. It does not connect to the Yaparo UI, read an advertiser account, or
make network requests. The fixture contains synthetic values and an
`example.invalid` destination.

Official TikTok documentation says the Traffic objective can direct people to a
website or app. This slice limits its scenario to a website, `TRAFFIC`,
`LANDING_PAGE_VIEW`, and TikTok placement. The API reference describes
`/campaign/create/` with `objective_type`, budget mode and budget; campaign
`operation_status: DISABLE` is explicitly supported. The preview leaves the ad
group's unverified status and required billing/bid/pacing combinations unmapped,
and creates no ad or creative payload.

The object is never dispatchable, even if all supplied inputs pass local shape
checks. Location IDs, account currency and minimums, Türkiye eligibility, the
complete ad-group/creative combination, and any provider validation result are
unknown. TikTok's current Marketing API documentation also describes a 2027
transition for selected legacy objectives; Traffic is not listed in that
specific transition notice, but this preview is not a long-term compatibility
guarantee. Recheck official version notes before implementation.

## Verification

Run from this directory:

```powershell
node tiktok-traffic.test.cjs
```

## Official sources checked on 30 October 2026

- [Traffic objective](https://ads.tiktok.com/resources/help/article/traffic-objective?lang=en)
- [Campaign create API v1.3](https://business-api.tiktok.com/gateway/docs/index?doc_id=1739318962329602)
- [Official JavaScript SDK ad-group create fields](https://github.com/tiktok/tiktok-business-api-sdk/blob/main/js_sdk/docs/AdgroupCreateBody.md)
- [Optimization-event documentation](https://business-api.tiktok.com/gateway/docs/index?doc_id=1739361474981889)
- [Marketing API v2.0 transition notice](https://business-api.tiktok.com/portal/docs/marketing-api/v2.0)
