---
name: godot-verify
description: Validate Godot project changes using gdlint, gdformat, and error checking. Use this skill when users want to verify GDScript code quality, check for lint errors, validate formatting, or parse error logs in a Godot project. This skill chains multiple godot-mcp tools to provide comprehensive validation.
license: MIT
---

# Godot Verification Skill

This skill validates Godot project changes by running a comprehensive check suite using the godot-mcp server tools.

## When to Use

- After making changes to GDScript files
- Before committing Godot project changes
- When debugging GDScript issues
- After running Godot exports
- When code review requires validation

## Workflow

Follow this process to validate Godot project changes:

### Step 1: Detect Godot Project Root

1. Find the project root directory containing `project.godot`
2. Use the current working directory or search parent directories
3. Verify the project path is absolute

### Step 2: Run Comprehensive Check

Use the `godot_check_all` tool with the detected project path:

```json
{
  "project": "<absolute_path_to_godot_project_root>"
}
```

This tool runs:
- **gdlint** on all GDScript files in the project
- **gdformat** in check mode (reports formatting issues without modifying)
- **godot_get_errors** to parse error logs

### Step 3: Parse Results

The tool returns results with:
- `success`: Overall success status
- `lint_results`: Linting output and any linting errors
- `format_results`: Formatting check output
- `export_results`: Export validation results (if requested)
- `error_logs`: Parsed error/warning patterns

### Step 4: Generate Report

Compile a validation report with:

**Format Issues:**
- List files with linting errors
- Show error counts and types

**Formatting Issues:**
- List files that need formatting
- Show what would change

**Error Log Issues:**
- Extract ERROR/Error/error patterns from logs
- Show file and line numbers if available

**Summary:**
- Total files checked
- Critical issues (errors)
- Warnings (formatting, style)
- Recommended actions

### Step 5: Provide Actionable Output

Report findings in a structured format:

```
=== Godot Verification Report ===

Project: <project_path>
Files Checked: <count>

[Critical Issues]
- <file>: <error description>

[Formatting Issues]
- <file>: <formatting suggestion>

[Warnings]
- <file>: <warning description>

[Recommendations]
1. Fix critical issues first
2. Run `gdformat` on files with formatting issues
3. Review warnings for potential improvements

Total: <N> issues found
```

## Error Handling

- If `godot_check_all` fails, try individual tools:
  - `gdlint` for linting
  - `gdformat` with `check: true` for formatting validation
  - `godot_get_errors` for log parsing

- If no Godot project found, report error with guidance:
  - "No `project.godot` file found in the current directory or parent directories"
  - "Please ensure you're in a valid Godot project directory"

## Example Output

```
=== Godot Verification Report ===

Project: D:/my-game
Files Checked: 47

[Critical Issues]
- res://scripts/Player.gd:12 - Variable 'health' shadows member variable
- res://scripts/Enemy.gd:45 - Unused variable 'old_velocity'

[Formatting Issues]
- res://scripts/Player.gd: Lines 20-25 need indentation adjustment
- res://scripts/GameManager.gd: Missing blank line before return statement

[Warnings]
- res://scripts/Enemy.gd:90 - Function 'take_damage' could be static

Recommendations:
1. Fix critical issues first (variable shadowing, unused variables)
2. Run `gdformat res://scripts/Player.gd` to fix formatting
3. Consider making 'take_damage' static if it doesn't use 'self'

Total: 5 issues found (2 critical, 2 formatting, 1 warning)
```

## Configuration

The skill uses these environment variables (configured in MCP Proxy):
- `GODOT_BIN`: Path to Godot executable (defaults to `godot` in PATH)

All paths must be absolute - the skill will handle path conversion if needed.
