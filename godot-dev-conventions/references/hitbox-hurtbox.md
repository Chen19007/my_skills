# HitBox / HurtBox

## 默认做法

- 攻击判定和受击判定拆成两个独立节点：`HitBox` 负责发起命中，`HurtBox` 负责接收命中。
- `HitBox` 继承 `Area2D`，持有攻击语义字段，例如 `attack_type`、`attack_damage`、`block_requirement`。
- `HurtBox` 继承 `Area2D`，只暴露统一的受击信号，不在盒体脚本里直接写角色业务逻辑。
- 攻击发起方通过 `HitBox.hit(target, source_direction)` 发出命中结果，受击方通过 `HurtBox.hurt(from, source_direction)` 进入自己的受击处理。
- 默认让场景结构保证盒体存在；角色、敌人、投射物都复用同一套命中协议，而不是各写一套临时逻辑。

## 为什么这样做

- 命中协议统一后，玩家、敌人、投射物、可破坏物都可以接入同一套战斗流程。
- 攻击语义集中在 `HitBox`，比把伤害、格挡要求、命中原因散落到调用点更稳定。
- `HurtBox` 只做转发，可以保持受击逻辑留在宿主脚本中，避免盒体脚本膨胀成业务中心。
- `source_direction` 由公共盒体层统一求值，能减少各角色自己推导受击方向时的重复代码。

## 约束

- `HitBox` 默认负责：
  - 监听 `area_entered`
  - 过滤非 `HurtBox`
  - 解析 `source_direction`
  - 调用 `hurt_box.take_hit(self, source_direction)`
  - 发出 `hit` 信号
- `HurtBox` 默认负责：
  - 加入 `hurtbox` 分组
  - 暴露 `hurt(from, source_direction)` 信号
  - 在 `take_hit()` 中转发受击事件
- 投射物型 `HitBox` 若需要更准确的受击方向，优先由飞行方向反推 `source_direction`，不要完全依赖中心点差值。
- 需要区分格挡要求、地面/空中命中条件时，优先扩展 `HitBox` 的公共字段，不要在多个角色脚本里各自补判断。

## 禁止项

- 不要让 `HitBox` 直接扣血、播受击动画、改状态机。它只负责命中判定和事件发出。
- 不要让 `HurtBox` 直接知道“玩家受击怎么处理”或“敌人受击怎么处理”。
- 不要为玩家、敌人、投射物分别定义三套不兼容的命中回调协议。
- 不要在业务脚本里到处手写 `if area is HurtBox` 的临时命中流程；优先复用公共 `HitBox`。

## 最小节点结构

```text
Combatant
├─ HurtBox (Area2D)
│  └─ CollisionShape2D
├─ HitBox (Area2D)
│  └─ CollisionShape2D
└─ AnimationPlayer
```

## 最小示例

```gdscript
class_name HurtBox
extends Area2D

signal hurt(from: HitBox, source_direction: Vector2)

func take_hit(from: HitBox, source_direction: Vector2 = Vector2.ZERO) -> void:
	hurt.emit(from, source_direction)
```

```gdscript
class_name HitBox
extends Area2D

signal hit(target: HurtBox, source_direction: Vector2)

@export var attack_damage: int = 1

func _on_area_entered(area: Area2D) -> void:
	var hurt_box: HurtBox = area as HurtBox
	if hurt_box == null:
		return
	var source_direction: Vector2 = (global_position - hurt_box.global_position).normalized()
	hurt_box.take_hit(self, source_direction)
	hit.emit(hurt_box, source_direction)
```

## 依据

- 公共命中协议真源：[system/HitBox.gd](D:/project/godot/blockking/system/HitBox.gd:1)、[system/HurtBox.gd](D:/project/godot/blockking/system/HurtBox.gd:1)
- 玩家场景结构：[player/Player.tscn](D:/project/godot/blockking/player/Player.tscn:761)
- 玩家脚本接线：[player/Player.gd](D:/project/godot/blockking/player/Player.gd:416)
- 敌人侧复用：[enemies/BaseEnemy.gd](D:/project/godot/blockking/enemies/BaseEnemy.gd:279)
- 投射物侧复用：[enemies/Projectile.gd](D:/project/godot/blockking/enemies/Projectile.gd:79)
