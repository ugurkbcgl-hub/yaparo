(function () {
  "use strict";

  const version = "linkedin-website-visit-image-preview-v2";
  const marketingApiVersion = "202610";
  const sources = {
    campaigns: "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-campaigns?view=li-lms-2026-10",
    creatives: "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-creatives?view=li-lms-2026-10",
    posts: "https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api?view=li-lms-2026-09",
    objectives: "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/campaign-objectives?view=li-lms-2026-10",
    access: "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/getting-started?view=li-lms-2026-10",
    changes: "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/recent-changes?view=li-lms-2026-10",
  };

  const required = [
    "accountUrn",
    "campaignGroupUrn",
    "organizationUrn",
    "campaignUrn",
    "sponsoredPostUrn",
    "campaignName",
    "dailyBudgetAmount",
    "accountCurrency",
    "locationUrn",
    "country",
    "language",
    "startAt",
    "endAt",
    "websiteUrl",
    "introText",
    "imageAssetUrn",
  ];

  function isHttpsUrl(value) {
    if (typeof value !== "string") return false;
    try {
      const url = new URL(value);
      return url.protocol === "https:" && Boolean(url.hostname) && !url.username && !url.password;
    } catch {
      return false;
    }
  }

  function map(brief) {
    if (!brief || typeof brief !== "object" || Array.isArray(brief)) {
      throw new TypeError("brief must be an object");
    }

    const missing = required.filter((field) =>
      brief[field] === undefined || brief[field] === null || brief[field] === "",
    );
    const blockers = [
      "image_upload_scopes_and_legacy_image_ad_guide_require_review",
      "inline_content_image_schema_not_verified",
      "marketing_api_version_202610_support_must_be_rechecked_before_provider_use",
      "account_access_role_and_organization_permission_not_verified",
      "creative_write_scope_and_ad_account_role_not_verified",
      "organization_post_read_scope_and_page_role_not_verified",
      "sponsored_post_owner_and_campaign_format_compatibility_not_verified",
      "turkey_account_currency_locale_and_location_urn_not_verified",
      "no_linkedin_account_authorization_or_provider_validation",
    ];

    for (const field of ["campaignName", "country", "language", "dailyBudgetAmount"]) {
      if (brief[field] !== undefined && typeof brief[field] !== "string") missing.push(`string_${field}`);
    }
    for (const [field, pattern, reason] of [
      ["accountUrn", /^urn:li:sponsoredAccount:\d+$/, "sponsored_account_urn"],
      ["campaignGroupUrn", /^urn:li:sponsoredCampaignGroup:\d+$/, "sponsored_campaign_group_urn"],
      ["organizationUrn", /^urn:li:organization:\d+$/, "organization_urn"],
      ["campaignUrn", /^urn:li:sponsoredCampaign:\d+$/, "sponsored_campaign_urn"],
      ["sponsoredPostUrn", /^urn:li:(?:share|ugcPost):\d+$/, "sponsored_post_urn"],
      ["locationUrn", /^urn:li:geo:\d+$/, "geo_location_urn"],
      ["imageAssetUrn", /^urn:li:digitalmediaAsset:[A-Za-z0-9:_-]+$/, "digital_media_asset_urn"],
    ]) {
      if (brief[field] !== undefined && !pattern.test(brief[field])) missing.push(`valid_${reason}`);
    }
    if (brief.accountCurrency !== undefined && !/^[A-Z]{3}$/.test(brief.accountCurrency)) {
      missing.push("iso_account_currency");
    }
    if (brief.dailyBudgetAmount !== undefined &&
        (typeof brief.dailyBudgetAmount !== "string" || !/^(?:0|[1-9]\d*)(?:\.\d{1,2})?$/.test(brief.dailyBudgetAmount) || Number(brief.dailyBudgetAmount) <= 0)) {
      missing.push("positive_decimal_daily_budget_amount");
    }
    if (brief.websiteUrl !== undefined && !isHttpsUrl(brief.websiteUrl)) missing.push("https_website_url");
    if (brief.country !== undefined && !/^[A-Z]{2}$/.test(brief.country)) missing.push("iso_country_code");
    if (brief.language !== undefined && !/^[a-z]{2}$/.test(brief.language)) missing.push("iso_language_code");
    if (brief.introText !== undefined && (typeof brief.introText !== "string" || brief.introText.trim().length === 0)) {
      missing.push("non_empty_intro_text");
    }
    for (const field of ["startAt", "endAt"]) {
      if (brief[field] !== undefined && (!Number.isSafeInteger(brief[field]) || brief[field] <= 0)) {
        missing.push(`positive_epoch_milliseconds_${field}`);
      }
    }
    if (Number.isSafeInteger(brief.startAt) && Number.isSafeInteger(brief.endAt) && brief.endAt <= brief.startAt) {
      missing.push("end_after_start");
    }

    const inputsComplete = missing.length === 0;
    return {
      version,
      // Documentation conflicts remain blockers even when every supplied field is shaped correctly.
      status: "blocked",
      missing: [...new Set(missing)],
      blockers,
      marketingApiVersion,
      canDispatch: false,
      externalCallMade: false,
      spendTry: 0,
      sources,
      candidateMapping: {
        campaignType: "SPONSORED_UPDATES",
        format: "STANDARD_UPDATE",
        creativeType: "SPONSORED_STATUS_UPDATE",
        objectiveType: "WEBSITE_VISITS",
        optimizationTargetType: "MAX_CLICK",
        costType: "CPM",
        bidType: "CPC",
        biddingMode: "AUTO",
        status: "DRAFT",
        inputs: inputsComplete ? {
          accountUrn: brief.accountUrn,
          campaignGroupUrn: brief.campaignGroupUrn,
          associatedEntityUrn: brief.organizationUrn,
          campaignUrn: brief.campaignUrn,
          sponsoredPostUrn: brief.sponsoredPostUrn,
          name: brief.campaignName,
          dailyBudget: { amount: brief.dailyBudgetAmount, currencyCode: brief.accountCurrency },
          locale: { country: brief.country, language: brief.language },
          runSchedule: { start: brief.startAt, end: brief.endAt },
          locationUrn: brief.locationUrn,
          destinationUrl: brief.websiteUrl,
          introText: brief.introText,
          imageAssetUrn: brief.imageAssetUrn,
        } : null,
      },
      creativeCandidate: inputsComplete ? {
        route: "existing_post_reference",
        campaignUrn: brief.campaignUrn,
        content: { reference: brief.sponsoredPostUrn },
        intendedStatus: "DRAFT",
      } : null,
      providerBody: null,
    };
  }

  window.YaparoV3LinkedInWebsiteVisit = { version, mode: "preview_only", sources, map };
}());
