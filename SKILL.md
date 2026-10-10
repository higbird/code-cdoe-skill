---
name: code-cdoe-skill
description: Organize research analysis stages that can be run and checked independently with input/, output/, code.txt, and readme.md. Use to create or organize analysis modules, maintain Bash/R/Python scripts, rerun results, restore entry points from evidence, or repair figures. Analysis and its supporting plots can share a stage; independent downstream analyses need separate four-item layouts. Keep inputs limited to data, execution in one script, documentation in the README, and outputs concise. Protect raw data and verify actual execution. Do not create project structures for concept explanations, paper reading, or local code questions.
---

# Lightweight Research Analysis Workflow

Help researchers and small teams use coding agents for clearly organized data analysis that can be rerun and whose results are checked. Suitable for bioinformatics, statistical analysis, and other research tasks based primarily on scripts.

This skill covers project organization, execution constraints, and delivery checks. It does not independently establish the scientific basis for statistical method selection, experimental design, or domain interpretation. Successful execution does not replace scientific judgment.

## Hosts and Paths

The same skill supports Claude Code, Codex, and Hermes Agent. Use the host's file reading, editing, and terminal capabilities without relying on specific tool names, models, plugins, or client SDKs. Use the current project's environment. The optional runner requires Python 3.11+; confirm R, Bash, and analysis dependencies as the project requires.

Use the directory of the currently loaded `SKILL.md` as `<skill>` and resolve `scripts/`, `references/`, and `assets/` from it. Do not treat the skill installation directory as the analysis project. The module root is the stage's four-item directory; `code.txt` resolves inputs and outputs from the working directory declared in the README. Quote paths containing spaces correctly for the current shell; do not assume the terminal uses Bash.

Before execution, confirm that the terminal environment can access skill resources, the project, and the interpreter. Paths in remote environments, containers, or sandboxes may differ from those on the host that loaded the skill. If paths are unavailable, resolve resource mapping within the authorized scope before execution. If execution capabilities or permissions are missing, complete feasible checks and state which parts were not run. A description or successful loading is not evidence of successful execution. See [Host Integration](references/agents.md) for installation, invocation, and acceptance checks across the three hosts.

## 1. Goals and Priorities

Use the simplest approach that meets the task and retain the fewest files sufficient for it. Structure serves the analysis; do not create extra work solely for conventions, review, or reporting.

Subject to higher-priority instructions and permission boundaries, resolve tradeoffs in this order:

1. User authorization, raw data protection, and result correctness.
2. User-confirmed methods, parameters, reference versions, and applicable project conventions.
3. Repeatable execution, necessary result provenance, and validation.
4. Simple structure, concise file sets, and consistent naming.

If a user-confirmed method has a clear problem, explain the evidence and implications. Do not silently substitute another method or present results from a questionable method as reliable conclusions.

Fewer files do not justify omitting required dependencies, failure evidence, data versions, or validation. Keep explanations of data, methods, versions, environments, and necessary evidence in `readme.md`; place actual inputs and script products as specified in Section 3. The four-item top-level layout applies to new modules and directories the user explicitly asks to organize. Modifying, diagnosing, or rerunning an existing project does not authorize directory restructuring.

## 2. Workflow

### 2.1 Identify the Task and Current State

Check the user's objective, target directory, specified reference files, existing entry points, input and output status, and project environment.

For large projects, first read the README, existing input manifests, and a shallow directory listing. Locate only files needed for the current task. Do not default to recursively traversing raw data directories, printing entire large tables in the conversation, or treating full-file line counts as inexpensive checks. Read headers, selected regions, and necessary statistics as needed; still perform full validation when scientifically required.

Distinguish requests to create an analysis, modify implementation, rerun results, organize structure, or only explain and diagnose. Stay read-only for explanation or diagnosis. Make requested repairs or organizational changes within the corresponding authorization. If the user requests only draft code or a specification, deliver that content and state that the analysis was not run; do not invent a research task for validation.

"Organize the four-item layout" includes placing files and adapting an entry point supported by evidence under Section 3; it does not automatically authorize running the analysis. "Adapt a runnable entry point" requires connecting the execution logic and completing necessary preflight checks within the declared scope. "Run and generate results" also requires actual execution and result validation. A complete directory layout cannot substitute for entry point adaptation, and empty directories do not justify expanding execution scope.

Do not treat existing figures, caches, old results, or historical success records as evidence that the current code has passed validation. Existing changes belong to the user; preserve unrelated content.

Results, logs, scripts, and partial inputs copied from a server or cluster form an existing analysis snapshot. Identify each file's role rather than treating the entire downloaded directory as input. An organization-only request does not default to deleting, renaming, rerunning, or regenerating existing results. Place files and restore an entry point supported by evidence under Sections 3-5. For a request to continue downstream analysis, reuse suitable existing results without incidental directory restructuring or upstream reruns.

Resolve questions directly when file inspection and conversation context provide the answer. Use reasonable defaults for low-risk implementation choices that do not affect scientific meaning, and state them briefly. When missing information affects method selection or result interpretation, complete independent work before raising specific decisions that remain open.

Existing choices and valid approvals remain applicable. Follow actual requirements for charges, external uploads, installation, publication, and separate stage approvals; this skill does not expand authorization. An approval requirement blocks only actions that depend on it.

### 2.2 Define Analysis Boundaries and Expected Products

Define the question, input data, confirmed methods and key parameters, expected results, and necessary validation criteria. State these in the conversation if useful; no extra plan file is required.

Set the analysis start and end points before determining required inputs. Distinguish existing upstream products, the current steps, and subsequent steps. Check existing intermediate products for format, required fields, sample correspondence, and verifiable provenance. If a product meets the current input requirements, an entry point may start from it; state any limits on verification of its upstream source or version. Missing raw inputs outside the scope must not block downstream work. If the user explicitly requests full reproduction from raw data, do not reduce that scope without authorization.

Block a dependent step only when an irreplaceable input, key parameter, or required step within the declared scope is missing and cannot be recovered through inspection. Distinguish unchecked items, verified absence, and permission or service errors. An unchecked environment is not evidence that execution is impossible. Continue authorized work independent of the blocker, and do not report partial workflow success as overall completion.

Each four-item layout records one analysis stage with defined inputs, an analysis objective, and target products that can be run and checked independently: `code.txt` processes A in `input/` to produce B in `output/`, with the process explained in `readme.md`. A stage may contain necessary sequential computations. Do not create a separate layout for every function, command, intermediate file, or rerun.

Computations, diagnostic plots, and result figures for the same stage may be combined. For example, basic single-cell processing, dimensionality reduction, clustering, and supporting QC and UMAP plots can share one `code.txt`. Differential expression and its result plots can also share one layout. A large number of figures or a palette adjustment does not automatically require splitting a stage.

Create a separate four-item layout when another analysis takes completed, independently reusable upstream results as input and needs independent execution and checking. Examples include functional enrichment after differential expression, pseudotime or cell communication analysis from a completed cell object, and COJO after GWAS. Organize each by its own inputs and target products. Downstream stages use upstream products or valid links in their own `input/`. Do not combine these independent stages into one large layout merely to reduce directories or fit everything into one script. A single script may itself contain independent analyses that should be separated.

### 2.3 Make Minimal Changes

Prefer editing the existing entry point and README. Change only what is necessary for the current objective. Unless the user requests structural organization, avoid incidental renaming, directory migration, script splitting, or refactoring unrelated analyses.

When fixing similar issues, first scan for affected occurrences within the requested scope. If the user asks to fix all such issues, state the affected scope in the conversation and cover every affected result and panel after the repair. Preserve specified reference methods and parameters. If the reference code is questionable, explain the issue first; do not copy known errors to obtain a consistent appearance.

### 2.4 Execute and Validate

When the task includes running an analysis or rerunning after changes, use the project's specified environment, working directory, and entry point declared in the README. Syntax checks, static parsing, and dry runs are preflight checks, not substitutes for actual execution.

Check exit status, products from the current run, and content correctness relevant to the task under Section 6. If long computations require a cluster, additional charges, or specific approval, complete feasible checks and state what remains unverified. Job submission is not computation completion.

For organization-only work on existing server analyses, check file placement, input references, execution wiring, available script or log evidence, and the README. Perform necessary static checks and preflight checks without analysis side effects on the adapted entry point; do not run the analysis solely to validate the entry point without authorization. Report organization, entry point adaptation, and the absence of a rerun separately. Historical products do not establish successful reproduction. If the entry point remains blocked, report partial completion under Section 6.

### 2.5 Deliver

State the status first, then briefly describe changes, actual execution scope, validation results, and unresolved items. Distinguish "completed," "delivered for acceptance," and "partially completed with blockers." Do not declare acceptance on the user's behalf when it has not occurred.

Structure checks may pass while execution remains unverified. A successful run may still leave uncertainty in scientific interpretation. State these separately rather than combining partial successes into a claim of complete success.

## 3. Module Structure and Entry Points

When creating or organizing an analysis stage, keep four items at the module root and use lowercase `readme.md` for documentation. If the user specifies organization within `a/`, use `a/` directly as the stage root. Use separate four-item layouts for independent stages rather than combining them into a general orchestration module. If no directory is specified, short names with workflow numbers may be used:

```text
03_GWAS/
├── input/
│   ├── genotype.bed
│   ├── genotype.bim
│   ├── genotype.fam
│   ├── pheno.tsv
│   └── covar.tsv
├── output/
│   ├── assoc.tsv
│   ├── sig.tsv
│   ├── manhattan.pdf
│   └── qq.pdf
├── code.txt
└── readme.md
```

- `input/`: Only actual input data for this stage or necessary valid data links.
- `code.txt`: Only the directly executable stage script, with parameters, path handling, and checks required for execution.
- `output/`: Only results, figures, and necessary native software products generated by the stage script.
- `readme.md`: Central documentation for data, analysis methods and parameters, software and package versions, environment dependencies, and execution instructions, including target products, provenance, and validation limits.

Keep `input/` and `output/` even when data or results are unavailable. If there are no local inputs, record input locations supported by evidence and their accessibility in `readme.md`; do not fill `input/` with explanatory files or fake data. Do not create `input/src/`, `config.json`, `workflow.json`, `paths.md`, or environment documentation files. Incorporate helper execution logic into `code.txt` and explanations into `readme.md`. The README is documentation for people; scripts need not parse Markdown as configuration.

`code.txt` must run directly with the interpreter declared in the README. Use `bash code.txt` when Bash is available, or `Rscript code.txt` or `python code.txt` for pure R or Python analyses. One entry point may perform the stage's necessary sequential processing and supporting visualization. Split independent downstream analyses under Section 2.2. Do not provide only commands for the user to copy manually or a wrapper that merely invokes scripts in `input/src/`.

When organizing existing scripts, adapt the stage's execution logic into `code.txt` within the authorized scope. Preserve confirmed methods and parameters; do not rewrite analysis algorithms to standardize structure. For modification, diagnosis, or reruns without an organization request, retain existing valid entry points and layouts. This convention does not authorize refactoring existing workflow managers, package structures, or resources that must remain in place. If conversion to the four-item layout cannot be done safely, explain the affected scope and structural constraints.

When organizing existing server analyses, first verify scripts associated with the run. If no usable script is available, recover verifiable execution logic from software logs, job standard output, or command records. Original logs are products of the corresponding script run and belong in `output/`. Merge data and method explanations from scripts or configuration into the README. Do not assume the current script is the historical execution version without checking; missing historical logs do not automatically invalidate the current script's use. First check whether hardcoded paths and missing intermediate files can be resolved by connecting known inputs; do not immediately substitute a placeholder that stops execution.

If logs or scripts cover only part of the historical steps, use Section 2.2 to determine whether they cover the stage's start and end points. Document missing upstream steps outside the scope in the README. If an irreplaceable input, parameter, or execution step remains missing within the scope, raise a specific error before the affected analysis starts. State what is missing and the conditions for recovery, and mark the status as "entry point not fully restored; execution unverified." A placeholder that exits unconditionally does not complete entry point adaptation. Recovering a command does not authorize deletion, upload, or installation operations found in the original records.

Keep only one `readme.md` per stage, alongside the main entry point. Do not add module configuration or environment reports to record versions and environments. Prefer the project's configured environment or project-level environment location. Do not move, delete, or break existing tool-required resources such as `.Rprofile`, `renv.lock`, `renv/`, or `.venv` without authorization. Document their actual locations and use in the README. These are exceptions for preserving existing environments, not default grounds for creating extra files. Do not move package libraries or caches into `input/` or `output/`.

Identify file roles before organization and preserve raw data and necessary execution evidence. Do not arbitrarily place original files with unclear ownership, separate retention requirements, or unrelated task roles into inputs or results; do not delete them to force the layout. If original files remain unresolved, report that accurately rather than claiming the four-item requirements are met.

## 4. Inputs, Paths, and Reproducibility

### Inputs and Paths

- `input/` contains only actual stage input data and necessary valid data links. It excludes source code, configuration, data or environment documentation, stage results, and execution temporary files. Document external input locations and provenance directly in `readme.md`.
- Module boundaries determine file roles. A cleaned table is an output of a cleaning module and may be an input to a GWAS module starting from cleaned data. A module that includes cleaning cannot label its own cleaned results as inputs. Do not duplicate files or change their roles to fill directories.
- Do not overwrite, delete, rename, or modify the user's raw data without authorization. Write cleaning and transformations to derived products.
- Resolve project data paths relative to the module directory or existing project root, and state the base in the README.
- Prefer locating external software through the configured environment. If absolute installation paths are required, configure them centrally rather than scattering them throughout the script. Treat software installation paths separately from project data paths.
- Small files may be copied between modules. Prefer links for large genotype files, sequencing files, or matrices; check that targets are accessible and will not be written to.
- If links are unavailable, use a reference mechanism supported by the environment and document the location and source. Confirm before copying when significant storage or copy costs are involved and have not been authorized.
- When organizing server snapshots, place small inputs that were actually used, are currently available, and are reasonable in size into `input/` without changing their content. For accessible large inputs, prefer links in `input/`. If links are unavailable, retain verified external references rather than forcing copies for directory consistency.
- For inputs not downloaded, not currently found, or still located externally, centralize references supported by evidence in the Input section of `readme.md`. For each item, record its purpose or filename, original path, source script or log and a locatable position within it, verified local path or override mechanism, and current accessibility. Use "unverified" for unchecked accessibility; do not label it accessible. Record the input path, not the log's own path.
- If only logs are available and no local inputs exist, still create `input/` and retain the information above in `readme.md`. Do not create fake data, empty data placeholders, or broken links. If an original record provides only a relative path and its working directory cannot be confirmed, preserve the path and mark "absolute path cannot be resolved." If logs provide no input location, write "cannot be confirmed from existing records" rather than guessing. Preserve filename prefixes required by the original software and check required companion files.
- In `code.txt`, use paths relative to the declared project root for local inputs. Configure external input paths centrally and allow overrides through existing parameters or environment variables. Original server paths may serve only as defaults supported by provenance; check actual input accessibility before running. Overridable paths do not establish that the local execution environment is available.
- A link to upstream output does not fix the input version. To reproduce historical results, retain explicit data versions, checksums or other verification information, or suitable snapshots.

### Environment, Parameters, and Randomness

Before running analysis, read [Environment Checks and Recovery](references/environment.md) and follow its procedure to confirm the actual interpreter, dependencies, permissions, and availability. For R analyses, integrate `require_r_environment` from `scripts/r_environment.R` into the actual entry point, or use an existing equivalent project preflight check. Preserve original errors on failure; do not label every failure as a package library path issue. Follow the environment reference's failure procedure to check the actual interpreter, startup configuration, and active libraries, and merge diagnostic evidence into the existing README. Repair and recheck within existing authorization, then continue the analysis; do not end the task merely upon finding a missing package. Organization-only tasks do not authorize running analysis. Do not claim an issue is the "only blocker" without comprehensive preflight checks.

Prefer reusing the project's venv, conda, renv, container, or lock files, and avoid arbitrary interpreter changes. Briefly record language runtimes, key software versions, and necessary dependencies in the README; continue maintaining existing environment files.

Centralize version, dependency, and environment information in `readme.md`. Do not place version inventories or environment explanations in `code.txt`, or create environment configuration under `input/` or duplicate reports. Imports, dependency preflight checks, and path handling needed for execution remain part of the script. Use existing environment tools and lock files according to project conventions. When the user explicitly requests new lock files, containers, or reproduction materials for submission, work within that authorization and explain the structural exception. Do not promise reproduction across environments without verifying it.

Maintain execution parameters in `code.txt` or the command-line parameters it accepts; do not add `config.json` or `workflow.json`. Document thresholds, covariates, PC counts, windows, permutation counts, thread counts, and random seeds in `readme.md`, keeping them synchronized with the actual script.

Explicitly set and record seeds for random sampling, data splits, permutations, bootstrap, and similar steps. Fixed seeds do not guarantee bitwise identity across hardware and parallel implementations. Use numerical tolerances where needed and state uncontrolled nondeterminism.

### Parameter Conflicts

Code shows the execution logic it contains. It cannot alone prove what was historically executed or what should be executed.

When the README, code, configuration, or result explanations conflict, check the current user request, confirmed methods, and specified reference version. If intent can be established, correct the erroneous source and synchronize documentation. Rerun affected results when the task includes rerunning. For organization-only work on historical analyses, record differences without altering historical logs or regenerating results. If intent is unclear and the difference affects scientific meaning, pause computations that depend on the decision and identify the specific conflict; continue other authorized work.

For example, if the README states FDR < 0.05 and the code uses P < 0.05, check the user-confirmed testing criterion. Do not simply change the README to match the code to remove the conflict.

When restoring historical analyses, first seek the original run script, complete commands in software logs, and job submission scripts, then check the README or configuration. Results provide supporting evidence only; do not use them to guess original parameters. Association with the same run matters more than a fixed source ranking. Check available job identifiers, output prefixes, paths, versions, and time records; timestamps alone do not prove association. If conflicting sources cannot be resolved, state the conflict and "cannot be confirmed from existing records." Do not assume a script is always more reliable than the actual execution log.

## 5. Result Retention, Reuse, and Safe Updates

### Useful Products

`output/` retains only research results, downstream inputs, intermediates with clear reuse value, figures, and necessary native software outputs generated by the stage's `code.txt`. Keep files directly in this directory by default. Preserve directory structures required by the software and explain them in the README. Many figures or files do not automatically justify additional nesting.

Do not create `runs/<date>/`, `runs/<run_id>/`, or other per-run directories. Do not accumulate complete copies of every run by default or add agent summaries, reviews, work records, run receipts, or management files such as `.analysis-state/`. Centralize version, environment, method, and process explanations in `readme.md`.

For organization-only work with no existing results, `output/` may be empty. State "no existing results found; no results generated by execution." Do not run unauthorized computations to fill a directory, present inputs as results, or claim results have been delivered. If the user requests result generation, an empty directory is not completion. Statistically valid empty results still require Section 6 checks and must be distinguished from an unrun or failed analysis.

When organizing existing analyses copied from a server or cluster, `output/` holds research results and the software logs, job standard output, and necessary error logs directly associated with that analysis. Put these logs in `output/`, without creating `logs/` or retaining them at the module root. For example:

```text
output/
├── result.assoc
└── result.log
```

Place only files confirmed to belong to the target analysis. Do not combine unrelated tasks or evidence from different runs. For filename conflicts, retain both files and distinguish them within `output/` using traceable run identifiers; do not overwrite either. Preserve original filenames for native software products and logs. Rename only for a confirmed conflict or user request, and document the mapping in the existing README. This rule does not require restructuring ordinary project log directories outside the task scope.

Use short, identifiable names for new products, such as `assoc.tsv`, `sig.tsv`, and `manhattan.pdf`. Avoid repeating the module name or using ambiguous names such as `a.tsv` or `1.pdf`. Do not manage iterations with `new/fixed/final` or combinations of these labels.

Follow the user's requirements and actual use when choosing figure formats. If unspecified, prefer whichever of PDF or PNG is suitable. Provide other formats as needed for editing or submission; do not generate batches of unused formats.

### Multiple Datasets and Parameter Sets

Reuse code when methods and input formats match. Replacing only the input suits sequential tasks that do not need to retain old results. When a stage must compare multiple cohorts, batches, models, or parameter sets at once, distinguish them by scientifically meaningful filenames such as `assoc_discovery.tsv` and `assoc_replication.tsv`. Do not create history directories based on run dates or numbers.

Identifiers must map to inputs and actual parameters. Code reuse must not overwrite results still needed for comparison. Prefer a shared entry point with explicit parameters for repeated comparisons; create new modules only for independent research tasks. Follow the user's version-retention requirements, and do not create whole-project copies for routine repairs.

### Updating Existing Results

A rerun updates the stage's corresponding target products. Before overwriting, establish which results the run will generate and which result set must remain consistent. When protected replacement is needed, generate and validate products in a temporary location exclusive to the current run, then replace the final products. After success, clean up staging files and temporary recovery copies rather than retaining them as permanent `runs/` history. Do not empty all of `output/` at the start of each run or delete unrelated results or results still needed for comparison.

Treat tables, figures, and corresponding software logs that need simultaneous updates as a group. Do not pair old logs with new results. Replacing multiple files one by one is not inherently atomic. Use a recoverable replacement approach when necessary to avoid presenting a mixture of old and new results. Keep temporary recovery copies only for valid products that may be replaced by this run, and clean them up after success.

On failure, preserve the last valid results and identify them as belonging to an older run. If an existing workflow cannot isolate outputs, first apply suitable protection and identify current-run products. State recovery and validation limits accurately; do not claim rollback guarantees that have not been implemented.

Clean only temporary paths created for this run whose purpose has ended. Verify targets before deletion; do not bulk-delete user files based on keywords such as `tmp`, `old`, or `log` in filenames. Preserve necessary evidence while diagnosis is incomplete so cleanup does not obstruct it. After explicitly authorized deletion, check remaining files and state recovery conditions.

## 6. Validation and Completion Criteria

Select necessary checks for the task's scale. Do not add unrelated tests to demonstrate thoroughness. Keep the checking process in the conversation by default, without extra review files.

Check these states separately as the user requires; none substitutes for the others:

- **Structure organization**: Files are placed appropriately, content is preserved, and references and accessibility are recorded accurately.
- **Entry point adaptation**: Existing scripts are connected into valid execution logic for the declared scope, with paths, task selection, and dependency checks adapted. If static checks pass but execution has not occurred, state that without claiming successful execution.
- **Actual execution**: Authorized steps have run, and exit status and failure information have been checked.
- **Result validation**: Expected products and necessary content checks pass, with old results clearly distinguished from current results.

A placeholder entry point does not meet adaptation requirements. When result generation is required, products that have not been generated by execution or validated do not meet delivery requirements. If only structure checks pass, report the relevant state, such as "directory organization completed; entry point not yet adapted; analysis not run." If other requested work remains blocked, report overall partial completion.

For organization-only server snapshots, verify that placement did not change existing file content, referenced locations and accessibility are recorded accurately, entry point commands are supported by original records, and missing items and conflicts are marked. Do not default to repeated full scans of large files merely to confirm placement. Select necessary checks for the actual operations. The following execution requirements apply to parts that involve reruns or new analyses.

### Execution and Products

- Check errors from the main process and called programs. Do not report success after catching errors and continuing execution.
- Confirm that the expected result set was generated by the current run, and check counts of missing, nonempty, and zero-byte files. Temporary output locations and before/after comparisons can help identify current products; timestamps alone do not establish correctness.
- Identify valid empty results. For example, a header-only `sig.tsv` may be valid when no significant associations are found. Do not fabricate records to pass a nonempty-file check.
- Old results not regenerated, partially checked subsets, and residual products from abnormal exits cannot establish complete success.

### Data and Statistical Content

Choose a small set of checks that can detect the main errors relevant to the task, for example:

- Sample ID uniqueness, sample matching, group labels, and input/output sample counts.
- Required columns, missing and infinite values, units, value ranges, and output structure.
- Consistency of actual testing criteria, thresholds, and confirmed parameters.
- Known reference results or numerical tolerances; rerun only when repeatability needs to be checked.

Do not presuppose significance, effect direction, or a particular sample count to force results to fit a hypothesis. Validation criteria come from input requirements, method requirements, or reliable references.

### Figures

When rendering is possible, check final figures for blank content, clipping, and missing panels. Verify axes, units, groups, and consistency between figure statistics and result tables. If visual inspection is unavailable, state what was checked and the remaining limits.

Cover every affected panel when a repair affects multiple panels. Appearance-only changes do not require rerunning expensive upstream analysis, but confirm that reused data matches the current analysis version.

Report the corresponding work as complete only when necessary execution and checks within the requested scope are finished. Plausible outputs that pass checks do not establish that a research hypothesis is true or that scientific conclusions are confirmed.

## 7. README and Necessary Records

The README should let users understand the purpose, inputs, methods and parameters, environment and execution instructions, and results without reading the code.

State the start and end points covered by the entry point, reused upstream products, and provenance limits. In Run, distinguish an adapted but unrun entry point, required dependency blockers, and verified execution. In Output, distinguish existing results, current-run results, and results not generated. Describe missing items only within their actual affected scope.

Use these sections concisely when relevant; do not fill unrelated sections mechanically:

```text
Purpose: Analysis question and scope.
Input: Required files, key formats, data sources or versions.
Method: Confirmed methods, actual parameters, and their location in code.txt or how they are passed.
Run: Working directory, entry point command, software and package versions, required environment and dependencies.
Output: Core products and necessary interpretation, including valid empty results.
```

For server snapshots, `readme.md` must also briefly record the following. In Input, distinguish local files, links, and inputs not downloaded; centralize key original server paths, sources, and access status. In Method, identify the existing script or log supplying commands or parameters. In Run, state the interpreter, working directory, overridable paths, and known missing dependencies; distinguish restored, not fully restored, and verified execution. In Output, list core results and corresponding logs. For information that existing records cannot establish, write "cannot be confirmed from existing records." Do not guess or create a separate provenance report.

Do not explain code line by line, copy entire terminal logs, or write agent reasoning, self-checks, change reports, or "task completed" statements.

Do not generate `review.md`, `audit.md`, `summary.md`, `report.md`, `checklist.md`, `agent_log.md`, duplicate environment reports, or extra execution logs by default. This limits unnecessary new products; it does not authorize deleting existing files or waiving explicit delivery requirements.

Prefer merging data descriptions, field definitions, parameter explanations, versions, environments, and necessary diagnostic evidence into `readme.md`. Native software logs are actual script products and may remain in `output/`; agent work records are not program products. If the user explicitly requests an independent review report, formal data dictionary, or reproduction materials for submission, deliver them for the specified purpose and location, and explain the explicitly requested structural exception. Do not extend all four-item layouts on that basis.

Distinguish program execution evidence from agent self-reports. Do not discard software logs, failure diagnostics, or necessary verification information merely because they are record files.

## 8. Internal Checks Before Delivery

Confirm that task boundaries and reference methods were not changed without authorization, and raw data and unrelated changes are preserved. Establish the main entry point and environment. Complete necessary execution and content checks for executed parts; complete placement and evidence checks for organization-only parts and mark them as not rerun. Ensure the README matches actual methods and execution, outputs do not mix old and new results, and current temporary files are handled safely.

For new or organized stages, list top-level items including hidden items. Confirm `input/`, `output/`, `code.txt`, and `readme.md` are present; any other items must be existing environment metadata that must remain in place or explicitly requested exceptions. Check that `input/` contains only data or valid links, execution logic is centralized in `code.txt`, and explanations are in `readme.md`. Check that `output/` contains only stage script products, without default `runs/` history, management state, or agent records, and that staging files from successful runs have been removed. Missing inputs or logs-only snapshots do not justify omitting the four items. Passing structure checks does not establish that missing inputs have been supplied or the entry point has been fully reproduced.

Check structure, entry point, execution, and result status separately under Section 6, then provide result locations, completion status, brief validation evidence, and remaining limits. The presence of all four names does not establish entry point usability. Do not generate another check report merely to demonstrate compliance with this convention.

## 9. Existing Runner Compatibility

New four-item layouts execute and check the stage directly through `code.txt`. Do not add configuration files, persistent execution state, or a multistage orchestrator by default. The [Minimal Example](assets/minimal/readme.md) uses one script to produce a table and supporting figures from input data, run with `python code.txt`.

The repository retains `scripts/analysis_workflow.py` only for existing runner workflows whose continued maintenance the user explicitly authorizes. Its JSON configuration, stage receipts, dependency plans, and recovery state differ from the default layout for new stages. Tool availability does not justify creating `input/workflow.json`, `input/src/`, or `output/.analysis-state/`, or combining independent analysis stages for compatibility. Read-only checks also require an existing contract; do not create configuration merely to use a checker.

Before maintaining an integrated workflow, read [Tool Reference](references/tools.md). Identify existing configuration, source code, output, and state locations; retain necessary dependencies and recovery capabilities; document actual differences in the README. The optional runner requires Python 3.11+ and uses the standard library. Do not automatically install environments, migrate layouts, or delete old receipts. If such a project must be organized into a new four-item layout, adapt the stage script within the corresponding authorization. Renaming directories alone does not meet the requirements.

The runner's plan, skip, or file-existence checks do not establish that the analysis ran in the current attempt. Incomplete configuration cannot reveal hidden dependencies or scientific criteria. After timeouts or incomplete recovery, first confirm that the original process and its child programs have stopped, then follow the tool reference; do not automatically release locks. Protected replacement covers only its declared scope. It does not isolate arbitrary script writes or guarantee atomic commits across the workflow or recovery after power loss. Set verification strength for large files according to actual reproduction requirements; do not automatically weaken it based on size or treat old checksums as current validation.
