"use strict";

const fs = require("node:fs");
const vm = require("node:vm");
const assert = require("node:assert/strict");

const fixture = JSON.parse(fs.readFileSync("fixtures/meta-link-traffic-preview.json", "utf8"));
const context = { window: {}, URL };
vm.createContext(context);
vm.runInContext(fs.readFileSync("meta-link-traffic-mapping.js", "utf8"), context, {
  filename: "meta-link-traffic-mapping.js",
});
const adapter = context.window.YaparoV3MetaLinkTraffic;
const result = adapter.map(fixture.brief);

assert.equal(adapter.version, "meta-graph-v26-link-traffic-preview-v1");
assert.equal(result.status, "preview_only_unverified");
assert.equal(result.missing.length, 0);
assert.equal(result.payload.apiVersion, "v26.0");
assert.equal(result.payload.accountPath, "/act_SYNTHETIC_ONLY");
assert.deepEqual(Array.from(result.payload.resourceOrder), ["campaigns", "adsets", "adcreatives", "ads"]);
assert.equal(result.payload.campaign.objective, "OUTCOME_TRAFFIC");
assert.deepEqual(Array.from(result.payload.campaign.special_ad_categories), ["NONE"]);
assert.equal(result.payload.campaign.status, "PAUSED");
assert.equal(result.payload.adSet.daily_budget, 25000);
assert.equal(result.payload.adSet.billing_event, "IMPRESSIONS");
assert.equal(result.payload.adSet.optimization_goal, "LINK_CLICKS");
assert.equal(JSON.stringify(result.payload.adSet.targeting), JSON.stringify({ geo_locations: { countries: ["TR"] } }));
assert.equal(result.payload.adSet.status, "PAUSED");
assert.equal(result.payload.creative.object_story_spec.page_id, "SYNTHETIC_PAGE");
assert.equal(result.payload.creative.object_story_spec.link_data.link, "https://example.invalid/koleksiyon");
assert.equal(result.payload.ad.status, "PAUSED");
assert.equal(result.payload.creative.object_story_spec.link_data.call_to_action.type, "LEARN_MORE");
assert.equal(result.canDispatch, false);
assert.equal(result.externalCallMade, false);
assert.equal(fixture.expected.externalCallMade, false);
assert.equal(fixture.expected.spendTry, 0);

const missing = adapter.map({ campaignName: "partial" });
assert.equal(missing.status, "blocked");
for (const field of ["adAccountId", "specialAdCategories", "accountCurrency", "dailyBudgetMinor", "targeting", "pageId", "websiteUrl", "primaryText", "headline", "imageHash"]) {
  assert(missing.missing.includes(field), `missing ${field} should block`);
}
assert.equal(missing.canDispatch, false);

for (const specialAdCategories of ["NONE", ["INVALID"], ["NONE", "HOUSING"]]) {
  const invalid = adapter.map({ ...fixture.brief, specialAdCategories });
  assert.equal(invalid.status, "blocked");
  assert(invalid.missing.includes("valid_special_ad_categories"));
}
for (const dailyBudgetMinor of [0, -1, 1.2, "25000", Number.MAX_SAFE_INTEGER + 1]) {
  const invalid = adapter.map({ ...fixture.brief, dailyBudgetMinor });
  assert.equal(invalid.status, "blocked");
  assert(invalid.missing.includes("positive_integer_daily_budget_minor"));
}
for (const websiteUrl of ["http://example.invalid", "javascript:alert(1)", "https://", "https://user:pass@example.invalid", "not-a-url"]) {
  const invalid = adapter.map({ ...fixture.brief, websiteUrl });
  assert.equal(invalid.status, "blocked");
  assert(invalid.missing.includes("https_website_url"));
}
for (const accountCurrency of ["try", "TÜR", "US"]) {
  const invalid = adapter.map({ ...fixture.brief, accountCurrency });
  assert.equal(invalid.status, "blocked");
  assert(invalid.missing.includes("iso_currency_code"));
}
for (const targeting of [{ age_min: 18 }, { geo_locations: { countries: ["Turkey"] } }, { geo_locations: { countries: [] } }]) {
  const invalid = adapter.map({ ...fixture.brief, targeting });
  assert.equal(invalid.status, "blocked");
  assert(invalid.missing.includes("supported_country_only_targeting"));
}
assert.throws(() => adapter.map(null), /brief must be an object/);
console.log("Meta link traffic preview: v26 field mapping, explicit blockers, PAUSED-only objects, synthetic fixture and no-dispatch invariants passed.");
