# Environment Checks, Recovery, and Analysis Entry Points

1. Use the project's existing environment and specified interpreter. Without a project convention, resolve and verify the interpreter from the user's configuration, then PATH. Report an unavailable specified path rather than silently switching. Do not scan entire disks or hard-code the author's paths.
2. On the execution side, verify the system, architecture, interpreter version and location, input readability, output writability, and required external programs. A pure R analysis does not need the Python runner; do not assume Bash is available on Windows.
3. For R, check R.home(), .libPaths(), individual package versions, and loading errors. Cross-check dependencies against the project's code and declarations, including dynamically loaded packages. Do not make example packages such as rMVP mandatory for every project. Distinguish a missing runtime, a package absent from the active libraries, loading failure, version conflict, and permission error.
4. Continue when the environment is usable. Add an omitted library path only after verifying compatibility with the current R and architecture. Do not copy binary libraries from another system. Use the same R and library configuration for checks, installation, and analysis.
5. Restore dependencies, recheck, and continue within existing authorization. If installation is not authorized, identify the packages, sources, destination, and operation, pausing only dependent work. Do not request an existing approval again or automatically upgrade packages, change system settings or methods, or upload data.

## Verify both the interpreter and package libraries

A fixed Rscript path fixes the runtime, not the libraries. Before first execution, resolve the interpreter from the project environment, the user's configuration, then PATH, and record its absolute path. Reuse that path and startup configuration for checks, recovery, and analysis. In `readme.md`, document the verified command and working directory, including how Rscript was resolved rather than only naming a bare `Rscript`. Keep machine paths and environment descriptions in `readme.md`; let `code.txt` receive required execution paths through arguments or environment variables. Do not create separate documentation or configuration files or embed machine-specific paths in the general skill. Do not parse `readme.md` as configuration. Report an unavailable specified path without silently switching to another R installation.

In the failing execution environment, record R.home(), R.version.string, .libPaths(), the working directory, the library-related R_LIBS, R_LIBS_USER, and R_LIBS_SITE variables, and whether the project environment is active. Distinguish the startup directory from a directory later selected with setwd(); setwd() does not rerun startup configuration. Check whether startup arguments bypass .Rprofile/.Renviron. A check with --vanilla cannot substitute for an entry point that relies on those files. Do not expose unrelated environment variables or credentials from configuration.

## Handling preflight failures

- Package absent from active libraries: verify the interpreter, execution account, project activation, and declared library directories. If previous environments or installation records exist, check only candidate locations supported by that evidence; do not scan the entire disk. A package in another library is not necessarily compatible. Do not merge old version-specific libraries without checking. After repairing paths, recheck through the same entry point.
- Package present but loading fails: preserve the original error and investigate missing dependencies, DLL or system dependencies, version conflicts, and permissions. Do not label every failure as a missing package or begin with reinstallation.
- Follow the authorization rules below for installation or recovery. If running the analysis is already authorized, continue after recovery and successful rechecking. A request only to organize files does not authorize analysis execution during dependency checks.
- Complete required checks that do not depend on the failure. List established blockers separately from unchecked conditions. Do not call an issue the only blocker unless other runtime conditions have been checked. Local success or failure does not establish the cause of a remote failure.

Add the minimum diagnostic evidence to the existing README: the interpreter and startup command, active libraries, package status and relevant original errors, attempted recovery and recheck results, and any remaining specific operations. Mark unverified execution conditions as "not verified"; a status summary is not the original error. Report completed organization separately from blocked analysis.

## Executable R preflight

Before analysis code in `code.txt`, source `scripts/r_environment.R` from the loaded skill installation and call require_r_environment. An existing equivalent project preflight may be reused. Resolve skill_root from the loaded location and pass it to the entry point through an explicit argument or environment variable. Do not copy auxiliary code into `input/src/` or hard-code the author's paths. For a standalone delivery without access to the skill tools, include the required preflight logic in `code.txt` and document dependencies and execution in `readme.md`.

```r
source(file.path(skill_root, 'scripts', 'r_environment.R'))
# Interface example only; use this project's actual dependency list.
require_r_environment(c('stats', 'utils'))
# Run this entry point's analysis code after preflight succeeds.
```

check_r_environment returns individual package status without exiting for missing packages. require_r_environment raises an error on any failure, which must propagate to the process exit code. Pass an existing library directory through `library`; use `versions`, for example `versions=c(package='verified-version')`, for exact version checks. Do not catch errors and continue the analysis.

The default check does not access the network or create directories; package loading may run initialization code. writable_hint is only a permission hint. The script does not discover R, infer dependencies, or determine the system's build environment. Library settings remain active in the current process. A separate R process must activate the same environment or configure the libraries again.

## Recovery

- Existing renv or similar environment: use its existing activation and lockfile restoration rather than bypassing the lockfile with a general installer. Recheck in a new R process after restoration. Preserve verified versions, source repositories, and pinned commits.
- No lockfile and installation authorized: create a specified project or user library and call install_missing_r_packages(packages, library, repos) with the same R and an explicit repository. Request only missing packages and their required dependencies. Dependency resolution may introduce other versions; this function is not a version-restoration tool and offers no rollback on failure. Before delivery across machines, verify required versions and the environment and document them in `readme.md`. Maintain existing lockfiles; create a new one only when the user explicitly requests it, not by default for each stage.
- Installed package fails to load or has a version conflict: diagnose from the original error. If needed and authorized, create a new isolated environment rather than reinstalling without evidence. Report network, mirror, system-library, and compiler errors separately. Do not automatically change sources or remove installation locks.
- Offline: reuse a compatible, verified cache. Without one, report the blocker. renv does not install R itself or all system dependencies. A container or remote environment may be proposed for complex system requirements, but do not deploy, upload, or incur costs by default.

## Layout and validation

Environment exceptions to the four-part stage layout are limited to existing environment files that must remain in place, such as .Rprofile, renv.lock, renv/, and .venv, or new environment-tool metadata explicitly requested by the user. Explain their purpose in `readme.md`; do not delete or damage an existing environment to simplify the directory. Prefer the overall project's environment rather than creating a lockfile or environment directory for each stage. Keep software and package versions, dependency descriptions, and installation or recovery instructions in `readme.md`, without additional configuration or environment-description files in `input/`. Package libraries and caches are neither research inputs nor results; do not put them in input/output or copy machine-specific libraries into a release package.

Report validation separately for directory relocation, actual R preflight and failure blocking, isolated-library recovery, each system and architecture, and real clients. Simulated errors test control flow, not live network installation or cross-platform validation. Claim support only where evidence exists.

References: [R library search paths](https://stat.ethz.ch/R-manual/R-devel/library/base/html/libPaths.html), [renv and its scope](https://rstudio.github.io/renv/articles/renv.html).
