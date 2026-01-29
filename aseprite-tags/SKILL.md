---
name: aseprite-tags
description: Extract animation tag metadata (names, frame ranges, directions, colors) from .aseprite files without Aseprite; use when asked to list actions/animations, frame tags, or audit tags across multiple Aseprite assets.
---

# Aseprite Tag Extraction

## Quick start
- Run `python scripts/extract_aseprite_tags.py <file-or-folder-or-glob> [...]`.
- Directories are scanned for `*.aseprite`.
- Output is Markdown by default; use `--json` for structured output.

## Workflow
1. Identify target `.aseprite` files.
2. Run the script with a file, folder, or glob.
3. Use tag names and inclusive frame ranges (`from-to`) as animation actions.

## Notes
- Frame ranges are **inclusive**.
- Tag chunks may appear multiple times; the script de-duplicates identical tags.
- If no tags exist, it prints `(no tags found)` for that file.

## Examples
```bash
python scripts/extract_aseprite_tags.py d:\project\godot\blockking\assets
python scripts/extract_aseprite_tags.py "d:\project\godot\blockking\assets\*.aseprite"
python scripts/extract_aseprite_tags.py d:\project\godot\blockking\assets\Knight Templar.aseprite --json
```

## scripts/
- `scripts/extract_aseprite_tags.py`: Parse Aseprite binary format and output tag lists.
