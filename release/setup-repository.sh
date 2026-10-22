#!/usr/bin/env bash
# Prepares a GitHub repository for releases from signed tags: the environment "release" limited
# to release tags, its secret RELEASE_ALLOWED_SIGNERS, and a ruleset that lets only repository
# admins create, move or delete release tags. Safe to run again.
#
# Usage: setup-repository.sh [<owner/repo>] [<allowed_signers file>]
# Run it in the project: the repository defaults to the origin remote, the allowed signers to
# user.email and user.signingkey of the project's git configuration.
set -euo pipefail

fail() {
	echo "setup-repository: $*" >&2
	exit 1
}

here=$(cd "$(dirname "$0")" && pwd)
repo=${1:-$(gh repo view --json nameWithOwner --jq .nameWithOwner)}
login=$(gh api user --jq .login)
[[ "${repo%%/*}" == "$login" ]] ||
	fail "gh is logged in as $login, not as the owner of $repo; run gh auth switch"

signers=$(mktemp)
trap 'rm -f "$signers"' EXIT
if [[ -n "${2:-}" ]]; then
	cp "$2" "$signers"
else
	key=$(git config user.signingkey || true)
	[[ "$key" == ssh-* ]] || fail "user.signingkey is not an SSH public key; pass an allowed_signers file"
	printf '%s namespaces="git" %s\n' "$(git config user.email)" "$key" >"$signers"
fi

echo "environment release, release tags only"
gh api -X PUT "repos/$repo/environments/release" --silent --input - <<<'{"deployment_branch_policy": {"protected_branches": false, "custom_branch_policies": true}}'
policies=$(gh api "repos/$repo/environments/release/deployment-branch-policies" --jq '.branch_policies[] | select(.type == "tag") | .name')
if ! grep -qx 'v\[0-9\]\*' <<<"$policies"; then
	gh api -X POST "repos/$repo/environments/release/deployment-branch-policies" --silent -f name='v[0-9]*' -f type=tag
fi

echo "secret RELEASE_ALLOWED_SIGNERS:"
cat "$signers"
gh secret set RELEASE_ALLOWED_SIGNERS --repo "$repo" --env release <"$signers"

echo "ruleset release tags"
id=$(gh api "repos/$repo/rulesets" --jq '.[] | select(.name == "release tags") | .id')
if [[ -n "$id" ]]; then
	gh api -X PUT "repos/$repo/rulesets/$id" --silent --input "$here/ruleset.json"
else
	gh api -X POST "repos/$repo/rulesets" --silent --input "$here/ruleset.json"
fi
echo "done; add the signing key to the GitHub account as a signing key for the Verified badge"
