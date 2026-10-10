# Code Cdoe Skill

一套面向科研数据分析 Agent 的轻量工作规范，用四件套记录以 Bash、R、Python 完成的独立分析阶段：输入数据经 `code.txt` 生成输出，`readme.md` 说明数据、方法、参数、版本、环境与运行方式。仓库同时保留既有 Python 运行器的兼容工具。

*A lightweight Agent Skill for organizing, running, and validating reproducible scientific data-analysis projects.*

## 功能

- 新建或整理时，每个可独立运行和检查的分析阶段对应一套 input/、output/、code.txt、readme.md。
- 同阶段的分析和配套可视化可以合并；独立下游分析另建四件套，复用上游产物。
- 输入只存数据或必要链接，运行代码集中于 code.txt，所有说明集中于 readme.md。
- 输出默认平铺，只保留本阶段脚本产物，不默认积累 runs/ 历史目录。
- 保护原始数据，使用明确的输入、输出和路径约定。
- 维持一个清晰的运行入口，减少重复脚本和隐藏步骤。
- 修改已有项目时控制范围，保留用户文件和无关改动。
- 实际运行受影响的分析，并检查退出状态、产物及关键数据内容。
- 避免生成无用途的总结、审查、日志和 Agent 工作记录。

本 skill 管理分析工作流，不代替统计方法选择、实验设计、领域解释或人工科研判断。

## 既有运行器兼容

新建四件套直接通过 `code.txt` 运行，不要求运行器、JSON 配置、辅助源码目录或持久状态。可复制 [合成数据示例](assets/minimal/readme.md)，通过 `python code.txt` 同时生成表格与配套图件。

`scripts/analysis_workflow.py` 保留已有文件检查、安全替换、运行凭据、依赖计划及恢复接口，仅供用户明确授权继续维护的既有工作流使用。它需要 Python 3.11+ 标准库，详细接口及限制见 [兼容工具说明](references/tools.md)。不将其 `input/workflow.json`、`input/src/`、`output/.analysis-state/` 布局用于新四件套，也不因工具支持多阶段就合并独立分析。

维护旧流程时继续核对必要依赖、实际执行、结果与恢复边界。工具不隔离任意脚本写入，不保证整组文件始终原子可见，也不推断未声明的依赖或科学口径；这些兼容能力不构成自动迁移、安装或删改历史状态的授权。

## 适用场景

- 创建新的科研分析模块。
- 整理结构混乱的生物信息学或统计分析目录。
- 修改 Bash、R、Python 分析脚本并重新生成结果。
- 修复表格或多面板图件，并验证全部受影响产物。
- 核对 README、代码、参数和实际结果之间的一致性。
- 整理服务器或集群已有分析：实际输入或链接归入 `input/`，输入位置、来源和可访问性直接记于 `readme.md`；结果与对应软件原生日志归入 `output/`，依据已有脚本或日志适配 `code.txt`；只整理时不重跑，不补猜缺失参数。

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
├── scripts/
│   ├── analysis_workflow.py
│   └── r_environment.R
├── references/
│   ├── tools.md
│   ├── environment.md
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
使用 code-cdoe-skill，在当前目录整理这批服务器分析材料，建立本阶段的 input/、output/、code.txt、readme.md。实际输入或链接放在 input/，结果和对应软件日志放在 output/，恢复可确认的 code.txt；输入位置与访问状态、方法参数、软件版本和环境直接写入 readme.md。只整理，不重跑；缺失步骤和参数明确标注。
```

这一能力由 Agent 按技能规范读取记录完成，运行器不会自动解析任意软件日志。整理完成不代表历史分析已经复现；日志不完整时也不承诺生成完整可执行入口。

## 分析阶段交付结构

新建或整理一个分析阶段时，目标目录保留以下四项；这不改变上面的 skill 安装包结构。用户指定在 `a/` 整理单个阶段时直接使用 `a/`，不另建一层模块目录：

```text
a/
├── input/
├── output/
├── code.txt
└── readme.md
```

| 项目 | 内容 |
|---|---|
| `input/` | 实际输入数据或必要的有效数据链接。 |
| `code.txt` | 本阶段可直接执行的运行脚本及必要执行参数。 |
| `output/` | 本阶段脚本生成的结果、图件及确有需要的软件原生产物。 |
| `readme.md` | 数据说明、方法与参数说明、软件及包版本、依赖环境和运行方式。 |

不新建 `input/src/`、`config.json`、`workflow.json`、`paths.md` 或重复环境报告。执行逻辑并入 `code.txt`，说明并入 `readme.md`；脚本不需要解析 README 作为配置。Bash、R 或 Python 入口分别使用 `bash code.txt`、`Rscript code.txt` 或 `python code.txt`，实际工作目录和解释器由 README 声明。

没有本地输入时仍保留 `input/`，在 README 的 Input 段记录有依据的原路径、来源和当前可访问性。只有相对路径且无法确认原工作目录时原样记录并说明限制，不编造绝对路径、数据或链接。

`output/` 默认平铺，不建立 `runs/<日期>/`、`runs/<编号>/` 或管理状态目录，不额外存放 Agent 总结、审查或工作记录。重复运行更新对应产物，成功后清理本次暂存与临时恢复副本；失败时保护上次有效结果，不在运行前清空整个输出。软件本身必需的结果目录结构按真实要求保留并说明。

阶段边界按输入、目标和产物确定。同阶段的必要计算、诊断图和结果图可以合并，例如单细胞基础处理、聚类及配套 UMAP，或差异表达及对应图件。后续以已完成结果为输入，开展可独立运行和检查的另一项分析时，另建四件套，例如差异表达后的功能富集、已有细胞对象后的拟时序或细胞通讯。下游在自己的 `input/` 复用上游产物；函数多、图多或保存中间文件不自动要求拆分，也不为缩减目录把整条独立分析链装进一个大脚本。

只修改、诊断或重跑已有项目而未要求整理时，保留原有有效入口与布局。已有必须原位保留的环境资源不擅自搬动或删除，位置和使用方式写入 README；不为说明环境而新建额外模块文件。整理前先识别归属，保留原始数据和运行证据；尚有不能安全归位的原文件时，说明结构限制，不宣称四件套已达标。

## 许可证

本项目采用 [MIT License](LICENSE)。

## 环境适配

运行前按 [环境检查与恢复](references/environment.md) 选择实际解释器并预检。R 辅助脚本 `scripts/r_environment.R` 提供逐包诊断、失败阻断及显式安装缺失包；不自动安装 R 或恢复锁文件。安装与分析使用相同 R 和包库。已有项目环境优先，不把示例包变成通用依赖。

R 测试通过 PATH 的 Rscript 或测试专用 `TEST_RSCRIPT` 定位；未提供 R 时明确 skip。目录搬迁测试不代表跨系统或客户端端到端验证。

验证入口为 `python -B -m unittest discover -s tests -v`。新示例测试检查搬迁后直接执行、结果内容、输出平铺与重复运行；运行器测试用于验证既有接口兼容，R 测试验证预检与失败阻断。测试通过不代表真实联网安装、跨系统或客户端端到端验收；库安装失败通过模拟离线安装器检查。

本次验证环境为 Windows、Python 3.11.9、R 4.5.2：66 项测试中 65 项通过，1 项因系统不允许创建符号链接而跳过，包含 8 项 R 预检测试。Skill 元数据校验通过；单细胞基础分析与已有差异结果后继续富集两个场景完成只读规则检查。
