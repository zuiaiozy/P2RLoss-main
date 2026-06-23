#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Prepare ShanghaiTech annotations and label protocols for P2RLoss.

The official dataloader expects:
  part_A/train_data/new-anno/GT_IMG_1.npy
  part_A/test_data/new-anno/GT_IMG_1.npy

Protocol files must contain image file names such as "IMG_1.jpg", one per line.
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path

import numpy as np
from scipy.io import loadmat


def extract_points(mat_path: Path) -> np.ndarray:
    mat = loadmat(mat_path)
    image_info = mat["image_info"]
    try:
        points = image_info[0, 0][0, 0]["location"]
    except Exception:
        # ShanghaiTech .mat files are nested MATLAB structs. This fallback
        # keeps the converter usable if scipy exposes the fields positionally.
        points = image_info[0, 0][0, 0][0]

    points = np.asarray(points, dtype=np.float32)
    if points.size == 0:
        return np.zeros((0, 2), dtype=np.float32)
    return points.reshape(-1, 2)


def convert_split(part_root: Path, split: str) -> int:
    gt_dir = part_root / split / "ground-truth"
    out_dir = part_root / split / "new-anno"
    if not gt_dir.exists():
        raise FileNotFoundError(f"Missing ground-truth directory: {gt_dir}")

    out_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for mat_path in sorted(gt_dir.glob("GT_*.mat")):
        points = extract_points(mat_path)
        out_path = out_dir / f"{mat_path.stem}.npy"
        np.save(out_path, points)
        count += 1
    return count


def generate_protocols(part_root: Path, output_dir: Path, name: str, percents: list[int], seed: int) -> None:
    image_dir = part_root / "train_data" / "images"
    images = sorted(p.name for p in image_dir.glob("*.jpg"))
    if not images:
        raise FileNotFoundError(f"No .jpg images found in {image_dir}")

    rng = random.Random(seed)
    for percent in percents:
        n_labeled = max(1, round(len(images) * percent / 100.0))
        chosen = sorted(rng.sample(images, n_labeled))
        out_path = output_dir / f"{name}-{percent}.txt"
        out_path.write_text("\n".join(chosen) + "\n", encoding="utf-8")
        print(f"[protocol] {out_path}: {len(chosen)}/{len(images)} labeled images")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare ShanghaiTech for P2RLoss reproduction.")
    parser.add_argument("--part-root", required=True, type=Path, help="Path to ShanghaiTech/part_A or part_B.")
    parser.add_argument("--name", default="sha", help="Protocol prefix, e.g. sha or shb.")
    parser.add_argument("--protocol-dir", default=Path("protocols"), type=Path)
    parser.add_argument("--percents", nargs="+", default=[5, 10, 40], type=int)
    parser.add_argument("--seed", default=2024, type=int)
    parser.add_argument("--skip-anno", action="store_true", help="Only generate protocols.")
    args = parser.parse_args()

    part_root = args.part_root.resolve()
    if not part_root.exists():
        raise FileNotFoundError(part_root)

    if not args.skip_anno:
        for split in ("train_data", "test_data"):
            count = convert_split(part_root, split)
            print(f"[anno] converted {count} files under {part_root / split}")

    protocol_dir = args.protocol_dir.resolve()
    protocol_dir.mkdir(parents=True, exist_ok=True)
    generate_protocols(part_root, protocol_dir, args.name, args.percents, args.seed)


if __name__ == "__main__":
    main()
