# .github

[![verify](https://github.com/carpe-diem-innovations-inc/.github/actions/workflows/verify.yml/badge.svg)](https://github.com/carpe-diem-innovations-inc/.github/actions/workflows/verify.yml)

Organisation-level GitHub configuration for
[Carpe Diem Innovations Inc.](https://github.com/carpe-diem-innovations-inc)

`profile/README.md` is the file GitHub renders on the organisation's front page. That exact
path is the contract — renaming or moving it silently removes the front page.

## Verification

Every push is verified before it lands.

| stage | what it proves | where |
|---|---|---|
| **works** | `profile/README.md` is present and non-empty, the asset it embeds resolves, and every repository it advertises still exists and is still public | locally, then again in CI |
| **safe** | no committed secrets, a clean tree, this README documenting verification | locally |
| **elsewhere** | the same checks pass on a clean runner | GitHub Actions, `ubuntu-latest` |

```bash
python scripts/verify_profile.py
```

**The public-repo check is the one that catches real drift.** This page advertises other
repositories. If one is renamed, deleted, or made private, the organisation front page turns
into dead links — and nothing in *this* repo changed, so a push-only trigger would never find
out. CI therefore also runs weekly on a schedule.

## Note on the local checkout

This repository is named `.github`. A directory of that name is hidden and is skipped by the
tooling that walks the repository tree, so the local working copy is checked out as
`dot-github` instead. Git does not care what the containing directory is called.
