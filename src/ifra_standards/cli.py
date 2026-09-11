"""Command line interface: ``ifra-standards <command>``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .__about__ import __version__
from .client import discover_config, fetch_raw_html
from .diff import diff_standards, format_markdown, load_export
from .export import write
from .parse import parse_standards
from .pdf_detail import DETAIL_FIELDS, fetch_all_details, fetch_standard_detail
from .pdfs import download_pdfs


def _load_standards(args) -> list:
    if getattr(args, "from_raw", None):
        html = Path(args.from_raw).read_text(encoding="utf-8")
    else:
        html = fetch_raw_html(limit=args.limit, polite_delay=args.delay)
        if args.save_raw:
            Path(args.save_raw).write_text(html, encoding="utf-8")
    return parse_standards(html)


def _cmd_fetch(args) -> int:
    standards = _load_standards(args)
    path = write(standards, args.output, fmt=args.format,
                 explode_cas=args.explode_cas, pretty=not args.compact,
                 retrieved_at=not args.stable)
    print(f"Saved {len(standards)} standards to {path}", file=sys.stderr)
    return 0


def _cmd_pdfs(args) -> int:
    if args.from_export:
        standards = load_export(args.from_export)
    else:
        standards = parse_standards(fetch_raw_html(polite_delay=1.0))
    if args.limit:
        standards = standards[: args.limit]
    written = download_pdfs(standards, args.out_dir, overwrite=args.overwrite,
                            delay=args.delay)
    print(f"Downloaded {len(written)} PDFs to {args.out_dir}", file=sys.stderr)
    return 0


def _cmd_diff(args) -> int:
    d = diff_standards(load_export(args.old), load_export(args.new))
    if args.format == "json":
        import json
        out = json.dumps(
            {
                "added": [s.to_dict() for s in d["added"]],
                "removed": [s.to_dict() for s in d["removed"]],
                "changed": [
                    {"document_id": s.document_id, "name": s.name, "changes": deltas}
                    for s, deltas in d["changed"]
                ],
            },
            indent=2, ensure_ascii=False,
        )
    else:
        out = format_markdown(d)
    if args.output:
        Path(args.output).write_text(out + "\n", encoding="utf-8")
    else:
        print(out)
    return 0


def _cmd_token(args) -> int:
    print(discover_config())
    return 0


def _cmd_detail(args) -> int:
    import json

    d = fetch_standard_detail(args.source)
    out = json.dumps(d.to_dict(), indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(out + "\n", encoding="utf-8")
        print(f"Saved to {args.output}", file=sys.stderr)
    else:
        print(out)
    return 0


def _cmd_details(args) -> int:
    import csv
    import json as jsonlib

    if args.from_export:
        standards = load_export(args.from_export)
    else:
        standards = parse_standards(fetch_raw_html(polite_delay=1.0))
    if args.limit:
        standards = standards[: args.limit]

    rows = []
    errors = 0
    total = len(standards)
    for i, row in enumerate(fetch_all_details(standards, pdf_dir=args.pdf_dir,
                                              delay=args.delay), start=1):
        if row["error"]:
            errors += 1
        print(f"  [{i}/{total}] {row['name']}"
              + (f"  -- {row['error']}" if row["error"] else ""), file=sys.stderr)
        rows.append(row)

    fmt = args.format or Path(args.output).suffix.lstrip(".")
    if fmt == "json":
        Path(args.output).write_text(
            jsonlib.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    else:
        with open(args.output, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(DETAIL_FIELDS))
            w.writeheader()
            w.writerows(rows)

    print(f"Saved {total} standards ({errors} with an error reading the PDF) "
          f"to {args.output}", file=sys.stderr)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ifra-standards",
        description="Make a spreadsheet of every published IFRA Standard.",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    f = sub.add_parser("fetch", help="get the list and save it to a file")
    f.add_argument("-o", "--output", default="ifra_standards.csv",
                   help="where to save it (default: %(default)s). "
                        "End the name with .csv, .json, or .xlsx to pick the format.")
    f.add_argument("--format", choices=["csv", "json", "xlsx"],
                   help="force the format instead of guessing from the file name")
    f.add_argument("--explode-cas", action="store_true",
                   help="one row per CAS number (a Standard with several CAS is repeated)")
    f.add_argument("--limit", type=int, default=2000,
                   help="how many rows to ask for in one page (default: %(default)s)")
    f.add_argument("--compact", action="store_true", help="smaller, unformatted JSON")
    f.add_argument("--stable", action="store_true",
                   help="leave out the fetch timestamp, so re-runs produce identical files")
    f.add_argument("--delay", type=float, default=0.5,
                   help="seconds to wait between the two page loads (default: %(default)s)")
    f.add_argument("--save-raw", metavar="PATH", help="also save the raw web page")
    f.add_argument("--from-raw", metavar="PATH",
                   help="read a saved web page instead of going online")
    f.set_defaults(func=_cmd_fetch)

    d = sub.add_parser("pdfs", help="download every Standard PDF into a folder")
    d.add_argument("out_dir", help="folder to put the PDFs in (created if needed)")
    d.add_argument("--from-export", metavar="PATH",
                   help="use a saved .json list instead of fetching a new one")
    d.add_argument("--limit", type=int, default=0, help="only the first N PDFs")
    d.add_argument("--overwrite", action="store_true", help="re-download files that already exist")
    d.add_argument("--delay", type=float, default=1.0,
                   help="seconds between downloads (default: %(default)s)")
    d.set_defaults(func=_cmd_pdfs)

    g = sub.add_parser("diff", help="compare two saved .json lists")
    g.add_argument("old", help="the older .json file")
    g.add_argument("new", help="the newer .json file")
    g.add_argument("-o", "--output", help="write the result to a file instead of the screen")
    g.add_argument("--format", choices=["md", "json"], default="md")
    g.set_defaults(func=_cmd_diff)

    t = sub.add_parser("token", help="print the current access token (for troubleshooting)")
    t.set_defaults(func=_cmd_token)

    e = sub.add_parser(
        "detail",
        help="read one Standard's PDF: its limits, recommendation, and other fields",
    )
    e.add_argument("source", help="a Standard PDF's web address, or a path to one you saved")
    e.add_argument("-o", "--output", help="write to a file instead of the screen")
    e.set_defaults(func=_cmd_detail)

    a = sub.add_parser(
        "details",
        help="read every Standard's PDF: limits and other fields, one row each",
    )
    a.add_argument("-o", "--output", default="ifra_standards_details.csv",
                   help="where to save it (default: %(default)s)")
    a.add_argument("--format", choices=["csv", "json"],
                   help="force the format instead of guessing from the file name")
    a.add_argument("--from-export", metavar="PATH",
                   help="use a saved .json list instead of fetching a new one")
    a.add_argument("--pdf-dir", metavar="DIR",
                   help="a folder of PDFs already saved with 'ifra-standards pdfs'; "
                        "only what is missing gets downloaded")
    a.add_argument("--limit", type=int, default=0, help="only the first N Standards")
    a.add_argument("--delay", type=float, default=1.0,
                   help="seconds between downloads (default: %(default)s)")
    a.set_defaults(func=_cmd_details)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
