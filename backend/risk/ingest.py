"""Bounded extraction in a disposable process. Only extracted text is staged."""

import csv
import hashlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from .safety import contains_directive

MAX_BYTES = 2 * 1024 * 1024
MAX_TEXT = 64000


def parse(raw: bytes, kind: str) -> list[tuple[str, str]]:
    records = []
    if kind == "pdf":
        if not raw.startswith(b"%PDF-"):
            raise ValueError("Expected a PDF file.")
        reader = PdfReader(io.BytesIO(raw), strict=True)
        if reader.is_encrypted or len(reader.pages) > 32:
            raise ValueError("Use an unencrypted PDF of at most 32 pages.")
        for n, page in enumerate(reader.pages, 1):
            text = page.extract_text() or ""
            records.append((f"Page {n}", text))
            if sum(len(t) for _, t in records) > MAX_TEXT:
                raise ValueError("Extracted text exceeds 64,000 characters.")
    else:
        csv.field_size_limit(8000)
        rows = csv.reader(io.StringIO(raw.decode("utf-8-sig"), newline=""), strict=True)
        headers = next(rows, [])
        if not 1 <= len(headers) <= 20 or any(not h.strip() for h in headers):
            raise ValueError("CSV requires a header with 1–20 named columns.")
        for n, row in enumerate(rows, 2):
            if not row:
                continue
            if n > 501 or len(row) != len(headers):
                raise ValueError("CSV supports up to 500 rows with consistent columns.")
            records.append(
                (f"Row {n}", " · ".join(f"{h}: {v}" for h, v in zip(headers, row, strict=True)))
            )
    if sum(len(t) for _, t in records) > MAX_TEXT:
        raise ValueError("Extracted text exceeds 64,000 characters.")
    chunks = []
    for locator, body in records:
        clean = " ".join(body.split())
        if not clean:
            continue
        for i in range(0, len(clean), 800):
            chunks.append((locator, clean[i : i + 900]))
            if i + 900 >= len(clean):
                break
    if not chunks:
        raise ValueError("No readable text found. Supply text-based PDF pages or CSV data rows.")
    if any("\x00" in body for _, body in chunks):
        raise ValueError("Binary text is unsupported.")
    if any(contains_directive(text) for _, text in records):
        raise ValueError("Document contains instruction-like content and requires source cleanup.")
    return chunks


def stage_file(name: str, raw: bytes) -> dict:
    if (
        not 0 < len(raw) <= MAX_BYTES
        or not name
        or len(name) > 100
        or Path(name).name != name
        or any(ord(ch) < 32 for ch in name)
        or "\\" in name
    ):
        raise ValueError("Use a short filename and a nonempty file of at most 2 MiB.")
    kind = Path(name).suffix.lower().lstrip(".")
    if kind not in {"csv", "pdf"}:
        raise ValueError("Choose a PDF or CSV.")
    try:
        worker = subprocess.run(
            [sys.executable, "-m", "backend.risk.ingest", kind],
            input=raw,
            capture_output=True,
            timeout=6,
            env={
                k: v for k, v in os.environ.items() if k in {"PATH", "LANG", "LC_ALL", "SYSTEMROOT"}
            },
        )
    except subprocess.TimeoutExpired:
        raise ValueError("Document extraction timed out.") from None
    if worker.returncode or not worker.stdout:
        raise ValueError("Document could not be safely extracted.")
    result = json.loads(worker.stdout)
    if "error" in result:
        raise ValueError(result["error"])
    return {
        "title": name,
        "kind": kind.upper(),
        "digest": hashlib.sha256(raw).hexdigest(),
        "entries": result["entries"],
    }


if __name__ == "__main__":
    import resource

    resource.setrlimit(resource.RLIMIT_CPU, (4, 5))
    if sys.platform.startswith("linux"):
        resource.setrlimit(resource.RLIMIT_AS, (384 * 1024**2, 384 * 1024**2))
    try:
        print(json.dumps({"entries": parse(sys.stdin.buffer.read(MAX_BYTES + 1), sys.argv[1])}))
    except (ValueError, UnicodeError, csv.Error, PdfReadError) as exc:
        print(json.dumps({"error": str(exc)[:200]}))
