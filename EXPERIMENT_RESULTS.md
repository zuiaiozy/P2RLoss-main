# Experiment Results

Metrics are reported on ShanghaiTech Part_A test set. Experiment outputs, logs,
and checkpoints are kept outside Git.

The current protocol files are nested: `sha-5.txt` is contained in `sha-10.txt`,
and `sha-10.txt` is contained in `sha-40.txt`. The 5% split is preserved from the
first run; 10% and 40% should be rerun with the nested protocols.

| Label | Protocol | Tag | Epochs | Best Epoch | Best MAE | Best MSE | Paper MAE | Paper MSE | Train Time | Notes |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 5% | `protocols/sha-5.txt` | `sha-L5` | 1500 | 1280 | 72.841 | 124.598 | 69.9 | 119.5 | 4:12:54 | Base split, 15 labeled images. |
| 10% | `protocols/sha-10.txt` | `sha-L10` | 1500 | 750 | 65.308 | 113.567 | TBD | TBD | 5:29:48 | Nested split, 30 labeled images. |
| 40% | `protocols/sha-40.txt` | `sha-L40-nested` | 1500 | 904 | 58.18 | 95.83 | TBD | TBD | TBD | Temporarily using interrupted epoch-904 result; replace after rerun. |

## 5% Run Details

- Best checkpoint: `exp/sha-L5/output/ckpt_epoch_best.pth`
- Stage checkpoint: `exp/sha-L5/output/ckpt_epoch_stage2.pth`
- Config: `exp/sha-L5/output/config.json`
- Best MAE epoch: 1280
- Best validation line: `* MAE 72.841 MSE 124.598`
- Best log line: `Min total MAE|MSE|Loss: 72.840659 | 124.598 | 4334.36`
- The 5% labeled protocol contains 15 labeled images out of 300 training images.


## 10% Run Details

- Best checkpoint: `exp/sha-L10/output/ckpt_epoch_best.pth`
- Latest checkpoint: `exp/sha-L10/output/ckpt_epoch_latest.pth`
- Stage checkpoint: `exp/sha-L10/output/ckpt_epoch_stage2.pth`
- Config: `exp/sha-L10/output/config.json`
- Best MAE epoch: 750
- Best validation line: `* MAE 65.308 MSE 113.567`
- Best log line: `Min total MAE|MSE|Loss: 65.307692 | 113.57 | 3703.49`
- Training time: 5:29:48
- The 10% labeled protocol contains 30 labeled images out of 300 training images and includes all 15 images from the 5% protocol.


## 40% Run Details

- Current result is temporarily taken from the interrupted run at epoch 904.
- Best validation summary: `Min total MAE|MSE|Loss: 58.175824 | 95.83 | 3090.03`
- This should be replaced after a clean full rerun with resumable checkpoints.

## Previous Non-Nested Runs

These results used the old independently sampled protocols, so they are kept for
reference but should not be compared directly with the nested 5% split.

| Label | Protocol | Tag | Epochs | Best MAE | Best MSE | Train Time | Notes |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| 10% | old `protocols/sha-10.txt` | `sha-L10` | 1500 | 80.04 | 144.29 | 5:35:51 | Overlapped with only 3 of the 15 images in the 5% protocol. |

## Interrupted / Partial Runs

These runs are useful for debugging and comparison, but they are not final
reported results.

| Label | Protocol | Tag | Reached Epoch | Best MAE | Best MSE | Loss | Notes |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 40% | `protocols/sha-40.txt` | `sha-L40-nested` | 904 | 58.18 | 95.83 | 3090.03 | Interrupted before the resumable-checkpoint fix; old checkpoint stores weights but not epoch/optimizer state. |