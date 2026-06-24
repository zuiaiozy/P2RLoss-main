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
from typing import Optional

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


def read_protocol(protocol_path: Optional[Path]) -> list[str]:
    if protocol_path is None:
        return []
    if not protocol_path.exists():
        raise FileNotFoundError(protocol_path)
    return [line.strip() for line in protocol_path.read_text(encoding="utf-8").splitlines() if line.strip()]


def generate_protocols(
    part_root: Path,
    output_dir: Path,
    name: str,
    percents: list[int],
    seed: int,
    base_protocol: Optional[Path] = None,
) -> None:
    image_dir = part_root / "train_data" / "images"
    images = sorted(p.name for p in image_dir.glob("*.jpg"))
    if not images:
        raise FileNotFoundError(f"No .jpg images found in {image_dir}")

    base_images = read_protocol(base_protocol)
    unknown_base = sorted(set(base_images) - set(images))
    if unknown_base:
        raise ValueError(f"Base protocol contains images not found in {image_dir}: {unknown_base[:5]}")

    rng = random.Random(seed)
    base_set = set(base_images)
    remaining = [image for image in images if image not in base_set]
    rng.shuffle(remaining)

    for percent in sorted(set(percents)):
        n_labeled = max(1, round(len(images) * percent / 100.0))
        if len(base_images) > n_labeled:
            raise ValueError(
                f"Base protocol has {len(base_images)} images, more than the {percent}% target {n_labeled}."
            )
        chosen = sorted(base_images + remaining[: n_labeled - len(base_images)])
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
    parser.add_argument(
        "--base-protocol",
        default=None,
        type=Path,
        help="Optional protocol whose images must be included in every generated split.",
    )
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
    generate_protocols(part_root, protocol_dir, args.name, args.percents, args.seed, args.base_protocol)


if __name__ == "__main__":
    main()
