---
name: godot-verify
description: |
  Validate Godot GDScript files using gdlint, gdformat, gdradon, and LSP diagnostics.
  Use when users want to: (1) Check code quality after making changes, (2) Validate before committing, (3) Run code metrics analysis, (4) Run export validation, (5) Get real-time LSP diagnostics.
  Uses command-line tools directly and MCP tools for LSP integration.
license: MIT
---

# Godot Verification Skill

Validate Godot project changes using gdlint, gdformat, gdradon, godot export commands, and LSP diagnostics.

## 排除规则

**不要检查和处理 `addons` 目录下的任何文件。**

`addons` 目录通常包含第三方插件或外部资源，这些代码不由项目维护，不应纳入项目代码质量检查范围。

## 检查项

| 检查 | 命令/工具 | 说明 |
|------|----------|------|
| Lint | `gdlint` | Lint GDScript 代码 |
| Format | `gdformat` | 格式化/检查格式 |
| Metrics | `gdradon cc` | 代码指标分析 |
| Export | `godot --export-pack` | 导出验证 |
| **LSP Diagnostics** | **`godot-lsp__diagnostics`** | **实时语法检查（通过 MCP）** |

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
gdlint "<project-root>/scripts/Player.gd"

# Format 检查
gdformat --check "<project-root>/scripts/Player.gd"

# 代码指标
gdradon cc "<project-root>/scripts"

# LSP 诊断（通过 MCP 工具获取）
# 调用 MCP 工具获取诊断（只需 uri 参数）
godot-lsp__diagnostics(uri="file:///absolute/path/to/project/player.gd")

# LSP 诊断（修改代码后使用 refresh=true）
godot-lsp__diagnostics(uri="file:///absolute/path/to/project/player.gd", refresh=true)

# 完整检查
gdlint "<project-root>/scripts" && gdformat "<project-root>/scripts" && gdradon cc "<project-root>/scripts"

# 导出验证
godot --headless --path "<project-root>" --export-pack "Web" "<output-dir>/export.pck"
```

## LSP Diagnostics

**Godot LSP 诊断提供实时的语法检查和错误检测，与 Godot 编辑器显示的诊断一致。**

### 前置条件

1. **Godot 编辑器运行**（Godot LSP 服务器在编辑器启动时自动开启，默认端口 6005）
2. **Godot LSP diagnostics MCP 工具可用**（只通过 MCP 工具获取诊断）

### MCP 工具调用

**工具名**: `godot-lsp__diagnostics`

> 不要直接调用 DiagnosticsServer 的 HTTP API；这是内部实现细节，agent 只能通过 `godot-lsp__diagnostics` MCP 工具获取诊断。若 MCP 工具不可用，应报告“当前线程不可用”，不要改用 HTTP 兜底。

**参数**:
- `uri` (必需): `file://` URI，例如 `file:///absolute/path/to/project/player.gd`
- `refresh` (可选): 是否强制刷新诊断缓存，默认 false

**返回**:
```json
{
  "uri": "file:///absolute/path/to/project/player.gd",
  "diagnostics": [
    {
      "range": { "start": { "line": 4, "character": 0 }, "end": { "line": 4, "character": 56 } },
      "severity": 2,
      "code": 9,
      "source": "gdscript",
      "message": "(SHADOWED_GLOBAL_IDENTIFIER): The constant \"AttackType\" has the same name as a global class..."
    }
  ],
  "cached": false  // true 表示从缓存返回，false 表示新打开文件
}
```

**说明**:
- MCP diagnostics 工具会读取目标文件内容，无需传递 `text` 参数
- 首次查询会打开文件并等待诊断（约 500ms）
- 后续查询直接从缓存返回，速度更快
- **修改代码后推荐使用 `refresh=true` 强制刷新缓存**，确保获取最新诊断结果

### 诊断级别 (severity)

| 级别 | 值 | 说明 |
|------|-----|------|
| Error | 1 | 错误，必须修复 |
| Warning | 2 | 警告，建议修复 |
| Information | 3 | 信息 |
| Hint | 4 | 提示 |

### 常见诊断代码

| 代码 | 消息 | 说明 |
|------|------|------|
| 1 | `PARSER_ERROR` | 语法错误 |
| 9 | `SHADOWED_GLOBAL_IDENTIFIER` | 常量名与全局类冲突 |
| 12 | `STATIC_VARIABLE_TYPE_MISMATCH` | 静态变量类型不匹配 |
| 21 | `RETURN_VALUE_DISCARDED` | 返回值未使用 |
| 30 | `UNSAFE_CALL` | 不安全的函数调用 |
| 40 | `UNASSIGNED_VARIABLE_ACCESS` | 访问未赋值的变量 |

### 与 gdlint 对比

| 特性 | LSP Diagnostics | gdlint |
|------|----------------|--------|
| 实时性 | 实时（缓存） | 需要运行 |
| 错误类型 | 语法 + 语义 | Lint 规则 |
| 与编辑器一致 | 完全一致 | 可能不同 |
| 速度 | 快（有缓存） | 慢（需解析） |
| 需要 Godot | 是 | 否 |

**建议**: 使用 LSP Diagnostics 作为快速检查，gdlint 作为补充 lint 规则检查。

## 资源导入前置检查

当在项目中新增 `png`、`tscn` 等资源后，如果 `preload("res://...")`、Godot 编辑器或 `godot-lsp__diagnostics` 报告 `has no resource loaders` 或 `No loader found for resource` 错误，**请先不要** 将代码修改为运行时文件读取方式。

应按以下步骤进行检查和修复：

1. **检查导入状态**：验证资源文件旁是否存在对应的 `.import` 文件，以及 `.godot/imported/` 目录下是否生成了相应的导入产物（如 `.ctex`、`.md5` 文件）。
2. **执行导入命令**：若缺失导入产物，优先执行 Godot 的官方导入链进行修复：
   ```bash
   godot --headless --path "<项目根目录绝对路径>" --import --quit
   ```

导入成功后，应能在资源旁看到对应 `.import` 文件，并在 `.godot/imported/` 下看到相应导入产物；随后再重新检查 `preload("res://...")`、编辑器或 LSP 诊断中的资源加载错误。

## 场景与 UID 验证

修改 `.tscn` / `.tres` 后，运行本 skill 自带的 UID 验证脚本、Godot 导入链和目标场景加载验证。

必须用 PowerShell 7+ 的 `pwsh` 运行 `scripts/verify_godot_uids.ps1`，不要用 Windows PowerShell 5.1 的 `powershell.exe`。脚本内部也会检查 PowerShell 版本；Windows PowerShell 5.1 缺少 `[System.IO.Path]::GetRelativePath`，会被明确拒绝。

从 `godot-verify` skill 目录运行：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File "./scripts/verify_godot_uids.ps1" -ProjectRoot "<project-root>"
```

从任意目录运行时，使用脚本的绝对路径：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File "<skill-root>/scripts/verify_godot_uids.ps1" -ProjectRoot "<project-root>"
```

目标场景加载验证示例：

```bash
godot --headless --path "<project-root>" --scene "res://path/to/scene.tscn" --quit
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
gdlint "<project-root>/scripts/Player.gd"
```

### Pre-commit Validation
```bash
gdlint "<project-root>/scripts" && gdformat "<project-root>/scripts"
```

### Code Metrics Analysis
```bash
gdradon cc "<project-root>/scripts"
```
输出示例：
```
.\character_body_2d.gd
    F 13:0 _physics_process - C (15)
```

### Export Validation
```bash
godot --headless --path "<project-root>" --export-pack "Web" "<output-dir>/export.pck"
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






