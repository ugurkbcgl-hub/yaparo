"use strict";

const fs = require("node:fs");
const vm = require("node:vm");
const assert = require("node:assert/strict");

const fixture = JSON.parse(fs.readFileSync("fixtures/tiktok-traffic-preview.json", "utf8"));
const context = { window: {}, URL };
vm.createContext(context);
vm.runInContext(fs.readFileSync("tiktok-traffic-mapping.js", "utf8"), context, {
  filename: "tiktok-traffic-mapping.js",
});
const adapter = context.window.YaparoV3TikTokTraffic;
const result = adapter.map(fixture.brief);

assert.equal(adapter.version, "tiktok-marketing-api-v1.3-website-traffic-preview-v1");
assert.equal(result.apiVersion, "v1.3");
assert.equal(result.status, "preview_only_unverified");
assert.equal(result.missing.length, 0);
assert.equal(result.campaign.objective_type, "TRAFFIC");
assert.equal(result.campaign.operation_status, "DISABLE");
assert.equal(result.campaign.budget_mode, "BUDGET_MODE_TOTAL");
assert.equal(result.websiteTraffic.destination, "https://example.invalid/koleksiyon");
assert.equal(result.websiteTraffic.optimization_goal, "LANDING_PAGE_VIEW");
assert.equal(result.websiteTraffic.placement, "PLACEMENT_TIKTOK");
assert.equal(result.adGroup.promotion_type, "WEBSITE");
assert.equal(result.ad, null);
assert.equal(result.providerBody, null);
assert.equal(result.canDispatch, false);
assert.equal(result.externalCallMade, false);
assert.equal(result.spendTry, 0);
assert.equal(fixture.expected.externalCallMade, false);
assert.equal(fixture.expected.spendTry, 0);
assert.equal(fixture.expected.providerBody, null);

const blocked = adapter.map({ campaignName: "partial" });
assert.equal(blocked.status, "blocked");
for (const field of ["advertiserId", "budgetMode", "budgetAmount", "budgetCurrency", "websiteUrl", "locationIds", "scheduleStartTime", "optimizationGoal", "placement"]) {
  assert(blocked.missing.includes(field), `missing ${field} should block`);
}
assert.equal(blocked.canDispatch, false);
assert.equal(blocked.providerBody, null);

for (const [key, value, issue] of [
  ["budgetAmount", 0, "positive_finite_budget_amount"],
  ["budgetAmount", Infinity, "positive_finite_budget_amount"],
  ["budgetMode", "BUDGET_MODE_INFINITE", "supported_budget_mode"],
  ["budgetCurrency", "try", "iso_currency_code"],
  ["websiteUrl", "http://example.invalid", "https_website_url"],
  ["websiteUrl", "https://user:pass@example.invalid", "https_website_url"],
  ["locationIds", [], "nonempty_location_id_list"],
  ["optimizationGoal", "CONVERT", "supported_traffic_optimization_goal"],
  ["placement", "PLACEMENT_PANGLE", "supported_placement"],
]) {
  const invalid = adapter.map({ ...fixture.brief, [key]: value });
  assert.equal(invalid.status, "blocked", `${key}=${String(value)} should block`);
  assert(invalid.missing.includes(issue), `expected ${issue} for ${key}`);
  assert.equal(invalid.canDispatch, false);
  assert.equal(invalid.providerBody, null);
}
assert.throws(() => adapter.map(null), /brief must be an object/);

console.log("TikTok website traffic preview: v1.3 objective mapping, synthetic requirements, blockers and no-dispatch/no-spend invariants passed.");
