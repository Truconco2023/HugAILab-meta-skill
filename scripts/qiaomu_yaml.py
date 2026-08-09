"""Minimal YAML-subset loader used when PyYAML is unavailable.

The Qiaomu/HugAILab scripts only need a small, predictable subset of YAML:
nested mappings, block and flow lists, quoted/plain scalars, booleans, nulls,
numbers, comments, and ``|``/``>`` block scalars.  This module implements that
subset with the standard library so package validation and Skill IR export keep
working on machines without PyYAML (for example Codex's bundled Python).

It is intentionally not a general YAML parser.  When PyYAML is installed the
scripts prefer it; this loader is the dependency-light fallback.
"""

from __future__ import annotations

import re
from typing import Any


SCRIPT_INTERFACE = "internal-module"

_BLOCK_SCALAR_RE = re.compile(r"^[|>][+-]?\d*$")
_INT_RE = re.compile(r"^[-+]?\d+$")
_FLOAT_RE = re.compile(r"^[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?$")
_NULL_WORDS = {"null", "~", ""}
_BOOL_WORDS = {"true": True, "false": False, "yes": True, "no": False, "on": True, "off": False}


class YamlSubsetError(ValueError):
    """Raised when the input uses YAML features outside the supported subset."""


def _strip_comment(line: str) -> str:
    in_single = False
    in_double = False
    for index, char in enumerate(line):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double and (index == 0 or line[index - 1] in " \t"):
            return line[:index].rstrip()
    return line.rstrip()


def _tokenize(text: str) -> list[tuple[int, str]]:
    tokens: list[tuple[int, str]] = []
    for raw in text.splitlines():
        if "\t" in raw[: len(raw) - len(raw.lstrip(" \t"))]:
            raise YamlSubsetError("tab indentation is not supported")
        stripped = _strip_comment(raw)
        if not stripped.strip():
            continue
        indent = len(stripped) - len(stripped.lstrip(" "))
        tokens.append((indent, stripped.lstrip(" ")))
    return tokens


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    if len(value) >= 2 and value[0] == value[-1] == '"':
        body = value[1:-1]
        return (
            body.replace('\\"', '"')
            .replace("\\n", "\n")
            .replace("\\t", "\t")
            .replace("\\\\", "\\")
        )
    return value


def _parse_plain_scalar(value: str) -> Any:
    lowered = value.lower()
    if lowered in _NULL_WORDS:
        return None
    if lowered in _BOOL_WORDS:
        return _BOOL_WORDS[lowered]
    if _INT_RE.fullmatch(value):
        return int(value)
    if _FLOAT_RE.fullmatch(value):
        return float(value)
    return value


def _parse_flow_list(value: str) -> list[Any]:
    body = value.strip()
    if not body.startswith("[") or not body.endswith("]"):
        raise YamlSubsetError(f"invalid flow list: {value!r}")
    inner = body[1:-1].strip()
    if not inner:
        return []
    items: list[str] = []
    current: list[str] = []
    in_single = False
    in_double = False
    depth = 0
    for char in inner:
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif not in_single and not in_double:
            if char in "[{":
                depth += 1
            elif char in "]}":
                depth -= 1
        if char == "," and depth == 0 and not in_single and not in_double:
            items.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    items.append("".join(current).strip())
    return [_parse_inline(item) for item in items if item != ""]


def _parse_inline(value: str) -> Any:
    value = value.strip()
    if not value:
        return None
    if value.startswith("["):
        return _parse_flow_list(value)
    if value[0] in "'\"":
        return _unquote(value)
    return _parse_plain_scalar(value)


def _split_key(content: str) -> tuple[str | None, str | None]:
    in_single = False
    in_double = False
    depth = 0
    for index, char in enumerate(content):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif not in_single and not in_double:
            if char in "[{":
                depth += 1
            elif char in "]}":
                depth -= 1
            elif char == ":" and depth == 0:
                key = content[:index].strip()
                if not key:
                    raise YamlSubsetError(f"empty mapping key: {content!r}")
                rest = content[index + 1 :].strip()
                return _unquote(key), rest
    return None, None


def _is_block_scalar_marker(value: str) -> bool:
    return bool(_BLOCK_SCALAR_RE.fullmatch(value))


def _collect_block_scalar(
    tokens: list[tuple[int, str]], index: int, parent_indent: int
) -> tuple[list[str], int]:
    collected: list[str] = []
    content_indent: int | None = None
    cursor = index
    while cursor < len(tokens) and tokens[cursor][0] > parent_indent:
        indent, content = tokens[cursor]
        if content_indent is None:
            content_indent = indent
        collected.append(" " * (indent - content_indent) + content)
        cursor += 1
    return collected, cursor


def _decode_block_scalar(marker: str, lines: list[str]) -> str:
    folded = marker.startswith(">")
    chomping = "-" if "-" in marker else ("+" if "+" in marker else "")
    text = "\n".join(lines)
    if folded:
        paragraphs = re.split(r"\n\s*\n", text)
        text = "\n".join(" ".join(paragraph.split()) for paragraph in paragraphs)
    if chomping == "-":
        text = text.rstrip("\n")
    elif chomping == "":
        text = text.rstrip("\n") + "\n"
    return text


def _parse_mapping(
    tokens: list[tuple[int, str]], index: int, indent: int
) -> tuple[dict[str, Any], int]:
    result: dict[str, Any] = {}
    cursor = index
    while cursor < len(tokens):
        current_indent, content = tokens[cursor]
        if current_indent < indent:
            break
        if current_indent > indent:
            raise YamlSubsetError(f"unexpected indentation: {content!r}")
        if content.startswith("-"):
            break
        key, rest = _split_key(content)
        if key is None:
            raise YamlSubsetError(f"expected mapping entry, got: {content!r}")
        cursor += 1
        if rest is None or rest == "":
            if cursor < len(tokens) and tokens[cursor][0] > indent:
                child, cursor = _parse_block(tokens, cursor, tokens[cursor][0])
                result[key] = child
            else:
                result[key] = None
        elif _is_block_scalar_marker(rest):
            raw, cursor = _collect_block_scalar(tokens, cursor, indent)
            result[key] = _decode_block_scalar(rest, raw)
        else:
            result[key] = _parse_inline(rest)
    return result, cursor


def _parse_sequence(
    tokens: list[tuple[int, str]], index: int, indent: int
) -> tuple[list[Any], int]:
    result: list[Any] = []
    cursor = index
    while cursor < len(tokens):
        current_indent, content = tokens[cursor]
        if current_indent != indent or not content.startswith("-"):
            break
        rest = content[1:].strip()
        cursor += 1
        if not rest:
            if cursor < len(tokens) and tokens[cursor][0] > indent:
                child, cursor = _parse_block(tokens, cursor, tokens[cursor][0])
                result.append(child)
            else:
                result.append(None)
        elif _is_block_scalar_marker(rest):
            raw, cursor = _collect_block_scalar(tokens, cursor, indent)
            result.append(_decode_block_scalar(rest, raw))
        elif _split_key(rest)[0] is not None and not rest.startswith(("[", "'", '"')):
            inline: list[tuple[int, str]] = [(indent + 1, rest)]
            while cursor < len(tokens) and tokens[cursor][0] > indent:
                inline.append(tokens[cursor])
                cursor += 1
            child, _ = _parse_mapping(inline, 0, indent + 1)
            result.append(child)
        else:
            result.append(_parse_inline(rest))
    return result, cursor


def _parse_block(
    tokens: list[tuple[int, str]], index: int, indent: int
) -> tuple[Any, int]:
    if index >= len(tokens):
        return None, index
    content = tokens[index][1]
    if content.startswith("-"):
        return _parse_sequence(tokens, index, indent)
    if _split_key(content)[0] is not None:
        return _parse_mapping(tokens, index, indent)
    value, next_index = _parse_inline(content), index + 1
    return value, next_index


def safe_load(text: str) -> Any:
    """Parse a YAML-subset document and return the corresponding Python value."""
    tokens = _tokenize(text)
    if not tokens:
        return None
    value, _ = _parse_block(tokens, 0, tokens[0][0])
    return value
