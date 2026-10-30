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

assert.equal(adapter.version, "linkedin-website-visit-image-preview-v2");
assert.equal(result.status, "blocked");
assert.deepEqual(Array.from(result.missing), []);
assert.equal(result.marketingApiVersion, "202610");
assert.equal(result.candidateMapping.campaignType, "SPONSORED_UPDATES");
assert.equal(result.candidateMapping.format, "STANDARD_UPDATE");
assert.equal(result.candidateMapping.creativeType, "SPONSORED_STATUS_UPDATE");
assert.equal(result.candidateMapping.objectiveType, "WEBSITE_VISITS");
assert.equal(result.candidateMapping.optimizationTargetType, "MAX_CLICK");
assert.equal(result.candidateMapping.costType, "CPM");
assert.equal(result.candidateMapping.bidType, "CPC");
assert.equal(result.candidateMapping.biddingMode, "AUTO");
assert.equal(result.candidateMapping.status, "DRAFT");
assert.equal(result.candidateMapping.inputs.dailyBudget.amount, "100.00");
assert.equal(result.candidateMapping.inputs.dailyBudget.currencyCode, "TRY");
assert.equal(result.candidateMapping.inputs.locationUrn, "urn:li:geo:900000004");
assert.deepEqual(JSON.parse(JSON.stringify(result.creativeCandidate)), {
  route: "existing_post_reference",
  campaignUrn: "urn:li:sponsoredCampaign:900000005",
  content: { reference: "urn:li:ugcPost:900000006" },
  intendedStatus: "DRAFT",
});
assert.equal(result.providerBody, null);
assert.equal(result.canDispatch, false);
assert.equal(result.externalCallMade, false);
assert.equal(result.spendTry, 0);
assert.equal(fixture.expected.providerBody, null);
assert.equal(fixture.expected.canDispatch, false);
assert.equal(fixture.expected.externalCallMade, false);
assert.equal(fixture.expected.spendTry, 0);
for (const blocker of [
  "image_upload_scopes_and_legacy_image_ad_guide_require_review",
  "inline_content_image_schema_not_verified",
  "marketing_api_version_202610_support_must_be_rechecked_before_provider_use",
  "creative_write_scope_and_ad_account_role_not_verified",
  "organization_post_read_scope_and_page_role_not_verified",
  "sponsored_post_owner_and_campaign_format_compatibility_not_verified",
  "turkey_account_currency_locale_and_location_urn_not_verified",
]) assert(result.blockers.includes(blocker), `expected blocker ${blocker}`);

const partial = adapter.map({ campaignName: "partial" });
assert.equal(partial.status, "blocked");
for (const field of ["accountUrn", "campaignGroupUrn", "organizationUrn", "campaignUrn", "sponsoredPostUrn", "dailyBudgetAmount", "accountCurrency", "locationUrn", "country", "language", "startAt", "endAt", "websiteUrl", "introText", "imageAssetUrn"]) {
  assert(partial.missing.includes(field), `missing ${field} should block`);
}
assert.equal(partial.candidateMapping.inputs, null);
assert.equal(partial.providerBody, null);
assert.equal(partial.creativeCandidate, null);

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
  { campaignUrn: "urn:li:sponsoredCampaign:synthetic" },
  { sponsoredPostUrn: "urn:li:digitalmediaAsset:synthetic" },
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
