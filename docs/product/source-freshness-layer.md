# Source connection and freshness layer

Implemented27October2026 for local decision studio8014. Isolated prototype
service, not production account readiness, deployment or stack/database change.

## Implemented

`sources.py`: adapter boundary, normalized snapshots, public FX cache/lifecycle.
`serve.py`: closed same-origin JSON status/refresh endpoints. `sources.js`:
issuer/date/expiry/status UI and late-response/context guards.

- Fixed HTTPS TCMB USD ForexSelling and ECB daily XML adapters. ECB rate is
  EURTRY / EURUSD, Decimal rounded8places. It is a reference, not TCMB selling
  rate or an executable transaction quote. Explicit issuer selector defaults ECB;
  there is NO automatic issuer fallback.
- TCMB connections timed out here. Actual ECB retrieval and normal IAB readback
  succeeded: source date2026-10-26, EURUSD1.1188/EURTRY55.6746 →
  USDTRY49.76278155. These values are historical evidence, not runtime constants.
- Advertising registry returns access_required/no snapshot for selected products.
  Google/Meta/Yandex/LinkedIn forecasts are NOT connected. No ad/AI API or key use.

## Records and boundaries

Snapshot: version, ID, kind, issuer, scope, context hash, source_as_of,
fetched_at, expires_at, quality, payload and SHA256 of upstream bytes. Hashes
provide integrity IDs, not signed attestations or authorization. Lifecycle
validation refuses wrong account/context, synthetic quality presented as official,
tampering, bad/future/expired timestamps. Parsers reject bad/ambiguous rates,
wrong currency units, XML DTD/entities and oversized source responses.

Public FX uses public scope/USDTRY context and is reusable across budgets.
Future account forecasts must bind the authenticated workspace/account and
geo/keywords/audience/creative/objective/date/budget/currency/rule context.
Current HTTP scope is fixed local-synthetic and accepts no actor/account/tenant,
arbitrary source URL or uploaded snapshot. It is not production authentication.

## Freshness and cache

Publication and retrieval dates are different: fetching yesterday's publication
today does not make it today's observation. Public FX TTL1hour, maximum source
age4calendar days and refresh cooldown60seconds per issuer/process. This is a
bounded prototype policy; full provider/Turkey holiday calendars remain pending.

On page load missing/expired FX is fetched; valid cache is reused. Context input
updates are debounced; fresh public FX is shared, account forecasts never would
be. The open page requests refresh at expiry. Explicit Refresh requests a fresh
read subject to cooldown. Concurrent calls share an issuer lock. This is not a
background scheduler when the app is closed; the next request rechecks expiry.

Only PUBLIC FX cache persists under `%LOCALAPPDATA%/Yaparo/source-cache`, outside
Git/OneDrive. Issuer files are separate, atomically replaced. Failures retain the
last record but make it unusable for current calculation. Errors/body suppressed;
expiry/max-age/payload/provider policy is revalidated after restart. No user brief,
advertiser snapshot, source XML or credential is persisted there.

Responses carry requested context; sequence/context guards discard late replies.
A changed/expired quote marks an existing decision stale; recomputation is explicit
and records issuer/date/rate/record ID in the decision and review. A source update
does not silently reset user allocations. Historical SC01 mode keeps example FX.
Interactive simulation may use public FX; ad CPC/CPM/CPA/reach/account readiness
remain authored examples and every result remains nonpublishable.

## Transport and HTTP

Windows uses fixed System32 curl/Schannel with OS certificate verification,
HTTPS-only/no redirects,8second limit,256KiB limit, no shell/user URL interpolation.
Other systems use verified standard-library HTTPS. No TLS downgrade, insecure
option or credential. Native transport absence fails closed.

Exact loopback Host/Origin, JSON/custom header, closed issuer/channel/body/context
and8KiB request bound. Duplicate keys refuse; no CORS/OPTIONS permission.
CSP permits same-origin connections only. Upstream fixed-source GETs are server
side and contain no campaign/customer context.

## Evidence and next work

8offline source checks cover date/hash/expiry, ECB cross/issuer, bad XML/rates,
scope/context/quality/tamper, cache/restart/failure, concurrent refresh and closed
HTTP boundaries.5isolated browser journeys cover prior editor/assistant/mobile
and refreshed quote→stale decision→recompute→pinned review/source selection.
Browser adapters are injected fixtures, not live-source proof. Separate actual
ECB fetch/IAB readback supplied live evidence. Node checks retain original sample
and allocation guards and verify FX affects simulated USD minima, never publishing.

Next: qualify the first account-authorized read-only ad forecast adapter with
typed payload/expiry/quota rules and access proof. Preserve protected Google TEST
candidate, real-data/financial/recovery/launch gates. FX alone does not qualify ads.

Official references:
[ECB](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html),
[TCMB](https://www.tcmb.gov.tr/wps/wcm/connect/TR/TCMB+TR/Main+Menu/Temel+Faaliyetler/Doviz+Efektif/Doviz+ve+Efektif+Piyasalari/Gosterge+Niteligindeki+Kurlar),
[Google planning/cache](https://developers.google.com/google-ads/api/docs/keyword-planning/overview).
