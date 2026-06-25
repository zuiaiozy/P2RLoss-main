# Experiment Results

Metrics are reported on ShanghaiTech Part_A test set. Experiment outputs, logs,
and checkpoints are kept outside Git.

The current protocol files are nested: `sha-5.txt` is contained in `sha-10.txt`,
and `sha-10.txt` is contained in `sha-40.txt`. The 5% split is preserved from the
first run; 10% and 40% should be rerun with the nested protocols.

| Label | Protocol | Tag | Epochs | Best Epoch | Best MAE | Best MSE | Paper MAE | Paper MSE | Train Time | Notes |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 5% | `protocols/sha-5.txt` | `sha-L5` | 1500 | 1280 | 72.841 | 124.598 | 69.9 | 119.5 | 4:12:54 | Base split, 15 labeled images. |
| 10% | `protocols/sha-10.txt` | `sha-L10-nested` | 1500 | TBD | TBD | TBD | TBD | TBD | TBD | Nested split, 30 labeled images. |
| 40% | `protocols/sha-40.txt` | `sha-L40-nested` | 1500 | TBD | TBD | TBD | TBD | TBD | TBD | Nested split, 120 labeled images. |

## 5% Run Details

- Best checkpoint: `exp/sha-L5/output/ckpt_epoch_best.pth`
- Stage checkpoint: `exp/sha-L5/output/ckpt_epoch_stage2.pth`
- Config: `exp/sha-L5/output/config.json`
- Best MAE epoch: 1280
- Best validation line: `* MAE 72.841 MSE 124.598`
- Best log line: `Min total MAE|MSE|Loss: 72.840659 | 124.598 | 4334.36`
- The 5% labeled protocol contains 15 labeled images out of 300 training images.

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