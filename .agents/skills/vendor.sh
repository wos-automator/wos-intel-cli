#!/bin/sh
# Vendors a version of agent-skills into .agents/skills of the current git repository: clones the
# tag, verifies its SSH signature against the allowed signers, replaces the directory with the
# tag's content (without the files marked export-ignore) and writes VERSION. The result is staged;
# commit it as one signed commit "chore(agents): vendor agent-skills v<version>".
#
# Usage: vendor.sh v<version>
# Environment: AGENT_SKILLS_URL     the library (default https://github.com/thst71/agent-skills.git)
#              AGENT_SKILLS_SIGNERS allowed_signers file (default ~/.agents/allowed_signers)
set -eu

fail() {
	echo "vendor.sh: $*" >&2
	exit 1
}

main() {
	tag=${1:-}
	url=${AGENT_SKILLS_URL:-https://github.com/thst71/agent-skills.git}
	signers=${AGENT_SKILLS_SIGNERS:-$HOME/.agents/allowed_signers}
	case $tag in
	v[0-9]*.[0-9]*.[0-9]*) ;;
	*) fail "usage: vendor.sh v<major>.<minor>.<patch>" ;;
	esac
	[ -f "$signers" ] ||
		fail "no allowed signers in $signers; add the line '<email> namespaces=\"git\" <ssh public key>' of the library's maintainer"
	root=$(git rev-parse --show-toplevel)
	target="$root/.agents/skills"

	work=$(mktemp -d)
	trap 'rm -rf "$work"' EXIT
	git clone -q --depth 1 --branch "$tag" "$url" "$work/library" 2>/dev/null ||
		fail "cannot clone $tag from $url"
	library="$work/library"
	[ "$(git -C "$library" cat-file -t "refs/tags/$tag")" = tag ] || fail "$tag is not an annotated tag"
	output=$(git -C "$library" -c gpg.ssh.program=ssh-keygen -c gpg.ssh.allowedSignersFile="$signers" \
		verify-tag "$tag" 2>&1) || fail "$tag is not signed by an allowed signer: $output"
	principal=$(printf '%s\n' "$output" | sed -n 's/^Good "git" signature for \(.*\) with .* key .*$/\1/p')
	tagger=$(git -C "$library" for-each-ref --format='%(taggeremail:trim)' "refs/tags/$tag")
	[ "$principal" = "$tagger" ] || fail "$tag is signed by $principal but tagged by $tagger"

	rm -rf "$target"
	mkdir -p "$target"
	git -C "$library" archive "$tag" | tar -x -C "$target"
	printf '%s\n' "${tag#v}" >"$target/VERSION"
	git -C "$root" add -A "$target"
	echo "vendored agent-skills $tag, signed by $principal; commit it as: chore(agents): vendor agent-skills $tag"
}

# The whole script is read before main runs, so replacing .agents/skills/vendor.sh is safe.
main "$@"
