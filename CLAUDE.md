# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

This is a **Claude Code Skills** project for developing and managing custom Claude Code skills. Each skill is a subdirectory with its own SKILL.md.

## Directory Structure

```
D:/project/docs/my_skills/
├── godot-verify/        # Skill: Godot project verification
│   └── SKILL.md
├── another-skill/       # Another skill
│   └── SKILL.md
├── .claude/             # Claude Code configuration (project settings)
└── CLAUDE.md            # This file
```

## Path Requirements

- All path parameters MUST be absolute paths

## Build & Test Commands

```bash
# Test skill locally (load from project root)
cc --plugin-dir D:/project/docs/my_skills
```

## Skill Development

After modifying skills in this project, manually sync to global skills directory:
- Source: `D:/project/docs/my_skills/<skill-name>`
- Target: `C:\Users\hpc\.claude\skills\<skill-name>`
