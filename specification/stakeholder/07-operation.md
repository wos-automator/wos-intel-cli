## 7. Operation

```
python -m wos_intel run            # normal operation
python -m wos_intel run --dry-run  # detects and logs, does not tap
python -m wos_intel detect image.png  # detection on a file, writes image.debug.png
python -m wos_intel snap name      # ADB screenshot to ref/name.png (collect references)
```

- Log with timestamp on stdout: detected state, symbols (type/tier/status/position), taps.
- `--debug` saves, per step, the image with the hits drawn in under `debug/`.
- Configuration (thresholds, waiting times, coordinates) in `config.toml`.
