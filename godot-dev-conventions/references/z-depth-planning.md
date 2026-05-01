# Z Depth Planning

## 默认做法

- 世界内的渲染层级用统一常量表管理，不在各处零散拍脑袋写 `z_index`。
- 统一通过一个公共入口给世界对象赋层级，例如 `apply_world_z_index()`。
- 世界对象默认关闭相对层级：`z_as_relative = false`。
- 角色、投射物、命中特效、前后景装饰各有固定层段，避免局部“临时加 1”一路蔓延。

## 当前公共层段模式

- `WORLD_BACKGROUND_BACK_DECOR_Z_INDEX = -3100`
- `WORLD_BACKGROUND_DECOR_Z_INDEX = -3000`
- `WORLD_STATIC_PROP_BACK_Z_INDEX = -1000`
- `WORLD_STATIC_PROP_Z_INDEX = 0`
- `WORLD_PICKUP_Z_INDEX = 800`
- `WORLD_COMBATANT_BACK_FX_Z_INDEX = 1800`
- `WORLD_COMBATANT_Z_INDEX = 2000`
- `WORLD_COMBATANT_FRONT_FX_Z_INDEX = 2400`
- `WORLD_PROJECTILE_TRAIL_Z_INDEX = 2800`
- `WORLD_PROJECTILE_Z_INDEX = 3000`
- `WORLD_IMPACT_VFX_Z_INDEX = 3400`
- `WORLD_FOREGROUND_DECOR_Z_INDEX = 4000`

## 推荐规则

- 角色本体默认放在 `WORLD_COMBATANT_Z_INDEX`
- 角色身后特效默认放在 `WORLD_COMBATANT_BACK_FX_Z_INDEX`
- 角色身前特效默认放在 `WORLD_COMBATANT_FRONT_FX_Z_INDEX`
- 投射物默认放在 `WORLD_PROJECTILE_Z_INDEX`
- 投射物拖尾默认放在 `WORLD_PROJECTILE_TRAIL_Z_INDEX`
- 命中、格挡、冲击类反馈默认放在 `WORLD_IMPACT_VFX_Z_INDEX`
- 前景装饰始终明确高于角色和特效，不靠“单个场景里额外 +1”解决遮挡

## 为什么这样做

- 层级集中后，角色、特效、投射物之间的前后关系可以稳定复用。
- `z_as_relative = false` 能避免父节点层级变化把子节点一起拖乱。
- 把层级写成“层段”而不是零散点值，后续给某一类对象扩展子层级时更可控。

## 禁止项

- 不要在多个脚本里直接写无来源的 `z_index = 7`、`z_index = 19` 这类数值。
- 不要把“角色前景特效”“投射物”“命中爆点”混在同一层段里再靠节点顺序碰运气。
- 不要在需要世界统一深度时继续使用相对层级。
- 不要把某个项目里偶发的局部偏移，当成公共默认规则写进公共 skill。

## 最小示例

```gdscript
const SectionRenderLayersClass = preload("res://system/SectionRenderLayers.gd")

func _ready() -> void:
	SectionRenderLayersClass.apply_world_z_index(
		self,
		SectionRenderLayersClass.WORLD_PROJECTILE_Z_INDEX
	)
```

```gdscript
static func apply_world_z_index(target: CanvasItem, world_z_index: int) -> void:
	if target == null:
		return
	target.z_as_relative = false
	target.z_index = world_z_index
```

## 依据

- 渲染层级真源：[system/SectionRenderLayers.gd](D:/project/godot/blockking/system/SectionRenderLayers.gd:1)
- 玩家层级接入：[player/Player.gd](D:/project/godot/blockking/player/Player.gd:433)
- 敌人层级接入：[enemies/BaseEnemy.gd](D:/project/godot/blockking/enemies/BaseEnemy.gd:300)
- 玩家投射物层级接入：[player/PlayerHeavySlashProjectile.gd](D:/project/godot/blockking/player/PlayerHeavySlashProjectile.gd:60)
- 敌人投射物层级接入：[enemies/Projectile.gd](D:/project/godot/blockking/enemies/Projectile.gd:61)
