Changelog
=========

[1.0.7] - 2024-07-02
--------------------

### Bug Fixes

- fix: add support for EL10 (#109)

### Other Changes

- test: Skip hosts on s390x. Asserting error doesn't work due to a bug (#107)
- ci: ansible-lint action now requires absolute directory (#108)

[1.0.6] - 2024-06-11
--------------------

### Bug Fixes

- fix: Set user.cfg path to /boot/grub2/ on EL 9 UEFI (#101)

### Other Changes

- ci: use tox-lsr 3.3.0 which uses ansible-test 2.17 (#102)
- ci: tox-lsr 3.4.0 - fix py27 tests; move other checks to py310 (#104)
- ci: Add supported_ansible_also to .ansible-lint (#105)

[1.0.5] - 2024-04-22
--------------------

### Bug Fixes

- fix: Fail on the s390x architecture with a not supported msg (#96)

### Other Changes

- refactor: Refactor bootloader_settings to run cmds from functions, use mock in unittests (#97)

[1.0.4] - 2024-04-04
--------------------

### Bug Fixes

- fix: Add /etc/default/grub if missing (#93)

### Other Changes

- ci: bump ansible/ansible-lint from 6 to 24 (#92)
- ci: bump mathieudutour/github-tag-action from 6.1 to 6.2 (#94)

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

### Other Changes

- ci: bump codecov/codecov-action from 3 to 4 (#84)
- ci: fix python unit test - copy pytest config to tests/unit (#85)

[1.0.0] - 2024-01-09
--------------------

### New Features

- feat: Initial release of bootloader role (#71)
