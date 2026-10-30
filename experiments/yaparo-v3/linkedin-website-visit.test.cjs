"use strict";

const fs = require("node:fs");
const vm = require("node:vm");
const assert = require("node:assert/strict");

const fixture = JSON.parse(fs.readFileSync("fixtures/linkedin-website-visit-preview.json", "utf8"));
const context = { window: {}, URL };
vm.createContext(context);
vm.runInContext(fs.readFileSync("linkedin-website-visit-mapping.js", "utf8"), context, {
  filename: "linkedin-website-visit-mapping.js",
});
const adapter = context.window.YaparoV3LinkedInWebsiteVisit;
const result = adapter.map(fixture.brief);

assert.equal(adapter.version, "linkedin-website-visit-image-preview-v1");
assert.equal(result.status, "blocked");
assert.deepEqual(Array.from(result.missing), []);
assert.equal(result.candidateMapping.campaignType, "SPONSORED_UPDATES");
assert.equal(result.candidateMapping.format, "STANDARD_UPDATE");
assert.equal(result.candidateMapping.creativeType, "SPONSORED_STATUS_UPDATE");
assert.equal(result.candidateMapping.optimizationTargetType, "MAX_CLICK");
assert.deepEqual(Array.from(result.candidateMapping.objectiveTypeCandidates), ["WEBSITE_VISIT", "WEBSITE_VISITS"]);
assert.equal(result.candidateMapping.costType, null);
assert.equal(result.candidateMapping.status, "DRAFT");
assert.equal(result.candidateMapping.inputs.dailyBudget.amount, "100.00");
assert.equal(result.candidateMapping.inputs.dailyBudget.currencyCode, "TRY");
assert.equal(result.candidateMapping.inputs.locationUrn, "urn:li:geo:900000004");
assert.equal(result.providerBody, null);
assert.equal(result.canDispatch, false);
assert.equal(result.externalCallMade, false);
assert.equal(result.spendTry, 0);
assert.equal(fixture.expected.providerBody, null);
assert.equal(fixture.expected.canDispatch, false);
assert.equal(fixture.expected.externalCallMade, false);
assert.equal(fixture.expected.spendTry, 0);
for (const blocker of [
  "linkedin_objective_enum_conflicts_between_official_documents",
  "max_click_cost_type_mapping_requires_official_resolution",
  "creative_payload_schema_and_image_upload_flow_not_verified",
  "marketing_api_version_header_not_pinned",
  "turkey_account_currency_locale_and_location_urn_not_verified",
]) assert(result.blockers.includes(blocker), `expected blocker ${blocker}`);

const partial = adapter.map({ campaignName: "partial" });
assert.equal(partial.status, "blocked");
for (const field of ["accountUrn", "campaignGroupUrn", "organizationUrn", "dailyBudgetAmount", "accountCurrency", "locationUrn", "country", "language", "startAt", "endAt", "websiteUrl", "introText", "imageAssetUrn"]) {
  assert(partial.missing.includes(field), `missing ${field} should block`);
}
assert.equal(partial.candidateMapping.inputs, null);
assert.equal(partial.providerBody, null);

for (const invalid of [
  { websiteUrl: "http://example.invalid" },
  { websiteUrl: "javascript:alert(1)" },
  { websiteUrl: "https://user:pass@example.invalid" },
  { accountCurrency: "try" },
  { country: "Turkey" },
  { language: "TR" },
  { accountUrn: "urn:li:sponsoredAccount:synthetic" },
  { campaignGroupUrn: "urn:li:sponsoredCampaignGroup:synthetic" },
  { organizationUrn: "urn:li:organization:synthetic" },
  { locationUrn: "urn:li:geo:synthetic" },
  { imageAssetUrn: "https://example.invalid/image.png" },
  { dailyBudgetAmount: "0" },
  { dailyBudgetAmount: "1.234" },
  { startAt: "1793404800000" },
  { endAt: 1793404800000 },
]) {
  const invalidResult = adapter.map({ ...fixture.brief, ...invalid });
  assert.equal(invalidResult.status, "blocked", JSON.stringify(invalid));
}
assert(adapter.map({ ...fixture.brief, endAt: fixture.brief.startAt }).missing.includes("end_after_start"));
assert.throws(() => adapter.map(null), /brief must be an object/);

console.log("LinkedIn website visit preview: source-bound candidate mapping, ambiguity blockers, synthetic input validation, draft-only/no-body/no-dispatch invariants passed.");
