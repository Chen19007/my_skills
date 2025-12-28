---
name: godot-verify
description: Validate Godot GDScript files using gdlint, gdformat, and error log parsing. Use when users want to: (1) Check code quality after making changes, (2) Validate before committing, (3) Debug runtime errors, (4) Run export validation. Chains godot-mcp tools for comprehensive project checking.
license: MIT
---

# Godot Verification Skill

Validate Godot project changes using gdlint, gdformat, and error log parsing via godot-mcp server.

## Available Tools

| Tool | Purpose | Parameters |
|------|---------|------------|
| `gdlint` | Lint GDScript files | `project`, `file`, `all` |
| `gdformat` | Format/check GDScript | `project`, `file`, `check` |
| `godot_export_validate` | Validate export dependencies | `project`, `preset` |
| `godot_get_errors` | Parse error logs | `project`, `log_file` |
| `godot_check_all` | Run all checks sequentially | `project`, `file` |

## Quick Start

```json
// Run full project check
{ "project": "D:/path/to/godot-project" }

// Check single file
{ "project": "D:/path/to/godot-project", "file": "D:/path/to/script.gd" }

// Check format only (no changes)
{ "project": "D:/path/to/godot-project", "file": "D:/path/to/script.gd", "check": true }
```

## Path Conversion

godot-mcp returns paths in `res://` format. Convert to local paths:

```
res://scripts/Player.gd → {project}/scripts/Player.gd
res://autoload/Game.gd → {project}/autoload/Game.gd
res://:// → {project}/
```

## Lint Rules (gdlint)

| Rule | Severity | Description |
|------|----------|-------------|
| `unused-variable` | Error | Variable declared but never used |
| `shadowed-variable` | Error | Variable shadows member variable |
| `function-name` | Error | Function name violates naming convention |
| `constant-name` | Error | Constant name violates naming convention |
| `trailing-whitespace` | Warning | Lines have trailing whitespace |
| `missing-docstring` | Warning | Function missing documentation |
| `line-too-long` | Warning | Line exceeds 120 characters |

## Error Log Patterns

Parse logs for these patterns:
- `ERROR:` / `Error` / `error` - Critical errors
- `Identifier` - Undefined identifier references
- `res://` - File paths in error messages

## Report Format

```
=== Godot Verification Report ===

Project: {project}
Time: {timestamp}

[CRITICAL] {count}
  - {file}:{line} - {error message}

[WARNING] {count}
  - {file}:{line} - {warning message}

[FORMATTING] {count}
  - {file} - {what needs fixing}

[EXPORT] {pass|fail}
  - {export errors if any}

Summary: {total} issues found
  - {critical} critical, {warning} warnings, {formatting} formatting
```

## Error Handling

| Error | Solution |
|-------|----------|
| `No project.godot found` | Navigate to project root or provide absolute path |
| `gdlint not found` | Install: `pip install gdtoolkit` |
| `GDOT_BIN not set` | Set env or use `godot` in PATH |
| `Path must be absolute` | Convert relative to absolute paths |

## Common Workflows

### After Code Changes
```json
{ "project": "{project_path}", "file": "{changed_file}" }
```

### Pre-commit Validation
```json
{ "project": "{project_path}" }
```

### Debug Runtime Errors
1. Get errors: `godot_get_errors` with `log_file`
2. Check affected files: `gdlint` on specific files
3. Fix and format: `gdformat` (without check)

### Export Validation
```json
{ "project": "{project_path}", "preset": "Web" }
```

## Configuration

Set via MCP Proxy environment:
```
GODOT_BIN=godot          # Default: godot (in PATH)
```

## Tips

- Use `file` param to check only changed files (faster)
- `gdformat` with `check: true` shows what would change
- Export validation catches dependency issues lint misses
- Error logs show runtime issues lint misses
