# Claude Code、Codex 与 Hermes Agent 适配

## 共用约定

技能内容以 `SKILL.md` 为入口。安装目录和显式调用见 [README](../README.md)。`agents/openai.yaml` 不承担执行逻辑，不应把必要规则仅放在该文件中。

通用正文不依赖 Claude 的动态命令注入、参数替换或子代理字段，也不依赖 Codex 或 Hermes 专属工具。由客户端读取所需资源并调用其可用的终端；不会因安装 skill 自动运行分析或获得额外权限。

区分三个位置：

- skill 根：本次加载的 `SKILL.md` 所在位置，用来查找参考文档、示例和必要工具。
- 分析阶段根：顶层为 `input/`、`output/`、`code.txt`、`readme.md`。一套对应有明确输入、目标和产物、可独立运行与检查的分析阶段；阶段内的计算及配套诊断图、结果图可以合并，需要独立执行的下游分析另建一套。
- 执行环境：真正执行 Python/R/Bash 的本机、容器或远程主机，决定可见路径与可用依赖。

`input/` 只放实际输入数据或必要链接；运行代码与必要执行参数集中在 `code.txt`。数据说明、分析方法与参数说明、软件及包版本、依赖环境和运行方式集中在 `readme.md`。不要新建 `input/src/`、`workflow.json`、`config.json` 或 `paths.md` 承载代码、配置或说明。`readme.md` 是说明文档，不用作程序读取的配置。

`output/` 默认平铺，只保留本阶段脚本生成的产物；不默认创建 `runs/`、状态、审计或日志历史目录。重复运行更新对应产物，成功后清理本次安全暂存和恢复副本。已有文件与必要环境元数据仍按 `SKILL.md` 的保留和授权要求处理，不能为结构整齐擅自删除。

先使用项目已配置的 Python、conda 或虚拟环境；无项目约定时按用户配置、PATH 顺序确认实际解释器。运行器的既有兼容功能要求 Python 3.11+，普通分析按本阶段实际需要确认版本。R 或 Bash 仅在被调分析使用它们时需要。不要硬编码开发者机器的解释器路径。

## 读取与执行

Claude Code 与 Codex：从本次加载位置读取必要支持文件，通过现有文件和终端工具访问分析入口。不要假定当前工作目录就是 skill 或分析阶段目录。

Hermes Agent：可通过 `skill_view` 加载 skill 与支持文件。读取成功不证明终端后端能访问同一路径；特别是 Docker、SSH 等后端，应先确认分析入口、输入、必要 skill 工具和解释器在执行侧的位置。需要复制时仅将必要的 skill 资源放入已授权且可见的位置，不放入新阶段的 `input/`；不要自动上传科研数据。

所有客户端均使用执行侧的实际解释器，以 `readme.md` 中声明的工作目录运行 `code.txt`。以下是纯 Python 阶段的语法示例，路径必须替换；R 或 Bash 阶段使用对应解释器：

POSIX shell：

```sh
cd "/path/to/analysis-stage"
"/path/to/python" code.txt
```

PowerShell：

```powershell
Set-Location -LiteralPath 'D:/path/to/analysis-stage'
& 'C:/path/to/python.exe' 'code.txt'
```

环境、版本和运行命令的说明写在 `readme.md`，不在 `code.txt` 中堆放安装指南或运行记录。执行前遵循 [环境检查与恢复](environment.md)，不能用静态检查代替实际分析和产物验证。

## 既有工作流兼容

`scripts/analysis_workflow.py` 的配置、多阶段、运行凭据及持久恢复接口仅用于用户明确授权继续维护的既有工作流，详见 [工具说明](tools.md)。其原有 `input/workflow.json`、辅助源码和 `output/.analysis-state/` 不作为新四件套的模板。没有维护授权时不自动接入、迁移或删除既有配置与状态。

## 验证与证据边界

本仓库兼容工具测试不要求安装任何 Agent 客户端：

```text
python -B -m unittest discover -s <skill>/tests -v
```

运行器测试检查兼容接口、凭据、依赖重跑及故障恢复等行为，其既有配置与状态布局不代表新四件套要求。新资源可移植性用例在不同 skill 安装位置和含空格的项目路径中直接运行 `code.txt`，检查合成数据与图件、平铺输出及重复运行不累积历史目录，也覆盖不带 `agents/openai.yaml` 的运行。这些测试不模拟客户端的技能发现、权限控制或模型行为。

安装后的客户端验收：

1. 新建会话，确认技能列表包含 `code-cdoe-skill`，显式调用并核对实际加载位置。
2. 请 Agent 读取 `assets/minimal/readme.md`，将整个合成示例复制到单独的可写分析阶段目录。
3. 请 Agent 按示例 `readme.md` 运行 `code.txt`，检查输入、结果与图件，确认顶层四项和 input/output 内容符合职责。
4. 再次运行该示例，确认对应产物更新，没有累积 `runs/`、状态或运行历史目录，本次临时文件已清理。

示例只验证合成计算与结构，不代表真实科学分析已通过。无终端或缺少依赖时可以提供检查与修改建议，但要如实标注未执行部分。真实科学数据、R/Bash 环境和不同远程后端仍需各自验收。

兼容依据为 [Claude Code Skills](https://code.claude.com/docs/en/skills)、[Codex Skills](https://learn.chatgpt.com/docs/build-skills)、[Hermes Skills](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/)。格式兼容与程序测试通过不等于三端模型端到端验收通过。

四项阶段目录规则的环境例外仅为必须原位保留的既有环境文件，或用户明确要求新增的环境工具元数据；不默认每阶段新建锁文件或环境目录。合成 Python 示例没有这些元数据，仍检查四项。Rscript 按项目环境、用户指定配置、PATH 顺序定位；检查、恢复和分析复用同一解释器与启动配置。固定解释器不代表固定包库，失败后按 environment.md 定位并在 `readme.md` 记录必要原始证据，不能用 RStudio 中能加载包代替实际执行环境的检查。
