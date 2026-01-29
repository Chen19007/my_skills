---
name: git-commit
description: "智能提交与仓库初始化：自动生成 .gitignore、筛选提交文件、隐私扫描、配置 GitHub SSH 远程。用于初始化仓库、提交变更、设置远程、准备项目版本控制。"
---

# Git-Commit

## 概览
自动化 git 初始化/提交流程：识别项目类型、生成带注释的 .gitignore、智能筛选待提交文件、进行敏感信息扫描，并在需要时配置 GitHub SSH 远程。

## 核心工作流（按序执行）
1. 评估仓库：检测当前目录与 git 状态；若非仓库再执行初始化。
2. 识别项目类型：根据文件/清单判断语言栈（Python/Node/Go/Rust/Web 等）。
3. 生成或补全 .gitignore：不存在则创建；存在则只追加缺失段落。
4. 文件筛选：列出未跟踪/修改文件，按“可提交/应排除”分类并给出理由表。
5. 隐私扫描：仅扫描“可提交文件”中的敏感模式与高风险文件扩展。
6. 暂存与提交：仅暂存“可提交”清单；生成提交信息并提交。
7. GitHub 远程：检查 remotes；无 origin 时创建仓库并添加 SSH remote。
8. 提示用户：仅给出 `git push -u origin <branch>` 指令，不自动 push。

## 关键约束
- 不自动执行 `git push`。
- 远程必须使用 SSH：`git@github.com:<owner>/<repo>.git`。
- 若已有 `.git/` 或已有 `origin`，不得重复初始化或重复添加。
- 只提交筛选后的“可提交文件”，不要盲目 `git add .`。
- 隐私扫描发现风险时必须征询用户是否继续。

## 文件筛选规则（摘要）
**可提交**：源码/配置/文档/构建脚本/测试/锁文件。
**应排除**：构建产物、依赖目录、编辑器配置、系统文件、临时文件、日志、`.env` 等敏感文件。

## 隐私扫描
- 高风险关键词：`api_key`, `token`, `password`, `secret`, `private_key`, `credentials`。
- 高风险扩展：`.pem`, `.key`, `.crt`, `.env*`, `*.sqlite`。
- 仅扫描“可提交文件”，避免本地路径等低价值匹配。
- 发现问题时给出文件/行号/风险级别/建议，并询问继续或中止。

## .gitignore 模板（按需补全）
```gitignore
# Python
__pycache__/
*.py[cod]
.venv/
venv/
dist/
build/
*.egg-info/
.pytest_cache/
.coverage*

# Node.js
node_modules/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
dist/
build/
.env
.env.*
!.env.example

# Go
*.exe
*.dll
*.so
*.dylib
*.test
*.out

# Rust
/target/

# Web/General Build
out/
output/

# IDE
.vscode/
.idea/
.vs/
.cursor/

# OS
.DS_Store
Thumbs.db
Desktop.ini

# Temp
*.tmp
*.bak
*~
```

## 输出格式（要点）
- “可提交文件表 / 排除文件表” 两个表格，含原因。
- 隐私扫描：通过则输出“✅ 通过”；发现风险则输出明细并请求用户确认。
- 远程配置成功后仅输出手动 push 指令。

## 失败处理（简要）
- GitHub 创建失败：保留本地提交，给出手动创建远程步骤。
- 远程为 HTTPS：转换为 SSH (`git remote set-url origin ...`)。

## 提交信息建议
- 新仓库：`Initial commit: ...`
- 已有仓库：`Add:` / `Fix:` / `Update:` / `Remove:` + 简短摘要
```
