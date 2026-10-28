"""Import the owner supplied V2 reference catalogs, without evaluating workbook code.

Only seven declarative catalogs are published. Market scores, forecasts, source
verification claims and integration credentials are deliberately outside this import.
"""

import argparse
import hashlib
import json
import math
import posixpath
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

SOURCE_HASH = "3a1a0b117902d35bda23acb9c56a7e6ba7552b8c012d2a02b81f269c3cf5817d"
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CATALOGS = (
    (
        "intents",
        "01_NIYETLER",
        10,
        "intent_id label_tr base_module sort_order selection",
    ),
    (
        "outcomes",
        "02_SONUCLAR",
        20,
        "outcome_id label_tr module_id primary_kpi measurement_note",
    ),
    (
        "routes",
        "03_ESLESMELER",
        200,
        "route_id intent_id outcome_id route_state recommended_rank show_initial "
        "module_ids kpi requires_goal_confirmation reason_code source_urls",
    ),
    (
        "questions",
        "04_SORULAR",
        131,
        "field_id label_tr module_id stage required_for type option_set_id visible_when "
        "validation help_tr tier sort_order source_kind data_class reask_policy affects "
        "source_urls",
    ),
    ("options", "05_SECENEKLER", 161, "option_set_id value label_tr sort_order"),
    ("modules", "06_MODULLER", 43, "module_id title_tr composition"),
    ("module_rules", "07_FORM_KURALLARI", 10, "rule_id when add_modules"),
)
JSON_COLUMNS = {
    "module_ids": list,
    "visible_when": dict,
    "validation": dict,
    "when": dict,
    "add_modules": list,
    "affects": list,
}
MAX_SOURCE_BYTES = 12 * 1024 * 1024
MAX_XML_BYTES = 16 * 1024 * 1024
MAX_EXPANDED_BYTES = 64 * 1024 * 1024


class CatalogError(ValueError):
    """The supplied artifact does not satisfy the declarative catalog contract."""


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise CatalogError(f"Duplicate JSON property: {key}")
        result[key] = value
    return result


def invalid_constant(value):
    raise CatalogError(f"Non-finite JSON value: {value}")


def xml_member(archive, name):
    try:
        info = archive.getinfo(name)
    except KeyError as exc:
        raise CatalogError(f"Missing workbook member: {name}") from exc
    if info.file_size > MAX_XML_BYTES:
        raise CatalogError(f"Workbook member exceeds size limit: {name}")
    data = archive.read(info)
    if b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
        raise CatalogError("DTD and entity declarations are forbidden")
    try:
        return ET.fromstring(data)
    except ET.ParseError as exc:
        raise CatalogError(f"Malformed XML: {name}") from exc


def cell_value(cell, shared):
    if cell.find("s:f", NS) is not None:
        raise CatalogError("Formulas are forbidden in reference catalogs")
    kind = cell.get("t")
    value = cell.findtext("s:v", default="", namespaces=NS)
    if kind == "inlineStr":
        return "".join(node.text or "" for node in cell.findall(".//s:t", NS))
    if kind == "s":
        try:
            index = int(value)
            if index < 0:
                raise ValueError
            return shared[index]
        except (ValueError, IndexError) as exc:
            raise CatalogError("Invalid shared-string index") from exc
    if kind == "b":
        if value not in {"0", "1"}:
            raise CatalogError("Invalid boolean cell")
        return value == "1"
    if kind in {"str", "d"}:
        return value or None
    if kind not in {None, "n"}:
        raise CatalogError(f"Unsupported or error cell type: {kind}")
    if not value:
        return None
    try:
        numeric = float(value)
        if not math.isfinite(numeric):
            raise ValueError
        return int(numeric) if numeric.is_integer() else numeric
    except ValueError as exc:
        raise CatalogError("Invalid numeric cell") from exc


def read_catalog(archive, member, shared, sheet, columns, count):
    root = xml_member(archive, member)
    records = []
    seen_rows = set()
    header_seen = False
    for row in root.findall("s:sheetData/s:row", NS):
        row_number = int(row.get("r", "0"))
        if row_number in seen_rows or not 1 <= row_number <= 10000:
            raise CatalogError(f"Invalid or duplicate row in {sheet}")
        seen_rows.add(row_number)
        values = {}
        for cell in row.findall("s:c", NS):
            reference = cell.get("r", "")
            match = re.fullmatch(r"([A-Z]{1,3})([1-9][0-9]*)", reference)
            if not match or int(match[2]) != row_number:
                raise CatalogError(f"Invalid cell reference in {sheet}")
            column = 0
            for character in match[1]:
                column = column * 26 + ord(character) - 64
            if column in values:
                raise CatalogError(f"Duplicate cell in {sheet}")
            values[column] = cell_value(cell, shared)
        if row_number < 5:
            continue
        if row_number == 5:
            expected = {index + 1: column for index, column in enumerate(columns)}
            if {
                key: value for key, value in values.items() if value is not None
            } != expected:
                raise CatalogError(f"Unexpected headers in {sheet}")
            header_seen = True
            continue
        if not any(value is not None for value in values.values()):
            continue
        if any(
            key > len(columns) and value is not None for key, value in values.items()
        ):
            raise CatalogError(f"Unexpected populated column in {sheet}")
        record = {column: values.get(index + 1) for index, column in enumerate(columns)}
        for column, expected_type in JSON_COLUMNS.items():
            if column not in record:
                continue
            raw = record[column]
            if not isinstance(raw, str):
                raise CatalogError(
                    f"Expected JSON text in {sheet}:{row_number}:{column}"
                )
            try:
                parsed = json.loads(
                    raw,
                    object_pairs_hook=unique_object,
                    parse_constant=invalid_constant,
                )
            except (ValueError, TypeError) as exc:
                raise CatalogError(
                    f"Invalid JSON in {sheet}:{row_number}:{column}"
                ) from exc
            if not isinstance(parsed, expected_type):
                raise CatalogError(f"Wrong JSON type in {sheet}:{row_number}:{column}")
            record[column] = parsed
        record["source_row"] = row_number
        records.append(record)
    if not header_seen or len(records) != count:
        raise CatalogError(f"Unexpected catalog size/header: {sheet} ({len(records)})")
    return records


def require_ids(records, key, label):
    values = [record[key] for record in records]
    if any(not isinstance(value, str) or not value for value in values):
        raise CatalogError(f"Missing or invalid ID: {label}")
    if len(set(values)) != len(values):
        raise CatalogError(f"Duplicate ID: {label}")
    return set(values)


def validate_catalog(data):
    intents = require_ids(data["intents"], "intent_id", "intent")
    outcomes = require_ids(data["outcomes"], "outcome_id", "outcome")
    modules = require_ids(data["modules"], "module_id", "module")
    fields = require_ids(data["questions"], "field_id", "question")
    require_ids(data["routes"], "route_id", "route")
    require_ids(data["module_rules"], "rule_id", "module rule")
    option_pairs = [(row["option_set_id"], row["value"]) for row in data["options"]]
    if any(
        not all(isinstance(value, str) and value for value in pair)
        for pair in option_pairs
    ) or len(set(option_pairs)) != len(option_pairs):
        raise CatalogError("Invalid or duplicate option ID")
    option_sets = {pair[0] for pair in option_pairs}

    def module_references(values):
        if not isinstance(values, list) or any(
            not isinstance(value, str) or value not in modules for value in values
        ):
            raise CatalogError("Unknown module reference")
        if len(set(values)) != len(values):
            raise CatalogError("Duplicate module reference")

    def condition(value):
        op = value.get("op")
        if op in {"always", "cross_border"}:
            return
        if op in {"all", "any"}:
            children = value.get("args")
            if not isinstance(children, list) or not children:
                raise CatalogError("Invalid composite condition")
            for child in children:
                if not isinstance(child, dict):
                    raise CatalogError("Invalid child condition")
                condition(child)
            return
        if op not in {"eq", "in"} or value.get("field") not in fields | {
            "intent_id",
            "outcome_id",
        }:
            raise CatalogError("Unknown condition operator or field")
        if op == "in" and not isinstance(value.get("value"), list):
            raise CatalogError("Condition membership requires an array")

    for record in data["intents"]:
        module_references([record["base_module"]])
    for record in data["outcomes"]:
        module_references([record["module_id"]])
    route_pairs = []
    for record in data["routes"]:
        route_pairs.append((record["intent_id"], record["outcome_id"]))
        module_references(record["module_ids"])
        if record["route_state"] not in {"resolved", "clarify"}:
            raise CatalogError("Unknown route state")
        if any(
            type(record[key]) is not bool
            for key in ("show_initial", "requires_goal_confirmation")
        ):
            raise CatalogError("Route flags must be booleans")
    if len(set(route_pairs)) != len(route_pairs) or set(route_pairs) != {
        (intent, outcome) for intent in intents for outcome in outcomes
    }:
        raise CatalogError("Routes must cover every intent/outcome pair exactly once")
    referenced_option_sets = set()
    for record in data["questions"]:
        module_references([record["module_id"]])
        option_set = record["option_set_id"]
        if option_set is not None:
            if option_set not in option_sets:
                raise CatalogError("Unknown question option set")
            referenced_option_sets.add(option_set)
        if record["type"] in {"select", "multiselect"} and option_set is None:
            raise CatalogError("Choice question requires an option set")
        condition(record["visible_when"])
        if any(not isinstance(item, str) for item in record["affects"]):
            raise CatalogError("Question affects must contain strings")
    if referenced_option_sets != option_sets:
        raise CatalogError("Unreferenced option set")
    for record in data["module_rules"]:
        module_references(record["add_modules"])
        condition(record["when"])


def import_workbook(source):
    source = Path(source)
    if source.stat().st_size > MAX_SOURCE_BYTES:
        raise CatalogError("Workbook exceeds source size limit")
    raw = source.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != SOURCE_HASH:
        raise CatalogError("Workbook fingerprint differs from the reviewed V2 source")
    with zipfile.ZipFile(source) as archive:
        infos = archive.infolist()
        if len(infos) > 1000 or len({info.filename for info in infos}) != len(infos):
            raise CatalogError("Excessive or duplicate archive members")
        if sum(info.file_size for info in infos) > MAX_EXPANDED_BYTES:
            raise CatalogError("Expanded workbook exceeds size limit")
        workbook = xml_member(archive, "xl/workbook.xml")
        relationships = xml_member(archive, "xl/_rels/workbook.xml.rels")
        targets = {}
        for relation in relationships:
            if relation.get("TargetMode") == "External":
                continue
            target = relation.get("Target", "")
            member = posixpath.normpath(
                target.lstrip("/")
                if target.startswith("/")
                else posixpath.join("xl", target)
            )
            if not member.startswith("xl/") or "\\" in member:
                raise CatalogError("Invalid worksheet path")
            targets[relation.get("Id")] = member
        sheets = {}
        for sheet in workbook.findall("s:sheets/s:sheet", NS):
            name = sheet.get("name")
            if name in sheets:
                raise CatalogError("Duplicate sheet name")
            sheets[name] = targets.get(sheet.get(f"{{{REL_NS}}}id"))
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            strings = xml_member(archive, "xl/sharedStrings.xml")
            shared = [
                "".join(text.text or "" for text in node.findall(".//s:t", NS))
                for node in strings.findall("s:si", NS)
            ]
        data = {
            "version": "yaparo-v2-catalog-1",
            "source_hash": digest,
            "source_name": source.name,
        }
        for key, sheet, count, headers in CATALOGS:
            if not sheets.get(sheet):
                raise CatalogError(f"Missing catalog sheet: {sheet}")
            data[key] = read_catalog(
                archive, sheets[sheet], shared, sheet, headers.split(), count
            )
    validate_catalog(data)
    data["source_qualification"] = {
        "kind": "owner_supplied_reference",
        "header_row": 5,
        "independent_market_verification": False,
        "performance_forecasts_imported": False,
        "live_connectors_imported": False,
        "upstream_test_claims_independently_verified": False,
        "catalogs": {
            key: {"sheet": sheet, "count": len(data[key])}
            for key, sheet, _, _ in CATALOGS
        },
    }
    return data


def render_javascript(data):
    payload = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)
    payload = (
        payload.replace("<", "\\u003c")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )
    return (
        "// Generated by import_v2.py from the fingerprinted owner supplied reference.\n"
        "// Declarative product design; not verified market or performance evidence.\n"
        "(function (root) {\n  'use strict';\n  const catalog = "
        + payload
        + ";\n  if (typeof module !== 'undefined' && module.exports) module.exports = catalog;\n"
        "  root.YaparoV2Catalog = catalog;\n"
        "})(typeof window !== 'undefined' ? window : globalThis);\n"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    parser.add_argument(
        "--output", type=Path, default=Path(__file__).parent / "dist" / "v2-data.js"
    )
    parser.add_argument(
        "--check", action="store_true", help="Compare output without writing"
    )
    args = parser.parse_args()
    try:
        data = import_workbook(args.workbook)
        rendered = render_javascript(data)
        if args.check:
            if (
                not args.output.exists()
                or args.output.read_text(encoding="utf-8") != rendered
            ):
                raise CatalogError("Generated catalog is missing or stale")
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8", newline="\n")
    except (CatalogError, OSError, zipfile.BadZipFile) as exc:
        parser.exit(1, f"V2 catalog import rejected: {exc}\n")
    print(
        json.dumps(
            {
                "source_hash": data["source_hash"],
                "counts": {key: len(data[key]) for key, _, _, _ in CATALOGS},
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
