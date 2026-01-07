---
name: godot-verify
description: Validate Godot GDScript files using gdlint, gdformat, and gdradon. Use when users want to: (1) Check code quality after making changes, (2) Validate before committing, (3) Run code metrics analysis, (4) Run export validation. Uses command-line tools directly.
license: MIT
---

# Godot Verification Skill

Validate Godot project changes using gdlint, gdformat, gdradon, and godot export commands.

## 检查项

| 检查 | 命令 | 说明 |
|------|------|------|
| Lint | `gdlint` | Lint GDScript 代码 |
| Format | `gdformat` | 格式化/检查格式 |
| Metrics | `gdradon cc` | 代码指标分析 |
| Export | `godot --export-pack` | 导出验证 |

## gdradon 输出

```
gdradon cc <path>
```

输出格式：
```
F <line>:<col> <function_name> - <grade> (<cc>)
```

| 字段 | 说明 |
|------|------|
| F | 函数 (Function) |
| `<line>:<col>` | 行号和列号 |
| `<function_name>` | 函数名 |
| `<grade>` | 复杂度等级: A(简单), B(中等), C(复杂), D(非常复杂), F(极复杂) |
| `<cc>` | 圈复杂度数值 |

示例：
```
.\character_body_2d.gd
    F 13:0 _physics_process - C (15)
```

## 使用示例

```bash
# Lint 检查
gdlint "D:/project/scripts/Player.gd"

# Format 检查
gdformat --check "D:/project/scripts/Player.gd"

# 代码指标
gdradon cc D:/project/scripts/

# 完整检查
gdlint D:/project/scripts/ && gdformat D:/project/scripts/ && gdradon cc D:/project/scripts/

# 导出验证
godot --headless --path "D:/project" --export-pack "Web" "D:/export.pck"
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

## Error Handling

| Error | Solution |
|-------|----------|
| `No project.godot found` | Navigate to project root or provide absolute path |
| `gdlint not found` | Install: `pip install gdtoolkit` |
| `gdradon not found` | Install: `pip install gdradon` |
| `godot not found` | Add godot to PATH |
| `Path must be absolute` | Convert relative to absolute paths |

## Common Workflows

### After Code Changes
```bash
gdlint "D:/project/scripts/Player.gd"
```

### Pre-commit Validation
```bash
gdlint D:/project/scripts/ && gdformat D:/project/scripts/
```

### Code Metrics Analysis
```bash
gdradon cc D:/project/scripts/
```
输出示例：
```
.\character_body_2d.gd
    F 13:0 _physics_process - C (15)
```

### Export Validation
```bash
godot --headless --path "D:/project" --export-pack "Web" "D:/export.pck"
```

## 安装要求

- `pip install gdtoolkit` (gdlint, gdformat)
- `pip install gdradon` (code metrics)
- `godot` in PATH (export validation)

## Tips

- Use `file` param to check only changed files (faster)
- `gdformat --check` shows what would change without modifying
- `gdradon cc` shows complexity and maintainability metrics
- Export validation catches dependency issues lint misses
