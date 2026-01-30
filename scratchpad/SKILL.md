---
name: scratchpad
description: |
  Workflow standardization for isolated trial experiments.
  Use when: (1) Testing hypotheses, (2) Trying API usage, (3) Debugging isolated issues, (4) Keeping main context clean. Focus on RESULTS, not process.
license: MIT
---

# Scratchpad Skill

Isolated temporary testing environment for quick code experiments and hypothesis validation. Focus on RESULTS, not process.

## 目的

快速验证猜想，不污染主上下文：
- 明确的开始/结束标识
- 结果导向：只返回关键结论
- 工作流标准化：所有尝试性操作遵循相同模式

## 进入/退出标识

### 进入 Scratchpad 模式

**触发信号：**
- 用户说 "试一下"、"测试一下"、"验证一下"
- 用户说 "创建一个测试文件"、"写个脚本试试"
- 大模型决定需要尝试验证某个假设

**进入动作：**
```
[进入 Scratchpad 模式]
1. 使用 temp_create_directory 创建临时目录
2. 记录 directory_id 和 modify_delete_key
3. 声明："正在创建临时测试环境..."
```

### 退出 Scratchpad 模式

**触发信号：**
- 实验完成，得到明确结论
- 实验失败，确认假设不成立
- 用户要求"回到主上下文"、"停止测试"

**退出动作：**
```
[退出 Scratchpad 模式]
1. 提取关键结果（成功/失败、关键数据、结论）
2. 可选：手动清理临时文件（temp_delete）
3. 声明："测试完成，返回结果："
4. 只展示关键结论，不展示过程
```

## MCP 工具映射

| 工作流步骤 | MCP 工具 | 参数 | 返回值 |
|-----------|---------|------|--------|
| 创建环境 | `temp_create_directory` | 无 | directory_id, path, modify_delete_key |
| 写入文件 | `temp_write` | directory_id, modify_delete_key, content, filename? | 文件路径 |
| 读取文件 | `temp_read` | directory_id, filename | 文件内容 |
| 列出文件 | `temp_list` | directory_id, pattern? | 文件列表 |
| 删除文件 | `temp_delete` | directory_id, modify_delete_key, filename | 删除结果 |
| 获取信息 | `temp_info` | directory_id | 目录信息 |
| 强制清理 | `temp_cleanup` | 无 | 清理结果 |

## 工作流示例

### 示例 1：Python 猜想验证

```
[进入 Scratchpad 模式]

用户："试一下 Python 的 re.split 是否支持多个分隔符"

大模型：
1. temp_create_directory → tmp_xxx
2. temp_write → test_regex.py
3. 执行：python E:/.llm/tmp_xxx/test_regex.py
4. 读取输出，验证结论
5. temp_delete → 清理测试文件

[退出 Scratchpad 模式]

返回：
✓ Python re.split 支持多个分隔符
用法：re.split(r'\||,', text)  # 使用 | 分隔多个模式
```

### 示例 2：API 用法测试

```
[进入 Scratchpad 模式]

用户："测试一下 requests 的 stream 参数如何使用"

大模型：
1. 创建临时目录
2. 写入测试脚本
3. 执行并验证
4. 清理

[退出 Scratchpad 模式]

返回：
✓ requests stream 参数用法：

| 参数 | 说明 | 适用场景 |
|------|------|---------|
| stream=True | 迭代读取响应内容 | 大文件下载 |
| stream=False（默认） | 立即下载全部内容 | 小文件/API 请求 |

示例：
```python
with requests.get(url, stream=True) as r:
    for chunk in r.iter_content(chunk_size=8192):
        f.write(chunk)
```
```

### 示例 3：Shell 脚本验证

```
[进入 Scratchpad 模式]

用户："验证一下 find 命令的 -mtime 参数"

大模型：
1. 创建临时测试环境
2. 生成测试文件
3. 执行 find 命令
4. 验证结果
5. 清理

[退出 Scratchpad 模式]

返回：
✓ find -mtime 参数用法：

| 参数 | 说明 | 示例 |
|------|------|------|
| -mtime 0 | 24小时内修改的文件 | find . -mtime 0 |
| -mtime +7 | 7天前修改的文件 | find . -mtime +7 |
| -mtime -3 | 3天内修改的文件 | find . -mtime -3 |
```

### 示例 4：GDScript 信号测试

```
[进入 Scratchpad 模式]

用户："测试 Godot 4.x 的自定义信号传递参数"

大模型：
1. 创建临时 GDScript 文件
2. 测试信号定义、连接、发送
3. 验证参数传递
4. 清理

[退出 Scratchpad 模式]

返回：
✓ Godot 4.x 自定义信号支持多参数传递

```gdscript
signal health_changed(new_value: int, old_value: int)

func take_damage(amount: int) -> void:
    var old = health
    health -= amount
    health_changed.emit(health, old)  # ✓ 支持多个参数
```

注意：Godot 4.x 使用 .emit() 而非 3.x 的 .emit_signal()
```

## 结果提取原则

### 应该返回

- ✓ 实验结论（成功/失败）
- ✓ 关键数据（性能指标、API 返回值）
- ✓ 验证后的正确用法
- ✓ 错误原因和解决方案
- ✓ 对比表格（如果适用）

### 不应该返回

- ✗ 临时文件路径
- ✗ MCP 工具调用细节
- ✗ 中间调试步骤
- ✗ 冗长的执行日志
- ✗ 失败的尝试过程

### 输出示例对比

**核心原则：只返回结论，不展示过程**

#### 示例 1：Python API 测试

❌ **错误输出（过程导向）：**
```
我正在创建临时目录...
调用 temp_create_directory 成功，返回：directory_id=tmp_abc123
创建测试文件 E:/.llm/tmp_abc123/test_regex.py
执行命令：python E:/.llm/tmp_abc123/test_regex.py
输出结果：
Testing regex pattern...
Pattern 1: ✅ passed
Pattern 2: ✅ passed
Pattern 3: ❌ failed
Retrying with fix...
All tests passed!
删除临时文件...
✓ 测试完成
```

✅ **正确输出（结果导向）：**
```
✓ Python re.split 支持多个分隔符

**用法：**
```python
import re

# 多个分隔符：使用 | 分隔多个模式
re.split(r'\||,', text)  # 按空格或逗号分割

# 注意：每个模式需用括号分组以避免优先级问题
re.split(r'(:)|(\.)', 'a.b:c')  # 结果: ['a', '.', 'b', ':', 'c']
```

**验证结论：** 支持多个分隔符，使用 | 符号连接，复杂模式建议用括号分组
```

#### 示例 2：性能对比测试

❌ **错误输出（过程导向）：**
```
创建临时目录 E:/.llm/tmp_xyz789
写入 test_method_a.py
写入 test_method_b.py
执行 python test_method_a.py...
Start: 10:30:45
End: 10:30:46
Duration: 1.2s

执行 python test_method_b.py...
Start: 10:30:47
End: 10:30:48
Duration: 0.8s

清理文件...
结果：方法 B 更快
```

✅ **正确输出（结果导向）：**
```
✓ 方法 B 性能优于方法 A

| 方法 | 执行时间 | 相对性能 |
|------|---------|---------|
| 方法 A | 1.2s | 基准 |
| 方法 B | 0.8s | **快 50%** |

**建议：** 优先使用方法 B
```

#### 示例 3：错误排查

❌ **错误输出（过程导向）：**
```
尝试 1：
创建测试文件 test.py
执行：python test.py
错误：ImportError: No module named 'xxx'

尝试 2：
修改文件，添加 import
执行：python test.py
错误：AttributeError: module has no attribute

尝试 3：
查阅文档，发现正确的 API 是 yyy()
修改代码
执行：python test.py
✓ 成功

结论：应该使用 yyy() 而不是 xxx()
```

✅ **正确输出（结果导向）：**
```
✓ 正确的 API 是 `module.yyy()` 而非 `module.xxx()`

**错误原因：**
- `xxx()` 在 v2.0 中已废弃
- v2.0+ 应使用 `yyy()` 替代

**正确用法：**
```python
# ❌ 旧版本（v1.x）
from module import xxx
result = xxx()

# ✅ 新版本（v2.0+）
from module import yyy
result = yyy()
```

**兼容方案：**
```python
try:
    from module import yyy
except ImportError:
    from module import xxx as yyy
```
```

#### 示例 4：GDScript 信号测试

❌ **错误输出（过程导向）：**
```
[进入 Scratchpad 模式]
创建临时目录：tmp_def456
写入 test_signal.gd
文件内容：
extends Node
signal test(value)
func _ready():
    test.emit(42)
    print("done")

执行测试...
✓ 信号发送成功

清理文件
[退出 Scratchpad 模式]
```

✅ **正确输出（结果导向）：**
```
✓ Godot 4.x 自定义信号支持多参数传递

**信号定义：**
```gdscript
signal health_changed(new_value: int, old_value: int)
```

**信号发送：**
```gdscript
func take_damage(amount: int) -> void:
    var old = health
    health -= amount
    health_changed.emit(health, old)  # 多参数传递
```

**版本差异：**
| 版本 | 发送方法 |
|------|---------|
| Godot 4.x | `signal_name.emit(args)` |
| Godot 3.x | `emit_signal("signal_name", args)` |
```

## 文件命名规范

| 类型 | 模式 | 示例 |
|------|------|------|
| 测试脚本 | `test_<topic>.<ext>` | test_regex.py, test_find.sh |
| 数据文件 | `data_<topic>.<ext>` | data_input.json, data_config.yaml |
| 输出文件 | `output_<topic>.<ext>` | output_result.txt, output_log.txt |
| 说明文档 | `README.md` | 记录实验目的（可选） |

## 最佳实践

1. **快速验证** - 每个实验只验证一个假设
2. **及时退出** - 得到结论立即退出 scratchpad
3. **结果精炼** - 用表格或代码块展示关键信息
4. **清理资源** - 完成后手动删除临时文件（不依赖自动清理）
5. **记录假设** - 在退出时说明"验证了什么假设"
6. **绝对路径** - 所有路径使用绝对路径（遵循项目约定）

## 对比表

| 维度 | Scratchpad | 传统 test_xxx.py |
|------|-----------|------------------|
| 隔离性 | ✓ 完全隔离（临时目录） | ✗ 污染项目目录 |
| 清理 | ✓ 自动/手动清理 | ✗ 需手动管理 |
| 上下文 | ✓ 不占用主对话 | ✗ 混在主对话中 |
| 结果导向 | ✓ 只返回结论 | ✗ 展示所有过程 |
| 生命周期 | ✓ 1小时 TTL | ✗ 永久存在 |

## 故障排除

| 问题 | 解决方案 |
|------|---------|
| 目录不存在（1小时后过期） | 重新调用 `temp_create_directory` |
| 丢失 directory_id | 使用 `temp_list_directories` 查找 |
| 找不到 modify_delete_key | 检查 `temp_create_directory` 返回值 |
| 文件写入失败 | 检查内容大小（>50KB 应重定向输出） |
| 临时文件过多 | 调用 `temp_cleanup` 强制清理 |

## 高级场景

### 场景 1：多文件实验

创建多个相关文件，完成后批量清理：
```
1. 创建测试脚本 test_main.py
2. 创建数据文件 data_input.json
3. 创建配置文件 config.yaml
4. 执行测试
5. 批量删除所有文件
6. 返回综合结论
```

### 场景 2：迭代调试

在同一目录内多次修改测试文件：
```
1. 创建 test_v1.py，执行失败
2. 覆盖写入 test_v1.py，执行失败
3. 覆盖写入 test_v1.py，执行成功
4. 退出 scratchpad
5. 返回最终正确用法
```

### 场景 3：性能对比

创建多个测试脚本进行性能对比：
```
1. 创建 test_method_a.py
2. 创建 test_method_b.py
3. 分别执行并记录时间
4. 返回对比表格：

| 方法 | 执行时间 | 内存占用 |
|------|---------|---------|
| 方法 A | 1.2s | 50MB |
| 方法 B | 0.8s | 45MB |
```

### 场景 4：错误排查

隔离问题并测试解决方案：
```
1. 创建重现错误的测试文件
2. 验证错误存在
3. 修改测试文件，应用修复方案
4. 验证修复成功
5. 返回错误原因和解决方案
```

## 工作流总结

```
主上下文
   ↓
检测到"试一下"信号
   ↓
[进入 Scratchpad 模式]
   ↓
创建临时目录（temp_create_directory）
   ↓
写入测试文件（temp_write）
   ↓
执行测试（Bash 或其他工具）
   ↓
读取结果（temp_read）
   ↓
提取关键结论
   ↓
清理文件（temp_delete）
   ↓
[退出 Scratchpad 模式]
   ↓
返回主上下文（仅带结论）
```

## 注意事项

- 此 skill 使用 `tmpfile-server` MCP，确保已安装
- 所有临时文件存储在 `E:/.llm/tmp_*` 目录
- 自动清理 TTL 为 1 小时，建议手动清理
- 使用绝对路径访问临时文件
- 退出时必须明确声明结果，不要遗漏关键信息
