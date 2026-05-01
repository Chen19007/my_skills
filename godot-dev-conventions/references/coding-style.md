# GDScript 编码规范

## 核心目标

用足够明确的写法降低歧义，让脚本结构、成员职责和类型边界一眼可读。

## 默认约定

- 文件名使用 `snake_case.gd`。
- `class_name` 使用 `PascalCase`。
- 变量名使用 `snake_case`。
- 常量使用 `CONSTANT_CASE`。
- 信号使用过去式或事件式命名，如 `health_changed`、`attack_finished`。
- 私有成员使用 `_prefix`。
- 函数参数、返回值、变量默认写显式类型。

## 成员顺序

默认按下面顺序组织脚本：

1. `signal`
2. `enum`
3. `const`
4. `@export`
5. 公有变量
6. 私有变量
7. `@onready`
8. `_init()`
9. `_ready()`
10. 其他引擎虚函数
11. 公有方法
12. 私有方法

## 推荐写法

```gdscript
class_name PlayerController
extends CharacterBody2D

signal health_changed(new_health: int)

const MAX_SPEED: float = 240.0

@export var move_speed: float = 180.0

var facing_direction: int = 1
var _health: int = 100

@onready var sprite: Sprite2D = $Sprite2D

func _ready() -> void:
    _refresh_visual()

func take_damage(amount: int) -> void:
    _health = max(_health - amount, 0)
    health_changed.emit(_health)

func _refresh_visual() -> void:
    sprite.flip_h = facing_direction < 0
```

## 节点引用

- 已知且必需的子节点，优先使用 `@onready var node: Type = $Path`。
- 不要在多个函数里重复 `get_node()` 查找同一节点。
- 只有在节点确实可选时，才使用显式可空处理。

## `class_name` 与 autoload

- 若脚本已经作为 autoload 注册到 `project.godot`，默认不要再声明同名 `class_name`。
- 避免出现 `Class "<Name>" hides an autoload singleton.` 这类冲突。

## 避免的写法

- `var value := something` 到处依赖类型推断。
- 为了临时绕错，在多个调用点重复补 `if x == null`。
- 在业务逻辑里硬编码一串深层节点路径并反复直接访问。
- 把测试逻辑、调试逻辑直接揉进生产分支条件里。
