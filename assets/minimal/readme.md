# 合成数据分组均值示例

本四件套记录一个独立分析阶段：读取合成数据，计算分组均值并生成配套条形图。分析与绘图由同一个 `code.txt` 完成，不据此拆成两套；本例不用于推断科学结论。

- 输入：`input/data.tsv`，随包提供的 4 个合成样本，未引用外部真实数据。`id` 是唯一且非空的样本标识，`group` 是非空组名，`value` 是有限非负数；至少有一行数据。
- 方法：先将每个 `value` 乘以 `scale`，再按 `group` 计算样本数 `n` 和算术均值 `mean`；按组名排序。SVG 条形图展示同一结果，不新增分析步骤。
- 参数：`--scale` 默认为 `1`，必须为有限非负数；`--title` 默认为 `Synthetic group means`；`--color` 默认为 `#3568a8`，指定 SVG 条形填充色。参数的执行定义在 `code.txt`，解释集中在本文件。
- 软件与环境：Python 3.11+；本次验证使用 Python 3.11.9。仅依赖 Python 标准库，不需要第三方包、Skill 安装目录或运行器配置。优先使用项目已有 Python 环境。
- 输出：`output/summary.tsv`，列为 `group`、`n`、`mean`；`output/means.svg`，分组均值条形图。默认输入产生 A 组 `n=2, mean=3`，B 组 `n=2, mean=7`。

复制整个 `minimal` 文件夹到独立工作目录，在该目录执行：

```text
python code.txt
```

必要时调整运行参数，例如：

```text
python code.txt --scale 2 --title "Scaled synthetic group means" --color "#6a4c93"
```

也可从其他工作目录使用 `code.txt` 的绝对路径；脚本从自身位置定位 `input/` 和 `output/`，不依赖终端当前目录。Windows PowerShell 指定解释器的示例：

```powershell
& 'C:\path\to\python.exe' 'D:\path with spaces\group_means\code.txt'
```

`output/` 在运行时创建，不需要为 Git 空目录添加占位文件。重复运行更新同名产物，成功后只保留本脚本生成的上述两个文件，不创建 `runs/`、运行编号或隐藏状态目录。已有不属于本脚本的文件不会被擅自清除，整理历史产物需另行核对其归属。

`input/` 只包含本阶段输入数据；数据来源、字段、参数、版本、环境及运行方式均记录于本文件。若下游基于本阶段结果开展独立分析，应另建四件套，并从其 `input/` 使用本阶段产物。
