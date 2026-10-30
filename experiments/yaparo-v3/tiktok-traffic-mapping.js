(function () {
  "use strict";

  const version = "tiktok-marketing-api-v1.3-website-traffic-preview-v1";
  const budgetModes = new Set(["BUDGET_MODE_TOTAL", "BUDGET_MODE_DAY"]);
  const optimizationGoals = new Set(["LANDING_PAGE_VIEW"]);
  const placements = new Set(["PLACEMENT_TIKTOK"]);
  const required = [
    "advertiserId",
    "campaignName",
    "budgetMode",
    "budgetAmount",
    "budgetCurrency",
    "websiteUrl",
    "locationIds",
    "scheduleStartTime",
    "optimizationGoal",
    "placement",
  ];
  const sources = {
    trafficObjective: "https://ads.tiktok.com/resources/help/article/traffic-objective?lang=en",
    campaignCreate: "https://business-api.tiktok.com/gateway/docs/index?doc_id=1739318962329602",
    adGroupCreateSdk: "https://github.com/tiktok/tiktok-business-api-sdk/blob/main/js_sdk/docs/AdgroupCreateBody.md",
    optimizationEvents: "https://business-api.tiktok.com/gateway/docs/index?doc_id=1739361474981889",
    apiLifecycle: "https://business-api.tiktok.com/portal/docs/marketing-api/v2.0",
  };

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
    if (brief.advertiserId !== undefined && typeof brief.advertiserId !== "string") {
      missing.push("string_advertiserId");
    }
    if (brief.campaignName !== undefined && typeof brief.campaignName !== "string") {
      missing.push("string_campaignName");
    }
    if (brief.budgetMode !== undefined && !budgetModes.has(brief.budgetMode)) {
      missing.push("supported_budget_mode");
    }
    if (
      brief.budgetAmount !== undefined &&
      (typeof brief.budgetAmount !== "number" || !Number.isFinite(brief.budgetAmount) || brief.budgetAmount <= 0)
    ) {
      missing.push("positive_finite_budget_amount");
    }
    if (brief.budgetCurrency !== undefined && !/^[A-Z]{3}$/.test(brief.budgetCurrency)) {
      missing.push("iso_currency_code");
    }
    if (brief.websiteUrl !== undefined && !isHttpsUrl(brief.websiteUrl)) {
      missing.push("https_website_url");
    }
    if (
      brief.locationIds !== undefined &&
      (!Array.isArray(brief.locationIds) || brief.locationIds.length === 0 ||
        brief.locationIds.some((id) => typeof id !== "string" || !id.trim()))
    ) {
      missing.push("nonempty_location_id_list");
    }
    if (brief.scheduleStartTime !== undefined && typeof brief.scheduleStartTime !== "string") {
      missing.push("string_schedule_start_time");
    }
    if (brief.optimizationGoal !== undefined && !optimizationGoals.has(brief.optimizationGoal)) {
      missing.push("supported_traffic_optimization_goal");
    }
    if (brief.placement !== undefined && !placements.has(brief.placement)) {
      missing.push("supported_placement");
    }

    return {
      version,
      apiVersion: "v1.3",
      mode: "preview_only",
      status: missing.length ? "blocked" : "preview_only_unverified",
      missing: [...new Set(missing)],
      campaign: {
        advertiser_id: brief.advertiserId || "<verified_advertiser_id>",
        campaign_name: brief.campaignName || "<campaign_name>",
        objective_type: "TRAFFIC",
        budget_mode: brief.budgetMode || "<account-qualified_budget_mode>",
        budget: typeof brief.budgetAmount === "number" ? brief.budgetAmount : null,
        operation_status: "DISABLE",
      },
      websiteTraffic: {
        destination: brief.websiteUrl || "<https_website_url>",
        location_ids: Array.isArray(brief.locationIds) ? [...brief.locationIds] : [],
        schedule_type: "SCHEDULE_FROM_NOW",
        schedule_start_time: brief.scheduleStartTime || "<provider-formatted_start_time>",
        optimization_goal: brief.optimizationGoal || "<confirmed_traffic_goal>",
        placement: brief.placement || "<verified_placement>",
      },
      adGroup: {
        promotion_type: "WEBSITE",
        campaign_id: "<campaign_id returned by TikTok>",
        requiredButUnmapped: ["budget", "billing_event", "bid_type", "pacing", "ad_group operation_status"],
      },
      ad: null,
      blockers: [
        "no_tiktok_account_authorization_or_request",
        "TRY_account_budget_units_minimums_and_Turkey_location_id_not_verified",
        "complete_manual_traffic_ad_group_field_combination_not_verified",
        "ad_identity_creative_upload_and_review_flow_not_mapped",
        "no_provider_validate_only_or_draft_acceptance_evidence",
      ],
      providerBody: null,
      canDispatch: false,
      externalCallMade: false,
      spendTry: 0,
      sources,
    };
  }

  window.YaparoV3TikTokTraffic = { version, mode: "preview_only", sources, map };
}());
