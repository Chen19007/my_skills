---
name: godot-tdd-full
description: Complete TDD workflow for Godot projects. Integrates interface design, GUT testing, code implementation, and verification tools.
---

# Godot TDD 完整工作流

本 Skill 提供 Godot TDD（测试驱动开发）的完整工作流，整合接口设计、测试开发、代码实现和质量验证。

## 快速开始

```json
// 开始新功能的 TDD 流程
{ "skill": "godot-tdd-full", "action": "start", "feature": "功能名称", "description": "功能描述" }

// 设计文件写入后，等待用户确认
{ "skill": "godot-tdd-full", "action": "approve_design" }

// 用户确认后，进入测试阶段
{ "skill": "godot-tdd-full", "action": "next_phase" }

// 运行测试验证
{ "skill": "godot-tdd-full", "action": "run_tests", "project": "D:/path/to/project" }
```

## TDD 工作流（带用户确认）

```
┌─────────────────────────────────────────────────────────────────────┐
│                       TDD 完整流程                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. start          → 生成设计文档                                   │
│       ↓                                                                │
│  2. [等待用户确认]  → 用户评审 design.md                             │
│       ↓                                                                │
│  3. approve_design → 用户批准设计                                   │
│       ↓                                                                │
│  4. next_phase     → 进入测试阶段                                   │
│       ↓                                                                │
│  5. 编写测试       → 运行测试（预期失败 red）                        │
│       ↓                                                                │
│  6. next_phase     → 进入实现阶段                                   │
│       ↓                                                                │
│  7. 最小实现       → 让测试通过（green）                             │
│       ↓                                                                │
│  8. next_phase     → 进入验证阶段                                   │
│       ↓                                                                │
│  9. verify         → lint/format 检查                               │
│       ↓                                                                │
│  10. next_phase    → 进入测试阶段                                   │
│       ↓                                                                │
│  11. run_tests     → 运行测试验证（refactor）                       │
│       ↓                                                                │
│  循环直到功能完成                                                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 用户参与点

| 阶段 | 操作 | 说明 |
|-----|------|------|
| `start` | LLM 执行 | 生成设计文档 |
| `approve_design` | **用户执行** | 评审并批准设计 |
| `next_phase` | LLM 执行 | 进入下一阶段 |
| `run_tests` | LLM 执行 | 运行测试 |

### 关键规则

1. **设计阶段必须等待用户确认** - 使用 `approve_design` 显式确认
2. **用户确认后才能写测试** - 确保设计被认可
3. **实现必须严格遵循设计** - 如需修改接口，返回设计阶段

---

## Phase 1: 接口设计 (Design)

### Godot 类系统基础

在 Godot 中，脚本不是真正的类，而是附加到引擎内置类的资源：

```gdscript
# 脚本继承 Node，成为其扩展
class_name Player extends Node

# 也可以不写 extends，隐式继承 RefCounted
class_name MathUtils
```

**关键点**：
- 脚本通过 `class_name` 注册到 ClassDB
- 无 `extends` 时隐式继承 `RefCounted`
- 场景是可复用、可实例化、可继承的节点组

### 状态查询方法（必备）

测试需要能够验证对象状态，必须提供查询方法：

```gdscript
class_name Player extends Node

var _health: int = 100
var _speed: float = 300.0

# 状态查询方法（供测试断言使用）
func get_health() -> int:
    return _health

func is_alive() -> bool:
    return _health > 0
```

### 动作方法签名

```gdscript
# 好的例子：有明确的类型注解和返回值
func move_to(target: Vector2) -> void:
    ...

func take_damage(amount: int) -> void:
    ...

func heal(amount: int) -> int:  # 返回实际恢复的血量
    ...
```

### 信号定义（解耦）

```gdscript
class_name Player extends Node

# 状态变化信号
signal health_changed(new_health: int, old_health: int)
signal died()

# 使用示例
func take_damage(amount: int) -> void:
    var old_health = _health
    _health = max(0, _health - amount)
    health_changed.emit(_health, old_health)
    if _health == 0:
        died.emit()
```

### 错误处理

```gdscript
class_name FileManager extends Node

# 使用 Error 枚举作为返回值
func load_file(path: String) -> Error:
    var file = FileAccess.open(path, FileAccess.READ)
    if not file:
        return FileAccess.get_open_error()
    return OK
```

### 接口契约测试（重要）

**核心原则**：测试覆盖 = 被测模块 + 它调用的所有依赖

#### 问题案例

```gdscript
# DifficultySelect.gd (UI层) - 调用者
func _show_description():
    # ❌ 调用了不存在的方法
    var desc = DifficultyManager.get_difficulty_description_by_id(_difficulty)

# DifficultyManager.gd - 提供者
func get_difficulty_description(id: int) -> String:  # ✅ 实际方法名
    ...
```

**为什么测试没发现**：
- 只测试了 DifficultyManager 内部逻辑
- 没有测试 DifficultySelect 的调用路径

#### 测试覆盖规则

| 修改的文件 | 必须测试的内容 |
|-----------|---------------|
| Manager.gd | 内部逻辑 + 所有公开 API |
| UI.gd | UI 逻辑 + 它调用的 Manager 方法 |
| 新增交互 | 两个模块的集成测试 |

#### 调用者测试示例

```gdscript
# test_difficulty_select.gd
extends GutTest

func test_difficulty_select_calls_manager():
    var dm = DifficultyManager.new()
    var ui = DifficultySelect.new()
    ui.manager = dm

    ui._on_selected(1)

    # 如果方法名错误，这里会失败
    assert_called(dm, "get_difficulty_description", [1])
```

### 设计检查清单

- [ ] 符合 Godot 类系统规则
- [ ] 单一职责
- [ ] 有测试友好的查询方法
- [ ] 所有方法有类型注解

---

### 设计文档模板

设计阶段需要输出以下文档到项目目录：

```
{project}/
├── specs/                          # 设计文档目录
│   └── {feature}/                  # 按功能划分
│       ├── design.md               # 需求 + 接口设计（合并）
│       ├── test_cases.md           # 测试用例清单
│       └── implementation_plan.md  # 实现计划/伪代码
```

#### design.md 模板

```markdown
# {功能名} 设计文档

## 1. 需求描述

### 1.1 功能概述
描述功能的核心目的和业务价值。

### 1.2 功能列表
| 编号 | 功能 | 优先级 | 说明 |
|-----|------|-------|------|
| F1  |      | P0    |      |

### 1.3 用户故事
**作为** [角色]
**我希望** [功能]
**以便** [价值]

### 1.4 输入输出
#### 输入
| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|

#### 输出
| 结果 | 类型 | 说明 |
|-----|------|------|

### 1.5 约束条件
- 性能要求
- 兼容性要求
- 其他约束

### 1.6 验收标准
- [ ] 验收标准1
- [ ] 验收标准2

---

## 2. 接口设计

### 2.1 类定义
#### {ClassName}
```gdscript
class_name {ClassName} extends {BaseClass}

# 导出配置
@export var {prop}: {Type} = {default}

# 私有变量
var _{prop}: {Type}

# 状态查询方法
func get_{property}() -> {Type}:
func is_{condition}() -> bool:

# 动作方法
func {method}({params}) -> {ReturnType}:

# 信号
signal {signal_name}({params})
```

### 2.2 接口清单
| 类 | 方法/属性 | 类型 | 说明 |
|---|----------|------|------|

### 2.3 状态机设计
| 当前状态 | 操作 | 下一状态 |

---

## 3. 版本历史
| 版本 | 日期 | 变更说明 |
|-----|------|---------|
| v1.0 |      | 初始版本 |
```

#### test_cases.md 模板

```markdown
# {功能名} 测试用例

## 1. 测试类
`test_{feature}.gd`

## 2. 等价类划分
| 输入类型 | 有效类 | 无效类 |
|---------|-------|-------|
| {param} | 1-100 | <1, >100 |

## 3. 边界值测试
| 用例 | 输入 | 预期 |
|-----|------|------|
| test_{name} | {value} | {result} |

## 4. 状态转换测试
| 当前状态 | 操作 | 下一状态 |

## 5. 版本历史
| 版本 | 日期 | 变更说明 |
|-----|------|---------|
| v1.0 |      | 初始版本 |
```

---

### 接口修改规则

**核心原则**：实现必须严格遵循设计定义的接口

#### 允许修改接口的流程

```
发现需要修改接口
       ↓
┌─────────────────────────────────────────────┐
│  不能直接修改代码！循环到设计阶段            │
│       ↓                                     │
│  1. 在 design.md 中更新接口定义              │
│  2. 更新 test_cases.md (如果需要)           │
│  3. 用户评审设计变更                        │
│  4. 设计确认后重新实现                       │
└─────────────────────────────────────────────┘
```

#### 禁止行为

- ❌ 直接在实现代码中修改接口签名
- ❌ 跳过设计阶段直接添加方法
- ❌ 忽略设计文档进行编码

---

## Phase 2: 测试开发 (Test)

### 前置条件

**安装 GUT 插件：**
```bash
cd your-project/addons
git clone https://github.com/bitwes/Gut.git gut
```

### 测试脚本结构

```gdscript
extends GutTest

func before_all():
    # 所有测试前执行一次
    pass

func test_my_functionality():
    # 测试代码
    assert_eq(result, expected, "描述")

func before_each():
    # 每个测试前执行

func after_each():
    # 每个测试后执行
```

### 常用断言

```gdscript
assert_eq(actual, expected, message)
assert_ne(a, b, message)
assert_true(condition, message)
assert_false(condition, message)
assert_null(value, message)
assert_not_null(value, message)
assert_between(value, min_val, max_val, message)
```

### 测试命名约定

```gdscript
# 文件命名
test_player.gd
test_math_utils.gd

# 方法命名
func test_player_take_damage_reduces_health():
    ...
```

### 参数化测试

```gdscript
func get_damage_test_params():
    return [
        ["damage_10", 10, 90],
        ["damage_50", 50, 50],
        ["damage_overkill", 1000, 0],
    ]

func test_params_damage(data = get_damage_test_params()):
    var amount = data[1]
    var expected = data[2]
    var player = Player.new()
    player.take_damage(amount)
    assert_eq(player.get_health(), expected)
```

### 测试 Autoload 单例

GUT **支持加载 Autoload 单例**，并提供专门的 API 进行 Mock/Stub。

#### 访问单例

```gdscript
extends GutTest

# GUT 默认会加载项目的所有 autoload
func test_access_singleton():
    # 直接访问单例（使用真实实例）
    var score = GameManager.get_score()
    assert_eq(score, 0)
```

#### Mock 单例（Double）

```gdscript
# 创建单例的完整 Double
func test_with_singleton_double():
    var gm = double_singleton("GameManager")

    # Stub 方法
    stub(gm, "get_score").to_return(100)

    # 测试代码
    assert_eq(gm.get_score(), 100)
```

#### Partial Double 单例（推荐）

```gdscript
# 使用 Partial Double 保留原始实现
func test_with_partial_singleton_double():
    var gm = partial_double_singleton("GameManager")

    # 只 stub 需要的方法，其他方法保持原始行为
    stub(gm, "reset_game").to_do_nothing()

    # 保留原始方法行为
    assert_eq(gm.get_level(), 1)
    assert_true(gm.is_game_active())
```

#### 完整示例

```gdscript
extends GutTest

# 测试 Player 与 GameManager 单例的交互
func test_player_death_updates_game_manager():
    # 使用 partial double 保留大部分行为
    var gm = partial_double_singleton("GameManager")
    stub(gm, "on_player_died").to_do_nothing()

    var player = Player.new()
    player.take_damage(100)

    # 验证调用了单例方法
    assert_called(gm, "on_player_died")
```

#### 单例测试最佳实践

| 场景 | 使用方法 |
|------|---------|
| 只需读取单例状态 | 直接访问真实单例 |
| 需要控制单例返回值 | `double_singleton()` |
| 需要保留大部分行为 | `partial_double_singleton()`（推荐） |
| 验证方法调用 | `assert_called()` + spy |

### 测试检查清单

- [ ] 测试能运行
- [ ] 测试失败（预期行为，尚未实现）
- [ ] 命名符合约定：`test_<类名>_<方法名>_<场景>`

---

## Phase 3: 代码实现 (Implement)

### GDScript 风格规则

#### 类型注解

```gdscript
# 函数参数和返回值（强制）
func move_to(target: Vector2) -> void:
    ...

func calculate_damage(base: float, multiplier: float) -> float:
    return base * multiplier

# 变量类型注解
var health: int = 100
var speed: float = 300.0
var position: Vector2 = Vector2.ZERO
```

#### 属性可见性

```gdscript
# 私有属性（使用下划线前缀）
var _health: int = 100
var _velocity: Vector2 = Vector2.ZERO

# 只读属性（使用 getter）
var health: int:
    get:
        return _health

# 导出变量（编辑器配置）
@export var max_health: int = 100
@export var move_speed: float = 300.0
```

#### 常量命名

```gdscript
const MAX_HEALTH := 100
const MOVE_SPEED := 300.0
const GRAVITY := 980.0
```

### Godot 特性使用

#### Signal（观察者模式）

```gdscript
signal health_changed(new_health: int)

func take_damage(amount: int) -> void:
    _health = max(0, _health - amount)
    health_changed.emit(_health)

func _ready() -> void:
    health_changed.connect(_on_health_changed)
```

#### @onready（节点引用）

```gdscript
extends Node2D

@onready var sprite: Sprite2D = $Sprite2D
@onready var animation: AnimationPlayer = $AnimationPlayer
```

### @export（编辑器配置）

```gdscript
@export var max_health: int = 100
@export var move_speed: float = 300.0

# 资源类型
@export var bullet_scene: PackedScene

# 枚举类型
@export_enum("Fast", "Normal", "Slow") var speed_mode: String = "Normal"
```

### 常见反模式

| 反模式 | 错误示例 | 正确做法 |
|-------|---------|---------|
| 直接暴露内部变量 | `var health: int = 100` | `var _health; func get_health()` |
| 缺少类型注解 | `func move_to(target):` | `func move_to(target: Vector2)` |
| 不使用 @onready | `get_node("Sprite2D")` | `@onready var sprite = $Sprite2D` |
| 测试逻辑污染 | `if is_in_test_mode:` | 测试逻辑完全分离 |

### 实现检查清单

- [ ] 所有函数有类型注解
- [ ] 变量有类型注解
- [ ] 私有属性使用下划线前缀
- [ ] 使用 @onready 而非 get_node()
- [ ] 信号正确解耦
- [ ] 避免循环依赖

---

## Phase 4: 质量验证 (Verify)

### 可用工具

| 工具 | 用途 | 参数 |
|------|------|------|
| `gdlint` | Lint GDScript 文件 | `project`, `file`, `all` |
| `gdformat` | 格式化/检查 GDScript | `project`, `file`, `check` |
| `godot_get_errors` | 解析错误日志 | `project`, `log_file` |
| `godot_check_all` | 运行所有检查 | `project`, `file` |

### Lint 规则

| 规则 | 严重性 | 描述 |
|------|--------|------|
| `unused-variable` | Error | 变量声明但未使用 |
| `shadowed-variable` | Error | 变量遮蔽成员变量 |
| `function-name` | Error | 函数名违反命名约定 |
| `trailing-whitespace` | Warning | 行尾有空白 |
| `missing-docstring` | Warning | 函数缺少文档 |
| `line-too-long` | Warning | 行超过 120 字符 |

### 使用示例

```json
// 运行完整项目检查
{ "project": "D:/path/to/godot-project" }

// 检查单个文件
{ "project": "D:/path/to/godot-project", "file": "D:/path/to/script.gd" }

// 仅检查格式（不修改）
{ "project": "D:/path/to/godot-project", "file": "D:/path/to/script.gd", "check": true }
```

### 验证检查清单

- [ ] lint 通过
- [ ] format 通过
- [ ] 无错误

---

## Phase 5: 运行测试 (Run Tests)

### 命令格式

```bash
godot --path <project> -s addons/gut/gut_cmdln.gd [options]
```

### 可用选项

| 选项 | 描述 |
|-----|------|
| `-gdir=<path>` | 测试目录（默认：`res://test/`） |
| `-gtest=<path>` | 特定测试文件路径 |
| `-gselect=<pattern>` | 按名称模式匹配测试文件 |
| `-gunit_test_name=<name>` | 运行特定测试方法 |
| `-gexit` | 测试完成后退出 |
| `-glog=<0-3>` | 日志级别 |

### 示例

```bash
# 运行所有测试
godot --path . -s addons/gut/gut_cmdln.gd -gexit

# 运行特定测试文件
godot --path . -s addons/gut/gut_cmdln.gd -gtest=res://test/test_player.gd -gexit

# 按模式运行测试
godot --path . -s addons/gut/gut_cmdln.gd -gselect=player -gexit
```

### 测试结果解读

**返回码：**
- `0` = 所有测试通过
- `1` = 部分测试失败

**输出格式：**
```
res://test/test_example.gd
* test_should_pass
* test_another_pass
[2/2 passed]

Totals
------
Scripts: 1
Tests: 2
Passing: 2
Failing: 0
```

### 运行测试检查清单

- [ ] 所有测试通过
- [ ] 覆盖率满足要求

---

## 完整示例

### 需求：Player 受伤系统

```json
{
  "skill": "godot-tdd-full",
  "action": "start",
  "feature": "Player受伤系统",
  "description": "实现 Player 受伤后扣除血量并发出信号的功能"
}
```

### Phase 1: 设计

```gdscript
# Player.gd (接口定义)
class_name Player extends Node

signal health_changed(new_health: int)
signal died()

func get_health() -> int:
    ...

func take_damage(amount: int) -> void:
    ...
```

### Phase 2: 测试

```gdscript
# test_player.gd
extends GutTest

func test_player_take_damage_reduces_health():
    var player = Player.new()
    player.take_damage(10)
    assert_eq(player.get_health(), 90)

func test_player_dies_when_health_reaches_zero():
    var player = Player.new()
    player.take_damage(100)
    assert_false(player.is_alive())
```

### Phase 3: 实现

```gdscript
# Player.gd (完整实现)
class_name Player extends Node

var _health: int = 100

signal health_changed(new_health: int)
signal died()

func get_health() -> int:
    return _health

func is_alive() -> bool:
    return _health > 0

func take_damage(amount: int) -> void:
    _health = max(0, _health - amount)
    health_changed.emit(_health)
    if _health == 0:
        died.emit()
```

### Phase 4: 验证

```json
{ "project": "D:/path/to/project", "file": "D:/path/to/Player.gd" }
```

### Phase 5: 运行测试

```bash
godot --path . -s addons/gut/gut_cmdln.gd -gtest=res://test/test_player.gd -gexit
```

---

## 循环依赖处理

当脚本存在循环依赖时：

```gdscript
# 错误：循环依赖
func register_character(character: Character2D, height_x: float):

# 解决：使用基类参数
func register_character(character: Node, height_x: float):
```

---

## 最佳实践

1. **测试隔离** - 每个测试独立，不依赖其他测试
2. **描述性命名** - `test_player_jump_calculation` 而不是 `test1`
3. **单一断言** - 每个测试验证一个具体行为
4. **清理资源** - 测试后调用 `queue_free()`
5. **浮点数比较** - 使用 `is_equal_approx()` 避免精度问题
6. **只测试公共接口** - 通过设计阶段定义的接口测试

---

## 故障排除

| 错误 | 解决方案 |
|-----|---------|
| `File not found: addons/gut/gut_cmdln.gd` | 安装 GUT 插件 |
| `Nonexistent function 'is_above'` | 修复脚本循环依赖 |
| `Cannot call non-static function on class` | 检查 autoload 配置 |
| `GUT class_names not imported` | 先运行 `godot --import` |
| 测试未找到 | 检查 `-gdir` 路径和 `-gprefix` 设置 |
| `overlaps_body` 类型错误 | PhysicsBody 用 `overlaps_body`，Area2D 用 `overlaps_area` |

---

## 注意事项

1. **每个阶段必须通过检查点才能进入下一阶段**
   - Phase 1: 设计完成并经用户确认
   - Phase 2: 测试能运行且失败（预期）
   - Phase 3: 测试通过
   - Phase 4: lint/format 检查通过
   - Phase 5: 所有测试通过

2. **重构必须确保测试通过**
   - 重构前确保所有测试通过
   - 重构后运行测试验证
   - 保持测试覆盖率

3. **所有代码修改后必须运行完整验证**
   - 静态检查：gdlint + gdformat
   - 运行时检查：GUT 测试（捕获动态错误）
   - 两者缺一不可

4. **测试命名遵循约定**
   - 文件命名：`test_<类名>.gd`
   - 方法命名：`test_<类名>_<方法名>_<场景>`

5. **接口契约不可破坏**
   - 实现必须严格遵循设计定义的接口
   - 如需修改接口，必须返回 Phase 1 更新设计文档
   - 禁止直接在实现代码中修改接口签名

6. **测试覆盖 = 被测模块 + 它调用的所有依赖**
   - 修改 Manager.gd → 测试 Manager 内部逻辑 + 所有公开 API
   - 修改 UI.gd → 测试 UI 逻辑 + 它调用的 Manager 方法
   - 新增交互 → 测试两个模块的集成
