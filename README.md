# Code Cdoe Skill

A workflow specification for script-based scientific data analysis. Each independent analysis stage uses `input/`, `output/`, `code.txt`, and `readme.md` to describe its inputs, execution, outputs, and methods. The repository also retains tools for existing runner-based workflows.

## Capabilities

- Organize each independently runnable and verifiable analysis stage with four entries.
- Keep analysis and its diagnostic or result plots together; use a separate layout for independent downstream analyses.
- Store only data or valid data links in `input/`, execution code in `code.txt`, and documentation in `readme.md`.
- Keep `output/` flat by default, without accumulating per-run directories.
- Protect raw data and preserve unrelated files and changes.
- Run authorized analyses and check exit status, expected outputs, and relevant data content.
- Avoid unnecessary summaries, reviews, logs, and agent work records.

This skill governs workflow organization and validation. It does not replace statistical method selection, experimental design, domain interpretation, or scientific judgment.

## Existing runner compatibility

New stages run directly through `code.txt`; they do not require a runner, JSON configuration, auxiliary source directory, or persistent state. Copy the [synthetic example](assets/minimal/readme.md) and run `python code.txt` to generate a table and its plot.

`scripts/analysis_workflow.py` retains file checks, protected output replacement, run receipts, dependency planning, and recovery interfaces for existing workflows the user has authorized maintaining. It requires Python 3.11+ and uses only the standard library. See the [compatibility tool reference](references/tools.md). Its `input/workflow.json`, `input/src/`, and `output/.analysis-state/` layout is not a template for new stages.

The runner does not isolate arbitrary script writes, keep all files atomically visible during replacement, or infer undeclared dependencies or scientific validity. Compatibility does not authorize migration, installation, or deletion of historical state.

## Use cases

- Create a scientific analysis stage.
- Organize an existing bioinformatics or statistical analysis directory.
- Modify Bash, R, or Python scripts and regenerate affected results.
- Repair tables or multi-panel figures and verify affected outputs.
- Check consistency among documentation, code, parameters, and results.
- Organize server or cluster snapshots: place actual inputs or links in `input/`, document external paths and access status in `readme.md`, and preserve results and associated software logs in `output/`. Recover `code.txt` from available scripts or logs. Organization alone does not authorize rerunning the analysis or guessing missing parameters.

Concept explanations, paper reading, and local code questions do not require this layout.

## Installation and invocation

Use the same skill directory with Claude Code, Codex, or NousResearch Hermes Agent. Copy the complete `code-cdoe-skill` folder rather than only `SKILL.md`; avoid an extra nested folder with the same name.

| Client | Default personal installation directory | Explicit invocation |
|---|---|---|
| Claude Code | `~/.claude/skills/code-cdoe-skill/` | `/code-cdoe-skill Organize and validate this scientific analysis project.` |
| Codex | `~/.agents/skills/code-cdoe-skill/` | `$code-cdoe-skill Organize and validate this scientific analysis project.` |
| Hermes Agent | `~/.hermes/skills/code-cdoe-skill/` | `/code-cdoe-skill Organize and validate this scientific analysis project.` |

Project-level directories are `.claude/skills/` for Claude Code and `.agents/skills/` for Codex. Place the complete skill folder inside them. For a custom Hermes home or profile, use its active skills directory. `~` denotes the user home directory; Windows paths depend on client configuration. Sources: [Claude Code](https://code.claude.com/docs/en/skills), [Codex](https://learn.chatgpt.com/docs/build-skills), and [Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/).

An existing Codex installation already verified under `~/.codex/skills/` can remain there. Avoid multiple divergent copies for one client. After installation, start a new session and check the skill list and loaded path. Automatic selection also depends on client configuration and model behavior.

Keep these resources together:

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

`agents/openai.yaml` provides optional Codex interface metadata. Claude Code and Hermes do not depend on it. Shared instructions use the standard `name` and `description` fields; no OpenAI, Anthropic, or Hermes SDK is required. See the [host adaptation guide](references/agents.md) for environment handling, command quoting, and client verification.

## Examples

Append these requests to the client's explicit skill invocation, or use them as natural-language requests:

```text
Use code-cdoe-skill to build a runnable GWAS stage from these inputs, generating association results and a Manhattan plot.
```

```text
Use code-cdoe-skill to fix all group-label errors in this R analysis, rerun affected tables and plots, and verify that they came from the current run.
```

```text
Use code-cdoe-skill to check whether the README and code agree on FDR, covariates, and PC counts. Correct confirmed inconsistencies and rerun affected results. Report unresolved conflicts that affect scientific meaning.
```

For server results such as `result.assoc` and `result.log`:

```text
Use code-cdoe-skill to organize these server analysis files as input/, output/, code.txt, and readme.md. Keep actual inputs or links in input/, results and associated software logs in output/, and recover the supported execution logic in code.txt. Document input locations and access status, methods, parameters, versions, and the environment in readme.md. Organize only; do not rerun. Identify missing steps and parameters.
```

The agent reads and interprets the available records; the runner does not parse arbitrary software logs. Organization does not establish historical reproducibility, and incomplete logs may not support a complete executable entry point.

## Analysis stage layout

A new or reorganized stage uses these four entries. This requirement applies to analysis stages, not the skill package. When the user specifies a single stage directory `a/`, use it directly:

```text
a/
├── input/
├── output/
├── code.txt
└── readme.md
```

| Entry | Contents |
|---|---|
| `input/` | Actual input data or necessary valid data links. |
| `code.txt` | The directly executable stage script and necessary execution parameters. |
| `output/` | Results, plots, and necessary native software outputs generated by the stage script. |
| `readme.md` | Data descriptions, methods and parameter explanations, software and package versions, dependencies, environment, and run instructions. |

Do not create `input/src/`, `config.json`, `workflow.json`, `paths.md`, or duplicate environment reports. Consolidate execution logic in `code.txt` and explanations in `readme.md`; the script should not parse the README as configuration. Use `bash code.txt`, `Rscript code.txt`, or `python code.txt` as appropriate, with the working directory and interpreter documented in the README.

Keep `input/` even when inputs are unavailable locally. Record supported original paths, sources, and access status in the README. Preserve unresolved relative paths as recorded; do not invent absolute paths, data, or links.

Keep `output/` flat by default. Do not create `runs/<date>/`, `runs/<id>/`, management state directories, or agent summaries and work records. Reruns update the relevant outputs; remove temporary staging and recovery copies after success. Protect previous valid results on failure, and do not clear the entire output directory before running. Preserve directory structures required by the analysis software and document them.

Define stages by inputs, objectives, and outputs. Necessary calculations and associated plots can share a stage, such as single-cell preprocessing and clustering with QC and UMAP plots, or differential expression with its result plots. A downstream analysis that independently uses completed upstream results gets a separate layout, such as enrichment, trajectory inference, or cell communication analysis. Use upstream results through the downstream `input/`. Function count, figure count, and saved intermediate files alone do not require splitting; fewer directories alone do not justify combining independent analyses.

For modification, diagnosis, or rerunning without a request to reorganize, preserve the existing valid entry point and layout. Do not move or delete required existing environment resources; document their locations and use. Organization must preserve raw data and execution evidence. Report unresolved file placement or structural constraints rather than claiming the layout is complete.

## License

This project uses the [MIT License](LICENSE).

## Environment and validation

Follow the [environment guide](references/environment.md) to select the actual interpreter and check dependencies. `scripts/r_environment.R` provides per-package diagnostics, failure blocking, and explicitly authorized installation of missing packages. It does not install R or automatically restore a lockfile. Use the same R executable and library configuration for installation and analysis; prefer the existing project environment.

R tests locate Rscript through `PATH` or the test-specific `TEST_RSCRIPT`. They report a skip when R is unavailable. Directory relocation tests do not establish cross-system or client end-to-end compatibility.

Run tests with `python -B -m unittest discover -s tests -v`. Example tests cover relocation, direct execution, result content, flat outputs, and reruns. Runner tests cover existing interfaces; R tests cover preflight checks and failure blocking. A simulated offline installer tests installation failure handling, not live network installation.

Recorded validation used Windows, Python 3.11.9, and R 4.5.2: 65 of 66 tests passed, with one skipped because the system did not permit symbolic links. This includes eight R preflight tests. Skill metadata validation passed. A read-only review covered single-cell basic analysis and enrichment from existing differential-expression results. These checks do not establish macOS/Linux support, live installation behavior, or client end-to-end acceptance.
