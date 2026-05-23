# 场景结构与架构范式

## 核心目标

尽量让场景结构本身表达依赖关系，减少靠运行时分支兜底。

## 默认范式

- 场景负责提供必需节点结构。
- 脚本负责消费这些结构，而不是边运行边猜节点是否存在。
- 模块之间优先通过信号、明确接口和节点组合协作。
- 只有真正可选的依赖，才设计成可缺失。

## 优先做法

### 用场景保证不变量

如果某个节点是运行必需的，就让它成为场景结构的一部分，然后在脚本中直接以强类型引用它。

```gdscript
@onready var animation_player: AnimationPlayer = $AnimationPlayer
@onready var hurt_box: Area2D = $HurtBox
```

优先这一类写法，而不是：

```gdscript
var animation_player: AnimationPlayer = get_node_or_null("AnimationPlayer")
if animation_player != null:
    animation_player.play("idle")
```

### 用组合替代过度继承

- 节点树天然适合表达“由多个部件组成的对象”。
- 只有在确实存在稳定抽象和共享行为时，再上脚本继承层级。

### 用信号替代横向硬耦合

- 事件通知优先用 `signal`。
- 不要让 A 直接深入操作 B 的内部节点和内部状态，除非它们本来就是同一职责边界。

### 资源 UID 与场景引用

- Godot 的 `uid://` 引用可以在资源移动或重命名后保持引用稳定，但重复 UID、过期 UID 缓存或复制资源时遗留的 `.uid` 文件，会让运行时加载结果违背 `.tscn` 文本路径的直觉。
- 复制、移动或手工编辑脚本、场景、贴图等资源后，必须确认对应 `.uid` 文件没有重复；不要只看 `ext_resource path` 是否正确。
- 排查资源错绑时，先搜索重复 UID，再用运行时证据确认实际加载对象，例如检查 `node.get_script().resource_path`、资源实例路径或信号连接目标。
- 修复顺序优先为：修正重复 `.uid` 文件，运行 Godot 导入或加载验证；若新 UID 尚未被当前缓存识别并持续出现 `invalid UID, using text path instead`，可将该处引用临时收口为纯 `path` 引用，并再次验证运行时加载结果。

## 依赖边界

### autoload

- autoload 适合放全局配置、全局状态入口或少量跨场景服务。
- 不要把所有模块都堆进 autoload，避免单例膨胀。

### 纯逻辑类

- 不需要场景树能力的类，优先考虑 `RefCounted`。
- 需要节点生命周期、信号或场景挂载的类，再使用 `Node` 及其子类。

## 反模式

- 通过大量 `get_node_or_null()` 和 `has_node()` 掩盖场景结构不稳定。
- 通过跨模块直接改字段来实现交互，而不是建立明确接口。
- 一个脚本同时承担输入、移动、受击、动画、UI、音效等多种职责却没有边界。
