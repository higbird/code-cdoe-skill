# Code Cdoe Skill

一套面向科研数据分析 Agent 的轻量工作规范，附带可选 Python 执行工具，用于组织、修改、运行和验证以 Bash、R、Python 或混合工具完成的分析项目。

*A lightweight Agent Skill for organizing, running, and validating reproducible scientific data-analysis projects.*

## 功能

- 将具有独立科研意义的任务组织为清晰模块；新建或整理时，顶层默认为 input/、output/、code.txt、readme.md，允许工具必需的环境元数据原位保留。
- 保护原始数据，使用明确的输入、输出和路径约定。
- 维持一个清晰的运行入口，减少重复脚本和隐藏步骤。
- 修改已有项目时控制范围，保留用户文件和无关改动。
- 实际运行受影响的分析，并检查退出状态、产物及关键数据内容。
- 避免生成无用途的总结、审查、日志和 Agent 工作记录。

本 skill 管理分析工作流，不代替统计方法选择、实验设计、领域解释或人工科研判断。

## 可选程序功能

| 功能 | 已提供的实现 |
|---|---|
| 文件检查 | 提供 exists/header/full 分级检查；按声明检查文件、表头、唯一键、行数和数值，拒绝低等级静默跳过强规则。 |
| 安全运行 | 临时目录生成和检查，按阶段成组替换结果及凭据；替换异常回退，中断后可显式恢复。 |
| 运行凭据 | 记录 sha256/stat/external 实际指纹、参数、命令、版本和已执行/未执行检查，明确外部摘要是否重新验证。 |
| 依赖重跑 | 比较输入、代码、参数、环境和产物，阶段内复用哈希、执行后重新检查；可选择目标阶段及上游。 |

入口为 `scripts/analysis_workflow.py`，需要 Python 3.11+，无第三方依赖。命令用法、配置字段与保护边界见 [工具说明](references/tools.md)；可复制 [合成数据示例](assets/minimal/readme.md) 独立试运行。

工具要求被调脚本将本次产物写入指定临时目录，并正确传播错误；不隔离任意脚本写入、不保证整组文件在替换过程中始终原子可见，也不推断未声明的依赖或科学口径。已有工作流不必迁移。

默认保持严格指纹和原有表格验证。大文件可显式选择低成本模式；恢复备份仍执行严格 SHA-256。新版凭据为 version=2，旧凭据会触发重跑，旧恢复日志继续兼容。具体升级与成本边界见工具说明。

## 适用场景

- 创建新的科研分析模块。
- 整理结构混乱的生物信息学或统计分析目录。
- 修改 Bash、R、Python 分析脚本并重新生成结果。
- 修复表格或多面板图件，并验证全部受影响产物。
- 核对 README、代码、参数和实际结果之间的一致性。
- 整理服务器或集群已有分析：输入归入 `input/`，未下载或外部输入的位置说明放入 `input/paths.md` 并在 `readme.md` 展示；结果与对应日志一起放入 `output/`，依据已有脚本或日志恢复 `code.txt`；只整理时不重跑，不补猜缺失参数。

单纯解释统计概念、阅读论文或回答局部代码问题时，不需要创建该 skill 规定的项目结构。

## 安装与调用

同一份目录适用于 Claude Code、Codex 和 NousResearch Hermes Agent。按使用的客户端复制整个 `code-cdoe-skill` 文件夹；不要只复制 `SKILL.md`，也不要再嵌套一层同名目录。

| 客户端 | 默认个人安装目录 | 显式调用 |
|---|---|---|
| Claude Code | `~/.claude/skills/code-cdoe-skill/` | `/code-cdoe-skill 请整理并验证这个科研分析项目。` |
| Codex | `~/.agents/skills/code-cdoe-skill/` | `$code-cdoe-skill 请整理并验证这个科研分析项目。` |
| Hermes Agent | `~/.hermes/skills/code-cdoe-skill/` | `/code-cdoe-skill 请整理并验证这个科研分析项目。` |

Claude Code 项目级目录为 `.claude/skills/`，Codex 为 `.agents/skills/`，均在其中放置整个 skill 文件夹。Hermes 使用自定义 `HERMES_HOME` 或 profile 时，安装到该配置实际使用的 skills 目录。`~` 表示用户主目录；Windows 实际路径以客户端配置为准。目录与调用依据：[Claude Code 官方说明](https://code.claude.com/docs/en/skills)、[Codex 官方说明](https://learn.chatgpt.com/docs/build-skills)、[Hermes 官方说明](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/)。

已有 Codex 环境若已从 `~/.codex/skills/` 加载此 skill，可沿用当前已验证的目录；不要为同一客户端保留多个不同版本的同名副本。复制后新建会话并检查技能列表及实际加载路径；能否自动触发还取决于客户端配置和模型选择。

安装后应保留以下结构：

```text
code-cdoe-skill/
├── SKILL.md
├── agents/openai.yaml
├── README.md
├── LICENSE
├── scripts/analysis_workflow.py
├── references/
│   ├── tools.md
│   └── agents.md
├── assets/minimal/
└── tests/
```

`agents/openai.yaml` 仅提供 Codex 的可选界面元数据；Claude Code 和 Hermes 的执行不依赖它。共用指令只使用标准的 `name`、`description` 元数据。无须安装 OpenAI、Anthropic 或 Hermes SDK；运行器仅依赖 Python 标准库。

详细环境处理、命令引用和验收步骤见 [宿主适配说明](references/agents.md)。

## 使用示例

以下任务正文可接在对应客户端的显式调用后，也可直接用自然语言提出。

```text
使用 code-cdoe-skill，为这批 GWAS 输入建立一个可重复运行的分析模块，生成关联结果和 Manhattan 图。
```

```text
使用 code-cdoe-skill，修复当前 R 分析的所有分组标签问题，重跑受影响的表格和图，并确认结果来自本次运行。
```

```text
使用 code-cdoe-skill，检查 README 与代码中的 FDR、协变量和 PC 数是否一致；能确认的直接修正并重跑，影响科学含义但无法判断的冲突请指出。
```

例如整理服务器下载的 `result.assoc` 与 `result.log`：

```text
使用 code-cdoe-skill，在当前目录整理这批服务器分析材料，顶层只保留 input/、output/、code.txt、readme.md。结果和日志放到 output/，恢复可确认的 code.txt；没有本地输入时，在 input/paths.md 记录有依据的原服务器路径及访问状态，并在 readme.md 展示。只整理，不重跑；缺失步骤和参数明确标注。
```

这一能力由 Agent 按技能规范读取记录完成，运行器不会自动解析任意软件日志。整理完成不代表历史分析已经复现；日志不完整时也不承诺生成完整可执行入口。

## 分析模块交付结构

新建或整理分析模块时，目标目录顶层严格只保留以下四项；这不改变上面的 skill 安装包结构。用户指定在 `a/` 整理时直接使用 `a/`，不另建一层模块目录：

```text
a/
├── input/
├── output/
├── code.txt
└── readme.md
```

`code.txt` 是可执行主入口，`readme.md` 说明工作目录、解释器、方法、输入与结果。只修改或重跑已有项目而未要求整理时，保留原有有效入口，不擅自重构。

`input/` 存放输入数据、链接、输入位置说明，以及必要辅助代码和配置；`output/` 存放结果、对应日志和运行状态。没有本地输入时仍保留 `input/`，在 `input/paths.md` 写明输入用途、原路径、来源和当前可访问性，并在 `readme.md` 展示关键路径。只有相对路径且无法确认原工作目录时，原样记录并注明无法解析，不能编造绝对路径或数据文件。

辅助脚本可放在 `input/src/`；可选运行器的配置为 `input/workflow.json`，状态为 `output/.analysis-state/`，不在顶层添加隐藏目录。示例入口为 `python code.txt --skill-root <skill目录> [run|plan|recover]`，默认执行 run；调用时显式传模块根目录给运行器。

整理已有材料前先识别归属，保留原始数据与运行证据；遇到无关任务或必须原位保留的项目文件，不为四项结构擅自删除或移动，也不把未解决的结构问题称为整理完成。

## 许可证

本项目采用 [MIT License](LICENSE)。

## 环境适配

运行前按 [环境检查与恢复](references/environment.md) 选择实际解释器并预检。R 辅助脚本 `scripts/r_environment.R` 提供逐包诊断、失败阻断及显式安装缺失包；不自动安装 R 或恢复锁文件。安装与分析使用相同 R 和包库。已有项目环境优先，不把示例包变成通用依赖。

R 测试通过 PATH 的 Rscript 或测试专用 `TEST_RSCRIPT` 定位；未提供 R 时明确 skip。目录搬迁测试不代表跨系统或客户端端到端验证。

本次验证：Windows、R 4.5.2、Python 3.11；65 项测试中 64 项通过、1 项符号链接权限跳过，包含 8 项 R 预检测试。未验证真实联网安装、macOS/Linux 或真实客户端端到端执行。库安装失败用模拟离线安装器验证阻断行为。
