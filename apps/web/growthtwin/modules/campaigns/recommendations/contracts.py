"""Immutable local planning metadata, not authorization or accepted form analysis.

No database, HTTP, credential, clock or provider I/O. The future owner service must
resolve trusted scope, use the separate accepted bank validator, and enforce
transactional revision/nonce uniqueness before persisting these values.
"""

import hashlib
import json
import re
from dataclasses import dataclass, fields, is_dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import StrEnum
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

SCHEMA = "yaparo-recommendation-draft-v1"
FIRST_STAGE_SCHEMA = "yaparo-first-stage-v1"
MAX_MONEY = 999_999_999
ROUTES = (
    ("promote", ("remember", "understand", "traffic", "visit", "contact", "install")),
    ("sell", ("purchase", "visit", "message", "call", "traffic", "understand")),
    ("event", ("register", "ticket", "visit", "understand", "message")),
    ("lead", ("lead_form", "quote", "book", "call", "message", "meeting")),
    ("hire", ("apply", "traffic", "message")),
    (
        "fundraise",
        ("donate", "materials", "volunteer", "understand", "traffic", "share"),
    ),
    ("announce", ("understand", "remember", "traffic", "share", "follow")),
    ("community", ("join", "subscribe", "register", "traffic", "follow")),
    ("reputation", ("understand", "remember", "traffic", "share")),
)
RISKS = frozenset(
    {
        "normal",
        "fundraising",
        "health",
        "finance",
        "political",
        "children",
        "alcohol_tobacco",
        "gambling",
    }
)


class ContractError(ValueError):
    """Bounded rejection without echoing customer content."""


class Delivery(StrEnum):
    PAID = "paid"
    ORGANIC = "organic"
    HYBRID = "hybrid"
    CONTENT_ONLY = "content_only"
    UNSURE = "unsure"


class MetricStatus(StrEnum):
    AVAILABLE = "available"
    MISSING = "missing"
    UNSUPPORTED = "unsupported"
    UNAUTHORIZED = "unauthorized"
    STALE = "stale"
    PARTIAL = "partial"
    CONFLICTING = "conflicting"
    ERROR = "error"
    NOT_APPLICABLE = "not_applicable"


class SourceKind(StrEnum):
    AUTHORED_DEMO = "authored_demo"
    DECLARED_ASSUMPTION = "declared_assumption"
    MANUAL_EXPORT = "manual_export"
    OFFICIAL_FORECAST = "official_forecast"
    PLATFORM_ACTUAL = "platform_actual"
    BUSINESS_ACTUAL = "business_actual"


def _require(condition):
    if not condition:
        raise ContractError("Recommendation contract rejected.")


def _integer(value, low=0, high=MAX_MONEY):
    _require(type(value) is int and low <= value <= high)


def _text(value, maximum=200):
    _require(type(value) is str and 0 < len(value) <= maximum)
    _require(value == value.strip() and not any(ord(c) < 32 for c in value))
    try:
        value.encode("utf-8")
    except UnicodeError:
        raise ContractError("Recommendation contract rejected.") from None


def _uuid(value):
    _require(type(value) is UUID and value.int != 0)


def _aware(value):
    _require(type(value) is datetime and value.utcoffset() is not None)


def _utc(value):
    _aware(value)
    return value.astimezone(timezone.utc)


def _currency(value):
    # Deliberately bounded initial money contract; not a market capability claim.
    _require(type(value) is str and value in {"TRY", "USD", "EUR"})


def _country(value):
    # Structural country code only; no assertion of platform/policy support.
    _require(type(value) is str and re.fullmatch(r"[A-Z]{2}", value) is not None)


def _wire(value):
    if is_dataclass(value) and not isinstance(value, type):
        return {f.name: _wire(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, StrEnum):
        return value.value
    if type(value) is datetime:
        return value.astimezone(timezone.utc).isoformat()
    if type(value) in (UUID, date, Decimal):
        return str(value)
    if type(value) in (tuple, list):
        return [_wire(v) for v in value]
    if type(value) is dict:
        return {k: _wire(v) for k, v in value.items()}
    if value is None or type(value) in (str, bool, int, float):
        return value
    raise ContractError("Unsupported contract value.")


def _canonical(value):
    try:
        return json.dumps(
            _wire(value),
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError, UnicodeError, RecursionError):
        raise ContractError("Recommendation contract rejected.") from None


def _digest(value):
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class OwnerScope:
    """Scope metadata to compare with trusted service scope, never a grant."""

    owner_id: int
    workspace_id: int
    draft_id: UUID
    brand_id: int | None = None

    def __post_init__(self):
        _integer(self.owner_id, 1)
        _integer(self.workspace_id, 1)
        _uuid(self.draft_id)
        if self.brand_id is not None:
            _integer(self.brand_id, 1)


@dataclass(frozen=True, slots=True)
class DeclaredBrief:
    """Canonical unqualified declaration; AcceptedBrief separately validates fields.

    Constructor only accepts the closed envelope/route and bounded flat answers.
    No caller-provided valid/analysis/readiness field is trusted or retained.
    """

    canonical_snapshot: str

    def __post_init__(self):
        _require(type(self.canonical_snapshot) is str)
        _require(len(self.canonical_snapshot) <= 32_768)
        try:
            snapshot = json.loads(self.canonical_snapshot)
        except (ValueError, TypeError, RecursionError):
            raise ContractError("Invalid first-stage declaration.") from None
        _require(type(snapshot) is dict)
        _require(set(snapshot) == {"version", "intent", "outcome", "answers"})
        _require(snapshot["version"] == FIRST_STAGE_SCHEMA)
        _require(type(snapshot["intent"]) is str and type(snapshot["outcome"]) is str)
        _require(snapshot["outcome"] in dict(ROUTES).get(snapshot["intent"], ()))
        answers = snapshot["answers"]
        _require(type(answers) is dict and 1 <= len(answers) <= 100)
        for key, value in answers.items():
            _text(key, 100)
            values = value if type(value) is list else [value]
            _require(len(values) <= 30)
            for item in values:
                _require(item is None or type(item) in (str, int, float, bool))
                if type(item) is str:
                    _require(len(item) <= 4096)
                    try:
                        item.encode("utf-8")
                    except UnicodeError:
                        raise ContractError(
                            "Invalid first-stage declaration."
                        ) from None
        _require(
            type(answers.get("delivery_mode")) is str
            and answers["delivery_mode"] in {mode.value for mode in Delivery}
        )
        if "risk" in answers:
            _require(type(answers["risk"]) is str and answers["risk"] in RISKS)
        # Exact canonical encoding also rejects duplicate keys, NaN and Infinity.
        _require(self.canonical_snapshot == _canonical(snapshot))

    @classmethod
    def from_snapshot(cls, snapshot):
        _require(type(snapshot) is dict)
        _require(set(snapshot) == {"version", "intent", "outcome", "answers"})
        _require(snapshot["version"] == FIRST_STAGE_SCHEMA)
        _require(type(snapshot["intent"]) is str and type(snapshot["outcome"]) is str)
        _require(snapshot["outcome"] in dict(ROUTES).get(snapshot["intent"], ()))
        _require(type(snapshot["answers"]) is dict and len(snapshot["answers"]) <= 100)
        # Bound flat input before canonical serialization, including list values.
        for key, value in snapshot["answers"].items():
            _text(key, 100)
            values = value if type(value) is list else [value]
            _require(len(values) <= 30)
            for item in values:
                _require(item is None or type(item) in (str, int, float, bool))
                if type(item) is str:
                    _require(len(item) <= 4096)
        return cls(_canonical(snapshot))

    @property
    def delivery(self):
        return Delivery(json.loads(self.canonical_snapshot)["answers"]["delivery_mode"])

    @property
    def binding(self):
        return _digest(
            {"schema": FIRST_STAGE_SCHEMA, "snapshot": self.canonical_snapshot}
        )

    @property
    def risks(self):
        snapshot = json.loads(self.canonical_snapshot)
        declared = snapshot["answers"].get("risk")
        return tuple(
            dict.fromkeys(
                (["fundraising"] if snapshot["intent"] == "fundraise" else [])
                + ([declared] if declared else [])
            )
        )

    @property
    def validation_status(self):
        return "declared_unqualified"


@dataclass(frozen=True, slots=True)
class PlanBounds:
    business_country: str
    account_country: str | None
    target_markets: tuple[str, ...]
    language: str
    currency: str
    timezone: str
    start: date
    end: date
    media_budget_minor: int
    region_declaration: str

    def __post_init__(self):
        _country(self.business_country)
        if self.account_country is not None:
            _country(self.account_country)
        _require(
            type(self.target_markets) is tuple and 1 <= len(self.target_markets) <= 10
        )
        for country in self.target_markets:
            _country(country)
        _require(len(set(self.target_markets)) == len(self.target_markets))
        _text(self.language, 35)
        _currency(self.currency)
        _text(self.timezone, 80)
        try:
            ZoneInfo(self.timezone)
        except (ZoneInfoNotFoundError, ValueError):
            raise ContractError("Unsupported timezone.") from None
        _require(type(self.start) is date and type(self.end) is date)
        _require(1 <= self.days <= 365)
        _integer(self.media_budget_minor)
        _text(self.region_declaration, 500)

    @property
    def days(self):
        """Inclusive local calendar dates; not provider scheduling/pacing."""
        return (self.end - self.start).days + 1


@dataclass(frozen=True, slots=True)
class AccountReference:
    """Account/generation metadata, with no token or permission assertion."""

    provider: str
    account_id: str
    connector_id: UUID
    generation: UUID

    def __post_init__(self):
        _text(self.provider, 50)
        _text(self.account_id, 100)
        _uuid(self.connector_id)
        _uuid(self.generation)


@dataclass(frozen=True, slots=True)
class EvidenceMetric:
    """Structural observation declaration, not attestation of provider access."""

    scope: OwnerScope
    evidence_id: UUID
    metric: str
    source: SourceKind
    status: MetricStatus
    value: Decimal | None
    unit: str
    currency: str | None
    source_as_of: datetime | None
    fetched_at: datetime
    expires_at: datetime
    context_binding: str
    account: AccountReference | None = None
    reason: str | None = None

    def __post_init__(self):
        _require(type(self.scope) is OwnerScope)
        _uuid(self.evidence_id)
        _text(self.metric, 80)
        _require(type(self.source) is SourceKind and type(self.status) is MetricStatus)
        _require(type(self.unit) is str and self.unit in {"count", "money_minor"})
        _require(
            type(self.context_binding) is str
            and re.fullmatch(r"[0-9a-f]{64}", self.context_binding) is not None
        )
        _require(self.account is None or type(self.account) is AccountReference)
        if self.source in {SourceKind.OFFICIAL_FORECAST, SourceKind.PLATFORM_ACTUAL}:
            _require(type(self.account) is AccountReference)
        if self.unit == "money_minor":
            _currency(self.currency)
        else:
            _require(self.currency is None)
        _aware(self.fetched_at)
        _aware(self.expires_at)
        _require(_utc(self.expires_at) > _utc(self.fetched_at))
        if self.source_as_of is not None:
            _aware(self.source_as_of)
            _require(_utc(self.source_as_of) <= _utc(self.fetched_at))
        if self.status is MetricStatus.AVAILABLE:
            _require(type(self.value) is Decimal and self.value.is_finite())
            _require(self.source_as_of is not None)
            _require(self.reason is None)
            if self.unit == "money_minor":
                _require(self.value == self.value.to_integral_value())
            else:
                _require(self.value >= 0)
        else:
            _require(self.value is None)
            _text(self.reason, 200)

    def status_at(self, now):
        _aware(now)
        if _utc(self.fetched_at) > _utc(now):
            return "not_yet_observed"
        if self.status is MetricStatus.AVAILABLE and _utc(now) >= _utc(self.expires_at):
            return MetricStatus.STALE.value
        return self.status.value


@dataclass(frozen=True, slots=True)
class Allocation:
    channel: str
    amount_minor: int
    evidence_ids: tuple[UUID, ...] = ()

    def __post_init__(self):
        _text(self.channel, 80)
        _integer(self.amount_minor, 1)
        _require(type(self.evidence_ids) is tuple)
        for identifier in self.evidence_ids:
            _uuid(identifier)
        _require(len(set(self.evidence_ids)) == len(self.evidence_ids))


@dataclass(frozen=True, slots=True)
class DraftContent:
    brief: DeclaredBrief
    bounds: PlanBounds
    allocations: tuple[Allocation, ...]
    reserve_minor: int
    evidence: tuple[EvidenceMetric, ...] = ()

    def __post_init__(self):
        _require(type(self.brief) is DeclaredBrief and type(self.bounds) is PlanBounds)
        _require(type(self.allocations) is tuple and type(self.evidence) is tuple)
        _require(len(self.allocations) <= 50 and len(self.evidence) <= 200)
        _require(all(type(a) is Allocation for a in self.allocations))
        _require(all(type(e) is EvidenceMetric for e in self.evidence))
        _integer(self.reserve_minor)
        _require(len({a.channel for a in self.allocations}) == len(self.allocations))
        ids = {e.evidence_id for e in self.evidence}
        _require(len(ids) == len(self.evidence))
        _require(all(set(a.evidence_ids) <= ids for a in self.allocations))
        _require(all(e.currency in (None, self.bounds.currency) for e in self.evidence))
        _require(all(e.context_binding == self.context_binding for e in self.evidence))
        _require(
            sum(a.amount_minor for a in self.allocations) + self.reserve_minor
            == self.bounds.media_budget_minor
        )
        if self.brief.delivery in {
            Delivery.ORGANIC,
            Delivery.CONTENT_ONLY,
            Delivery.UNSURE,
        }:
            _require(self.bounds.media_budget_minor == 0 and not self.allocations)

    @property
    def binding(self):
        return _digest({"schema": SCHEMA, "content": self})

    @property
    def context_binding(self):
        return _digest({"schema": SCHEMA, "brief": self.brief, "bounds": self.bounds})

    @property
    def publication_enabled(self):
        return False


@dataclass(frozen=True, slots=True)
class DraftRevision:
    scope: OwnerScope
    revision: int
    request_id: UUID
    content: DraftContent
    recorded_at: datetime

    def __post_init__(self):
        _require(type(self.scope) is OwnerScope and type(self.content) is DraftContent)
        _require(all(e.scope == self.scope for e in self.content.evidence))
        _integer(self.revision, 1)
        _uuid(self.request_id)
        _aware(self.recorded_at)

    @property
    def fingerprint(self):
        return _digest({"schema": SCHEMA, "record": self})


def propose_revision(
    *, trusted_scope, history, request_id, expected_revision, content, now
):
    """Pure revision/replay decision for synthetic rehearsal, not a durable save.

    Full history and trusted_scope must later come from a locked owner service.
    Exact replay returns the original record, not an assertion that it is current.
    No caller-supplied flag can qualify the brief or authorize an external action.
    """
    _require(type(trusted_scope) is OwnerScope and type(content) is DraftContent)
    _require(type(history) is tuple and len(history) <= 10_000)
    _uuid(request_id)
    _integer(expected_revision)
    _aware(now)
    seen = set()
    previous_time = None
    for number, record in enumerate(history, 1):
        _require(type(record) is DraftRevision and record.scope == trusted_scope)
        _require(record.revision == number and record.request_id not in seen)
        instant = _utc(record.recorded_at)
        _require(instant <= _utc(now))
        _require(previous_time is None or instant >= previous_time)
        previous_time = instant
        seen.add(record.request_id)
    for record in history:
        if record.request_id == request_id:
            _require(
                record.content.binding == content.binding
                and expected_revision == record.revision - 1
            )
            return record
    _require(expected_revision == len(history))
    _require(
        content.bounds.start >= now.astimezone(ZoneInfo(content.bounds.timezone)).date()
    )
    return DraftRevision(trusted_scope, len(history) + 1, request_id, content, now)


def matches_current(record, *, trusted_scope, current_revision, content_binding):
    """Exact metadata binding only. A match never establishes execution authority."""
    _require(type(record) is DraftRevision and type(trusted_scope) is OwnerScope)
    _integer(current_revision, 1)
    _text(content_binding, 64)
    return (
        record.scope == trusted_scope
        and record.revision == current_revision
        and record.content.binding == content_binding
    )
