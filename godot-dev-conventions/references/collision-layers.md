# Collision Layers

## 默认做法

- 把“物理碰撞”和“战斗判定”分成两套层，不混在一个 layer 里。
- 用集中常量定义所有层级，不直接在业务脚本里散落魔法数字。
- 角色本体、攻击判定、受击判定、投射物命中目标各自使用稳定分工的 layer / mask 组合。
- 当对象只负责作为命中盒体时，优先让它的 `collision_mask` 只指向需要交互的盒体层，而不是顺手把世界碰撞也挂上。

## 当前公共分工模式

- `WORLD_PHYSICS = 1`
- `PLAYER_PHYSICS = 2`
- `ENEMY_PHYSICS = 4`
- `PLAYER_HURT_BOX = 16`
- `PLAYER_HIT_BOX = 32`
- `ENEMY_HURT_BOX = 64`
- `ENEMY_HIT_BOX = 128`

## 推荐规则

- 角色本体：
  - 玩家本体放在 `PLAYER_PHYSICS`
  - 敌人本体放在 `ENEMY_PHYSICS`
- 受击盒：
  - 玩家 `HurtBox` 放在 `PLAYER_HURT_BOX`
  - 敌人 `HurtBox` 放在 `ENEMY_HURT_BOX`
  - 默认 `collision_mask = 0`
- 攻击盒：
  - 玩家 `HitBox` 放在 `PLAYER_HIT_BOX`，默认只打 `ENEMY_HURT_BOX`
  - 敌人 `HitBox` 放在 `ENEMY_HIT_BOX`，默认只打 `PLAYER_HURT_BOX`
- 投射物本体：
  - 投射物根节点自身的 `collision_layer` 可为 `0`
  - 是否与世界碰撞，由投射物根节点的 `collision_mask` 决定
  - 真正的伤害交互仍由子节点 `HitBox` 负责

## 为什么这样做

- 物理移动、地形阻挡、命中判定的职责分离后，调试更清楚。
- 统一常量表后，角色、陷阱、投射物都能套同一组规则，不会每加一个对象就重新发明位图。
- 让 `HurtBox` 默认 `mask = 0`，可以明确表达“它是被动接收者，不主动探测别人”。

## 禁止项

- 不要直接在多个场景里手写 `16`、`32`、`64`、`128` 这类数字并把语义记在脑子里。
- 不要把角色本体碰撞和攻击盒判定塞在同一个 layer。
- 不要让 `HurtBox` 同时承担主动探测职责。
- 不要因为图省事把某个 `HitBox` 的 mask 直接开成“能撞到所有层”。

## 最小示例

```gdscript
const CollisionLayersClass = preload("res://system/CollisionLayers.gd")

func _ready() -> void:
	attack_hit_box.collision_layer = CollisionLayersClass.PLAYER_HIT_BOX
	attack_hit_box.collision_mask = CollisionLayersClass.ENEMY_HURT_BOX
	hurt_box.collision_layer = CollisionLayersClass.PLAYER_HURT_BOX
	hurt_box.collision_mask = 0
```

```gdscript
func _ready() -> void:
	collision_layer = 0
	collision_mask = 0 if passes_world else CollisionLayersClass.WORLD_PHYSICS
	projectile_hit_box.collision_layer = CollisionLayersClass.ENEMY_HIT_BOX
	projectile_hit_box.collision_mask = CollisionLayersClass.PLAYER_HURT_BOX
```

## 依据

- 层级常量真源：[system/CollisionLayers.gd](D:/project/godot/blockking/system/CollisionLayers.gd:1)
- 玩家层级分配：[player/Player.tscn](D:/project/godot/blockking/player/Player.tscn:742)
- 玩家投射物层级分配：[player/PlayerHeavySlashProjectile.tscn](D:/project/godot/blockking/player/PlayerHeavySlashProjectile.tscn:28)
- 敌人投射物公共逻辑：[enemies/Projectile.gd](D:/project/godot/blockking/enemies/Projectile.gd:61)
- 敌人场景层级分配示例：[enemies/Skeleton.tscn](D:/project/godot/blockking/enemies/Skeleton.tscn:294)
