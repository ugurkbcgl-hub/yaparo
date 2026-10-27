"""Owned source snapshots and public TCMB adapter; no advertising credentials."""

import hashlib
import json
import math
import os
import subprocess
import threading
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from http.client import HTTPSConnection
from pathlib import Path
from zoneinfo import ZoneInfo

UTC = timezone.utc
ISTANBUL = ZoneInfo("Europe/Istanbul")
TCMB_URL = "https://www.tcmb.gov.tr/kurlar/today.xml"
ECB_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
MAX_BYTES = 262_144
MAX_SOURCE_AGE_DAYS = 4
CACHE_TTL = timedelta(hours=1)
REFRESH_COOLDOWN = timedelta(seconds=60)
CHANNELS = frozenset(
    "google_search_maps google_pmax_shopping youtube google_display_demandgen "
    "meta_social meta_messages tiktok linkedin yandex_search_maps "
    "microsoft_search_shopping snapchat pinterest x_ads reddit spotify "
    "retail_media_marketplace influencer_creator programmatic_native_video "
    "owned_crm organic_local_profile".split()
)
CONTEXT_FIELDS = frozenset(
    "budget days value margin cpa capacity goal business audience sector risk "
    "communication action geo radius region start measurement fixture readiness "
    "video catalog tracking creative_id creative_revision rule_version".split()
)


def canonical(value):
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def timestamp(value):
    return value.astimezone(UTC).isoformat()


def parse_time(value):
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("Source timestamp must have a timezone.")
    return parsed.astimezone(UTC)


def validate_context(value):
    """Closed synthetic context; no arbitrary tenant/account/source URL input."""
    if not isinstance(value, dict) or set(value) != CONTEXT_FIELDS:
        raise ValueError("Plan context fields do not match.")
    numeric = {
        "budget": (0, 1_000_000),
        "days": (1, 365),
        "value": (0, 100_000_000),
        "margin": (0, 100),
        "cpa": (0, 10_000_000),
        "capacity": (0, 1_000_000),
        "radius": (1, 800),
        "creative_revision": (1, 1_000_000),
    }
    for key, (low, high) in numeric.items():
        n = value[key]
        if type(n) not in (int, float) or not math.isfinite(n) or not low <= n <= high:
            raise ValueError("Invalid numeric source context.")
        if key in {"days", "capacity", "radius", "creative_revision"} and int(n) != n:
            raise ValueError("Integer source context required.")
    for key in {"video", "catalog", "tracking"}:
        if type(value[key]) is not bool:
            raise ValueError("Boolean source context required.")
    for key in CONTEXT_FIELDS - numeric.keys() - {"video", "catalog", "tracking"}:
        if not isinstance(value[key], str) or not 1 <= len(value[key]) <= 200:
            raise ValueError("Invalid string source context.")
    date.fromisoformat(value["start"])
    return json.loads(canonical(value))


def make_snapshot(
    *,
    kind,
    source,
    scope,
    context,
    source_as_of,
    fetched_at,
    expires_at,
    quality,
    payload,
    source_sha256,
):
    record = {
        "schema": "yaparo-source-v1",
        "kind": kind,
        "source": source,
        "scope": scope,
        "context_hash": digest(context),
        "source_as_of": source_as_of,
        "fetched_at": timestamp(fetched_at),
        "expires_at": timestamp(expires_at),
        "quality": quality,
        "payload": payload,
        "source_sha256": source_sha256,
    }
    record["id"] = digest(record)
    return record


def snapshot_status(record, *, scope, context, now, allowed_quality):
    """Never use a different account/context, synthetic record, future or expired data."""
    try:
        if record.get("schema") != "yaparo-source-v1":
            return "invalid"
        expected_id = digest({k: v for k, v in record.items() if k != "id"})
        if record.get("id") != expected_id:
            return "invalid"
        if record["scope"] != scope or record["context_hash"] != digest(context):
            return "context_mismatch"
        if record["quality"] not in allowed_quality:
            return "unqualified"
        fetched = parse_time(record["fetched_at"])
        expires = parse_time(record["expires_at"])
        source_date = date.fromisoformat(record["source_as_of"][:10])
        if record.get("kind") not in {"fx", "forecast"}:
            return "invalid"
        if "T" in record["source_as_of"] and parse_time(
            record["source_as_of"]
        ) > fetched + timedelta(minutes=2):
            return "invalid"
        if fetched > now + timedelta(minutes=2) or expires <= fetched:
            return "invalid"
        if source_date > now.astimezone(ISTANBUL).date():
            return "invalid"
        if now >= expires:
            return "expired"
        return "available"
    except (KeyError, ValueError, TypeError, AttributeError):
        return "invalid"


def parse_tcmb(body, now):
    if not isinstance(body, bytes) or not body or len(body) > MAX_BYTES:
        raise ValueError("Invalid public source size.")
    if b"<!DOCTYPE" in body.upper() or b"<!ENTITY" in body.upper():
        raise ValueError("Source entities are not permitted.")
    root = ET.fromstring(body)
    if root.tag != "Tarih_Date":
        raise ValueError("Unexpected public source root.")
    as_of = datetime.strptime(root.attrib["Tarih"], "%d.%m.%Y").date()
    age = (now.astimezone(ISTANBUL).date() - as_of).days
    if not 0 <= age <= MAX_SOURCE_AGE_DAYS:
        raise ValueError("Public quote is too old or in the future.")
    usd = [c for c in root.findall("Currency") if c.get("CurrencyCode") == "USD"]
    if len(usd) != 1 or usd[0].findtext("Unit", "").strip() != "1":
        raise ValueError("Unexpected public currency unit.")
    try:
        selling = Decimal(usd[0].findtext("ForexSelling", ""))
        if not selling.is_finite() or not Decimal("0") < selling < Decimal("100000"):
            raise ValueError("Invalid public exchange rate.")
    except InvalidOperation as exc:
        raise ValueError("Invalid public exchange rate.") from exc
    oldest_expiry = datetime.combine(
        as_of + timedelta(days=MAX_SOURCE_AGE_DAYS + 1), datetime.min.time(), ISTANBUL
    ).astimezone(UTC)
    return make_snapshot(
        kind="fx",
        source="tcmb",
        scope="public",
        context={"base": "USD", "quote": "TRY"},
        source_as_of=as_of.isoformat(),
        fetched_at=now,
        expires_at=min(now + CACHE_TTL, oldest_expiry),
        quality="official_public",
        payload={
            "base": "USD",
            "quote": "TRY",
            "field": "ForexSelling",
            "rate": str(selling),
            "unit": 1,
            "source_url": TCMB_URL,
            "indicative_only": True,
        },
        source_sha256=hashlib.sha256(body).hexdigest(),
    )


def parse_ecb(body, now):
    if not isinstance(body, bytes) or not body or len(body) > MAX_BYTES:
        raise ValueError("Invalid public source size.")
    if b"<!DOCTYPE" in body.upper() or b"<!ENTITY" in body.upper():
        raise ValueError("Source entities are not permitted.")
    root = ET.fromstring(body)
    ns = {"e": "http://www.ecb.int/vocabulary/2002-08-01/eurofxref"}
    dated = root.findall(".//e:Cube[@time]", ns)
    if len(dated) != 1:
        raise ValueError("Unexpected ECB observation date.")
    as_of = date.fromisoformat(dated[0].attrib["time"])
    age = (now.astimezone(ISTANBUL).date() - as_of).days
    if not 0 <= age <= MAX_SOURCE_AGE_DAYS:
        raise ValueError("Public quote is too old or in the future.")
    rates = {}
    for currency in ("USD", "TRY"):
        values = dated[0].findall(f"e:Cube[@currency='{currency}']", ns)
        if len(values) != 1:
            raise ValueError("Ambiguous ECB currency.")
        rate = Decimal(values[0].attrib["rate"])
        if not rate.is_finite() or not 0 < rate < 1_000_000:
            raise ValueError("Invalid ECB reference rate.")
        rates[currency] = rate
    cross = (rates["TRY"] / rates["USD"]).quantize(Decimal("0.00000001"))
    if not 0 < cross < 100000:
        raise ValueError("Invalid ECB cross reference rate.")
    oldest_expiry = datetime.combine(
        as_of + timedelta(days=MAX_SOURCE_AGE_DAYS + 1), datetime.min.time(), ISTANBUL
    ).astimezone(UTC)
    return make_snapshot(
        kind="fx",
        source="ecb",
        scope="public",
        context={"base": "USD", "quote": "TRY"},
        source_as_of=as_of.isoformat(),
        fetched_at=now,
        expires_at=min(now + CACHE_TTL, oldest_expiry),
        quality="official_public",
        payload={
            "base": "USD",
            "quote": "TRY",
            "field": "EUR_cross_reference",
            "rate": str(cross),
            "unit": 1,
            "source_url": ECB_URL,
            "eur_usd": str(rates["USD"]),
            "eur_try": str(rates["TRY"]),
            "formula": "EURTRY / EURUSD",
            "indicative_only": True,
        },
        source_sha256=hashlib.sha256(body).hexdigest(),
    )


def fetch_public(provider):
    endpoints = {
        "tcmb": ("www.tcmb.gov.tr", "/kurlar/today.xml", TCMB_URL),
        "ecb": ("www.ecb.europa.eu", "/stats/eurofxref/eurofxref-daily.xml", ECB_URL),
    }
    host, path, url = endpoints[provider]
    if os.name == "nt":
        # Schannel retains OS certificate/chain verification. No -k or redirects.
        executable = (
            Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32/curl.exe"
        )
        result = subprocess.run(
            [
                str(executable),
                "--fail",
                "--silent",
                "--max-time",
                "8",
                "--max-filesize",
                str(MAX_BYTES),
                "--proto",
                "=https",
                url,
            ],
            capture_output=True,
            timeout=10,
            check=False,
        )
        if result.returncode or not 0 < len(result.stdout) <= MAX_BYTES:
            raise OSError("Public source unavailable.")
        return result.stdout
    return fetch_https(host, path)


def fetch_tcmb():
    return fetch_public("tcmb")


def fetch_https(host, path):
    """Fixed HTTPS origin/path, default TLS verification, bounded read, no redirects."""
    connection = HTTPSConnection(host, timeout=8)
    try:
        connection.request(
            "GET",
            path,
            headers={
                "Accept": "application/xml,text/xml",
                "User-Agent": "YaparoSourceTrial/1.0",
            },
        )
        response = connection.getresponse()
        if response.status != 200:
            raise OSError("Public source unavailable.")
        body = response.read(MAX_BYTES + 1)
        if len(body) > MAX_BYTES:
            raise ValueError("Public source oversized.")
        return body
    finally:
        connection.close()


class SourceService:
    """Private local cache of PUBLIC FX only. No advertiser snapshots stored yet."""

    def __init__(self, *, cache_path=None, transport=None, clock=None, provider="tcmb"):
        if provider not in {"tcmb", "ecb"}:
            raise ValueError("Unsupported public source provider.")
        self.provider = provider
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
        self.cache_path = (
            cache_path or base / f"Yaparo/source-cache/{provider}-usd-try-v1.json"
        )
        self.transport = transport or (lambda: fetch_public(self.provider))
        self.clock = clock or (lambda: datetime.now(UTC))
        self.lock = threading.Lock()
        self.last_attempt = None
        self.last_error = None

    def _read(self):
        try:
            if (
                not self.cache_path.is_file()
                or self.cache_path.stat().st_size > MAX_BYTES
            ):
                return None
            return json.loads(self.cache_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None

    def _fx(self):
        record = self._read()
        status = (
            "missing"
            if record is None
            else snapshot_status(
                record,
                scope="public",
                context={"base": "USD", "quote": "TRY"},
                now=self.clock(),
                allowed_quality={"official_public"},
            )
        )
        if self.last_error:
            status = "refresh_failed"
        if status == "available" and (
            record.get("source") != self.provider or record.get("kind") != "fx"
        ):
            status = "invalid"
        if status == "available":
            try:
                payload = record["payload"]
                rate = Decimal(payload["rate"])
                if (
                    payload.get("base") != "USD"
                    or payload.get("quote") != "TRY"
                    or payload.get("unit") != 1
                    or not rate.is_finite()
                    or not 0 < rate < 100000
                    or parse_time(record["expires_at"])
                    - parse_time(record["fetched_at"])
                    > CACHE_TTL
                    or (
                        self.clock().astimezone(ISTANBUL).date()
                        - date.fromisoformat(record["source_as_of"])
                    ).days
                    > MAX_SOURCE_AGE_DAYS
                ):
                    status = "invalid"
            except (KeyError, ValueError, TypeError, InvalidOperation):
                status = "invalid"
        if status in {"invalid", "context_mismatch", "unqualified"}:
            record = None
        return {
            "status": status,
            "usable": status == "available",
            "snapshot": record,
            "last_attempt": timestamp(self.last_attempt) if self.last_attempt else None,
            "error_code": self.last_error,
            "cache_ttl_seconds": int(CACHE_TTL.total_seconds()),
        }

    def describe(self, context, channels):
        context = validate_context(context)
        if (
            not isinstance(channels, list)
            or len(channels) > 20
            or not set(channels) <= CHANNELS
        ):
            raise ValueError("Unsupported channel source request.")
        with self.lock:
            return self._description(context, channels)

    def _description(self, context, channels):
        return {
            "source_provider": self.provider,
            "schema": "yaparo-source-status-v1",
            "context_hash": digest(context),
            "context": context,
            "scope": "local-synthetic",
            "fx": self._fx(),
            "forecasts": [
                {
                    "channel_id": c,
                    "status": "access_required",
                    "snapshot": None,
                    "usable": False,
                    "reason": "Hesap ve salt okunur tahmin erişimi doğrulanmadı.",
                }
                for c in sorted(set(channels))
            ],
            "publishable": False,
            "advertising_api_calls": 0,
        }

    def refresh(self, context, channels, *, force=False):
        context = validate_context(context)
        if (
            not isinstance(channels, list)
            or len(channels) > 20
            or not set(channels) <= CHANNELS
        ):
            raise ValueError("Unsupported channel source request.")
        with self.lock:
            now = self.clock()
            current = self._fx()
            result = "cache_reused"
            cooling = self.last_attempt and now - self.last_attempt < REFRESH_COOLDOWN
            if current["usable"] and not force:
                result = "cache_reused"
            elif cooling:
                result = "cooldown"
            elif force or not current["usable"]:
                self.last_attempt = now
                try:
                    parser = parse_tcmb if self.provider == "tcmb" else parse_ecb
                    record = parser(self.transport(), self.clock())
                    self.cache_path.parent.mkdir(parents=True, exist_ok=True)
                    temporary = self.cache_path.with_suffix(".tmp")
                    temporary.write_text(canonical(record), encoding="utf-8")
                    temporary.replace(self.cache_path)
                    self.last_error = None
                    result = "refreshed"
                except Exception:
                    # No raw transport/body/credential details are logged or returned.
                    self.last_error = "source_refresh_failed"
                    result = "failed"
            output = self._description(context, channels)
            output["refresh_result"] = result
            return output
