"""Actual R subprocess checks; no downloads or system-library changes."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

RSCRIPT = os.environ.get('TEST_RSCRIPT') or shutil.which('Rscript')
HELPER = Path(__file__).resolve().parents[1] / 'scripts/r_environment.R'

@unittest.skipUnless(RSCRIPT, 'Rscript unavailable; set TEST_RSCRIPT to test R support')
class REnvironmentTests(unittest.TestCase):
    def run_r(self, body):
        with tempfile.TemporaryDirectory(prefix='r env ') as directory:
            script = Path(directory) / 'check.R'
            script.write_text('source("' + HELPER.as_posix() + '")\n' + body, encoding='utf-8')
            return subprocess.run([RSCRIPT, '--vanilla', str(script)], cwd=directory,
                                  capture_output=True, text=True, errors='replace', timeout=60)

    def test_base_packages(self):
        r = self.run_r("x <- require_r_environment(c('stats','utils')); stopifnot(all(x$status == 'ok'))")
        self.assertEqual(r.returncode, 0, r.stdout+r.stderr)

    def test_missing_blocks_analysis(self):
        r = self.run_r("require_r_environment('SkillMissingPackageXyz123'); cat('ANALYSIS_STARTED')")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('missing', r.stdout)
        self.assertNotIn('ANALYSIS_STARTED', r.stdout)

    def test_version_mismatch(self):
        r = self.run_r("require_r_environment('stats', versions=c(stats='0.0.0'))")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('version_mismatch', r.stdout)

    def test_configured_library(self):
        r = self.run_r("dir.create('project library'); require_r_environment('stats', library='project library'); stopifnot(.libPaths()[1] == normalizePath('project library', winslash='/'))")
        self.assertEqual(r.returncode, 0, r.stdout+r.stderr)

    def test_missing_library_not_created(self):
        r = self.run_r("tryCatch(require_r_environment('stats', library='absent'), error=function(e) cat(conditionMessage(e))); stopifnot(!dir.exists('absent'))")
        self.assertEqual(r.returncode, 0, r.stdout+r.stderr)
        self.assertIn('Library does not exist', r.stdout)

    def test_load_error_preserved(self):
        # Malformed installed-package fixture, not a missing package.
        r = self.run_r("dir.create('lib'); dir.create('lib/BrokenFixture'); writeLines(c('Package: BrokenFixture','Version: 1.0','Title: Fixture','Description: Broken fixture.'), 'lib/BrokenFixture/DESCRIPTION'); x <- check_r_environment('BrokenFixture', library='lib'); stopifnot(x$status == 'load_error', nzchar(x$detail))")
        self.assertEqual(r.returncode, 0, r.stdout+r.stderr)

    def test_existing_packages_do_not_install_or_connect(self):
        r = self.run_r("dir.create('lib'); install.packages <- function(...) stop('INSTALL_CALLED'); install_missing_r_packages('stats', 'lib', 'https://invalid.example')")
        self.assertEqual(r.returncode, 0, r.stdout+r.stderr)

    def test_install_failure_cannot_pass(self):
        # Simulates offline installer: checks post-install verification, not network.
        r = self.run_r("dir.create('lib'); install.packages <- function(...) warning('offline fixture'); install_missing_r_packages('SkillMissingPackageXyz123', 'lib', 'https://invalid.example')")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('offline fixture', r.stderr)
        self.assertIn('preflight failed', r.stderr)

if __name__ == '__main__':
    unittest.main()
