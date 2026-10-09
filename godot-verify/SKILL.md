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

**Godot LSP 诊断检查对应项目中的 GDScript 语法与语义；必须先确认实际连接的是待检查项目。**

### 前置条件

1. **Godot 编辑器打开待检查文件所属的项目**，仅有编辑器进程或端口连通不代表项目匹配。
2. **Godot LSP diagnostics MCP 工具可用**。本技能不会安装或连接 MCP 服务；工具不可用时，报告“当前线程 LSP 工具不可用，检查未完成”。
3. 使用实际工具名及其当前参数定义；名称可能带有 MCP 服务前缀。只通过 MCP 工具获取诊断。

### MCP 工具调用

**工具名**: `godot-lsp__diagnostics`

> 不要直接调用 DiagnosticsServer 的 HTTP API；这是内部实现细节，agent 只能通过 `godot-lsp__diagnostics` MCP 工具获取诊断。若 MCP 工具不可用，应报告“当前线程不可用”，不要改用 HTTP 兜底。

**参数**:
- `uri` (必需): 待检查文件真实绝对路径对应的 `file://` URI。不要改成当前编辑器所在项目的同名文件，也不要使用 `res://`。
- `refresh` (可选): 检查修改后的代码时显式传入 `true`；具体默认值以工具参数定义为准。已核验的新版桥接工具每次读取磁盘代码并等待新诊断，即使传入 `false` 也不使用旧缓存判定通过。

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
  "cached": false
}
```

**说明**:
- MCP diagnostics 工具会读取目标文件内容，无需传递 `text` 参数
- 不假定固定返回时间；没有收到有效诊断时不能把超时解释为零错误。
- 新版桥接工具根据文件向上定位 `project.godot`，与 Godot 主动报告的实际项目目录比较；此规则适用于任意项目，不写死仓库或分支。
- 成功结果中的 `expectedRoot`、`actualRoot` 用于说明待检查项目和实际项目。目录规范化与项目核验由桥接工具负责，不能只按项目名称、文件名或相似结构判断。

### 检查结果与失败处理

先检查 MCP 外层 `isError`，再检查文本内容中的诊断结果。外层错误、正文包含 `error`、正文标记 `ok: false` 或缺少有效 `diagnostics` 数组，均表示 **LSP 检查未完成**；即使正文同时出现空数组，也不能报告通过。

只有成功收到当前文件的新诊断结果，才能根据诊断级别报告语法或语义错误。成功收到 `diagnostics: []` 表示本次文件没有诊断；非空列表按下表处理。旧缓存不能作为修改后代码的验证证据，其他 lint 或导出检查也不能冒充 LSP 验证。

| 失败情况 | 处理方式 |
|----------|----------|
| `LSP_PROJECT_MISMATCH` | 告知实际项目与目标项目，提醒用户关闭或切换现有 Godot 编辑器，打开错误中的 `expectedRoot`，然后重新检查；不改查另一项目的同名文件。 |
| `LSP_NOT_READY`、`LSP_PROJECT_UNKNOWN`、连接失败 | 提醒用户确认 Godot 已打开目标项目，并启用可连接的 LSP；不能确认实际项目时继续标记未完成。 |
| `LSP_DIAGNOSTICS_TIMEOUT`、断线 | 告知未收到有效诊断，提醒确认对应项目，必要时重启 Godot 编辑器；恢复后重新检查，不反复查询并把偶然空结果当作成功。 |
| 文件读取失败、URI 无效、找不到 `project.godot` | 检查实际文件路径和项目归属，不把这些失败归因于代码无错误。 |
| 错误正文已更新，但外层错误标记丢失 | 正文错误仍算失败；提示重新建立 Codex MCP 客户端连接，不能只重启后端服务后就认定客户端已加载新逻辑。 |

默认只报告失败并提示用户操作，不自动启动、关闭或重启 Godot。用户修正环境后复查；仍未完成时明确保留该阻塞，并继续不依赖 LSP 的独立检查。

依据：2026-10-09 实际通过 MCP 链路验证了 Demo 项目成功、正式版同名文件被拒绝、`isError: true` 与失败后恢复；重启 Codex 后当前聊天复查通过。Godot 4.6 官方源码中的 `gdscript_client/changeWorkspace` 通知提供实际项目目录：
https://github.com/godotengine/godot/blob/4.6-stable/modules/gdscript/language_server/gdscript_language_protocol.cpp （2026-10-09 获取）。

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
| 实时性 | 查询当前代码并等待诊断 | 需要运行 |
| 错误类型 | 语法 + 语义 | Lint 规则 |
| 项目上下文 | 必须连接对应项目 | 独立解析文件 |
| 速度 | 取决于连接与诊断推送 | 取决于文件解析 |
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






