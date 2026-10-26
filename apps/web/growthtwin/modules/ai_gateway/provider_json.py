"""Bounded unambiguous JSON; structural validation, never claim approval."""

import json
import math

from growthtwin.modules.content.creative import (
    CREATIVE_BODY_MAX_LENGTH,
    CREATIVE_CTA_MAX_LENGTH,
    CREATIVE_HEADLINE_MAX_LENGTH,
    CreativeVariant,
)

from .contracts import GENERATOR_ID_MAX_LENGTH, MAX_CREATIVE_VARIANTS

MAX_JSON_BYTES = 65_536
FIELDS = {
    "key": GENERATOR_ID_MAX_LENGTH,
    "angle": GENERATOR_ID_MAX_LENGTH,
    "headline": CREATIVE_HEADLINE_MAX_LENGTH,
    "body": CREATIVE_BODY_MAX_LENGTH,
    "call_to_action": CREATIVE_CTA_MAX_LENGTH,
}


class InvalidProviderJSON(ValueError):
    """Safe generic error; never include provider text in exception messages."""


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InvalidProviderJSON("Yinelenen JSON alanı reddedildi.")
        result[key] = value
    return result


def _constant(value):
    raise InvalidProviderJSON("Sonlu olmayan JSON sayısı reddedildi.")


def _float(value):
    result = float(value)
    if not math.isfinite(result):
        raise InvalidProviderJSON("Sonlu olmayan JSON sayısı reddedildi.")
    return result


def load_provider_object(raw):
    """Outer provider envelopes allow varying fields, but never ambiguity."""
    try:
        if (
            type(raw) is not str
            or not 0 < len(raw) <= MAX_JSON_BYTES
            or len(raw.encode("utf-8")) > MAX_JSON_BYTES
        ):
            raise InvalidProviderJSON("JSON boyutu veya türü geçersiz.")
        value = json.loads(
            raw, object_pairs_hook=_pairs, parse_constant=_constant, parse_float=_float
        )
        if type(value) is not dict:
            raise InvalidProviderJSON("JSON nesnesi gereklidir.")
        return value
    except (ValueError, TypeError, UnicodeError, RecursionError):
        raise InvalidProviderJSON("Sağlayıcı JSON yanıtı doğrulanamadı.") from None


def parse_creative_variants(raw):
    value = load_provider_object(raw)
    if (
        set(value) != {"variants"}
        or type(value["variants"]) is not list
        or not 1 <= len(value["variants"]) <= MAX_CREATIVE_VARIANTS
    ):
        raise InvalidProviderJSON("Reklam yanıt alanları geçersiz.")
    result = []
    for row in value["variants"]:
        if type(row) is not dict or set(row) != set(FIELDS):
            raise InvalidProviderJSON("Reklam seçeneği alanları geçersiz.")
        for field, maximum in FIELDS.items():
            text = row[field]
            if type(text) is not str or not text.strip() or len(text) > maximum:
                raise InvalidProviderJSON("Reklam seçeneği değeri geçersiz.")
            try:
                text.encode("utf-8")
            except UnicodeError:
                raise InvalidProviderJSON(
                    "Reklam seçeneği kodlaması geçersiz."
                ) from None
        result.append(CreativeVariant(**row))
    return tuple(result)
