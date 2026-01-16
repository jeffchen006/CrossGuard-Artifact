# utilsPackage

Small helpers that multiple packages import. These utilities keep file formats and settings consistent across the repo.

## What is in here

- `compressor.py`: read/write helpers for gzip + pickle data, plus small convenience helpers for list and cache files.
- `tomlHandler.py`: small helper to modify `settings.toml` programmatically.

## Notes

- The compressed JSON helpers actually use pickle under the hood, so they are Python-specific.
- If you change `settings.toml`, make sure other scripts that depend on it are rerun.
