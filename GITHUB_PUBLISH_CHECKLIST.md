# Private-to-public GitHub publication checklist

The repository may be created as private while integration is in progress.
Treat every commit as eventually public: changing visibility exposes Git
history and GitHub Actions history/logs, not only the current working tree.

## Authentication

- Prefer a repository-specific SSH deploy key or GitHub device login.
- If a fine-grained PAT is necessary, select only this repository, use a short
  expiry, and grant `Contents: read/write`; grant `Workflows` only if a workflow
  file must be changed.
- Never commit or paste PATs, SSH private keys, sudo passwords, remote-server
  passwords, `.env` files, or Docker registry credentials.

## Public repository versus complete cloud bundle

- Commit the files in this public repository only.
- Do not add compressed archives, split parts, Docker image archives or Isaac
  Sim to Git history, Git LFS or a public GitHub Release. The uncompressed
  repository itself is the official minimum artifact and builds the policy
  image directly.
- Put the checksummed complete offline bundle in private cloud storage or send
  it directly to the organizers. Do not make the bundled NVIDIA Isaac Sim
  image public unless redistribution permission has been independently
  confirmed.
- If the cloud bundle is linked as supplementary material, add its URL,
  expected SHA256 and integration instructions to the README before submission.

## Mandatory gate before changing visibility

- Scan the full object graph (`git rev-list --objects --all`) for secrets and
  unexpected large files, not only the checked-out branch.
- Review all branches, tags, pull requests, Actions workflow runs, logs and
  artifacts for credentials or private paths.
- Confirm no Git blob exceeds 100 MiB and the repository contains no archive
  or split-part payload.
- Verify `docker build`, the frozen entrypoint audit, observation isolation,
  fresh-scene blind smoke, archive SHA256 values and a clean-clone rebuild.
- Fill the registered team name, contact email and final public repository URL
  in `OFFICIAL_SUBMISSION.md`; do not guess them.
- Confirm licenses and `ARTIFACT_PROVENANCE.md`, then tag the exact audited
  commit. Keep the matching complete-bundle checksums with the cloud delivery.
- After changing visibility, re-check branch/ruleset protection because GitHub
  disables push rulesets during a private-to-public visibility change.
