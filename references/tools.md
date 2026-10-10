# Existing Workflow Compatibility Tools

This page documents the file-checking, protected execution, receipt, and dependency-rerun interfaces in `scripts/analysis_workflow.py` for existing workflows whose maintenance the user has explicitly authorized. Its configuration, auxiliary source, multistage, and persistent-state layouts are compatibility interfaces, not templates for four-entry analysis stages. Follow [SKILL.md](../SKILL.md) for stage boundaries, file roles, flat outputs, and direct `code.txt` execution. Do not integrate the runner into new analyses by default or automatically migrate or delete existing configuration, locks, or execution evidence. Preserve original data, unrelated files, required environment metadata, and working Snakemake, Nextflow, Makefile, or similar workflows within the requested maintenance scope.

The runner requires Python 3.11 or later and uses only the standard library. Bash, R, and other programs must already be configured in the user's environment. The tool neither installs software nor selects statistical methods.

## Integration and commands

First check whether the existing scripts accept an output directory and parameters. The replacement protection described here applies only if the script writes all artifacts from the run to the designated temporary directory.

For a project using the runner, retain its configuration location and explicitly pass its actual project root with `--root`. Inputs, source, and commands are resolved against that root; final artifacts are in `output/` and state is in `output/.analysis-state/`. Existing projects may use `input/workflow.json` and auxiliary source files. The tool neither creates analysis-stage directories nor automatically splits multistage workflows.

Omitting `--root` resolves the project root to the configuration's directory. If that directory is `input/`, pass the actual project root explicitly. A runner stage is a set of artifacts updated together and may be finer than an independently executable analysis stage. When reorganization is requested, identify analysis inputs, objectives, outputs, and entry points rather than creating one directory per runner stage.

The following compatibility commands run from the existing project root. Replace configuration placeholders with the project's existing paths. Use the existing entry point and commands documented in `readme.md` for routine execution. Use Python from the project environment and replace `<skill>` with the actual skill directory. In PowerShell, use the call operator `&` for interpreter paths that are absolute or contain spaces.

```text
python <skill>/scripts/analysis_workflow.py check <existing-check-config> --root .
python <skill>/scripts/analysis_workflow.py plan <existing-workflow-config> --root .
python <skill>/scripts/analysis_workflow.py run <existing-workflow-config> --root .
python <skill>/scripts/analysis_workflow.py run <existing-workflow-config> --root . --target plot
python <skill>/scripts/analysis_workflow.py run <existing-workflow-config> --root . --force --target analysis
```

- `check`: read-only checks of explicitly declared files. Paths default to the check configuration's directory; `--root` overrides the base. Fingerprints are also computed when explicitly configured.
- `plan`: reports `run/skip` and reasons for each stage without writing project files or running analyses. It executes declared version-query commands, which must be reviewed and have no write side effects.
- `run`: executes outdated stages in dependency order. A failed stage stops subsequent execution and returns a nonzero status.
- `--target`: repeatable; includes each selected stage and all its upstream dependencies, **not its downstream stages**. After an upstream-only rerun, unchanged downstream stages are marked outdated in the next full `plan`.
- `--force`: reruns the selected stage set. Without a target, all stages are selected.
- CLI exit codes are 0 for success, 1 for configuration, check, or execution failure, and 130 for interruption. Successful receipts record the analysis command's exit code; nonzero exits produce failure evidence.

The [minimal example](../assets/minimal/readme.md) demonstrates direct `code.txt` execution. Repository tests exercise synthetic runner interfaces and failure behavior; they do not represent real research results.

## File-check configuration

A standalone check configuration has one top-level field, `files`. An existing project may store it at `input/checks.json`:

```json
{
  "files": [
    {
      "path": "input/data.tsv",
      "columns": ["id", "group", "value"],
      "unique": ["id"],
      "numeric": {"value": {"min": 0, "allow_missing": false}},
      "min_rows": 1
    }
  ]
}
```

Each file rule supports:

| Field | Meaning |
|---|---|
| `path` | Required relative path using forward slashes. Absolute paths, `..`, and Windows reserved names are rejected. |
| `fingerprint` | sha256 (default), stat, or external; see below. |
| `checksum/verify_checksum` | Only for external mode. A checksum-file path is required; recomputation defaults to false. |
| `validation` | exists, header, or full. When omitted, the existing behavior is full for tables and exists for other files. |
| `allow_empty` | Defaults to false. Set true explicitly to allow a zero-byte file; a positive min_rows still fails. Tables should normally retain a header rather than use this option to conceal missing content. |
| `columns` | Required columns; additional columns are allowed. Headers cannot be blank or duplicated. |
| `unique` | Unique-key columns. Multiple columns form a composite key. Values are trimmed before checking; blank keys fail. To require each column to be unique independently, use separate rules. |
| `numeric` | Numeric constraints by column: min, max (inclusive), and allow_missing. Missing values, NaN, infinity, and nonnumeric values are rejected by default. When missing values are allowed, empty strings, NA, N/A, and null are recognized case-insensitively. |
| `min_rows/max_rows` | Data-row bounds, excluding the header. Zero rows are allowed by default. Do not set thresholds from guessed result counts. |
| `delimiter` | Single-character delimiter; comma for CSV and tab for TSV by default. |
| `encoding` | Defaults to utf-8-sig, supporting UTF-8 BOM. Specify other encodings from the actual input. |

Without an explicit validation level, csv/tsv files or files declaring table fields use full; other files use exists. Full validation requires each row's field count to match the header. It reports at most 20 errors per file but still scans the whole file. Unique checks retain a set of observed keys; assess memory cost for large tables. Existence and header checks do not enable unique checks automatically, but file size is not a reason to omit uniqueness validation required by the scientific task.

A header-only table with no significant results may pass when no positive min_rows is declared. A nonempty plot file does not prove that the image is valid; render it separately and check the figure and its scientific meaning. The tool does not infer statistical methods or unit semantics, compare sample sets across tables, or discover all parameters.

## Fingerprint modes and validation levels

Checks are not weakened automatically based on file size. `fingerprint` and `validation` are independent: `validation: exists` reduces content validation, but plan/run still reads the entire file to compute a hash if fingerprint remains sha256.

| fingerprint | Behavior | Receipt meaning |
|---|---|---|
| `sha256` (default) | Reads the entire file to compute SHA-256. | `content_verified: true` means a content digest was computed in this check, not that the scientific content is correct. |
| `stat` | Reads only file size and modification time in nanoseconds. | `content_verified: false`; changes preserving both size and modification time may be missed. |
| `external` | Reads an existing checksum file and records data size and modification time. | References the checksum by default, with `content_verified: false`; it does not establish that the current data matches the checksum. |
| `external` + `verify_checksum: true` | Reads all data again and compares the existing MD5/SHA-256. | Records `content_verified: true` only after a match. This is full verification and does not reduce data reading. |

Code, configuration, and command interpreters still use strict SHA-256. A path declared as both code and input cannot use a weaker input fingerprint. Modes can be selected for both inputs and outputs. The plan's `weaker_fingerprints` lists paths using weaker modes.

For a large file where lower-cost change detection is explicitly acceptable:

```json
{
  "path": "input/sample.bam",
  "fingerprint": "stat",
  "validation": "exists"
}
```

To reference an existing checksum file:

```json
{
  "path": "input/sample.fastq.gz",
  "fingerprint": "external",
  "checksum": "input/sample.fastq.gz.sha256",
  "verify_checksum": false,
  "validation": "exists"
}
```

The checksum path and data path use the same base directory. A checksum file must be no larger than 64 KiB and contain exactly one GNU md5sum/sha256sum-format record: a 32- or 64-character hexadecimal digest, one space, a space or asterisk, and a filename. Resolve the filename relative to the checksum file's directory; it must identify the declared data file. UTF-8 BOM is supported. Bare digests, multiple-file lists, incorrect filenames, and unparseable content are rejected.

For external mode on outputs, the checksum must also be an explicitly declared output of the same stage. It is staged, validated, and published with the data. An input checksum produced by another stage also requires the corresponding upstream dependency. Changes to external checksum content affect rerun decisions.

| validation | Checks performed | Row count |
|---|---|---|
| `exists` | Exists, is a regular file, and is nonzero in size unless explicitly allowed to be empty. | null for nonempty files, indicating no scan. |
| `header` | Additionally checks the header and required columns without traversing data rows. | null. |
| `full` | Header, field counts, row count, and declared numeric/unique rules. | Data-row count after a complete scan; null on a parsing failure, with rows_scanned recorded separately. |

For configuration compatibility, omitted validation defaults to full for CSV/TSV or files with table rules, and exists otherwise. Explicit full/header treats a file as a text table. Exists rejects columns, delimiter, numeric, unique, min_rows, and max_rows; header rejects numeric, unique, and row-count rules. Conflicts raise errors rather than silently skipping checks. Declaring only columns does not require every row to be nonempty; numeric and missing-value requirements needed for the scientific task must still be configured explicitly.

Check results and successful receipts contain `validation`, `completed_checks`, `not_performed`, `rows`, and `rows_scanned`. completed_checks identifies executed checks; use ok/errors to determine whether they passed. Undeclared numeric/unique checks also appear in not_performed. An explicitly allowed zero-byte file records rows=0 without claiming header or numeric checks were performed.

Standalone check performs validation without fingerprinting by default. It returns fingerprint evidence only when a file rule explicitly includes fingerprint. verify_checksum=true reads and verifies the data. For a faster check, select both an appropriate validation level and fingerprint mode.

### Caching, recovery, and version compatibility

Within a single read-only check phase, a complete hash is reused for the same real path, file identity, size, and time metadata. This avoids rereading an intermediate result used both as an output and a downstream input. The cache is not persistent and is not reused across analysis execution; pre-run and post-run checks still detect changes independently. Even within a phase, caching relies on filesystem metadata reflecting concurrent changes; it does not defend against external writes that deliberately preserve metadata.

Run reevaluates each stage. Plan marks downstream stages for rerunning when an upstream rerun is scheduled and defers checking data that has not yet been updated. Independent stages are still checked, and target selection keeps its existing semantics. Forced reruns still perform normal input and environment checks first.

**Recovery logs always retain separate, strict SHA-256 verification.** Even when outputs use stat or external, an existing final file is fully hashed before replacement and its backup is verified during recovery. This reading cost remains; lower-cost modes do not eliminate all reading of large files.

The workflow configuration remains version 1 and retains compatibility with existing configurations and strict defaults. New fields require the newer tool. Successful receipts use version=2. Older receipts cannot justify skipping: the first run marks their stages for rerunning, preserving old results and receipts until success. The recovery-log format still supports strict verification; protection and recovery of old root-level state are described below. Do not "upgrade" a receipt by manually changing its version number.

Changes to fingerprint modes, validation levels, or rules change stage signatures and trigger reruns and required downstream updates. Cost tests use synthetic data, read counts, and simulated large-file metadata; they are not real 100 GB throughput tests.

## Workflow configuration

The workflow configuration has the top-level structure `{"version": 1, "stages": [...]}`.

| Field | Required | Description |
|---|---|---|
| `id` | Yes | Starts with a lowercase letter, followed by lowercase letters, digits, underscores, or hyphens; at most 64 characters. |
| `command` | Yes | Nonempty argv array with no implicit shell. The executable is an absolute path, a path relative to the root, or a name on PATH. |
| `code` | Yes | Explicit relative paths of source, configuration, environment lockfiles, and other files affecting the stage. At least one is required; import/include dependencies are not scanned automatically. |
| `inputs` | No | Array of file-check rules, with paths relative to the project root. Missing inputs mark the plan outdated and fail checks before execution. |
| `outputs` | Yes | Array of file rules, with paths relative to the temporary or final output directory; omit the `output/` prefix. |
| `depends` | No | Upstream stage IDs. Cycles, unknown dependencies, and duplicates are rejected. |
| `params` | No | Stage parameter object, empty by default. The code must actually read it rather than maintain separate hidden parameters. |
| `versions` | No | Tool names mapped to version-query argv arrays. A query fails on a 15-second timeout or nonzero exit. |
| `timeout` | No | Positive limit in seconds for the main analysis process; omitted means no timeout. This is not a cluster-job monitor. |

Unknown fields are rejected to prevent ignored misspellings. Inputs and source files may refer to external files through project links. Output and state path components cannot be symbolic links, Windows junctions, or reparse points. `output/.analysis-state/` is reserved for the runner; outputs cannot declare `.analysis-state` or files beneath it, including case variants.

Stages cannot declare the same output, case variants, or conflicting file/directory prefixes. A stage reading `output/x` must declare its producer as an upstream dependency; transitive dependencies are allowed. Implicit dependencies involving aliases, links, directory datasets, or network resources are not inferred automatically. Declare actual dependencies explicitly; if that cannot be done completely, a skip decision does not establish result validity.

Command arguments support three literal substitution tokens:

- `{python}`: the Python interpreter running this tool.
- `{root}`: the absolute project-root path.
- `{output}`: the absolute temporary output path dedicated to this stage run.

The analysis process also receives:

- `ANALYSIS_ROOT`: the root directory.
- `ANALYSIS_OUTPUT_DIR`: the output directory for this run.
- `ANALYSIS_PARAMS`: a JSON string of the current stage parameters.

Python can use `json.loads(os.environ["ANALYSIS_PARAMS"])`. R can use the project's existing JSON parser or receive parameters through an existing interface; do not install a dependency for this by default. Bash must quote variables correctly and propagate errors, commonly with `set -euo pipefail`, while still checking its semantics and called programs' exit status.

`command` is part of the executable-code authorization scope. Do not execute untrusted configuration merely because it is presented as data. Parameters and version outputs enter receipts and must not contain secrets. The tool does not collect the full set of environment variables.

## Protected execution and failure recovery

A stage run proceeds as follows:

1. Validate declared inputs and record source, inputs, parameters, environment-query results, and interpreter identity.
2. Run in an empty `output/.analysis-state/transactions/<run_id>/output/` directory.
3. Check each declared artifact and recheck whether inputs, source, or environment changed.
4. Replace artifacts and the successful receipt in one recovery transaction, saving each original file before individual replacement.
5. Remove this run's dedicated temporary directory after success, retaining the latest successful receipt.

Only files explicitly listed in outputs are replaced; other output files are retained. Undeclared temporary artifacts generated by the script are not published and are removed with the temporary directory after success. Removing or renaming an outputs declaration does not delete old final files; handle those separately within user authorization.

- Nonzero command exit, missing artifact, or content-validation failure: final outputs and the previous successful receipt remain unchanged; temporary results and failure.json are retained.
- Replacement error: immediately attempt to restore previous valid artifacts and receipts. If restoration fails, retain the lock, transaction log, and backups.
- Forced termination, timeout, or interruption: a lock may remain. **Confirm that the tool and its child programs have stopped** before running:

```text
python <skill>/scripts/analysis_workflow.py recover <existing-workflow-config> --root . --confirm-stopped
```

This flag is an explicit operator confirmation of process state, not something inferred from a wait timeout. Recover uses transaction logs to restore unfinished replacements and verifies backup content. Missing or corrupt backups are not reported as successful recovery. Completed recovery can be repeated. Even with damaged configuration content, the original configuration path and consistent `--root` can locate the project root for recovery. Failure and staging evidence is retained by default; after diagnosis, clean only exact paths confirmed to belong to that run.

Protection scope and limits:

- The runner relies on cooperation from the scripts; **it does not isolate arbitrary file writes**. First fix scripts that hard-code final output paths, modify original inputs, background themselves, or swallow child-process errors. Do not claim the runner prevents those behaviors.
- Timeout management covers the direct child process and does not guarantee termination of grandchildren or cluster jobs. Verify that they have stopped before recovery.
- Replacement protection covers one stage's declared file set. A later stage failure does not undo earlier successful stages; old downstream results are marked outdated in plan.
- Multiple-file replacement can briefly expose mixed old and new files. Ordinary readers do not automatically respect the lock. If a complete set must be read consistently, pause consumers and check the lock and successful receipt. The tool does not promise database transaction semantics, durability after power loss, or network-filesystem atomicity.
- lock.json prevents concurrent writes by this tool to the same project root. Old locks are not removed automatically, and third-party writes are not prevented.
- Managed state is maintained only by the tool. Do not edit transaction logs manually or use it as a user-documentation directory.

### Old root-level state directory

If an older root-level `.analysis-state/` is detected, plan, run, and default recover fail. They do not ignore old locks or transactions or automatically migrate or delete evidence. Confirm that the original process and its child programs have stopped, verify the old configuration and project root, then explicitly recover the old state:

```text
python <skill>/scripts/analysis_workflow.py recover <existing-config> --root <existing-project-root> --legacy-state --confirm-stopped
```

If both old and new state directories exist, old-state recovery also refuses to proceed. Identify the runs they belong to; do not remove the conflict by deleting locks or overwriting directories. Successful recovery does not migrate the layout. Old receipts, failure evidence, and completed transactions may contain old paths, so moving directories does not necessarily allow continued reuse. Once no unfinished transactions remain, handle compatibility state within the authorized maintenance scope; unhandled old state continues to block the runner. For an authorized reorganization into four-entry stages, preserve necessary recovery evidence and adapt a direct script entry point according to [SKILL.md](../SKILL.md).

## Receipts and rerun decisions

`output/.analysis-state/receipts/<stage>.json` stores the stage's latest successful run:

- run_id, start and end times in UTC, expanded command, and exit code;
- actual input fingerprint modes and evidence, source SHA-256 and size, and all declared parameters and validation rules;
- tool version-query commands and outputs, runner hash, Python version, platform, and command-interpreter path and hash;
- upstream successful run IDs, artifact fingerprints and sizes, and input/output validation levels, completed checks, and checks not performed.

Receipts record this tool's execution evidence. The tool retains only the latest successful receipt by default, not a complete history. To reproduce historical results, preserve the original input versions, code, environment declarations, and outputs as the project requires. Receipts cannot restore original data or prove that every declared parameter was actually used.

Reruns are required when there is no valid receipt; inputs, code, parameters, environment, validation requirements, or the runner have changed; outputs are missing or modified; or an upstream rerun is scheduled or its successful run ID changes. An upstream run ID change conservatively invalidates downstream stages even when the new output bytes are identical.

If a configuration distinguishes plot and analysis, update plot params for changes only to figure parameters and keep analysis parameters in analysis params. Plot parameter changes alone do not define independent analysis-stage boundaries. Changing a shared source file reruns every runner stage declaring it; the tool does not infer semantic differences in code.

Full SHA-256 may take substantial time for large data. Explicit stat/external modes record weaker evidence as described above; timestamps or referenced digests are not verification of current content. Environment comparisons cover only declared version queries, listed environment files, and the actual command interpreter. They do not guarantee detection of undeclared dependencies or software differences under the same version number. Declare a seed in params for randomized steps and ensure the code uses it. Bit-for-bit reproducibility across hardware is not guaranteed.

## Development validation

```text
python -B -m unittest discover -s <skill>/tests -v
```

Compatibility-tool tests use synthetic data and isolated temporary directories. They cover failure protection, replacement and recovery faults, data rules, environment changes, dependency reruns, validation levels, fingerprint-strength boundaries, cache invalidation, and old-receipt migration. A symbolic-link test is skipped when Windows permissions prevent link creation; separate tests exercise Windows junctions. These tests do not establish validation on real GWAS or R/Bash analyses, or on all operating systems.

Resource and path tests across client installation layouts run with the suite. See [client integration](agents.md) for post-installation client validation.
