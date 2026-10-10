# Synthetic Group Means Example

A single `code.txt` reads synthetic data, calculates group means, and generates a bar chart. This example covers one analysis stage; it does not support scientific inference.

- Input: `input/data.tsv` contains four bundled synthetic samples and references no external research data. `id` is a unique, nonempty sample identifier; `group` is a nonempty group name; `value` is finite and nonnegative. At least one data row is required.
- Method: multiply each `value` by `scale`, then calculate the sample count `n` and arithmetic mean `mean` for each `group`. Results are sorted by group name. The SVG bar chart displays these same results.
- Parameters: `--scale` defaults to `1` and must be finite and nonnegative; `--title` defaults to `Synthetic group means`; `--color` defaults to `#3568a8` and specifies the SVG bar fill color. Executable parameter definitions are in `code.txt`; their descriptions are in this file.
- Software and environment: Python 3.11+, tested with Python 3.11.9. The script uses only the Python standard library and requires no third-party packages, installed Skill directory, or runner configuration. Prefer the project's existing Python environment.
- Output: `output/summary.tsv` contains `group`, `n`, and `mean`; `output/means.svg` displays the group means. The default input produces `n=2, mean=3` for group A and `n=2, mean=7` for group B.

Copy the entire `minimal` folder to a separate working directory and run:

```text
python code.txt
```

Adjust parameters as needed, for example:

```text
python code.txt --scale 2 --title "Scaled synthetic group means" --color "#6a4c93"
```

To run from another working directory, provide the absolute path to `code.txt`. The script locates `input/` and `output/` relative to its own location, regardless of the terminal's working directory. For example, specify the interpreter in Windows PowerShell:

```powershell
& 'C:\path\to\python.exe' 'D:\path with spaces\group_means\code.txt'
```

The script creates `output/` at runtime; Git needs no placeholder for an empty directory. Repeated runs replace the same named outputs. Starting from the bundled example, successful runs produce only the two files above, without `runs/`, numbered run directories, or hidden state directories. The script does not remove unrelated existing files; check their origin and purpose before cleaning up historical outputs.

`input/` contains only this stage's input data. This file records data sources, fields, parameters, versions, environment, and run instructions. An independent downstream analysis should have a separate stage layout and use this stage's outputs through its `input/`.
