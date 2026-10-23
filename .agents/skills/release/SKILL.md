---
name: release
description: >-
  Release a version from a signed tag: date the release notes, commit, hand over the signed tag to the user, watch the pipeline. Also sets up a repository for this once. Use for every release; never release through the GitHub web interface.
---

# Skill: Release

A release is a signed, annotated tag `v<semver>` pushed by the user. The pipeline of [release-actions](https://github.com/thst71/release-actions) verifies the signature, runs the quality gate, builds the artifacts, renders the documentation (see [spec-system](../spec-system/SKILL.md), Rendering) and publishes the release. The signature is the user's approval: only the user signs release tags.

## Files Modified

- `specification/release-notes/<version>.adoc` (heading dated)
- The version file of the component, if its toolchain profile names one
- On adoption: `.github/workflows/release.yml`

## Adoption (once per repository)

1. **Workflow**: Copy [release.yml](release.yml) to `.github/workflows/release.yml`. Replace the placeholder steps of the job `build` with the `Release Build` steps of the component's toolchain profile; drop `artifacts/dist/*` from the assets if there is no `dist` task.
2. **Repository**: With the user's consent and `gh` logged in as the repository owner, run [setup-repository.sh](setup-repository.sh) in the project. It creates the environment `release` (release tags only), its secret `RELEASE_ALLOWED_SIGNERS` from the project's `user.email` and `user.signingkey`, and the ruleset that lets only admins create, move or delete release tags.
3. **User, once per machine**: `git config tag.gpgSign true` in the identity's git configuration, so that `git tag -a` signs; the signing key added to the GitHub account as a signing key.

## Execution Steps

1. **Version**: Derive the version from the commits since the last release tag (Conventional Commits): a `BREAKING CHANGE` raises the major version (the minor one before 1.0.0), a `feat` the minor version, otherwise the patch version. Confirm it with the user.
2. **Quality Gate**: The `check` task passes (see [toolchain](../toolchain/SKILL.md)). If the profile has a `version` task, set the version where the profile says and check that the task prints it.
3. **Release Notes**: Change the heading of `specification/release-notes/<version>.adoc` from `== Release v<version> (unreleased)` to `== Release v<version> (YYYY-MM-DD)`, the day the user tags. Directly below it, the line `Built with agent-skills v<version>.` names the content of `.agents/skills/VERSION`. Check that every feat and fix since the last release is listed (see [spec-system](../spec-system/SKILL.md), Release Notes).
4. **Commit**: Commit with [commit](../commit/SKILL.md): `chore(release): <version>`.
5. **Hand Over**: Ask the user to sign, tag and push (1Password asks for approval):

   ```sh
   git tag -a v<version> -m "<project> <version>"
   git push origin <branch> v<version>
   ```

   Run these commands yourself only when the user asks for it in this session and is present to approve the signature.
6. **Watch**: Follow the run (`gh run watch`) and report the release URL, or the failing step with its message.
7. **On Failure**: Never move or delete a pushed release tag. Fix the cause and release the next patch version; a tag that failed verification is removed by the user (admins bypass the ruleset).

## Tags

- Only `v<major>.<minor>.<patch>[-pre][+build]` is a release tag; `-pre` makes a pre-release.
- Any other tag name is free for other uses and starts no release.
