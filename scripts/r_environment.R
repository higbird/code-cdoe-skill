# Source before analysis. Checks need only base R; installation is explicit.
check_r_environment <- function(packages, library = NULL, versions = NULL) {
  if (!is.character(packages) || anyNA(packages) || anyDuplicated(packages) ||
      any(!grepl('^[A-Za-z][A-Za-z0-9.]*$', packages))) stop('Invalid package names')
  if (!is.null(versions) && (is.null(names(versions)) ||
      any(!names(versions) %in% packages))) stop('Versions must name declared packages')
  if (!is.null(library)) {
    if (!dir.exists(library)) stop('Library does not exist: ', library)
    .libPaths(c(normalizePath(library, winslash = '/', mustWork = TRUE), .libPaths()))
  }
  cat('R:', R.version.string, '\nR home:', R.home(), '\nPlatform:', R.version$platform, '\n')
  print(data.frame(path = .libPaths(), writable_hint = file.access(.libPaths(), 2) == 0))
  rows <- lapply(packages, function(p) {
    location <- find.package(p, quiet = TRUE)
    status <- 'missing'; version <- ''
    detail <- 'Not found in active libraries; not evidence of absence elsewhere'
    if (length(location)) {
      status <- 'load_error'
      detail <- tryCatch({
        ns <- loadNamespace(p)
        version <- as.character(getNamespaceVersion(ns))
        location <- getNamespaceInfo(ns, 'path')
        status <- 'ok'
        if (!is.null(versions) && p %in% names(versions) && version != versions[[p]])
          status <- 'version_mismatch'
        if (status == 'ok') '' else paste('Required:', versions[[p]])
      }, error = function(e) conditionMessage(e))
    }
    data.frame(package=p, status=status, version=version,
               path=if(length(location)) location else '', detail=detail)
  })
  result <- if(length(rows)) do.call(rbind, rows) else
    data.frame(package=character(), status=character(), version=character(), path=character(), detail=character())
  print(result, row.names=FALSE)
  invisible(result)
}
require_r_environment <- function(packages, library = NULL, versions = NULL) {
  result <- check_r_environment(packages, library, versions)
  if(any(result$status != 'ok')) stop('R preflight failed; inspect original errors above')
  invisible(result)
}
# Use only with existing installation authorization, and no project lockfile.
install_missing_r_packages <- function(packages, library, repos) {
  if(!is.character(repos) || !length(repos) || anyNA(repos) ||
     any(!nzchar(repos)) || any(repos == '@CRAN@')) stop('Provide explicit repositories')
  if(!dir.exists(library)) stop('Create an authorized project/user library first')
  result <- check_r_environment(packages, library)
  if(any(!result$status %in% c('ok', 'missing'))) stop('Diagnose existing load failures before installing')
  missing <- result$package[result$status == 'missing']
  if(length(missing)) {
    probe <- tempfile('r-library-write-', tmpdir=library)
    on.exit(if(file.exists(probe)) unlink(probe), add=TRUE)
    if(!file.create(probe)) stop('Library not writable: ', library)
    unlink(probe)
    install.packages(missing, lib=library, repos=repos, dependencies=NA)
  }
  require_r_environment(packages, library)
}
