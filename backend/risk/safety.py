import re

# Additional screening of common instruction-like phrases. Tool authorization and
# server-side source validation remain independent of this heuristic.
_DIRECTIVE = re.compile(
    r"\b(ignore|override|disregard)\s+(all\s+)?(previous|prior|system|developer)\s+(rules|messages|instructions|prompts)\b|\b(reveal|print)\s+(the\s+)?system prompt\b",
    re.I,
)


def contains_directive(value: str) -> bool:
    return bool(_DIRECTIVE.search(value))
