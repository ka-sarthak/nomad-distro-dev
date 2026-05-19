#!/usr/bin/env bash
#
# Usage: ./scripts/add_submodule.sh <git-url> [packages/<name>]
#
# Examples:
#   ./scripts/add_submodule.sh https://github.com/FAIRmat-NFDI/nomad-measurements.git
#   ./scripts/add_submodule.sh git@github.com:FAIRmat-NFDI/nomad-measurements.git
#   ./scripts/add_submodule.sh https://github.com/FAIRmat-NFDI/nomad-measurements.git packages/my-measurements
#
# The repo name (without .git) is used as the submodule directory name under packages/.
# Run this script from the repository root.

set -euo pipefail

# ── Helpers ──────────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

die() {
    error "$*"
    exit 1
}

# ── Argument validation ───────────────────────────────────────────────────────

if [[ $# -lt 1 || $# -gt 2 ]]; then
    error "Wrong number of arguments."
    echo "Usage: $0 <git-url> [packages/<name>]" >&2
    echo "Example: $0 https://github.com/FAIRmat-NFDI/nomad-measurements.git" >&2
    exit 1
fi

GIT_URL="$1"

# ── Derive submodule name from URL ────────────────────────────────────────────

# Strip trailing .git and take the last path component
REPO_NAME="$(basename "${GIT_URL}" .git)"

if [[ -z "${REPO_NAME}" ]]; then
    die "Could not derive a repo name from '${GIT_URL}'. Please check the URL."
fi

# Allow optional override of the target path
if [[ $# -eq 2 ]]; then
    SUBMODULE_PATH="${2%/}"  # strip trailing slash
else
    SUBMODULE_PATH="packages/${REPO_NAME}"
fi

SUBMODULE_NAME="$(basename "${SUBMODULE_PATH}")"

# ── Sanity checks ─────────────────────────────────────────────────────────────

if [[ ! -d ".git" ]]; then
    die "No .git directory found. Run this script from the repository root."
fi

if [[ ! -f "pyproject.toml" ]]; then
    die "No pyproject.toml found. Run this script from the repository root."
fi

if [[ -d "${SUBMODULE_PATH}" ]]; then
    die "Directory '${SUBMODULE_PATH}' already exists. Remove it first or choose a different path."
fi

if git config -f .gitmodules --get "submodule.${SUBMODULE_PATH}.url" &>/dev/null; then
    die "Submodule '${SUBMODULE_PATH}' is already registered in .gitmodules."
fi

info "Adding submodule '${SUBMODULE_NAME}' from '${GIT_URL}' → '${SUBMODULE_PATH}' ..."

# ── Step 1: Add the git submodule ─────────────────────────────────────────────

info "Step 1/2 – Running: git submodule add '${GIT_URL}' '${SUBMODULE_PATH}' ..."
git submodule add "${GIT_URL}" "${SUBMODULE_PATH}" \
    || die "git submodule add failed."

# ── Step 2: Add to pyproject.toml via uv ─────────────────────────────────────

info "Step 2/2 – Running: uv add '${SUBMODULE_PATH}' ..."
uv add "${SUBMODULE_PATH}" \
    || die "uv add failed. The submodule was cloned but pyproject.toml was not updated."

info "✓ Submodule '${SUBMODULE_NAME}' successfully added at '${SUBMODULE_PATH}'."
info "  pyproject.toml [project.dependencies] and [tool.uv.sources] have been updated by uv."
info "  Don't forget to commit: git add .gitmodules pyproject.toml uv.lock && git commit"
