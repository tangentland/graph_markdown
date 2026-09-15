#!/usr/bin/env bash
# Lint this repo's own GMD docs — gmd dogfooding its own spec.
#
# Scope: the root doc set (README, SPEC, PRIMER, migration guide), the authoring
# templates, and the bundled examples. Uses the in-repo linter directly rather
# than a vendored copy — this repo IS the canonical tooling.
#
# Exit non-zero on errors; warnings are informational.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LINTER="$ROOT/lint.py"

if [[ ! -f "$LINTER" ]]; then
  echo "gmd lint not found at $LINTER" >&2
  exit 2
fi

cd "$ROOT"
SCOPE=(README.md SPEC.md PRIMER.md gmd-migration-guide.md)
[[ -d templates ]] && SCOPE+=(templates/)
[[ -d examples ]] && SCOPE+=(examples/)
exec python3 "$LINTER" "${SCOPE[@]}" "$@"
