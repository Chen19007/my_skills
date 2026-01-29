---
name: godot-web-e2e
description: End-to-end testing for any Godot Web export using Chrome DevTools and a local HTTP server. Use when verifying gameplay behavior in a Web build (not editor) and you need repeatable DevTools-driven input checks and console evidence.
---

# Godot Web E2e

## Overview

Verify Godot gameplay in Web exports using Chrome DevTools only. Export, serve, open in Chrome, focus the canvas, inject input events via DevTools tools, and confirm outcomes via console logs or visible state changes. This skill is project-agnostic; fill in paths, export preset names, and ports for the current project.

## Workflow

### 1) Export Web build

Locate the Godot executable and the project path. Identify the Web export preset name from `export_presets.cfg` (e.g., `Web`).

Run:

```
godot --headless --path "<PROJECT_PATH>" --export-release "<WEB_PRESET_NAME>" "<WEB_EXPORT_PATH>"
```

### 2) Serve the build

Run from the export directory (the folder containing the HTML/JS/WASM):

```
python -m http.server <PORT>
```

### 3) Open in Chrome DevTools

Open:

```
http://localhost:<PORT>/<EXPORT_HTML_FILENAME>
```

Use Chrome DevTools tools to:

- Focus canvas.
- Send input (press/hold keys).
- Read console logs for movement/blocking/transport/respawn confirmation.

### 4) Required validation signals

Confirm at least one of each category in DevTools Console:

- **Movement**: any position/velocity/animation log shows a change after left/right input.
- **Blocking/Action**: state toggles after block/action input.
- **Transport/Transition**: log shows section/scene switch.
- **Respawn/Restart**: log indicates respawn or restart completed.

### 5) Cleanup

Stop any `python -m http.server` processes started for the test.

## Rules

- Use Chrome DevTools for E2E input checks.
- Do NOT use in-game auto input scripts or WebInputTest as a substitute.
