#!/usr/bin/env bash
set -euo pipefail

# Example:
#   DATA_ROOT=/data/ShanghaiTech/part_A LABEL=5 TAG=sha-L5 CKPT=exp/sha-L5/output/ckpt_epoch_best.pth bash scripts/eval_sha.sh

DATA_ROOT=${DATA_ROOT:-/path/to/ShanghaiTech/part_A}
LABEL=${LABEL:-5}
PROTOCOL=${PROTOCOL:-protocols/sha-${LABEL}.txt}
BATCH_SIZE=${BATCH_SIZE:-1}
TAG=${TAG:-sha-L${LABEL}-eval}
CKPT=${CKPT:-exp/sha-L${LABEL}/output/ckpt_epoch_best.pth}

python main.py \
  --data-path "${DATA_ROOT}" \
  --label "${LABEL}" \
  --protocol "${PROTOCOL}" \
  --batch-size "${BATCH_SIZE}" \
  --tag "${TAG}" \
  --resume "${CKPT}" \
  --eval
