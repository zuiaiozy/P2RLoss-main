#!/usr/bin/env bash
set -euo pipefail

# Example:
#   DATA_ROOT=/data/ShanghaiTech/part_A LABEL=5 bash scripts/train_sha.sh

DATA_ROOT=${DATA_ROOT:-/path/to/ShanghaiTech/part_A}
LABEL=${LABEL:-5}
PROTOCOL=${PROTOCOL:-protocols/sha-${LABEL}.txt}
BATCH_SIZE=${BATCH_SIZE:-16}
EPOCHS=${EPOCHS:-1500}
NUM_WORKERS=${NUM_WORKERS:-8}
SAVE_FREQ=${SAVE_FREQ:-5}
TAG=${TAG:-sha-L${LABEL}}

mkdir -p "exp/${TAG}/train.log"
mkdir -p "exp/${TAG}/code"
cp -r datasets "exp/${TAG}/code/datasets"
cp -r models "exp/${TAG}/code/models"
cp -r losses "exp/${TAG}/code/losses"
cp -r scripts "exp/${TAG}/code/scripts"
cp ./*.py "exp/${TAG}/code/"
cp requirements.txt "exp/${TAG}/code/"

python main.py \
  --data-path "${DATA_ROOT}" \
  --label "${LABEL}" \
  --protocol "${PROTOCOL}" \
  --batch-size "${BATCH_SIZE}" \
  --tag "${TAG}" \
  --opts TRAIN.EPOCHS "${EPOCHS}" DATA.NUM_WORKERS "${NUM_WORKERS}" SAVE_FREQ "${SAVE_FREQ}" \
  2>&1 | tee "exp/${TAG}/train.log/running.log"
