---
name: aseprite-frame-extract
description: Batch-export per-tag animation frames from .aseprite files into categorized folders; use when asked to extract frames, split tags, or organize Aseprite animations into folders for engines like Godot.
---

# Aseprite Frame Extraction

## Quick start
- Run `python scripts/extract_aseprite_frames.py <file-or-folder-or-glob> [...]`.
- Outputs to `assets/<sprite-name>/<tag>/<frame>.png` by default.

## Workflow
1. Point to `.aseprite` files or a folder.
2. Provide `--aseprite` if Aseprite is not on PATH.
3. Check results in the output folder.

## Notes
- Uses Aseprite CLI `--split-tags` and `{tag}/{frame}.png` to classify frames.
- Tag names and frames are exported as-is; tag names become folder names.
- If a sprite has no tags, no frames are exported.

## Examples
```bash
python scripts/extract_aseprite_frames.py d:\project\godot\blockking\aseprite_assets --aseprite "D:\tools\Aseprite-v1.3.15.3-Windows\aseprite.exe" --output d:\project\godot\blockking\assets
python scripts/extract_aseprite_frames.py "d:\project\godot\blockking\aseprite_assets\*.aseprite" --preview
```

## scripts/
- `scripts/extract_aseprite_frames.py`: Calls Aseprite CLI to export per-tag frames into folders.
