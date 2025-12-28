---
name: godot-dev
description: Godot code implementation guidelines. Use when: (1) Writing GDScript code, (2) Following style conventions, (3) Using Godot features correctly, (4) Avoiding anti-patterns.
---

# Godot 代码实现规范

本 Skill 提供 GDScript 代码实现的规范和最佳实践，确保代码符合 Godot 引擎特性和 TDD 友好原则。

## 适用场景

- 编写新的功能代码
- 重构现有代码
- 遵循 GDScript 风格规范
- 使用 Godot 特有功能

## GDScript 风格规则

### 类型注解

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
var enemies: Array[Node] = []
```

### 属性可见性

```gdscript
# 私有属性（使用下划线前缀）
var _health: int = 100
var _velocity: Vector2 = Vector2.ZERO
var _cooldowns: Dictionary = {}

# 只读属性（使用 getter）
var health: int:
    get:
        return _health

# 导出变量（编辑器配置）
@export var max_health: int = 100
@export var move_speed: float = 300.0
@export var damage: float = 10.0
```

### 常量命名

```gdscript
const MAX_HEALTH := 100
const MOVE_SPEED := 300.0
const GRAVITY := 980.0
const TAG_ENEMY := "enemy"
```

### 信号定义

```gdscript
# 状态变化信号
signal health_changed(new_health: int, old_health: int)
signal died()
signal revived()

# 事件信号
signal attack_completed(target: Node)
signal level_up(level: int)

# 使用信号
func take_damage(amount: int) -> void:
    var old_health = _health
    _health = max(0, _health - amount)
    health_changed.emit(_health, old_health)
```

## Godot 特性使用

### Signal（观察者模式）

```gdscript
# 定义信号
signal health_changed(new_health: int)

# 发送信号
func take_damage(amount: int) -> void:
    _health = max(0, _health - amount)
    health_changed.emit(_health)

# 连接信号（推荐使用 callable 语法）
func _ready() -> void:
    health_changed.connect(_on_health_changed)

func _on_health_changed(new_health: int) -> void:
    print("Health: ", new_health)

# 一次性信号
health_changed.connect(_on_health_changed, CONNECT_ONE_SHOT)
```

### @onready（节点引用）

```gdscript
extends Node2D

@onready var sprite: Sprite2D = $Sprite2D
@onready var animation: AnimationPlayer = $AnimationPlayer
@onready var collision: CollisionShape2D = $CollisionShape2D
```

### @export（编辑器配置）

```gdscript
@export var max_health: int = 100
@export var move_speed: float = 300.0

# 资源类型
@export var bullet_scene: PackedScene

# 枚举类型
@export_enum("Fast", "Normal", "Slow") var speed_mode: String = "Normal"

# 分组
@export_group("Damage Settings")
@export var base_damage: float = 10.0
@export var critical_multiplier: float = 2.0
```

### Autoload（单例）

```gdscript
# 获取 autoload
var game_manager = Engine.get_main_loop().get_node("/root/GameManager")

# 安全访问
func _ready() -> void:
    if Engine.get_main_loop().has_node("/root/GameManager"):
        var gm = Engine.get_main_loop().get_node("/root/GameManager")
        gm.register_player(self)
```

## 依赖管理

### 循环依赖问题

GUT 无法加载存在循环依赖的脚本。

```gdscript
# 错误：循环依赖
class_name Player extends Node

func _ready() -> void:
    var manager = GameManager.get_instance()
    manager.register(self)

# GameManager.gd
class_name GameManager
func register_player(player: Player):  # 引用 Player
    ...
```

### 解决方案

```gdscript
# 方案1：使用基类参数
func register_character(character: Node, height_x: float) -> void:
    ...

# 方案2：延迟绑定
func _ready() -> void:
    var manager = _get_game_manager()
    if manager:
        manager.register(self)

func _get_game_manager() -> Node:
    if Engine.get_main_loop().has_node("/root/GameManager"):
        return Engine.get_main_loop().get_node("/root/GameManager")
    return null

# 方案3：避免 class_name 循环
extends Node2D  # 不使用 class_name
```

## 碰撞检测

### Area2D vs PhysicsBody

```gdscript
extends Area2D

func _ready() -> void:
    body_entered.connect(_on_body_entered)

func _on_body_entered(body: Node) -> void:
    # 使用 has_method 检查接口
    if body.has_method("take_damage"):
        body.take_damage(10)

# 检测 PhysicsBody
func check_player_overlap(player: Node) -> bool:
    return overlaps_body(player)

# 检测 Area2D
func check_hazard_overlap(hazard: Node) -> bool:
    return overlaps_area(hazard)
```

## 常见反模式

### 反模式 1：直接暴露内部变量

```gdscript
# 错误
var health: int = 100

# 正确
var _health: int = 100
func get_health() -> int:
    return _health
```

### 反模式 2：硬编码 autoload 引用

```gdscript
# 错误
func _ready() -> void:
    GameManager.add_player(self)  # 可能为 null

# 正确
func _ready() -> void:
    if Engine.get_main_loop().has_node("/root/GameManager"):
        Engine.get_main_loop().get_node("/root/GameManager").add_player(self)
```

### 反模式 3：测试逻辑污染

```gdscript
# 错误
func _process(delta: float) -> void:
    move_and_slide()
    if is_in_test_mode:  # 测试逻辑混入生产代码
        _record_test_data()

# 正确
# 测试逻辑完全分离，通过接口控制
```

### 反模式 4：缺少类型注解

```gdscript
# 错误
func move_to(target):  # 缺少类型
    ...

# 正确
func move_to(target: Vector2) -> void:
    ...
```

### 反模式 5：不使用 @onready

```gdscript
# 错误
func _ready() -> void:
    var sprite = get_node("Sprite2D")  # 每次调用都查找

# 正确
@onready var sprite: Sprite2D = $Sprite2D  # 缓存引用
```

## 避免的模式

### 对象池（不需要）

GDScript 使用引用计数，不是 GC 语言：

```gdscript
# 不需要对象池
var bullet = BulletScene.instantiate()
add_child(bullet)
# 当没有引用时自动释放
```

### ECS（除非 AAA 游戏）

Godot 的节点系统已经足够灵活：

```gdscript
# 使用节点组合而非 ECS
var player = PlayerScene.instantiate()
add_child(player)
player.attack.connect(_on_attack)
```

### 复杂状态机

状态超过 3-4 个才需要状态机：

```gdscript
# 简单情况使用状态变量
var state: String = "idle"

# 复杂情况使用 StateMachine 节点
```

## 检查清单

- [ ] 所有函数有类型注解
- [ ] 变量有类型注解
- [ ] 私有属性使用下划线前缀
- [ ] 使用 @onready 而非 get_node()
- [ ] 信号正确解耦
- [ ] autoload 安全访问
- [ ] 避免循环依赖
