# P2R Loss 复现说明

本目录基于官方仓库 `Elin24/P2RLoss` 整理，目标是复现 CVPR 2025 论文
《Point-to-Region Loss for Semi-Supervised Point-Based Crowd Counting》。

## 1. 环境

建议服务器使用 CUDA 版 PyTorch。示例：

```bash
conda create -n p2rloss python=3.10 -y
conda activate p2rloss
pip install -r requirements.txt
```

根据服务器 CUDA 版本，`torch/torchvision` 可优先按 PyTorch 官网命令单独安装。

## 2. 数据准备

官方 dataloader 当前支持 ShanghaiTech `part_A` 格式，目录需要如下：

```text
ShanghaiTech/part_A/
  train_data/
    images/
    ground-truth/
    new-anno/
  test_data/
    images/
    ground-truth/
    new-anno/
```

原始 ShanghaiTech 标注是 `.mat`，本项目训练读取 `new-anno/GT_IMG_x.npy`。
在服务器上执行：

```bash
python scripts/prepare_shanghai.py \
  --part-root /data/ShanghaiTech/part_A \
  --name sha \
  --protocol-dir protocols \
  --percents 5 10 40 \
  --seed 2024
```

该脚本会完成两件事：

- 将 `ground-truth/*.mat` 转为 `new-anno/*.npy`
- 生成 `protocols/sha-5.txt`、`protocols/sha-10.txt`、`protocols/sha-40.txt`

注意：当前 protocol 文件写入的是 `IMG_1.jpg` 这种完整文件名，因为 `datasets/shha.py`
按文件名判断是否属于 labeled set。

## 3. 训练

5% 标注协议：

```bash
DATA_ROOT=/data/ShanghaiTech/part_A \
LABEL=5 \
BATCH_SIZE=16 \
EPOCHS=1500 \
TAG=sha-L5 \
bash scripts/train_sha.sh
```

10% 和 40%：

```bash
DATA_ROOT=/data/ShanghaiTech/part_A LABEL=10 TAG=sha-L10 bash scripts/train_sha.sh
DATA_ROOT=/data/ShanghaiTech/part_A LABEL=40 TAG=sha-L40 bash scripts/train_sha.sh
```

训练日志和 checkpoint 会保存到：

```text
exp/<TAG>/train.log/running.log
exp/<TAG>/output/
```

## 4. 评估

```bash
DATA_ROOT=/data/ShanghaiTech/part_A \
LABEL=5 \
TAG=sha-L5-eval \
CKPT=exp/sha-L5/output/ckpt_epoch_best.pth \
bash scripts/eval_sha.sh
```

## 5. 论文对齐设置

- backbone：VGG16BN
- crop size：`256 x 256`
- warm-up：前 50 个 epoch 左右只用有标签监督；代码中 `STAGE_1=25`，`STAGE_2=50`
- 伪标签可靠阈值：logit `0.8472978603872036`，对应 sigmoid 后 `0.7`
- EMA momentum：`0.998`
- 默认训练 epoch：`1500`

## 6. 当前代码改动

相对官方代码，仅补充了复现辅助文件，并修复了 `--eval` 入口：

- `requirements.txt`
- `scripts/prepare_shanghai.py`
- `scripts/train_sha.sh`
- `scripts/eval_sha.sh`
- `README_REPRODUCE_CN.md`
- `main.py` 中 `--eval` 加载 checkpoint 后会实际执行验证
