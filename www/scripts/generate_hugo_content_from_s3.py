#!/usr/bin/env python3
"""Generate Hugo content pages from MP3 objects in an S3 bucket."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

DEFAULT_PUBLIC_BASE_URL = "https://www.nothinglefttolearn.com/001"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="List MP3 objects in an S3 bucket and generate Hugo markdown files."
    )
    parser.add_argument(
        "--bucket",
        default="nltl-001-mp3",
        help="S3 bucket name (default: nltl-001-mp3).",
    )
    parser.add_argument(
        "--prefix",
        default="",
        help="Optional prefix to filter S3 objects.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parents[1] / "content" / "audio"),
        help="Directory where markdown files will be written.",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_PUBLIC_BASE_URL,
        help=(
            "Public base URL for MP3 links. "
            "Defaults to https://www.nothinglefttolearn.com/001/<filename>.mp3."
        ),
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing markdown files.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned writes without creating files.",
    )
    return parser.parse_args()


def run_aws_list_objects(bucket: str, prefix: str, token: str | None) -> Dict:
    cmd = [
        "aws",
        "s3api",
        "list-objects-v2",
        "--bucket",
        bucket,
        "--output",
        "json",
        "--max-keys",
        "1000",
    ]
    if prefix:
        cmd.extend(["--prefix", prefix])
    if token:
        cmd.extend(["--continuation-token", token])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        stderr = result.stderr.strip() or "Unknown error"
        raise RuntimeError(f"Failed to list S3 objects: {stderr}")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("AWS CLI returned invalid JSON.") from exc


def list_mp3_objects(bucket: str, prefix: str) -> List[Dict]:
    objects: List[Dict] = []
    token: str | None = None

    while True:
        payload = run_aws_list_objects(bucket, prefix, token)
        contents = payload.get("Contents", [])
        for obj in contents:
            key = obj.get("Key", "")
            if key.lower().endswith(".mp3") and not key.endswith("/"):
                objects.append(obj)

        if not payload.get("IsTruncated"):
            break
        token = payload.get("NextContinuationToken")
        if not token:
            break

    return objects


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return slug or "untitled"


def title_from_key(key: str) -> str:
    stem = Path(key).stem
    return re.sub(r"[-_]+", " ", stem).strip() or "Untitled"


def parse_last_modified(raw: str | None) -> datetime:
    if not raw:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return datetime.now(timezone.utc)


def build_mp3_url(bucket: str, key: str, base_url: str | None) -> str:
    if base_url:
        filename = Path(key).name
        return f"{base_url.rstrip('/')}/{filename}"
    return f"https://{bucket}.s3.amazonaws.com/{key}"


def toml_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def build_markdown(bucket: str, key: str, last_modified: str | None, base_url: str | None) -> str:
    title = title_from_key(key)
    date = parse_last_modified(last_modified).isoformat()
    mp3_url = build_mp3_url(bucket, key, base_url)

    return f"""+++
title = "{toml_escape(title)}"
date = "{date}"
status = "Play"
mp3_url = "{toml_escape(mp3_url)}"
s3_key = "{toml_escape(key)}"
+++

[Listen to this track]({mp3_url})
"""


def main() -> int:
    args = parse_args()

    output_dir = Path(args.output_dir)
    objects = list_mp3_objects(args.bucket, args.prefix)
    if not objects:
        print("No MP3 objects found; nothing to write.")
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    skipped = 0
    for obj in objects:
        key = obj.get("Key", "")
        stem = Path(key).stem
        slug = slugify(stem)
        out_file = output_dir / f"{slug}.md"

        if out_file.exists() and not args.overwrite:
            skipped += 1
            continue

        body = build_markdown(
            bucket=args.bucket,
            key=key,
            last_modified=obj.get("LastModified"),
            base_url=args.base_url,
        )

        if args.dry_run:
            print(f"Would write: {out_file}")
        else:
            out_file.write_text(body, encoding="utf-8")
            print(f"Wrote: {out_file}")
        written += 1

    print(f"Processed {len(objects)} MP3 objects. Wrote {written} file(s), skipped {skipped}.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
