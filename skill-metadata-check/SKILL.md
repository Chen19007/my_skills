---
name: skill-metadata-check
description: 检查 SKILL.md 的 YAML 元数据是否可解析、是否包含 name/description，避免元数据问题影响加载。
---

# Skill 元数据检查

## 作用

批量检查目录内所有 `SKILL.md` 的 YAML 头部：
- 是否存在 frontmatter 分隔符
- YAML 是否可解析
- 是否包含 `name` / `description`
- `name` / `description` 类型是否为字符串

## 使用方式

1. 进入技能根目录后运行脚本。
2. 查看每个 `SKILL.md` 的检查结果。

## 脚本

- `scripts/check_skill_metadata_yaml.py`

## 执行示例

```bash
python {SKILL目录}/scripts/check_skill_metadata_yaml.py
```

## 输出说明

- `yaml_parse: ok` 表示 YAML 可解析
- `required_fields: ok` 表示包含 `name`/`description`
- 发现 `fail` 或 `missing` 时需要修复对应文件的 YAML 头部