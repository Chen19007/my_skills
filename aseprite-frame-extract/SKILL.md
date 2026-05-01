---
name: aseprite-frame-extract
description: Batch-export per-tag animation frames from .aseprite files into categorized folders; use when asked to extract frames, split tags, or organize Aseprite animations into folders for engines like Godot.
---

# Aseprite Frame Extraction

## Quick start
- Run `python scripts/extract_aseprite_frames.py <file-or-folder-or-glob> [...]`.
- Outputs to `assets/<sprite-name>/<tag>/<frame>.png` by default.
- Use `--layer-export` to split any named layer group into its own output root.
- Legacy `--split-shadow` remains supported and maps to the generic layer export flow.

## Workflow
1. Point to `.aseprite` files or a folder.
2. Provide `--aseprite` if Aseprite is not on PATH.
3. Add one or more `--layer-export` specs when a layer group should be exported separately.
4. Check results in the output folders.

## Notes
- Uses Aseprite CLI `--split-tags` and `{tag}/{frame}.png` to classify frames.
- Tag names and frames are exported as-is; tag names become folder names.
- If a sprite has no tags, no frames are exported.
- Every active `--layer-export` removes its matched layers from the main export automatically.
- `--main-ignore-layer` can additionally exclude specific layers from main export, even without corresponding `--layer-export`.
- `--tag` can restrict exports to selected tags only.
- `--layer-export` is repeatable, so one run can export `shadow`, `effect`, or other layer groups together.
- When a requested layer group is missing:
  - `strict=true` fails fast.
  - `strict=false` logs a warning and skips that extra export for the current sprite.
- `--clean-target` and per-export `clean=true` can delete output directories before export.

## Generic layer export
- Format:
```bash
--layer-export "name=<group>;output=<dir>;layers=<layer1,layer2>[;strict=true|false][;clean=true|false]"
```
- Fields:
  - `name`: label used in logs.
  - `output`: output root for this layer group.
  - `layers`: comma-separated layer names.
  - `strict`: optional, default `true`.
  - `clean`: optional, default `false`.

## Examples
```bash
python scripts/extract_aseprite_frames.py "D:\project\godot\blockking\aseprite_assets" --aseprite "D:\tools\Aseprite-v1.3.15.3-Windows\aseprite.exe" --output "D:\project\godot\blockking\assets"

python scripts/extract_aseprite_frames.py "D:\project\godot\blockking\aseprite_assets\*.aseprite" --preview

python scripts/extract_aseprite_frames.py "D:\project\godot\blockking\aseprite_assets\Archer.aseprite" --aseprite "D:\tools\Aseprite-v1.3.15.3-Windows\aseprite.exe" --output "D:\project\godot\blockking\assets" --layer-export "name=effect;output=D:\project\godot\blockking\assets_effect;layers=effect" --preview

python scripts/extract_aseprite_frames.py "D:\project\godot\blockking\aseprite_assets\Armored Orc.aseprite" --aseprite "D:\tools\Aseprite-v1.3.15.3-Windows\aseprite.exe" --output "D:\project\godot\blockking\assets" --layer-export "name=effect;output=D:\project\godot\blockking\assets_effect;layers=effect;strict=false" --main-ignore-layer shadow --tag Attack03 --preview

python scripts/extract_aseprite_frames.py "D:\project\godot\blockking\aseprite_assets" --aseprite "D:\tools\Aseprite-v1.3.15.3-Windows\aseprite.exe" --output "D:\project\godot\blockking\assets" --layer-export "name=effect;output=D:\project\godot\blockking\assets_effect;layers=effect;clean=true" --layer-export "name=shadow;output=D:\project\godot\blockking\assets_shadow;layers=shadow;strict=false;clean=true" --clean-target --preview

python scripts/extract_aseprite_frames.py "D:\project\godot\blockking\aseprite_assets" --aseprite "D:\tools\Aseprite-v1.3.15.3-Windows\aseprite.exe" --output "D:\project\godot\blockking\assets" --split-shadow --shadow-layer shadow --shadow-output "D:\project\godot\blockking\assets_shadow" --clean-target --clean-shadow-target --strict-shadow-layer
```

## Shadow compatibility
- `--split-shadow`: legacy helper for main/shadow dual export.
- `--shadow-layer <name>`: repeatable shadow layer names. Default: `shadow`.
- `--shadow-output <dir>`: shadow output root. Default: `assets_shadow`.
- `--strict-shadow-layer` / `--no-strict-shadow-layer`: strict mode is still the default.
- `--clean-shadow-target`: clean `shadow-output/<sprite-name>` before export. Requires `--split-shadow`.

## Safety
- The script checks for nested `.git` directories before recursive deletion.
- In `--preview` mode:
  - no output directories are deleted
  - no files are written
  - planned commands are printed for review

## scripts/
- `scripts/extract_aseprite_frames.py`: Calls Aseprite CLI to export per-tag frames into folders, with optional named layer-group exports.
