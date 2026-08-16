# Task 2 evaluation

## Official evaluator

The official Task 2 evaluator is in the benchmark repository at
[`scripts/evaluation/task2`](https://github.com/EBiM-Benchmark/benchmark/tree/main/scripts/evaluation/task2).
It runs as a separate ROS Jazzy container after policy motion has stopped. The
evaluator computes pad/target bounding-box IoU and checks orientation from the
eval-camera streams. The policy container does not start or call it.

Use the evaluator and Task 2 scene from the same benchmark checkout. The
evaluator resolves an occluded target through the loose target bounding-box
stream, so a mismatched scene and evaluator revision can invalidate results.

## Start the evaluator

Restore and start the complete cloud delivery as described in `README.md`, then
set the paths below:

```bash
export BENCHMARK=/absolute/empty/path/benchmark
export ISAAC_DOCKER_ROOT=/absolute/empty/docker-root
export RESULT_ROOT=$PWD/task2-results
mkdir -p "$RESULT_ROOT"

cd "$BENCHMARK"
bash scripts/evaluation/task2/setup.sh
docker compose --env-file scripts/evaluation/task2/.env \
  -f scripts/evaluation/task2/docker-compose.yml \
  --profile eval up -d --no-build eval_task2
bash scripts/evaluation/task2/run.sh status
```

The complete delivery already loads the matching `eval-task2:ebim2026` image,
so this command starts the evaluator without an image rebuild or network
access. `bash scripts/evaluation/task2/run.sh up` is retained as the official
source-build fallback for environments that do not have that preloaded image.

## Evaluate one episode

Use an explicit seed. Start one scene, run one policy container, then invoke
the evaluator once after that policy container exits:

```bash
seed=202681421
cd "$BENCHMARK"
runtime_workspace/restart_task2_isaac_randomized.sh \
  --seed "$seed" --terminal-controller rmpflow --headless \
  --render-hz 60 --ros-publish-rate 30 --policy-cameras-only \
  --strict-official-runtime \
  --robot-camera-keys head,wrist_left,wrist_right \
  --robot-camera-frame-skip 2 --robot-camera-sensor-data-qos \
  --force-render-loop

docker run --rm --network host --ipc host \
  -e ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-0}" \
  -e FASTDDS_BUILTIN_TRANSPORTS=UDPv4 \
  ebim-task2-policy:20260816-rmpflow-stagefix-final

bash scripts/evaluation/task2/run.sh evaluate
```

The official evaluator writes timestamped artifacts below
`$ISAAC_DOCKER_ROOT/eval-task2/evaluate/`, including
`eval_camera_iou_<timestamp>.json`. Preserve that JSON with the seed and
policy log. It contains the returned IoU, orientation decision and diagnostic
fields. When the campaign finishes, stop the evaluator with:

```bash
cd "$BENCHMARK"
bash scripts/evaluation/task2/run.sh down
```

## Evaluate multiple independent samples

Use one complete scene restart, one policy run and one evaluator call per
seed. Do not score several episodes against the same terminal frame, and do
not run policy containers concurrently on the same ROS domain.

Create and retain `seeds.txt` before the campaign, with one non-negative
integer per line. With the evaluator service already running, execute the
following sequential loop:

```bash
export BENCHMARK=/absolute/empty/path/benchmark
export ISAAC_DOCKER_ROOT=/absolute/empty/docker-root
export RESULT_ROOT=$PWD/task2-results
mkdir -p "$RESULT_ROOT"

while read -r seed; do
  test -n "$seed" || continue
  run_dir="$RESULT_ROOT/seed-$seed"
  mkdir -p "$run_dir"

  cd "$BENCHMARK"
  runtime_workspace/restart_task2_isaac_randomized.sh \
    --seed "$seed" --terminal-controller rmpflow --headless \
    --render-hz 60 --ros-publish-rate 30 --policy-cameras-only \
    --strict-official-runtime \
    --robot-camera-keys head,wrist_left,wrist_right \
    --robot-camera-frame-skip 2 --robot-camera-sensor-data-qos \
    --force-render-loop |& tee "$run_dir/scene.log"

  docker run --rm --network host --ipc host \
    -e ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-0}" \
    -e FASTDDS_BUILTIN_TRANSPORTS=UDPv4 \
    ebim-task2-policy:20260816-rmpflow-stagefix-final \
    |& tee "$run_dir/policy.log"

  bash scripts/evaluation/task2/run.sh evaluate |& tee "$run_dir/evaluate.log"
  latest=$(ls -1t "$ISAAC_DOCKER_ROOT"/eval-task2/evaluate/eval_camera_iou_*.json | head -n 1)
  cp "$latest" "$run_dir/result.json"
done < seeds.txt
```

The loop is deliberately sequential. It copies the newest evaluator JSON
immediately after each stateless evaluator call, preserving the pairing among
seed, scene log, policy log and score. Review every `result.json` first, then
aggregate only completed runs produced with the same benchmark/evaluator
revision and policy image tag.

For a transparent summary of the raw outputs:

```bash
find "$RESULT_ROOT" -name result.json -print0 | xargs -0 jq -s '
  {episodes: length,
   mean_iou: (map(.iou_thermalpad_vs_target_current) | add / length),
   orientation_correct: (map(select(.is_orientation_correct == true)) | length)}'
```

This is a local diagnostic. Do not choose an IoU pass threshold or present this
summary as an organizer leaderboard score; the official evaluator output and
organizer evaluation are authoritative.

## Packaged randomization and current evidence

The complete-delivery launcher invokes the Task 2 scene with:

```text
--randomize-objects
--randomize-xy-cm 2.0
--randomize-yaw-deg 0.0
--randomization-seed <seed>
```

Its validation record identifies this Stage 1 configuration as board swapping,
independent continuous board XY jitter in +/-2 cm, zero board yaw jitter, and
no pad or pad-base randomization. The seed makes an individual draw
reproducible; distinct seeds produce different draws from that configuration.

The stage-fix delivery contains one end-to-end reproducibility regression at
seed `202681421`: normal completion, IoU `0.7947761194029851`, correct
orientation, coverage `0.9594594594594594`, and precision
`0.8223938223938224`. This is one regression result, not a multi-seed success
rate or a promise of official aggregate performance.
