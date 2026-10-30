(function () {
  "use strict";

  const version = "meta-graph-v26-link-traffic-preview-v1";
  const allowedCategories = new Set([
    "CREDIT",
    "EMPLOYMENT",
    "FINANCIAL_PRODUCTS_SERVICES",
    "HOUSING",
    "ISSUES_ELECTIONS_POLITICS",
    "ONLINE_GAMBLING_AND_GAMING",
    "NONE",
  ]);
  const sources = {
    sdkRelease: "https://github.com/meta/facebook-nodejs-business-sdk/releases",
    campaign: "https://github.com/meta/facebook-nodejs-business-sdk/blob/v26.0.2/src/objects/campaign.js",
    adSet: "https://github.com/meta/facebook-nodejs-business-sdk/blob/v26.0.2/src/objects/ad-set.js",
    creative: "https://github.com/meta/facebook-nodejs-business-sdk/blob/v26.0.2/src/objects/ad-creative.js",
    ad: "https://github.com/meta/facebook-nodejs-business-sdk/blob/v26.0.2/src/objects/ad.js",
  };
  const required = [
    "adAccountId",
    "campaignName",
    "specialAdCategories",
    "accountCurrency",
    "dailyBudgetMinor",
    "targeting",
    "pageId",
    "websiteUrl",
    "primaryText",
    "headline",
    "imageHash",
  ];
  const targetingKeys = new Set(["geo_locations"]);

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
    for (const field of ["campaignName", "pageId", "primaryText", "headline", "imageHash"]) {
      if (brief[field] !== undefined && typeof brief[field] !== "string") missing.push(`string_${field}`);
    }
    if (
      brief.specialAdCategories !== undefined &&
      (!Array.isArray(brief.specialAdCategories) ||
        brief.specialAdCategories.some((item) => !allowedCategories.has(item)) ||
        (brief.specialAdCategories.includes("NONE") && brief.specialAdCategories.length !== 1))
    ) {
      missing.push("valid_special_ad_categories");
    }
    if (
      brief.dailyBudgetMinor !== undefined &&
      (!Number.isSafeInteger(brief.dailyBudgetMinor) || brief.dailyBudgetMinor <= 0)
    ) {
      missing.push("positive_integer_daily_budget_minor");
    }
    if (
      brief.websiteUrl !== undefined &&
      !isHttpsUrl(brief.websiteUrl)
    ) {
      missing.push("https_website_url");
    }
    if (brief.accountCurrency !== undefined && !/^[A-Z]{3}$/.test(brief.accountCurrency)) {
      missing.push("iso_currency_code");
    }
    if (brief.targeting !== undefined && (!brief.targeting || typeof brief.targeting !== "object" || Array.isArray(brief.targeting))) {
      missing.push("targeting_object");
    }
    if (brief.adAccountId !== undefined && !/^act_[A-Za-z0-9_]+$/.test(brief.adAccountId)) {
      missing.push("valid_ad_account_reference");
    }
    if (
      brief.targeting && typeof brief.targeting === "object" &&
      (Object.keys(brief.targeting).some((key) => !targetingKeys.has(key)) ||
        !brief.targeting.geo_locations ||
        !Array.isArray(brief.targeting.geo_locations.countries) ||
        brief.targeting.geo_locations.countries.length === 0 ||
        brief.targeting.geo_locations.countries.some((country) => !/^[A-Z]{2}$/.test(country)))
    ) {
      missing.push("supported_country_only_targeting");
    }

    const payload = {
      apiVersion: "v26.0",
      mode: "preview_only",
      accountPath: brief.adAccountId && /^act_[A-Za-z0-9_]+$/.test(brief.adAccountId)
        ? `/${brief.adAccountId}`
        : "/<authorized_ad_account>",
      resourceOrder: ["campaigns", "adsets", "adcreatives", "ads"],
      campaign: {
        name: brief.campaignName || "Yaparo synthetic traffic preview",
        objective: "OUTCOME_TRAFFIC",
        special_ad_categories: Array.isArray(brief.specialAdCategories) ? [...brief.specialAdCategories] : [],
        status: "PAUSED",
      },
      adSet: {
        name: brief.adSetName || "Yaparo synthetic traffic preview ad set",
        campaign_id: "<campaign_id returned by Meta>",
        daily_budget: Number.isSafeInteger(brief.dailyBudgetMinor) ? brief.dailyBudgetMinor : null,
        billing_event: "IMPRESSIONS",
        optimization_goal: "LINK_CLICKS",
        targeting: brief.targeting && typeof brief.targeting === "object" && brief.targeting.geo_locations
          ? { geo_locations: { countries: [...(brief.targeting.geo_locations.countries || [])] } }
          : null,
        status: "PAUSED",
      },
      creative: {
        name: brief.creativeName || "Yaparo synthetic website link creative",
        object_story_spec: {
          page_id: brief.pageId || "<page_id>",
          link_data: {
            link: brief.websiteUrl || "<https website url>",
            message: brief.primaryText || "<primary text>",
            name: brief.headline || "<headline>",
            image_hash: brief.imageHash || "<uploaded image hash>",
            call_to_action: {
              type: "LEARN_MORE",
              value: { link: brief.websiteUrl || "<https website url>" },
            },
          },
        },
      },
      ad: {
        name: brief.adName || "Yaparo synthetic traffic preview ad",
        adset_id: "<adset_id returned by Meta>",
        creative: { creative_id: "<creative_id returned by Meta>" },
        status: "PAUSED",
      },
    };

    return {
      version,
      status: missing.length ? "blocked" : "preview_only_unverified",
      missing: [...new Set(missing)],
      blockers: [
        "no_meta_account_authorization",
        "no_provider_request_or_validate_only_check",
        "budget_minor_unit_and_account_currency_not_verified",
        "targeting_and_nested_creative_schema_require_provider_validation",
      ],
      canDispatch: false,
      externalCallMade: false,
      spendTry: 0,
      sources,
      payload,
    };
  }

  window.YaparoV3MetaLinkTraffic = { version, mode: "preview_only", sources, map };
}());
