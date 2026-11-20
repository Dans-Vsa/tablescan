"""Command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from dataclasses import asdict
from typing import List, Optional

from . import __version__
from .loader import read_csv
from .profile import profile_table
from .render_html import render_html
from .render_text import render_issues, render_text


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="tablescan", description="Profile a CSV file.")
    p.add_argument("--version", action="version", version=f"tablescan {__version__}")
    sub = p.add_subparsers(dest="command", required=True)
    prof = sub.add_parser("profile", help="print a profile of a CSV file")
    prof.add_argument("file", help="path to the CSV file, or - for stdin")
    prof.add_argument("--format", choices=["text", "json"], default="text")
    prof.add_argument("--delimiter", help="field delimiter (auto-detected by default)")
    prof.add_argument("--encoding", default="utf-8-sig", help="file encoding (default: utf-8-sig)")
    chk = sub.add_parser("check", help="run data-quality checks; non-zero exit on warnings")
    chk.add_argument("file", help="path to the CSV file, or - for stdin")
    chk.add_argument("--format", choices=["text", "json"], default="text")
    chk.add_argument("--delimiter", help="field delimiter (auto-detected by default)")
    chk.add_argument("--encoding", default="utf-8-sig", help="file encoding (default: utf-8-sig)")
    chk.add_argument("--strict", action="store_true",
                     help="also fail on info-level findings")
    rep = sub.add_parser("report", help="write a self-contained HTML report")
    rep.add_argument("file", help="path to the CSV file, or - for stdin")
    rep.add_argument("-o", "--output", help="output path (default: <file>.report.html)")
    rep.add_argument("--delimiter", help="field delimiter (auto-detected by default)")
    rep.add_argument("--encoding", default="utf-8-sig", help="file encoding (default: utf-8-sig)")
    rep.add_argument("--title", help="report title (default: the file name)")
    return p


def _check(profile, args) -> int:
    failing = [i for i in profile.issues if args.strict or i.severity == "warning"]
    if args.format == "json":
        print(json.dumps({"issues": [asdict(i) for i in profile.issues],
                          "correlations": profile.correlations,
                          "passed": not failing}, indent=2))
    else:
        print("\n".join(render_issues(profile)).rstrip())
    return 2 if failing else 0


def _report(profile, args) -> int:
    out = Path(args.output) if args.output else Path(args.file).with_suffix(".report.html")
    title = args.title or f"{Path(args.file).name} - tablescan report"
    try:
        out.write_text(render_html(profile, title), encoding="utf-8")
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"wrote {out}")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "report" and args.file == "-" and not args.output:
        print("error: report needs -o/--output when reading from stdin", file=sys.stderr)
        return 1
    try:
        table = read_csv(args.file, delimiter=args.delimiter, encoding=args.encoding)
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    profile = profile_table(table)
    if args.command == "report":
        return _report(profile, args)
    if args.command == "check":
        return _check(profile, args)
    if args.format == "json":
        print(json.dumps(profile.to_dict(), indent=2))
    else:
        print(render_text(profile), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
