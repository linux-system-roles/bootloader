Changelog
=========

[1.0.3] - 2024-02-26
--------------------

### Bug Fixes

- fix: Fix the role for UEFI systems (#90)

[1.0.2] - 2024-02-26
--------------------

### Bug Fixes

- fix: Fix bug with extra spaces in variables (#88)

[1.0.1] - 2024-02-09
--------------------

### Bug Fixes

- fix: Modify grub timeout in grub config directly (#86)

  Enhancement: Modify grub timeout in grub config directly
  
  Reason: On RHEL 7, rebuilding grub config with grubby2-mkconfig has a bug that returns previously removed kernels
  
  Result: This workaround doesn't require rebuilding grub config and hence avoids the bug

### Other Changes

- ci: bump codecov/codecov-action from 3 to 4 (#84)

- ci: fix python unit test - copy pytest config to tests/unit (#85)

  This is fixed by tox-lsr 3.2.2 - all actions that use tox-lsr are updated to
  3.2.2, not just the python unit tests, even though the fix is only related to
  pytest.  All roles are updated to use tox-lsr 3.2.2 for the sake of consistency
  even if not affected by the pytest issue.
  
  Something changed recently in the way github actions provisions systems which
  means some of the directories are not readable by the python unit test actions.
  In addition, the python unit tests were causing a lot of unnecessary directory
  traversal doing collection/discovery of unit test files, because of using
  `pytest -c /path/to/tox-lsr/pytest.ini` Unfortunately, with `pytest`, the
  directory of the config file is the root directory for the tests and tests
  discovery, and there is no way around this.
  
  Therefore, the only solution is to copy the tox-lsr `pytest.ini` to the
  `tests/unit` directory, which makes that the test root directory.
  
  See also https://github.com/linux-system-roles/tox-lsr/pull/160
  
  Signed-off-by: Rich Megginson <rmeggins@redhat.com>


[1.0.0] - 2024-01-09
--------------------

### New Features

- feat: Initial release of bootloader role (#71)
