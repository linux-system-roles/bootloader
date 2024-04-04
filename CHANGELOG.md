Changelog
=========

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
