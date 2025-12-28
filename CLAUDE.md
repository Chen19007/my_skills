# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

This is a **Claude Code Skills** project for Godot development verification. It provides a `/godot-verify` skill to validate Godot project changes using the godot-mcp server.

## MCP Server Configuration

This project uses the **MCP Proxy** at `http://localhost:8082/godot` path to access Godot development tools:

- **godot-check**: Godot 项目检查工具（lint + format + export validation）
- **godot-docs**: Godot 引擎文档查询

Configure your Claude Code to connect to:
```
MCP Proxy URL: http://localhost:8082/godot
```

## Available Skill

### /godot-verify

Validate Godot project changes by running:
- **gdlint**: Lint GDScript files for code quality
- **gdformat**: Check GDScript formatting
- **godot_get_errors**: Parse error logs for issues
- **godot_export_validate**: Validate export presets (optional)

**Usage:**
```
/godot-verify
```

This skill will:
1. Detect the Godot project root directory
2. Run lint checks on modified/new GDScript files
3. Check formatting consistency
4. Parse any error logs
5. Report all findings and issues

## Build & Test Commands

```bash
# Start MCP Proxy (if not already running)
cd D:/project/python/mcp-proxy
python main.py

# Test godot-mcp server directly
cd E:/project/typescript/godot-mcp
npm test
```

## Path Requirements

- All path parameters MUST be absolute paths
- Godot project root must contain `project.godot` file
- GDScript files must have `.gd` extension
