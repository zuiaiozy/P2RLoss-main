#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Prepare CQUPT classroom crowd data for P2RLoss.

Input layout expected by default:
  CQUPTClass_processed/after_school/img/*.jpg
  CQUPTClass_processed/after_school/mat/*.mat      # annPoints, train split
  CQUPTClass_processed/after_school/test/img/*.jpg
  CQUPTClass_processed/after_school/test/mat/*.mat # annPoints, test split

Output layout follows the existing SHHA dataloader convention:
  CQUPTClass_p2r/train_data/images/out_0001.jpg
  CQUPTClass_p2r/train_data/new-anno/GT_out_0001.npy
  CQUPTClass_p2r/test_data/images/out_0008.jpg
  CQUPTClass_p2r/test_data/new-anno/GT_out_0008.npy
"""

from __future__ import annotations

import argparse
import random
import shutil
from pathlib import Path
from typing import Iterable

import numpy as np
from scipy.io import loadmat


def read_points(mat_path: Path) -> np.ndarray:
    mat = loadmat(mat_path)
    if "annPoints" not in mat:
        raise KeyError(f"{mat_path} does not contain annPoints")
    points = np.asarray(mat["annPoints"], dtype=np.float32)
    if points.size == 0:
        return np.zeros((0, 2), dtype=np.float32)
    return points.reshape(-1, 2)


def copy_split(image_dir: Path, mat_dir: Path, output_root: Path, split: str) -> list[str]:
    out_img_dir = output_root / split / "images"
    out_anno_dir = output_root / split / "new-anno"
    out_img_dir.mkdir(parents=True, exist_ok=True)
    out_anno_dir.mkdir(parents=True, exist_ok=True)

    names: list[str] = []
    for image_path in sorted(image_dir.glob("*.jpg")):
        mat_path = mat_dir / f"{image_path.stem}.mat"
        if not mat_path.exists():
            raise FileNotFoundError(f"Missing annotation for {image_path.name}: {mat_path}")
        shutil.copy2(image_path, out_img_dir / image_path.name)
        points = read_points(mat_path)
        np.save(out_anno_dir / f"GT_{image_path.stem}.npy", points)
        names.append(image_path.name)
    return names


def write_protocols(image_names: Iterable[str], output_dir: Path, prefix: str, percents: list[int], seed: int) -> None:
    images = sorted(image_names)
    if not images:
        raise ValueError("No training images found for protocol generation")

    rng = random.Random(seed)
    shuffled = images[:]
    rng.shuffle(shuffled)
    output_dir.mkdir(parents=True, exist_ok=True)

    for percent in sorted(set(percents)):
        n_labeled = max(1, round(len(images) * percent / 100.0))
        chosen = sorted(shuffled[:n_labeled])
        out_path = output_dir / f"{prefix}-{percent}.txt"
        out_path.write_text("\n".join(chosen) + "\n", encoding="utf-8")
        print(f"[protocol] {out_path}: {len(chosen)}/{len(images)} labeled images")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare CQUPTClass data for P2RLoss.")
    parser.add_argument("--source-root", type=Path, default=Path("CQUPTClass_processed/after_school"))
    parser.add_argument("--output-root", type=Path, default=Path("CQUPTClass_p2r"))
    parser.add_argument("--protocol-dir", type=Path, default=Path("protocols"))
    parser.add_argument("--protocol-prefix", default="cqupt")
    parser.add_argument("--percents", nargs="+", default=[5, 10, 40, 100], type=int)
    parser.add_argument("--seed", default=2024, type=int)
    args = parser.parse_args()

    source_root = args.source_root.resolve()
    output_root = args.output_root.resolve()

    train_images = copy_split(source_root / "img", source_root / "mat", output_root, "train_data")
    test_images = copy_split(source_root / "test" / "img", source_root / "test" / "mat", output_root, "test_data")
    write_protocols(train_images, args.protocol_dir.resolve(), args.protocol_prefix, args.percents, args.seed)

    print(f"[train] {len(train_images)} images written to {output_root / 'train_data'}")
    print(f"[test] {len(test_images)} images written to {output_root / 'test_data'}")


if __name__ == "__main__":
    main()
