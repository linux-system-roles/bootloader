Changelog
=========

[1.1.4] - 2025-08-08
--------------------

### Other Changes

- test: Skip all tests on s390x, avoid redundant clean ups (#158)

[1.1.3] - 2025-08-02
--------------------

### Other Changes

- test: test for boolean values and null values are not allowed (#156)

[1.1.2] - 2025-08-01
--------------------

### Bug Fixes

- fix: boolean values and null values are not allowed (#153)
- fix: Fix Python 2.7.5 compatibility by using msg= in fail_json() calls (#154)

[1.1.1] - 2025-07-15
--------------------

### Other Changes

- docs: Fix wording in README with the help of Cursor AI (#149)

[1.1.0] - 2025-07-02
--------------------

### New Features

- feat: Add ability to configure default kernel (#147)

[1.0.10] - 2025-06-25
--------------------

### Bug Fixes

- fix: Fix removing kernel options with values (#146)

### Other Changes

- ci: Add support for bootc end-to-end validation tests (#144)
- ci: Use ansible 2.19 for fedora 42 testing; support python 3.13 (#145)

[1.0.9] - 2025-05-21
--------------------

### Other Changes

- ci: bump codecov/codecov-action from 4 to 5 (#124)
- ci: Use Fedora 41, drop Fedora 39 (#125)
- ci: Use Fedora 41, drop Fedora 39 - part two (#126)
- ci: Check spelling with codespell (#127)
- ci: ansible-plugin-scan is disabled for now (#128)
- ci: bump ansible-lint to v25; provide collection requirements for ansible-lint (#131)
- refactor: fix python black formatting (#132)
- ci: Add test plan that runs CI tests and customize it for each role (#133)
- ci: In test plans, prefix all relate variables with SR_ (#134)
- ci: Fix bug with ARTIFACTS_URL after prefixing with SR_ (#135)
- ci: several changes related to new qemu test, ansible-lint, python versions, ubuntu versions (#136)
- ci: use tox-lsr 3.6.0; improve qemu test logging (#138)
- ci: skip storage scsi, nvme tests in github qemu ci (#139)
- ci: bump sclorg/testing-farm-as-github-action from 3 to 4 (#140)
- ci: bump tox-lsr to 3.8.0; rename qemu/kvm tests (#141)
- ci: Add Fedora 42; use tox-lsr 3.9.0; use lsr-report-errors for qemu tests (#142)

[1.0.8] - 2024-10-30
--------------------

### Other Changes

- ci: Add tft plan and workflow (#111)
- ci: Update fmf plan to add a separate job to prepare managed nodes (#113)
- ci: bump sclorg/testing-farm-as-github-action from 2 to 3 (#114)
- ci: Add workflow for ci_test bad, use remote fmf plan (#115)
- ci: Fix missing slash in ARTIFACTS_URL (#116)
- ci: Add tags to TF workflow, allow more [citest bad] formats (#117)
- ci: ansible-test action now requires ansible-core version (#118)
- ci: add YAML header to github action workflow files (#119)
- refactor: Use vars/RedHat_N.yml symlink for CentOS, Rocky, Alma wherever possible (#121)

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
