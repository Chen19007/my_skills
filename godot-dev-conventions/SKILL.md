---
name: godot-dev-conventions
description: 沉淀可复用的 Godot 开发规范与实现范式，减少 zero-shot 式临场发挥。适用于编写或重构 GDScript、设计场景/节点关系、整理模块边界、统一常见写法，或在缺少项目专属约定时提供默认实现方向。
---

# Godot Dev Conventions

## 概述

这个 skill 不负责测试、导出、搜索或项目流程，只负责提供可复用的 Godot 开发约束与默认范式。

目标是把已经验证过的经验沉淀下来，让 Codex 在写 Godot 代码时优先复用既有模式，而不是每次从零猜一套写法。

## 使用方式

1. 先判断当前问题属于哪一类：编码风格、场景依赖、动画状态、还是常用玩法范式。
2. 只读取对应的 `references/` 文件，不要把全部参考一次性塞进上下文。
3. 若当前仓库已有明确约定，先服从仓库约定；本 skill 只提供公共默认值。
4. 若没有显式仓库约定，优先采用本 skill 的默认范式。

## 默认原则

- 显式优于隐式：优先写清楚类型、依赖、节点结构和状态边界。
- 结构保证优于运行时补丁：能通过场景结构、节点树和类型约束保证的，不要散落 `null` 防御。
- 组合优于耦合：优先用节点组合、信号和清晰职责边界，而不是跨模块硬引用。
- 默认范式优于临场发明：常见问题先套用已有模式，再考虑局部偏离。
- 公共 skill 保持项目无关：不要把当前仓库的热键、章节、资源路径、专有名词写进这里。

## 参考导航

- `references/coding-style.md`
  读取时机：编写或重构 GDScript，统一命名、类型、成员顺序和节点引用方式时。
- `references/scene-and-architecture.md`
  读取时机：设计场景结构、模块边界、依赖关系、autoload 访问方式，或排查资源 UID / 场景引用错绑时。
- `references/animation-and-state.md`
  读取时机：处理 `AnimationPlayer`、状态切换、演出驱动逻辑时。
- `references/hitbox-hurtbox.md`
  读取时机：设计攻击判定、受击判定、命中确认、投射物命中协议时。
- `references/collision-layers.md`
  读取时机：规划物理层、战斗层、`collision_layer` / `collision_mask` 分工时。
- `references/z-depth-planning.md`
  读取时机：规划角色、投射物、特效、前后景的 `z_index` 关系时。
- `references/pattern-backlog.md`
  读取时机：需要补充新的公共范式时，先看这里的待沉淀主题与收录标准。

## 适用边界

- 这个 skill 不替代仓库自己的 `AGENTS.md`、设计文档或代码真源。
- 这个 skill 不负责验证命令、测试框架、Web E2E、搜索工作流。
- 这个 skill 只沉淀“写代码时怎么默认做”，不沉淀某个项目的玩法细节本身。
