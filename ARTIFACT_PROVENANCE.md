# Artifact provenance and runtime boundary

This repository intentionally separates the entrant-owned policy from organizer-provided data and environment components.

## Entrant-owned policy

- `runtime/*.so`: compiled Task 2 perception, odometry staging, guarded trajectory retargeting, and entry-point modules.
- Embedded JSON payloads: entrant-derived head-camera calibration and piecewise
  release/contact parameters, including a board_0-only right-wrist release
  long-axis gate and a board_1-only, 40-pixel-triggered pre-release alignment.
- `launch/`: small generic dispatch and policy-camera capture shims.

The compiled packaging is an implementation-disclosure reduction measure. It is not described as cryptographic protection.

## Organizer-provided/public demonstration-derived assets

The image embeds only two fixed trajectory seeds extracted from the public `hermanprawiro/task2_fixpos_200` demonstration dataset:

- episode 178 NPZ SHA256: `fbe452b8164c531dc96557f35117afbc4cc5d97c70063c92e23d29c1e738c499`
- episode 3 NPZ SHA256: `523a1a15592990d0098863d35a11cf99859b06e53cb12d64b3fc9fd41ccdb41d`

They are embedded as trajectory data and are not claimed as entrant-authored demonstrations. No training dataset is included.

## Explicitly not included in the policy repository/image

- Isaac Sim or the official Task 2 scene, robot, object, or material assets.
- Official randomization, reset, validator, evaluator, semantic-ID, or scoring code.
- Development recorders, videos, eval-camera frames, object poses, pad mesh points, reset seeds, or geometry diagnostic scripts.
- Auxiliary observer cameras or simulator-side pose corrections.

An independently checksummed complete offline companion may redistribute
organizer/runtime components for direct organizer reproduction. Its
`CONTENT_ORIGIN.tsv` keeps those bytes separate from this entrant-owned policy;
none is copied into or observed by the policy container.

## Runtime observation contract

The policy starts against the untouched organizer scene and is restricted to the official head, left-wrist, and right-wrist camera set plus normal robot state and odometry. The current right-arm path reads head/right-wrist RGB; left-wrist remains an allowed but unused official stream. It never subscribes to the eval camera and does not invoke reset or evaluation. Local QC is run by a separate host-side process only after the policy container exits.
