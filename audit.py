#!/usr/bin/env python3
"""gmd audit — report and repair GMD conformance gaps across a tree.

`gmd lint` answers "is this valid?" — it fails on broken structure and dangling
links. `gmd audit` answers the different question "is this fully GMD yet?", which
is what a conversion or cleanup pass needs: which files are still plain markdown,
which ids are missing their project namespace, which headings have no anchor.

Findings are grouped so a cleanup can be worked category by category rather than
file by file, and the mechanically unambiguous ones can be applied with --fix.

Usage:
  gmd audit <file-or-dir> [...]           # report
  gmd audit <file-or-dir> [...] --fix     # apply the safe repairs
  gmd audit <dir> --category unprefixed-id    # one category only
  gmd audit <dir> --quiet                 # summary table only

Categories, and whether --fix touches them:

  FIXABLE
    missing-id        no `id:` in frontmatter -> derive from filename stem
    unprefixed-id     id carries no `<project>/` namespace (SPEC §project-namespace)
    bad-id-shape      leading/trailing `/` or `//` (SPEC §3)
    missing-title     no `title:` -> take the first H1's text
    no-root-anchor    no `{#root}` anywhere -> put it on the first H1

  REPORT-ONLY (the repair is a judgment call, not a transform)
    no-gmd            no `gmd:` key; the file is not GMD at all yet
    missing-tags      no `tags:`; which labels apply is editorial
    unanchored-heading   heading with no `{#id}`; anchor names are semantic and
                         become permanent addresses, so they are authored not generated
    stem-mismatch     id's local part differs from the filename stem; either the
                      file or the id should move, and only the author knows which

Exit status: 0 when no findings (or all findings fixed), 1 when findings remain.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lint  # noqa: E402  — reuse the linter's parser, id rules and namespace logic

# Files that are deliberately not GMD. MEMORY.md is the flat per-project memory
# index (see MEMORY-RULES §index); flagging it as unconverted is noise.
NOT_GMD_BY_DESIGN = {"MEMORY.md", "README.md", "CHANGELOG.md", "LICENSE.md"}

FIXABLE = {
    "missing-id", "unprefixed-id", "bad-id-shape",
    "missing-title", "no-root-anchor",
}
REPORT_ONLY = {"no-gmd", "missing-tags", "unanchored-heading", "stem-mismatch"}

H1_RE = re.compile(r"^#\s+(.*?)\s*$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
ANCHOR_RE = re.compile(r"\{#([a-z0-9][a-z0-9._/-]*)[^}]*\}")


@dataclass
class Finding:
    path: Path
    line: int
    category: str
    detail: str
    fix: str | None = None   # human-readable description of what --fix would do


@dataclass
class FileReport:
    path: Path
    findings: list[Finding] = field(default_factory=list)


def _frontmatter(lines: list[str]) -> tuple[dict, int, int]:
    """(fields, fm_start, fm_end) — fm_end is the index of the closing `---`.
    (-1, -1) when the file has no frontmatter block."""
    if not lines or lines[0].strip() != "---":
        return {}, -1, -1
    for j, l in enumerate(lines[1:], 1):
        if l.strip() == "---":
            fm, _ = lint.parse_frontmatter(lines)
            return fm, 0, j
    return {}, -1, -1


def audit_file(path: Path) -> FileReport:
    rep = FileReport(path=path)
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    fm, _fm_start, fm_end = _frontmatter(lines)
    project = lint.project_name(path)

    # --- is it GMD at all? ---
    if not fm.get("gmd"):
        if path.name in NOT_GMD_BY_DESIGN:
            return rep
        rep.findings.append(Finding(
            path, 1, "no-gmd",
            "no `gmd:` key — file is plain markdown, not part of the graph",
        ))
        # Everything below assumes GMD intent; without it the rest is noise.
        return rep

    # --- id ---
    doc_id = fm.get("id")
    if not doc_id:
        suggested = f"{project}/{path.stem}" if project else path.stem
        rep.findings.append(Finding(
            path, 1, "missing-id", "no `id:` in frontmatter",
            f"add `id: {suggested}`",
        ))
    else:
        shape = lint.id_shape_issue(path, 1, "bad-id-shape", doc_id)
        if shape:
            cleaned = re.sub(r"/{2,}", "/", doc_id).strip("/")
            rep.findings.append(Finding(
                path, 1, "bad-id-shape", shape.msg,
                f"rewrite as `id: {cleaned}`",
            ))
        elif "/" not in doc_id and project:
            rep.findings.append(Finding(
                path, 1, "unprefixed-id",
                f"id `{doc_id}` has no project namespace",
                f"rewrite as `id: {project}/{doc_id}`",
            ))
        local = doc_id.rsplit("/", 1)[-1]
        if local and local != path.stem:
            rep.findings.append(Finding(
                path, 1, "stem-mismatch",
                f"id local part `{local}` != filename stem `{path.stem}`",
            ))

    # --- title / tags ---
    first_h1 = next(
        ((i, m.group(1)) for i, l in enumerate(lines)
         if (m := H1_RE.match(l)) and i > fm_end),
        None,
    )
    if not fm.get("title"):
        if first_h1:
            clean = ANCHOR_RE.sub("", first_h1[1]).strip()
            rep.findings.append(Finding(
                path, 1, "missing-title", "no `title:` in frontmatter",
                f'add `title: "{clean}"` (from the first H1)',
            ))
        else:
            rep.findings.append(Finding(
                path, 1, "missing-title",
                "no `title:` and no H1 to derive one from",
            ))
    if not fm.get("tags"):
        rep.findings.append(Finding(path, 1, "missing-tags", "no `tags:`"))

    # --- anchors ---
    in_fence = False
    anchored_ids: set[str] = set()
    unanchored: list[tuple[int, str]] = []
    for i, raw in enumerate(lines, 1):
        if i <= fm_end + 1:
            continue
        if lint.CODE_FENCE_RE.match(raw.strip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        scan = lint.strip_inline_code(raw)
        anchored_ids.update(m.group(1) for m in ANCHOR_RE.finditer(scan))
        hm = HEADING_RE.match(scan)
        if hm and not ANCHOR_RE.search(scan):
            unanchored.append((i, hm.group(2)))

    if "root" not in anchored_ids:
        if first_h1:
            rep.findings.append(Finding(
                path, first_h1[0] + 1, "no-root-anchor",
                "no `{#root}` anchor in the document",
                "add `{#root}` to the first H1",
            ))
        else:
            rep.findings.append(Finding(
                path, 1, "no-root-anchor",
                "no `{#root}` anchor and no H1 to attach one to",
            ))
    for line_no, htext in unanchored:
        rep.findings.append(Finding(
            path, line_no, "unanchored-heading",
            f"heading `{htext[:52]}` has no `{{#id}}`",
        ))
    return rep


def apply_fixes(rep: FileReport) -> list[str]:
    """Apply the FIXABLE findings for one file. Returns what was changed."""
    fixable = [f for f in rep.findings if f.category in FIXABLE and f.fix]
    if not fixable:
        return []
    text = rep.path.read_text(encoding="utf-8")
    lines = text.splitlines()
    fm, _s, fm_end = _frontmatter(lines)
    if fm_end < 0:
        return []
    done: list[str] = []

    def set_fm(key: str, value: str) -> None:
        for i in range(1, fm_end):
            if lines[i].startswith(f"{key}:"):
                lines[i] = f"{key}: {value}"
                return
        lines.insert(fm_end, f"{key}: {value}")

    project = lint.project_name(rep.path)
    for f in fixable:
        if f.category in ("missing-id", "unprefixed-id", "bad-id-shape"):
            cur = fm.get("id")
            if f.category == "missing-id":
                new = f"{project}/{rep.path.stem}" if project else rep.path.stem
            elif f.category == "unprefixed-id":
                new = f"{project}/{cur}"
            else:
                new = re.sub(r"/{2,}", "/", str(cur)).strip("/")
            set_fm("id", new)
            done.append(f"id -> {new}")
        elif f.category == "missing-title":
            h1m = next((m for i, l in enumerate(lines)
                        if i > fm_end and (m := H1_RE.match(l))), None)
            if h1m:
                title = ANCHOR_RE.sub("", h1m.group(1)).strip()
                set_fm("title", f'"{title}"')
                done.append(f"title -> {title}")
        elif f.category == "no-root-anchor":
            for i, l in enumerate(lines):
                if i > fm_end and H1_RE.match(l) and not ANCHOR_RE.search(l):
                    lines[i] = l.rstrip() + " {#root}"
                    done.append("added {#root} to the first H1")
                    break
    if done:
        rep.path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return done


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        prog="gmd audit", add_help=True,
        description="Report and repair GMD conformance gaps.")
    ap.add_argument("targets", nargs="+", help="files or directories")
    ap.add_argument("--fix", action="store_true",
                    help="apply the mechanically safe repairs")
    ap.add_argument("--category", action="append", default=[],
                    help="restrict to a category (repeatable)")
    ap.add_argument("--quiet", action="store_true",
                    help="summary table only, no per-file detail")
    args = ap.parse_args(argv[1:])

    root = lint._repo_root(Path(args.targets[0]))
    ignore = lint.load_config(root).get("ignore") if root else []
    files = lint.collect_files(args.targets, ignore or [])
    if not files:
        print("gmd audit: no files matched", file=sys.stderr)
        return 2

    reports = [audit_file(f) for f in files]
    if args.category:
        keep = set(args.category)
        for r in reports:
            r.findings = [f for f in r.findings if f.category in keep]

    fixed_counts: dict[str, int] = defaultdict(int)
    if args.fix:
        for r in reports:
            for _ in apply_fixes(r):
                pass
            # Re-audit so the report reflects reality after the write.
            before = {f.category for f in r.findings if f.category in FIXABLE}
            r.findings = audit_file(r.path).findings
            if args.category:
                r.findings = [f for f in r.findings if f.category in set(args.category)]
            after = {f.category for f in r.findings}
            for c in before - after:
                fixed_counts[c] += 1

    by_cat: dict[str, list[Finding]] = defaultdict(list)
    for r in reports:
        for f in r.findings:
            by_cat[f.category].append(f)

    if not args.quiet:
        for r in sorted(reports, key=lambda r: str(r.path)):
            if not r.findings:
                continue
            print(f"\n{r.path}")
            for f in sorted(r.findings, key=lambda f: (f.line, f.category)):
                tag = "FIX" if f.category in FIXABLE else "   "
                print(f"  {tag} {f.line:>4}: [{f.category}] {f.detail}")
                if f.fix and not args.fix:
                    print(f"            -> {f.fix}")

    total = sum(len(v) for v in by_cat.values())
    clean = sum(1 for r in reports if not r.findings)
    print(f"\ngmd audit: {len(files)} files, {clean} clean, {total} findings")
    if by_cat:
        width = max(len(c) for c in by_cat)
        for cat in sorted(by_cat, key=lambda c: (-len(by_cat[c]), c)):
            kind = "fixable" if cat in FIXABLE else "manual"
            print(f"  {cat:<{width}}  {len(by_cat[cat]):>4}  ({kind})")
    if fixed_counts:
        print("\n  repaired:")
        for cat, n in sorted(fixed_counts.items()):
            print(f"    {cat}: {n} file(s)")
    remaining_fixable = sum(len(v) for c, v in by_cat.items() if c in FIXABLE)
    if remaining_fixable and not args.fix:
        print(f"\n  {remaining_fixable} finding(s) are fixable: re-run with --fix")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
