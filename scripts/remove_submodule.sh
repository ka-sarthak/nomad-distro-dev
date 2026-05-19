#!/usr/bin/env bash
#
# Usage: ./scripts/remove_submodule.sh <submodule-path>
#
# Example: ./scripts/remove_submodule.sh packages/nomad-measurements
#
# Run this script from the repository root.

set -euo pipefail

# ── Helpers ──────────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

die() {
    error "$*"
    exit 1
}

# ── Argument validation ───────────────────────────────────────────────────────

if [[ $# -ne 1 ]]; then
    error "Wrong number of arguments."
    echo "Usage: $0 <submodule-path>" >&2
    echo "Example: $0 packages/nomad-measurements" >&2
    exit 1
fi

SUBMODULE_PATH="${1%/}"                        # strip any trailing slash
SUBMODULE_NAME="$(basename "${SUBMODULE_PATH}")"
SUBMODULE_KEY="submodule.${SUBMODULE_PATH}"

# ── Sanity checks ─────────────────────────────────────────────────────────────

# Must be run from the repo root (where .git exists)
if [[ ! -d ".git" ]]; then
    die "No .git directory found. Run this script from the repository root."
fi

# Check the submodule is actually registered
if ! git config -f .gitmodules --get "${SUBMODULE_KEY}.url" &>/dev/null; then
    die "Submodule '${SUBMODULE_PATH}' not found in .gitmodules. " \
        "Check the name and try again."
fi

info "Removing submodule '${SUBMODULE_PATH}' ..."

# ── Step 1: Remove from the index ────────────────────────────────────────────

info "Step 1/6 – Removing '${SUBMODULE_PATH}' from the Git index ..."
if git ls-files --error-unmatch "${SUBMODULE_PATH}" &>/dev/null; then
    git rm --cached "${SUBMODULE_PATH}" || die "Failed to remove '${SUBMODULE_PATH}' from the index."
else
    warn "'${SUBMODULE_PATH}' is not tracked in the index (already removed)."
fi

# ── Step 2: Remove the submodule directory ───────────────────────────────────

info "Step 2/6 – Removing directory '${SUBMODULE_PATH}' ..."
if [[ -d "${SUBMODULE_PATH}" ]]; then
    rm -rf "${SUBMODULE_PATH}" || die "Failed to remove directory '${SUBMODULE_PATH}'."
else
    warn "Directory '${SUBMODULE_PATH}' does not exist (already removed)."
fi

# ── Step 3: Remove the submodule's internal .git directory ───────────────────

info "Step 3/6 – Removing .git/modules/${SUBMODULE_PATH} ..."
GIT_MODULE_DIR=".git/modules/${SUBMODULE_PATH}"
if [[ -d "${GIT_MODULE_DIR}" ]]; then
    rm -rf "${GIT_MODULE_DIR}" || die "Failed to remove '${GIT_MODULE_DIR}'."
else
    warn "'${GIT_MODULE_DIR}' does not exist (already removed)."
fi

# ── Step 4: Remove entry from .gitmodules ────────────────────────────────────

info "Step 4/6 – Removing entry from .gitmodules ..."
if ! git config -f .gitmodules --remove-section "${SUBMODULE_KEY}" 2>/dev/null; then
    warn "Entry not found in .gitmodules (already removed or never added)."
fi

# ── Step 5: Remove entry from .git/config ────────────────────────────────────

info "Step 5/6 – Removing entry from .git/config ..."
if ! git config --remove-section "${SUBMODULE_KEY}" 2>/dev/null; then
    warn "Entry not found in .git/config (already removed or never added)."
fi

# ── Step 6: Remove from pyproject.toml ──────────────────────────────────────

info "Step 6/7 – Removing '${SUBMODULE_NAME}' from pyproject.toml ..."
PYPROJECT="pyproject.toml"

if [[ ! -f "${PYPROJECT}" ]]; then
    warn "No pyproject.toml found – skipping."
else
    python3 - "${PYPROJECT}" "${SUBMODULE_NAME}" <<'PYEOF'
import sys
import re

pyproject_path = sys.argv[1]
name = sys.argv[2]

with open(pyproject_path, encoding="utf-8") as fh:
    original = fh.read()

lines = original.splitlines(keepends=True)
result = []
removed_src = False

# For [tool.uv.sources]: name = { ... }
src_pattern = re.compile(
    r'^\s*' + re.escape(name).replace(r'\-', r'[\-_]') + r'\s*=\s*\{',
    re.IGNORECASE,
)

for line in lines:
    if src_pattern.match(line):
        removed_src = True
        continue  # drop the line
    result.append(line)

if not removed_src:
    print(f"  [WARN] '{name}' not found in [tool.uv.sources] – nothing changed.")
    sys.exit(0)

with open(pyproject_path, "w", encoding="utf-8") as fh:
    fh.writelines(result)

print(f"  Removed [tool.uv.sources] entry for '{name}'.")
PYEOF

    if [[ $? -ne 0 ]]; then
        die "Failed to update pyproject.toml."
    fi
fi

# ── Step 7: Commit the changes ───────────────────────────────────────────────

info "Step 7/7 – Committing changes ..."
git add .gitmodules "${PYPROJECT}" || die "Failed to stage files."

if git diff --cached --quiet; then
    warn "Nothing to commit (working tree already clean)."
else
    git commit -m "Remove ${SUBMODULE_NAME} submodule" \
        || die "Git commit failed."
fi

info "✓ Submodule '${SUBMODULE_NAME}' successfully removed."
