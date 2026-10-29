"""Pure owned bank validation; schema-valid declarations are not verified facts."""

import json
import math
import re
from dataclasses import dataclass
from datetime import date
from ipaddress import IPv4Address, IPv6Address
from urllib.parse import urlsplit

from .bank import VERSION as BANK_VERSION
from .bank import fields_for
from .contracts import (
    FIRST_STAGE_SCHEMA,
    ROUTES,
    ContractError,
    DeclaredBrief,
    _canonical,
    _digest,
)

VALIDATOR_VERSION = "yaparo-server-first-stage-v1"
# ECMAScript trim/whitespace set, unlike Python str.strip and regex \s.
JS_SPACE = "\u0009\u000a\u000b\u000c\u000d\u0020\u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000\ufeff"


@dataclass(frozen=True, slots=True)
class ValidationResult:
    canonical_snapshot: str | None
    errors: tuple[tuple[str, str], ...]
    removed_fields: tuple[str, ...] = ()

    @property
    def valid(self):
        return not self.errors

    @property
    def answers(self):
        # Fresh detached dictionary on every access, never mutable authority.
        return (
            json.loads(self.canonical_snapshot)["answers"]
            if self.canonical_snapshot
            else {}
        )


def _utf16_length(value):
    return len(value.encode("utf-16-le")) // 2


def _envelope(snapshot):
    if type(snapshot) is not dict or set(snapshot) != {
        "version",
        "intent",
        "outcome",
        "answers",
    }:
        raise ContractError("Invalid first-stage envelope.")
    if snapshot["version"] != FIRST_STAGE_SCHEMA:
        raise ContractError("Unsupported first-stage version.")
    intent, outcome, answers = (
        snapshot["intent"],
        snapshot["outcome"],
        snapshot["answers"],
    )
    if (
        type(intent) is not str
        or type(outcome) is not str
        or outcome not in dict(ROUTES).get(intent, ())
    ):
        raise ContractError("Unsupported first-stage route.")
    if type(answers) is not dict or len(answers) > 100:
        raise ContractError("Invalid first-stage answers.")
    for key, value in answers.items():
        if type(key) is not str or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,99}", key):
            raise ContractError("Invalid first-stage answer key.")
        items = value if type(value) is list else [value]
        if len(items) > 30:
            raise ContractError("Too many answer values.")
        for item in items:
            if item is not None and type(item) not in (str, int, float, bool):
                raise ContractError("Invalid answer type.")
            if type(item) is str:
                try:
                    if _utf16_length(item) > 4096:
                        raise ContractError("Answer too long.")
                except UnicodeError:
                    raise ContractError("Invalid answer encoding.") from None
            if type(item) in (int, float) and (
                not math.isfinite(item) or abs(item) > 1e15
            ):
                raise ContractError("Invalid numeric answer.")
    if len(_canonical(snapshot).encode("utf-8")) > 32768:
        raise ContractError("First-stage envelope too large.")
    return intent, outcome, answers


def _prune(intent, outcome, original):
    answers = {
        k: (
            [item if type(item) is str else None for item in v]
            if type(v) is list
            else v.strip(JS_SPACE)
            if type(v) is str
            else v
            if type(v) in (int, float)
            else None
        )
        for k, v in original.items()
    }
    for _ in range(100):
        active = {f.id for f in fields_for(intent, outcome, answers)}
        reduced = {
            k: v
            for k, v in answers.items()
            if k in active and v != "" and not (type(v) is list and not v)
        }
        if len(reduced) == len(answers):
            return reduced
        answers = reduced
    raise ContractError("Question visibility did not converge.")


def _valid_url(value):
    if not re.match(r"https?://", value, re.I):
        return False
    if any(c in JS_SPACE or ord(c) < 32 or ord(c) == 127 or c == "\\" for c in value):
        return False
    try:
        parts = urlsplit(value)
        host = parts.hostname
        if not host or parts.username is not None or parts.password is not None:
            return False
        if parts.port is not None and not 0 <= parts.port <= 65535:
            return False
        # No URL is fetched. Ambiguous encoded hosts are deliberately refused.
        if any(c in "%<>^|{}\u200c\u200d" for c in host):
            return False
        ascii_host = host.encode("idna").decode("ascii")
        if parts.netloc.startswith("["):
            IPv6Address(ascii_host)
        else:
            last = ascii_host.rstrip(".").split(".")[-1]
            if re.fullmatch(r"[0-9]+|0[xX][0-9a-fA-F]+", last):
                # Reject invalid numeric hosts and ambiguous legacy IPv4 forms.
                IPv4Address(ascii_host)
        return True
    except (ValueError, UnicodeError):
        return False


def _valid_field(field, value):
    if field.type == "number":
        return (
            type(value) in (int, float)
            and math.isfinite(value)
            and field.minimum <= value <= field.maximum
            and (not field.integer or value == int(value))
        )
    if field.type == "select":
        return type(value) is str and value in {v for v, _ in field.options}
    if field.type == "multiselect":
        return (
            type(value) is list
            and all(type(v) is str for v in value)
            and len(set(value)) == len(value)
            and all(v in {option for option, _ in field.options} for v in value)
        )
    if (
        type(value) is not str
        or not value.strip(JS_SPACE)
        or _utf16_length(value) > field.max_length
    ):
        return False
    # Harden literal declarations without interpreting them as HTML or commands.
    allowed_controls = "\r\n\t" if field.type == "textarea" else ""
    if any((ord(c) < 32 and c not in allowed_controls) or ord(c) == 127 for c in value):
        return False
    if field.type == "url":
        return _valid_url(value)
    if field.type == "date":
        try:
            return (
                re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value) is not None
                and 1900 <= date.fromisoformat(value).year <= 2200
            )
        except ValueError:
            return False
    if field.type == "time":
        return re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", value) is not None
    if field.type == "tel":
        return (
            re.fullmatch(r"\+?[0-9 ()-]+", value) is not None
            and 7 <= len(re.sub(r"[^0-9]", "", value)) <= 15
        )
    if field.type == "email":
        return re.fullmatch(r"[^@<>]+@[^@<>]+\.[^@<>]+", value) is not None and not any(
            c in JS_SPACE for c in value
        )
    return True


def validate_snapshot(snapshot, *, prune_hidden=False):
    """Default rejects unknown/inactive keys; explicit prune mode returns a preview.

    A successful result validates form semantics only; never account/policy facts.
    Error keys come from the trusted bank, not arbitrary caller strings.
    """
    if type(prune_hidden) is not bool:
        raise ContractError("Explicit prune mode required.")
    try:
        intent, outcome, original = _envelope(snapshot)
        answers = _prune(intent, outcome, original)
    except (ContractError, OverflowError):
        return ValidationResult(None, (("_snapshot", "invalid_envelope"),))
    fields = fields_for(intent, outcome, answers)
    errors = {}
    active = {f.id for f in fields}
    hidden = set(original) - active
    if hidden and not prune_hidden:
        errors["_hidden"] = "inactive_or_unknown_answers"
    for field in fields:
        if field.id not in answers:
            if field.required:
                errors[field.id] = "required"
        elif not _valid_field(field, answers[field.id]):
            errors[field.id] = "invalid_value"
    for prefix in ("sell", "event", "fundraise", "announce", "community"):
        start, end = answers.get(prefix + "_start"), answers.get(prefix + "_end")
        if type(start) is str and type(end) is str and end < start:
            errors[prefix + "_end"] = "end_before_start"
    for prefix in (
        "event_location",
        "hire_location",
        "announce_location",
        "community_location",
        "action_location",
    ):
        if (
            prefix + "_address" in active
            and not answers.get(prefix + "_address")
            and not answers.get(prefix + "_map_url")
        ):
            errors[prefix + "_address"] = "location_required"
    if (
        intent == "event"
        and outcome == "visit"
        and answers.get("event_mode") == "online"
    ):
        errors["event_mode"] = "physical_visit_required"
    price, regular = answers.get("sell_price"), answers.get("sell_regular_price")
    if (
        answers.get("sell_offer") == "discount"
        and type(price) in (int, float)
        and type(regular) in (int, float)
        and price > regular
    ):
        errors["sell_price"] = "discount_exceeds_regular"
    qualifications = answers.get("hire_qualifications")
    if (
        type(qualifications) is list
        and "none" in qualifications
        and "experience" in qualifications
    ):
        errors["hire_qualifications"] = "conflicting_experience"
    start, end = answers.get("announce_hours_start"), answers.get("announce_hours_end")
    if (
        type(start) is str
        and type(end) is str
        and answers.get("announce_overnight") == "no"
        and end <= start
    ):
        errors["announce_hours_end"] = "same_day_end_required"
    canonical = _canonical(
        {
            "version": FIRST_STAGE_SCHEMA,
            "intent": intent,
            "outcome": outcome,
            "answers": answers,
        }
    )
    return ValidationResult(
        canonical, tuple(sorted(errors.items())), tuple(sorted(hidden))
    )


@dataclass(frozen=True, slots=True)
class AcceptedBrief:
    """Server bank-valid user declaration; NOT verified truth or action consent."""

    canonical_snapshot: str

    def __post_init__(self):
        if (
            type(self.canonical_snapshot) is not str
            or len(self.canonical_snapshot) > 32768
        ):
            raise ContractError("Invalid accepted brief.")
        try:
            snapshot = json.loads(self.canonical_snapshot)
        except (ValueError, RecursionError):
            raise ContractError("Invalid accepted brief.") from None
        result = validate_snapshot(snapshot)
        if not result.valid or result.canonical_snapshot != self.canonical_snapshot:
            raise ContractError("Accepted brief must be canonical and bank-valid.")

    @classmethod
    def from_snapshot(cls, snapshot):
        result = validate_snapshot(snapshot)
        if not result.valid:
            raise ContractError("First-stage form is not valid.")
        return cls(result.canonical_snapshot)

    @property
    def binding(self):
        return _digest(
            {
                "validator": VALIDATOR_VERSION,
                "bank": BANK_VERSION,
                "snapshot": self.canonical_snapshot,
            }
        )

    @property
    def declaration(self):
        # Old declaration remains unqualified; no automatic DraftContent promotion.
        return DeclaredBrief(self.canonical_snapshot)

    @property
    def validation_status(self):
        return "server_form_valid_declaration"

    @property
    def publication_enabled(self):
        return False
