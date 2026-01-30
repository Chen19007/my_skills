---
name: godot-test
description: |
  Run GUT unit tests for Godot projects.
  Use when: (1) Running unit tests, (2) Verifying code changes, (3) TDD development, (4) CI/CD testing.
---

# Godot 测试框架 Skill (GUT)

本 Skill 提供 GUT (Godot Unit Testing) 框架的使用指南，用于运行和编写测试。

## 适用场景

- 运行单元测试
- 验证代码修改
- TDD 开发流程
- CI/CD 自动化测试

## 前置条件

**安装 GUT 插件：**

1. 从 Godot 资源库或 https://github.com/bitwes/Gut 下载
2. 解压到项目的 `addons/gut/` 目录
3. 在项目设置中启用插件

**或通过 git：**
```bash
cd your-project/addons
git clone https://github.com/bitwes/Gut.git gut
```

## 快速开始

```json
// 运行所有测试
{ "project": "D:/path/to/godot-project" }

// 运行特定测试文件
{ "project": "D:/path/to/godot-project", "file": "res://test/test_my_feature.gd" }

// 按模式运行测试
{ "project": "D:/path/to/godot-project", "pattern": "test_player" }
```

## 命令格式

```bash
godot --path <project> -s addons/gut/gut_cmdln.gd [options]
```

## 可用选项

| 选项 | 描述 |
|-----|------|
| `-gdir=<path>` | 测试目录（默认：`res://test/`） |
| `-gtest=<path>` | 特定测试文件路径 |
| `-gselect=<pattern>` | 按名称模式匹配测试文件 |
| `-gunit_test_name=<name>` | 运行特定测试方法 |
| `-gexit` | 测试完成后退出 |
| `-glog=<0-3>` | 日志级别（0=最少，3=详细） |
| `-gprefix=<prefix>` | 测试文件前缀（默认：`test_`） |
| `-gsuffix=<suffix>` | 测试文件后缀（默认：`.gd`） |

## 示例

```bash
# 运行所有测试
godot --path . -s addons/gut/gut_cmdln.gd -gexit

# 运行特定测试文件
godot --path . -s addons/gut/gut_cmdln.gd -gtest=res://test/test_player.gd -gexit

# 按模式运行测试
godot --path . -s addons/gut/gut_cmdln.gd -gselect=player -gexit

# 运行并输出详细日志
godot --path . -s addons/gut/gut_cmdln.gd -glog=3 -gexit
```

## 测试结果解读

**返回码：**
- `0` = 所有测试通过
- `1` = 部分测试失败

**输出格式：**
```
res://test/test_example.gd
* test_should_pass
* test_another_pass
[1/2 passed]

res://test/test_failing.gd
* test_will_fail
[FAILED]: Expected value did not match
[1/3 passed]

Totals
------
Scripts: 2
Tests: 5
Passing: 4
Failing: 1
```

## 编写测试

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

### GUT 核心规则

| 规则 | 说明 |
|-----|------|
| 脚本继承 | `extends GutTest` |
| 方法前缀 | `test_`（不可配置） |
| 文件前缀 | `test_`（可配置） |
| 内部类分组 | `class TestXXX extends GutTest` |

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

func test_math_utils_add_two_plus_three_equals_five():
    ...

# 使用内部类分组
class TestHealth:
    extends GutTest

    func test_take_damage_reduces_health():
        ...

class TestMovement:
    extends GutTest

    func test_move_to_changes_position():
        ...
```

## 高级特性

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

### 双分体 (Mock/Spy)

```gdscript
func test_with_stub():
    var player = partial_double(Player.new())
    stub(player).to_receive("take_damage").and_return(true)

    var result = player.take_damage(10)
    assert_true(result)
```

### 模拟引擎调用

```gdscript
func test_physics_simulation():
    var player = Player.new()
    # 模拟 1 秒的 _process
    simulate(player._process, 1.0)

    # 模拟 10 帧
    for i in range(10):
        player._process(get_process_delta_time())
```

## 最佳实践

1. **测试隔离** - 每个测试独立，不依赖其他测试
2. **描述性命名** - `test_player_jump_calculation` 而不是 `test1`
3. **单一断言** - 每个测试验证一个具体行为
4. **清理资源** - 测试后调用 `queue_free()`
5. **浮点数比较** - 使用 `is_equal_approx()` 避免精度问题
6. **只测试公共接口** - 通过 godot-design 定义的接口测试

## 处理循环依赖

当脚本存在循环依赖时：

```gdscript
# 问题：循环依赖导致 GUT 加载失败
func register_character(character: Character2D5D, height_x: float):

# 解决：使用基类参数
func register_character(character: Node, height_x: float):
```

## CI/CD 集成

```bash
# 运行测试，失败时退出
godot --path . -s addons/gut/gut_cmdln.gd -gexit
if [ $? -ne 0 ]; then
    echo "Tests failed!"
    exit 1
fi
```

## 故障排除

| 错误 | 解决方案 |
|-----|---------|
| `File not found: addons/gut/gut_cmdln.gd` | 安装 GUT 插件 |
| `Nonexistent function 'is_above'` | 修复脚本循环依赖 |
| `Cannot call non-static function on class` | 检查 autoload 配置 |
| `GUT class_names not imported` | 先运行 `godot --import` |
| 测试未找到 | 检查 `-gdir` 路径和 `-gprefix` 设置 |
| `overlaps_body` 类型错误 | PhysicsBody 用 `overlaps_body`，Area2D 用 `overlaps_area` |
