# Binary-policy reproducibility contract

The EBiM rules require a public repository with a Dockerfile and run guide and
explicitly state that policy source code is not required. This submission does
not publish readable source for its core policy, calibration, or expert
trajectory implementation.

## What is reproducible

- The exact policy implementation bytes are versioned as stripped CPython
  extension modules under `runtime/`.
- Embedded calibration/configuration and the two fixed expert assets are part
  of those versioned modules; startup materialization is deterministic.
- `docker build` uses only files in this repository and the public pinned base
  image. It requires no private package registry, remote inference endpoint,
  license server, secret, or decryption key.
- The image entrypoint, accepted ROS observations, command topics and one-run
  behavior are fixed and documented.
- `REPOSITORY_SHA256SUMS.txt` in the finalized public repository records every
  repository file hash. The separately delivered complete cloud bundle also
  records the resulting policy image ID, image-archive hashes and the exact
  frozen entrypoint argument contract.
- A fresh-scene blind smoke runs the exact compiled image with no evaluator,
  reset, recorder, dataset, or host policy-source mount.

This is execution/build reproducibility, not source-level reproducibility.

## Platform boundary

The extensions target Linux x86_64 and the CPython 3.12 ABI supplied by the
documented ROS Jazzy base image. The Dockerfile fixes that environment so the
host does not need a matching Python installation. Isaac Sim runs separately
in the organizer-provided GPU environment and communicates through the public
ROS graph.

## Disclosure and security boundary

Symbol stripping and compilation prevent direct publication of readable
policy source and raw trajectory files. They are not claimed to make reverse
engineering impossible. No credential, encrypted payload, hidden network
service, privileged simulator state, evaluator output, or QC camera is needed
to run the policy.
