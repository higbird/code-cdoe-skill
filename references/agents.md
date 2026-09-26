# Claude Code、Codex 与 Hermes Agent 适配

## 共用约定

技能内容以 `SKILL.md` 为入口，正文与运行器共用一份实现。安装目录和显式调用见 [README](../README.md)。`agents/openai.yaml` 不承担执行逻辑，不应把必要规则仅放在该文件中。

通用正文不依赖 Claude 的动态命令注入、参数替换或子代理字段，也不依赖 Codex 或 Hermes 专属工具。由客户端读取所需资源并调用其可用的终端；不会因安装 skill 自动运行分析或获得额外权限。

区分三个位置：

- skill 根：本次加载的 `SKILL.md` 所在位置，用来查找运行器、参考文档和示例。
- 项目根：分析模块目录，顶层为 `input/`、`output/`、`code.txt`、`readme.md`。配置放在 `input/workflow.json`，运行器通过 `--root` 明确此模块目录，以它解析输入、源码、输出和状态；状态在 `output/.analysis-state/`。
- 执行环境：真正执行 Python/R/Bash 的本机、容器或远程主机，决定可见路径与可用依赖。

先使用项目已配置的 Python、conda 或虚拟环境。没有项目约定时，确认可用 Python 为 3.11+ 后再调用；`python` 只是示例名。R 或 Bash 仅在被调分析使用它们时需要。不要硬编码开发者机器的解释器路径。

## 读取与执行

Claude Code 与 Codex：从本次加载位置读取 `references/tools.md`，通过现有文件和终端工具访问运行器。不要假定当前工作目录就是 skill 或项目目录。

Hermes Agent：可通过 `skill_view` 加载 skill 与支持文件。读取成功不证明终端后端能访问同一路径；特别是 Docker、SSH 等后端，应先确认运行器、分析项目和解释器在执行侧的位置。需要复制时仅将必要的 skill 资源放入已授权且可见的位置；不要自动上传科研数据。

所有客户端均使用执行侧的实际路径调用运行器。以下是语法示例，路径必须替换：

POSIX shell：

```sh
"/path/to/python" "/path/to/code-cdoe-skill/scripts/analysis_workflow.py" plan "/path/to/project/input/workflow.json" --root "/path/to/project"
```

PowerShell：

```powershell
& 'C:/path/to/python.exe' 'C:/path/to/code-cdoe-skill/scripts/analysis_workflow.py' plan 'D:/path/to/project/input/workflow.json' --root 'D:/path/to/project'
```

以上展示运行器接口；生成的模块通过 `code.txt` 统一调度，示例使用 `python code.txt --skill-root <skill目录> [run|plan|recover]`。`plan` 只生成计划；实际生成结果使用 `run`，随后再 `plan` 核对是否可跳过。分析命令在 JSON 中使用参数数组，避免把命令拼接成某个 shell 专属字符串。完整参数和保护边界见 [工具说明](tools.md)。

## 验证与证据边界

本仓库测试不要求安装任何 Agent 客户端：

```text
python -B -m unittest discover -s <skill>/tests -v
```

可移植性用例将完整技能复制到三种安装目录形状，在另一个含空格及中文路径的项目中运行合成示例，并检查数据、图件、output 内的凭据、再次计划跳过，以及运行前后顶层严格只有四项。也覆盖不带 `agents/openai.yaml` 的运行。它验证资源可重定位及程序独立性，不模拟客户端的技能发现、权限控制或模型行为。

安装后的客户端验收：

1. 新建会话，确认技能列表包含 `code-cdoe-skill`，显式调用并核对实际加载位置。
2. 请 Agent 读取 `assets/minimal/readme.md`，将整个合成示例复制到单独的可写项目目录。
3. 请 Agent 通过 `code.txt` 运行 `plan`、`run`、`plan`，确认模块顶层只保留四项，检查 `summary.tsv`、`means.svg` 和阶段凭据；第二次计划两阶段都应为 `skip`。
4. 修改示例 `input/workflow.json` 的 `plot.params.title`，检查只需重跑 plot，运行后核对图件标题。

无终端或缺少依赖时可以提供检查与修改建议，但要如实标注未执行部分。真实科学数据、R/Bash 环境和不同远程后端仍需各自验收。

兼容依据为 [Claude Code Skills](https://code.claude.com/docs/en/skills)、[Codex Skills](https://learn.chatgpt.com/docs/build-skills)、[Hermes Skills](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/)。格式兼容与程序测试通过不等于三端模型端到端验收通过。

分析前执行 [环境检查与恢复](environment.md)。四项模块目录规则允许工具必需环境元数据例外；合成 Python 示例没有这些元数据，仍检查四项。Rscript 按项目环境、用户指定配置、PATH 顺序定位；检查、恢复和分析复用同一解释器与启动配置。固定解释器不代表固定包库，失败后按 environment.md 定位并记录原始证据，不能用 RStudio 中能加载包代替实际执行环境的检查。
