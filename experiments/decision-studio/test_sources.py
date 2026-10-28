"""No-network contract, FX parsing, expiry, context isolation and source cache tests."""

import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from serve import make_server
from sources import (
    SourceService,
    canonical,
    make_snapshot,
    parse_ecb,
    parse_tcmb,
    snapshot_status,
    validate_context,
)

NOW = datetime(2026, 10, 27, 11, 0, tzinfo=timezone.utc)
XML = b'<Tarih_Date Tarih="26.10.2026"><Currency CurrencyCode="USD"><Unit>1</Unit><ForexSelling>49.7627</ForexSelling></Currency></Tarih_Date>'
CONTEXT = {
    "budget": 3000,
    "days": 7,
    "value": 500,
    "margin": 40,
    "cpa": 100,
    "capacity": 20,
    "goal": "store_visits",
    "business": "local_retail",
    "audience": "local_nearby",
    "sector": "fashion_beauty_lifestyle",
    "risk": "normal",
    "communication": "product_service_intro",
    "action": "visit_store",
    "geo": "district_city",
    "radius": 10,
    "region": "Sentetik İstanbul",
    "start": "2026-11-01",
    "measurement": "basic_utm",
    "fixture": "interactive",
    "readiness": "core",
    "video": False,
    "catalog": False,
    "tracking": False,
    "creative_id": "synthetic-1",
    "creative_revision": 1,
    "rule_version": "tr-rule-engine-v1.0.0",
}
ECB_XML = b'<Envelope xmlns="http://www.ecb.int/vocabulary/2002-08-01/eurofxref"><Cube><Cube time="2026-10-26"><Cube currency="USD" rate="2"/><Cube currency="TRY" rate="100"/></Cube></Cube></Envelope>'


class SourceTests(unittest.TestCase):
    def test_ecb_cross_rate_source_identity_and_ambiguous_values(self):
        record = parse_ecb(ECB_XML, NOW)
        self.assertEqual(record["source"], "ecb")
        self.assertEqual(record["payload"]["rate"], "50.00000000")
        self.assertEqual(record["payload"]["formula"], "EURTRY / EURUSD")
        self.assertEqual(record["source_as_of"], "2026-10-26")
        for xml in [
            ECB_XML.replace(b'rate="2"', b'rate="0"'),
            ECB_XML.replace(b"2026-10-26", b"2026-11-01"),
            ECB_XML.replace(
                b'<Cube currency="USD" rate="2"/>',
                b'<Cube currency="USD" rate="2"/><Cube currency="USD" rate="2"/>',
            ),
        ]:
            with self.assertRaises(ValueError):
                parse_ecb(xml, NOW)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "fx.json"
            path.write_text(canonical(record), encoding="utf-8")
            other = SourceService(cache_path=path, provider="tcmb", clock=lambda: NOW)
            self.assertFalse(other.describe(CONTEXT, [])["fx"]["usable"])

    def test_concurrent_requests_share_one_refresh(self):
        with tempfile.TemporaryDirectory() as temp:
            calls = []

            def transport():
                calls.append(1)
                return XML

            service = SourceService(
                cache_path=Path(temp) / "fx.json",
                transport=transport,
                clock=lambda: NOW,
            )
            with ThreadPoolExecutor(max_workers=4) as pool:
                results = list(
                    pool.map(
                        lambda _: service.refresh(CONTEXT, [], force=True), range(8)
                    )
                )
            self.assertEqual(len(calls), 1)
            self.assertTrue(all(r["fx"]["usable"] for r in results))

    def test_http_origin_closed_body_and_no_arbitrary_source_url(self):
        import json

        with tempfile.TemporaryDirectory() as temp:
            services = {
                name: SourceService(
                    cache_path=Path(temp) / f"{name}.json",
                    provider=name,
                    transport=lambda: XML,
                    clock=lambda: NOW,
                )
                for name in ["tcmb", "ecb"]
            }
            server = make_server(sources=services)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            origin = f"http://127.0.0.1:{server.server_port}"
            body = {
                "context": CONTEXT,
                "channels": ["google_search_maps"],
                "force": False,
                "source": "tcmb",
            }

            def post(payload, requested_origin=origin):
                data = (
                    payload
                    if isinstance(payload, bytes)
                    else json.dumps(payload).encode()
                )
                return urlopen(
                    Request(
                        origin + "/api/sources/status",
                        data=data,
                        headers={
                            "Content-Type": "application/json",
                            "Origin": requested_origin,
                            "X-Yaparo-Source": "local-synthetic",
                        },
                    ),
                    timeout=3,
                )

            try:
                with post(body) as response:
                    self.assertEqual(json.load(response)["fx"]["status"], "missing")
                for payload, request_origin, code in [
                    (body, "https://invalid.example", 403),
                    ({**body, "source": "https://invalid.example"}, origin, 400),
                    ({**body, "url": "https://invalid.example"}, origin, 400),
                    (
                        json.dumps(body)
                        .replace('"force": false', '"force": false, "force": true')
                        .encode(),
                        origin,
                        400,
                    ),
                ]:
                    with self.assertRaises(HTTPError) as rejected:
                        post(payload, request_origin)
                    self.assertEqual(rejected.exception.code, code)
            finally:
                server.shutdown()
                server.server_close()

    def test_fx_preserves_quote_date_separate_from_fetch_and_hash(self):
        record = parse_tcmb(XML, NOW)
        self.assertEqual(record["source_as_of"], "2026-10-26")
        self.assertEqual(record["fetched_at"], NOW.isoformat())
        self.assertEqual(record["payload"]["rate"], "49.7627")
        self.assertTrue(record["payload"]["indicative_only"])
        self.assertEqual(
            snapshot_status(
                record,
                scope="public",
                context={"base": "USD", "quote": "TRY"},
                now=NOW,
                allowed_quality={"official_public"},
            ),
            "available",
        )
        self.assertEqual(
            snapshot_status(
                record,
                scope="public",
                context={"base": "USD", "quote": "TRY"},
                now=NOW + timedelta(hours=6),
                allowed_quality={"official_public"},
            ),
            "expired",
        )

    def test_invalid_public_data_and_duplicate_currency_refuse(self):
        bad = [
            XML.replace(b"49.7627", b"NaN"),
            XML.replace(b"49.7627", b"-2"),
            XML.replace(b"<Unit>1", b"<Unit>100"),
            XML.replace(b"26.10.2026", b"01.10.2026"),
            XML.replace(b"26.10.2026", b"28.10.2026"),
            b'<!DOCTYPE x [<!ENTITY x "a">]>' + XML,
            XML.replace(b"</Tarih_Date>", XML.split(b">", 1)[1]),
            b"x" * 262145,
        ]
        for value in bad:
            with (
                self.subTest(value=value[:30]),
                self.assertRaises((ValueError, SyntaxError)),
            ):
                parse_tcmb(value, NOW)

    def test_context_account_quality_tamper_and_time_guards(self):
        record = make_snapshot(
            kind="forecast",
            source="google",
            scope="workspace-A/account-A",
            context=CONTEXT,
            source_as_of="2026-10-27",
            fetched_at=NOW,
            expires_at=NOW + timedelta(hours=1),
            quality="official_account",
            payload={"currency": "TRY"},
            source_sha256="a" * 64,
        )

        def status(r=record, scope="workspace-A/account-A", context=CONTEXT):
            return snapshot_status(
                r,
                scope=scope,
                context=context,
                now=NOW,
                allowed_quality={"official_account"},
            )

        self.assertEqual(status(), "available")
        self.assertEqual(status(scope="workspace-B/account-A"), "context_mismatch")
        self.assertEqual(
            status(context={**CONTEXT, "budget": 5000}), "context_mismatch"
        )
        self.assertEqual(status(r={**record, "payload": {}}), "invalid")
        for quality in ["demo_illustrative", "authored_simulation_NOT_market_data"]:
            synthetic = make_snapshot(
                kind="forecast",
                source="google",
                scope="workspace-A/account-A",
                context=CONTEXT,
                source_as_of="2026-10-27",
                fetched_at=NOW,
                expires_at=NOW + timedelta(hours=1),
                quality=quality,
                payload={},
                source_sha256="b" * 64,
            )
            self.assertEqual(status(r=synthetic), "unqualified")

    def test_cache_reuse_force_throttle_failure_and_restart(self):
        with tempfile.TemporaryDirectory() as temp:
            clock = [NOW]
            calls = []

            def fetch():
                calls.append(1)
                return XML

            path = Path(temp) / "fx.json"
            service = SourceService(
                cache_path=path, clock=lambda: clock[0], transport=fetch
            )
            self.assertEqual(
                service.describe(CONTEXT, ["google_search_maps"])["fx"]["status"],
                "missing",
            )
            first = service.refresh(CONTEXT, ["google_search_maps"])
            self.assertTrue(first["fx"]["usable"])
            self.assertEqual(first["forecasts"][0]["status"], "access_required")
            self.assertFalse(first["publishable"])
            service.refresh(CONTEXT, [], force=True)
            self.assertEqual(len(calls), 1)
            clock[0] += timedelta(minutes=2)
            service.refresh(CONTEXT, [])
            self.assertEqual(len(calls), 1)
            service.refresh(CONTEXT, [], force=True)
            self.assertEqual(len(calls), 2)
            restarted = SourceService(
                cache_path=path, clock=lambda: clock[0], transport=fetch
            )
            self.assertTrue(restarted.describe(CONTEXT, [])["fx"]["usable"])
            clock[0] += timedelta(minutes=2)

            def failing():
                raise OSError("suppressed")

            service.transport = failing
            failed = service.refresh(CONTEXT, [], force=True)
            self.assertEqual(failed["fx"]["status"], "refresh_failed")
            self.assertFalse(failed["fx"]["usable"])
            self.assertEqual(failed["fx"]["snapshot"]["source_as_of"], "2026-10-26")
            clock[0] += timedelta(hours=7)
            self.assertEqual(restarted.describe(CONTEXT, [])["fx"]["status"], "expired")
            path.write_text('{"bad":true}', encoding="utf-8")
            self.assertEqual(restarted.describe(CONTEXT, [])["fx"]["status"], "invalid")

    def test_closed_context_rejects_urls_tenant_ids_nan_and_unknown_channels(self):
        for patch in [
            {"url": "https://example.invalid"},
            {"tenant": "other"},
            {"budget": float("nan")},
            {"video": 1},
            {"start": "yesterday"},
        ]:
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                validate_context({**CONTEXT, **patch})
        self.assertEqual(canonical(validate_context(CONTEXT)), canonical(CONTEXT))
        with tempfile.TemporaryDirectory() as temp:
            service = SourceService(cache_path=Path(temp) / "fx.json")
            with self.assertRaises(ValueError):
                service.describe(CONTEXT, ["invented_channel"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
