---
name: aseprite-frame-extract
description: Batch-export per-tag animation frames from .aseprite files into categorized folders; use when asked to extract frames, split tags, or organize Aseprite animations into folders for engines like Godot.
---

# Aseprite Frame Extraction

## Quick start
- Run `python scripts/extract_aseprite_frames.py <file-or-folder-or-glob> [...]`.
- Outputs to `assets/<sprite-name>/<tag>/<frame>.png` by default.
- Use `--split-shadow` to export main sprites without shadow and shadow-only sprites separately.

## Workflow
1. Point to `.aseprite` files or a folder.
2. Provide `--aseprite` if Aseprite is not on PATH.
3. Check results in the output folder.

## Notes
- Uses Aseprite CLI `--split-tags` and `{tag}/{frame}.png` to classify frames.
- Tag names and frames are exported as-is; tag names become folder names.
- If a sprite has no tags, no frames are exported.
- When `--split-shadow` is enabled, the script:
  - exports main sprites using `--ignore-layer <shadow-layer>`
  - exports shadow sprites using `--layer <shadow-layer>`
- `--strict-shadow-layer` is enabled by default. Missing shadow layers will fail fast.
- `--clean-target` / `--clean-shadow-target` can delete output directories before export.

## Examples
```bash
python scripts/extract_aseprite_frames.py d:\project\godot\blockking\aseprite_assets --aseprite "D:\tools\Aseprite-v1.3.15.3-Windows\aseprite.exe" --output d:\project\godot\blockking\assets
python scripts/extract_aseprite_frames.py "d:\project\godot\blockking\aseprite_assets\*.aseprite" --preview

# Split shadow for one sprite (preview only, no files written)
python scripts/extract_aseprite_frames.py "D:\project\godot\blockking\aseprite_assets\Archer.aseprite" --aseprite "D:\tools\Aseprite-v1.3.15.3-Windows\aseprite.exe" --output "D:\project\godot\blockking\assets" --split-shadow --shadow-layer shadow --shadow-output "D:\project\godot\blockking\assets_shadow" --preview

# Full export for all sprites with directory cleanup (write mode)
python scripts/extract_aseprite_frames.py "D:\project\godot\blockking\aseprite_assets" --aseprite "D:\tools\Aseprite-v1.3.15.3-Windows\aseprite.exe" --output "D:\project\godot\blockking\assets" --split-shadow --shadow-layer shadow --shadow-output "D:\project\godot\blockking\assets_shadow" --clean-target --clean-shadow-target --strict-shadow-layer
```

## Shadow split export
- `--split-shadow`: Enable main/shadow dual export.
- `--shadow-layer <name>`: Repeatable shadow layer names. Default: `shadow`.
- `--shadow-output <dir>`: Shadow output root. Default: `assets_shadow`.
- `--strict-shadow-layer` / `--no-strict-shadow-layer`:
  - strict mode (default) fails when shadow layers are missing.
- `--clean-target`: Clean `output/<sprite-name>` before export.
- `--clean-shadow-target`: Clean `shadow-output/<sprite-name>` before export. Requires `--split-shadow`.

## Safety
- The script checks for nested `.git` directories before recursive deletion.
- In `--preview` mode:
  - no output directories are deleted
  - no files are written
  - planned commands are printed for review

## scripts/
- `scripts/extract_aseprite_frames.py`: Calls Aseprite CLI to export per-tag frames into folders.
